from __future__ import annotations

import json
import time

import pytest

from mimirsdk import webhook

SECRET = "whsec_test"
BODY = json.dumps(
    {
        "id": "ev1",
        "type": "training.finished",
        "time": "2026-11-13T06:47:47.123456789Z",
        "data": {"id": "j1", "status": "succeeded", "model_id": "m1", "accuracy": 0.91},
    }
).encode()


def test_sign_and_parse() -> None:
    ev = webhook.parse(SECRET, webhook.sign(SECRET, BODY), BODY)
    assert (ev.id, ev.type) == ("ev1", webhook.TRAINING_FINISHED)
    assert ev.time is not None and ev.time.year == 2026 and ev.time.microsecond == 123456
    job = ev.job()
    assert job["model_id"] == "m1" and job["accuracy"] == 0.91
    with pytest.raises(webhook.WebhookError, match="has no model data"):
        ev.model()


def test_matches_the_go_signature() -> None:
    # Made by the Go SDK: webhook.Sign("whsec_vector", time.Unix(1700000000, 0), body).
    body = b'{"id":"ev1","type":"test"}'
    want = "t=1700000000,v1=af13c1a596443d96473d576831bd5071fefc03a5783ea085d3653b8d2208f76e"
    assert webhook.sign("whsec_vector", body, at=1700000000) == want
    webhook.verify("whsec_vector", want, body, tolerance=10**10)


def test_rejects() -> None:
    with pytest.raises(webhook.NoSignatureError):
        webhook.verify(SECRET, None, BODY)
    with pytest.raises(webhook.NoSignatureError):
        webhook.verify(SECRET, "  ", BODY)
    with pytest.raises(webhook.BadSignatureError):
        webhook.verify("other", webhook.sign(SECRET, BODY), BODY)
    with pytest.raises(webhook.BadSignatureError):
        webhook.verify(SECRET, webhook.sign(SECRET, BODY), BODY + b" ")
    with pytest.raises(webhook.BadSignatureError):
        webhook.verify(SECRET, "t=abc,v1=00", BODY)
    with pytest.raises(webhook.BadSignatureError):
        webhook.verify(SECRET, f"t={int(time.time())}", BODY)
    with pytest.raises(webhook.ExpiredError):
        webhook.verify(SECRET, webhook.sign(SECRET, BODY, at=time.time() - 3600), BODY)
    # A longer tolerance lets an old delivery through.
    webhook.verify(SECRET, webhook.sign(SECRET, BODY, at=time.time() - 3600), BODY, tolerance=7200)


def test_any_of_several_signatures() -> None:
    good = webhook.sign(SECRET, BODY)
    ts = good.split(",")[0]
    webhook.verify(SECRET, f"{ts},v1=deadbeef,{good.split(',')[1]}", BODY)


def test_not_json() -> None:
    with pytest.raises(webhook.WebhookError, match="decode"):
        webhook.parse(SECRET, webhook.sign(SECRET, b"nope"), b"nope")
