from __future__ import annotations

import os
from typing import Any, Iterator, Mapping, Optional, Union
from urllib.parse import urlsplit

import httpx
from google.protobuf.message import Message

from ._access import APIKeyService, AuditService, AuthService, SignInService, TeamService, UserService
from ._admin import SettingsService, TemplateService, WebhookService, WorkerService
from ._benchmarks import BenchmarkService
from ._documents import DocumentService
from ._models import ModelService
from ._scorings import ScoringService
from ._training import DatasetService, TrainingService
from ._transport import (
    DEFAULT_MAX_RETRY_WAIT,
    DEFAULT_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_TIMEOUT,
    Transport,
    input_class,
    method,
    to_message,
)

# Environment variables Client.from_env reads.
ENV_URL = "MIMIR_URL"
ENV_API_KEY = "MIMIR_API_KEY"


class Client:
    """Talks to one mimir-server. Make one and share it; close it when done,
    or use it in a ``with`` block.

    ``timeout`` bounds each call that returns one response, retries
    included, in seconds; None means no bound. Streamed calls (``chat``,
    ``generate_stream``, ``documents.ask``) are not bounded by it.
    ``retries`` is how many times a failed call may be tried again: reads
    when the server is unavailable, and any call the server refused with a
    Retry-After of at most ``max_retry_wait`` seconds. Pass ``http_client``
    to send requests through your own ``httpx.Client``, such as one with a
    proxy; give it no overall timeout, or streamed chats are cut short.
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str = "",
        timeout: Optional[float] = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        max_retry_wait: float = DEFAULT_MAX_RETRY_WAIT,
        user_agent: str = "",
        headers: Optional[Mapping[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._base_url = _parse_base_url(base_url)
        self._t = Transport(
            self._base_url,
            api_key=api_key,
            http_client=http_client,
            timeout=timeout,
            retries=retries,
            retry_backoff=retry_backoff,
            max_retry_wait=max_retry_wait,
            user_agent=user_agent,
            headers=headers,
        )
        t = self._t
        self.auth = AuthService(t)
        self.api_keys = APIKeyService(t)
        self.users = UserService(t)
        self.teams = TeamService(t)
        self.audit = AuditService(t)
        self.models = ModelService(t)
        self.datasets = DatasetService(t)
        self.training = TrainingService(t)
        self.webhooks = WebhookService(t)
        self.workers = WorkerService(t)
        self.settings = SettingsService(t)
        self.templates = TemplateService(t)
        self.benchmarks = BenchmarkService(t)
        self.scorings = ScoringService(t)
        self.documents = DocumentService(t)
        self.sign_in = SignInService(t)

    @classmethod
    def from_env(cls, **kwargs: Any) -> Client:
        """A client for the server at $MIMIR_URL with the API key in
        $MIMIR_API_KEY. Keyword arguments win over the environment."""
        base = os.environ.get(ENV_URL, "")
        if not base:
            raise ValueError(f"mimirsdk: set {ENV_URL} to the server's address, like http://localhost:8080")
        key = os.environ.get(ENV_API_KEY, "")
        if key:
            kwargs.setdefault("api_key", key)
        return cls(base, **kwargs)

    @property
    def base_url(self) -> str:
        """The server address the client was made with, without a trailing
        slash."""
        return self._base_url

    @property
    def openai_base_url(self) -> str:
        """Where the server's OpenAI-compatible API lives
        (/v1/chat/completions, /v1/completions, /v1/embeddings, /v1/models).
        Point an OpenAI client library at it with a mimir API key to chat
        with language models."""
        return self._base_url + "/v1"

    def call(self, procedure: str, request: Union[Message, Mapping[str, Any], None] = None, **fields: Any) -> Any:
        """Call any unary procedure the server offers, such as
        ``mimir.v1.ModelService.GetModel``, with the client's API key,
        retries and timeout. The request is a message, a dict of its fields
        or keyword arguments."""
        m = method(procedure)
        return self._t.unary(m, to_message(input_class(m), request, fields))

    def stream(
        self, procedure: str, request: Union[Message, Mapping[str, Any], None] = None, **fields: Any
    ) -> Iterator[Any]:
        """``call`` for a procedure that streams its answer, yielding each
        message."""
        m = method(procedure)
        return self._t.server_stream(m, to_message(input_class(m), request, fields))

    def close(self) -> None:
        """Close the connections, unless the client was given its own
        httpx.Client."""
        self._t.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Client({self._base_url!r})"


def _parse_base_url(raw: str) -> str:
    raw = raw.strip()
    u = urlsplit(raw)
    if u.scheme not in ("http", "https"):
        if not u.netloc:
            raise ValueError(f"mimirsdk: {raw!r} is not a server address; use one like https://mimir.example.com")
        raise ValueError(f"mimirsdk: the server address must start with http:// or https://, not {u.scheme}://")
    if not u.hostname:
        raise ValueError(f"mimirsdk: {raw!r} is not a server address; use one like https://mimir.example.com")
    if u.username is not None or u.password is not None:
        raise ValueError("mimirsdk: don't put a username or password in the server address; use api_key")
    if u.query or u.fragment:
        raise ValueError("mimirsdk: the server address can't have a query or fragment")
    return raw.rstrip("/")
