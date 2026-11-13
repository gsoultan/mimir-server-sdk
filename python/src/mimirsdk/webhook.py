"""Check and read the events mimir-server sends to webhooks.

Each delivery is a JSON POST signed with the webhook's secret in a
Mimir-Signature header (``t=<unix seconds>,v1=<hex HMAC-SHA256 of
"<t>.<body>">``). Pass the raw body, before any JSON parsing, to
``parse``::

    from mimirsdk import webhook

    @app.post("/hooks/mimir")
    async def hook(request: Request):
        try:
            event = webhook.parse(SECRET, request.headers.get(webhook.SIGNATURE_HEADER), await request.body())
        except webhook.WebhookError:
            return Response(status_code=401)
        if event.type == webhook.TRAINING_FINISHED:
            print(event.job()["model_id"])
        return Response(status_code=204)

The server retries a delivery for about a day until it gets a 2xx, so the
same event can arrive more than once: use ``Event.id`` to skip repeats.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, TypedDict, Union

SIGNATURE_HEADER = "Mimir-Signature"
# How far a delivery's signed time may be from now, in seconds.
DEFAULT_TOLERANCE = 300.0
# The largest body worth reading.
MAX_BODY_BYTES = 1 << 20

# Event types.
MODEL_CREATED = "model.created"
MODEL_UPDATED = "model.updated"
MODEL_DELETED = "model.deleted"
# Sent, at most once a day for each model, when a model gets clearly fewer
# answers right in use than when trained.
ACCURACY_DROPPED = "model.accuracy_dropped"
TRAINING_QUEUED = "training.queued"
TRAINING_FINISHED = "training.finished"
TRAINING_FAILED = "training.failed"
SCORING_FINISHED = "scoring.finished"
SCORING_FAILED = "scoring.failed"
USER_CREATED = "user.created"
USER_DELETED = "user.deleted"
TEST = "test"


class WebhookError(Exception):
    """A delivery that isn't genuine or can't be read."""


class NoSignatureError(WebhookError):
    def __init__(self) -> None:
        super().__init__("webhook: no Mimir-Signature header")


class BadSignatureError(WebhookError):
    def __init__(self) -> None:
        super().__init__("webhook: the signature doesn't match the body")


class ExpiredError(WebhookError):
    def __init__(self) -> None:
        super().__init__("webhook: the signature is too old or from the future")


def _mac(secret: str, ts: str, body: bytes) -> bytes:
    return hmac.new(secret.encode(), ts.encode() + b"." + body, hashlib.sha256).digest()


def sign(secret: str, body: Union[bytes, str], at: Optional[float] = None) -> str:
    """The Mimir-Signature header value for body at unix time ``at`` (now
    when None), as the server makes it. It is for tests of a receiver."""
    if isinstance(body, str):
        body = body.encode()
    ts = str(int(time.time() if at is None else at))
    return f"t={ts},v1={_mac(secret, ts, body).hex()}"


def verify(secret: str, header: Optional[str], body: Union[bytes, str], tolerance: float = DEFAULT_TOLERANCE) -> None:
    """Check a Mimir-Signature header against the raw body, allowing the
    signed time to be up to ``tolerance`` seconds from now. Returns for a
    genuine delivery; raises NoSignatureError, BadSignatureError or
    ExpiredError otherwise."""
    if not header or not header.strip():
        raise NoSignatureError()
    if isinstance(body, str):
        body = body.encode()
    if tolerance <= 0:
        tolerance = DEFAULT_TOLERANCE
    ts = ""
    sigs: list[bytes] = []
    for part in header.split(","):
        k, _, v = part.strip().partition("=")
        if k == "t":
            ts = v
        elif k == "v1":
            try:
                sigs.append(bytes.fromhex(v))
            except ValueError:
                pass
    try:
        sec = int(ts)
    except ValueError:
        raise BadSignatureError() from None
    if not sigs:
        raise BadSignatureError()
    if abs(time.time() - sec) > tolerance:
        raise ExpiredError()
    want = _mac(secret, ts, body)
    if not any(hmac.compare_digest(want, s) for s in sigs):
        raise BadSignatureError()


class _ModelRef(TypedDict, total=False):
    id: str
    name: str
    architecture: str
    size_bytes: int
    version_id: str


class ModelEvent(TypedDict, total=False):
    """The data of model.created, model.updated and model.deleted."""

    model: _ModelRef
    # Who made the change: an email, or "key <name> (<email>)" for an API
    # key. Empty for a model a training run made.
    actor: str


class JobEvent(TypedDict, total=False):
    """The data of training.queued, training.finished and training.failed."""

    id: str
    name: str
    architecture: str
    dataset: str
    # "queued", "running", "succeeded", "failed" or "cancelled".
    status: str
    epoch: int
    epochs: int
    accuracy: float
    model_id: str
    error: str


class ScoringEvent(TypedDict, total=False):
    """The data of scoring.finished and scoring.failed."""

    id: str
    name: str
    model_id: str
    # The model's name.
    model: str
    # "succeeded", "failed" or "cancelled".
    status: str
    # How many rows the run read, answered, and couldn't answer.
    rows: int
    done: int
    failed: int
    error: str


class _UserRef(TypedDict, total=False):
    id: str
    email: str
    name: str


class UserEvent(TypedDict, total=False):
    """The data of user.created and user.deleted."""

    user: _UserRef
    actor: str


class _Week(TypedDict, total=False):
    answers: int
    feedback: int
    accuracy: float


class AccuracyEvent(TypedDict, total=False):
    """The data of model.accuracy_dropped."""

    model: _ModelRef
    # The last 7 days' answers, the feedback apps sent on them, and the
    # share of that feedback the model got right.
    week: _Week
    # The model's held-out score when trained.
    accuracy: float


@dataclass
class Event:
    """One delivery's body."""

    # The same for every retry of one event.
    id: str
    type: str
    time: Optional[datetime]
    # Depends on type; model(), accuracy(), job(), scoring() and user()
    # return it typed.
    data: dict[str, Any] = field(default_factory=dict)

    def _data(self, prefix: str) -> Any:
        if not self.type.startswith(prefix):
            raise WebhookError(f"webhook: a {self.type} event has no {prefix.rstrip('.')} data")
        return self.data

    def model(self) -> ModelEvent:
        return self._data("model.")

    def accuracy(self) -> AccuracyEvent:
        return self._data(ACCURACY_DROPPED)

    def job(self) -> JobEvent:
        return self._data("training.")

    def scoring(self) -> ScoringEvent:
        return self._data("scoring.")

    def user(self) -> UserEvent:
        return self._data("user.")


def _parse_time(v: Any) -> Optional[datetime]:
    if not isinstance(v, str) or not v:
        return None
    s = v.replace("Z", "+00:00")
    # Python before 3.11 reads at most 6 digits of a fraction.
    if "." in s:
        head, _, rest = s.partition(".")
        n = len(rest) - len(rest.lstrip("0123456789"))
        s = head + "." + rest[:n][:6].ljust(6, "0") + rest[n:]
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def parse(secret: str, header: Optional[str], body: Union[bytes, str], tolerance: float = DEFAULT_TOLERANCE) -> Event:
    """Verify a delivery's signature and decode its body."""
    if len(body) > MAX_BODY_BYTES:
        raise WebhookError("webhook: the body is larger than MAX_BODY_BYTES")
    verify(secret, header, body, tolerance)
    try:
        raw = json.loads(body)
    except ValueError as e:
        raise WebhookError(f"webhook: decode the event: {e}") from e
    if not isinstance(raw, dict):
        raise WebhookError("webhook: decode the event: not a JSON object")
    data = raw.get("data")
    return Event(
        id=str(raw.get("id", "")),
        type=str(raw.get("type", "")),
        time=_parse_time(raw.get("time")),
        data=data if isinstance(data, dict) else {},
    )
