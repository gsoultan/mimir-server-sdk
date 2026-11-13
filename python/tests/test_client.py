from __future__ import annotations

import io
import json
import time
import urllib.request

import httpx
import pytest

import mimirsdk
from mimirsdk import types as t


def count(server_url: str, run: str, procedure: str) -> int:
    url = f"{server_url}/test/count?run={run}&procedure={procedure}"
    with urllib.request.urlopen(url) as res:
        return json.load(res)["count"]


def test_list_and_get_models(client: mimirsdk.Client) -> None:
    models = client.models.list()
    assert [m.name for m in models] == ["churn", "llama"]
    assert models[0].size_bytes == 1 << 40  # int64 survives the trip
    assert models[0].status == mimirsdk.MODEL_STATUS_READY
    assert client.models.get("m2").architecture == "llama"


def test_not_found_is_a_typed_error(client: mimirsdk.Client) -> None:
    with pytest.raises(mimirsdk.NotFoundError) as info:
        client.models.get("nope")
    err = info.value
    assert err.code == mimirsdk.Code.NOT_FOUND
    assert err.message == 'no model "nope"'
    assert err.procedure == "/mimir.v1.ModelService/GetModel"
    assert str(err) == 'mimirsdk: ModelService/GetModel: not_found: no model "nope"'
    assert isinstance(err, mimirsdk.MimirError)
    assert not err.retryable


def test_needs_an_api_key(server_url: str) -> None:
    with mimirsdk.Client(server_url) as anon:
        assert anon.auth.setup_state() is not None
        with pytest.raises(mimirsdk.UnauthenticatedError):
            anon.models.list()


def test_headers_and_user_agent(server_url: str) -> None:
    with mimirsdk.Client(
        server_url, api_key="mimir_test_key", user_agent="my-app/1.2", headers={"X-Extra": "hello"}
    ) as c:
        me = c.auth.who_am_i()
    assert me.user.email == "test@example.com"
    assert me.user.name.startswith(f"my-app/1.2 mimir-server-sdk-python/{mimirsdk.__version__} (Python ")
    assert list(me.permissions) == ["hello"]


def test_reads_are_retried_when_unavailable(client: mimirsdk.Client, server_url: str, run: str) -> None:
    archs = client.models.architectures()
    assert archs[0].description == "attempt 3"
    assert count(server_url, run, "/mimir.v1.ModelService/ListArchitectures") == 3


def test_retries_can_be_turned_off(server_url: str, run: str) -> None:
    with mimirsdk.Client(server_url, api_key="mimir_test_key", retries=0, headers={"X-Test-Run": run}) as c:
        with pytest.raises(mimirsdk.UnavailableError) as info:
            c.models.architectures()
    assert info.value.retryable


def test_writes_are_not_retried_when_unavailable(client: mimirsdk.Client, server_url: str, run: str) -> None:
    with pytest.raises(mimirsdk.UnavailableError):
        client.models.delete("unavailable")
    assert count(server_url, run, "/mimir.v1.ModelService/DeleteModel") == 1


def test_retry_after_is_honoured(client: mimirsdk.Client, server_url: str, run: str) -> None:
    start = time.monotonic()
    job = client.training.start(name="busy", architecture="mim", dataset_id="d1")
    assert job.id == "j-ok"
    assert time.monotonic() - start >= 0.9
    assert count(server_url, run, "/mimir.v1.TrainingService/CreateJob") == 2


def test_long_retry_after_is_not_waited_for(client: mimirsdk.Client, server_url: str, run: str) -> None:
    with pytest.raises(mimirsdk.ResourceExhaustedError) as info:
        client.training.start({"name": "very-busy"})
    assert info.value.retry_after == 120
    assert info.value.retryable
    assert count(server_url, run, "/mimir.v1.TrainingService/CreateJob") == 1


def test_connection_refused_is_unavailable() -> None:
    with mimirsdk.Client("http://127.0.0.1:9", api_key="k", retries=1, retry_backoff=0.01) as c:
        with pytest.raises(mimirsdk.UnavailableError):
            c.models.list()


def test_predict(client: mimirsdk.Client) -> None:
    res = client.models.predict_fields("m1", {"plan": "monthly", "tenure": 3})
    assert res.guesses[0].label == "monthly!"
    assert res.guesses[0].probability == pytest.approx(0.75)
    assert client.models.send_feedback(res.prediction_id, "yes!") is True
    photo = client.models.predict_photo("m1", b"\x89PNG....")
    assert photo.guesses[0].label == "photo 8"
    with pytest.raises(mimirsdk.InvalidArgumentError):
        client.models.predict(model_id="m1")


def test_chat_streams(client: mimirsdk.Client) -> None:
    pieces = list(client.models.chat(model_id="m2", messages=[mimirsdk.user_message("hi there")]))
    assert [p.text for p in pieces] == ["You said", ": ", "hi there", ""]
    assert pieces[-1].done and pieces[-1].finished


def test_chat_text(client: mimirsdk.Client) -> None:
    reply = client.models.chat_text(
        model_id="m2",
        messages=[{"role": "user", "content": "a"}, mimirsdk.assistant_message("b"), mimirsdk.user_message("c")],
    )
    assert reply == mimirsdk.ChatReply(
        text="You said: c", prompt_tokens=3, generated_tokens=3, finished=True, duration_micros=42
    )


def test_chat_takes_a_request_message(client: mimirsdk.Client) -> None:
    req = t.ChatRequest(model_id="m2", messages=[t.ChatMessage(role="user", content="x")], max_tokens=5)
    assert client.models.chat_text(req).text == "You said: x"
    assert client.models.chat_text({"modelId": "m2", "messages": [{"role": "user", "content": "y"}]}).text == (
        "You said: y"
    )


def test_chat_error_mid_stream(client: mimirsdk.Client) -> None:
    got = []
    with pytest.raises(mimirsdk.ResourceExhaustedError) as info:
        for piece in client.models.chat(model_id="boom", messages=[mimirsdk.user_message("x")]):
            got.append(piece.text)
    assert got == ["You said"]
    assert info.value.message == "out of tokens"
    assert info.value.procedure == "/mimir.v1.PredictService/Chat"


def test_chat_stream_can_be_stopped_early(client: mimirsdk.Client) -> None:
    stream = client.models.chat(model_id="m2", messages=[mimirsdk.user_message("x")])
    assert next(stream).text == "You said"
    stream.close()  # what breaking out of a for loop does
    assert client.models.get("m1").name == "churn"  # the client still works


def test_stream_needs_an_api_key(server_url: str) -> None:
    with mimirsdk.Client(server_url) as anon:
        with pytest.raises(mimirsdk.UnauthenticatedError):
            list(anon.models.chat(model_id="m2", messages=[mimirsdk.user_message("x")]))


def test_upload_streams_a_file(client: mimirsdk.Client, tmp_path) -> None:
    path = tmp_path / "net.mim"
    path.write_bytes(b"x" * 3_000_000)
    m = client.models.upload_file(path, "mim")
    assert m.name == "net"
    assert m.description == "upload u-3000000-3000000"

    m = client.models.upload("raw", "mim", b"abc")
    assert m.description == "upload u-3-3"

    class Pipe(io.RawIOBase):  # a stream that can't tell its length
        def __init__(self) -> None:
            self.left = 5

        def readable(self) -> bool:
            return True

        def readinto(self, b) -> int:  # type: ignore[no-untyped-def]
            n = min(self.left, len(b))
            b[:n] = b"y" * n
            self.left -= n
            return n

    m = client.models.upload("piped", "mim", Pipe())  # type: ignore[arg-type]
    assert m.description == "upload u-5--1"

    with pytest.raises(mimirsdk.InvalidArgumentError, match="the file is empty"):
        client.models.upload("empty", "mim", b"")


def test_upload_needs_an_api_key(server_url: str) -> None:
    with mimirsdk.Client(server_url) as anon:
        with pytest.raises(mimirsdk.UnauthenticatedError):
            anon.models.upload("x", "mim", b"abc")


def test_create_model_with_weights(client: mimirsdk.Client) -> None:
    m = client.models.create(name="w", architecture="mim", weights=b"\x00\x01\x02")
    assert m.description == "weights 3"


def test_audit_pages(client: mimirsdk.Client) -> None:
    page = client.audit.list_page(page_size=2)
    assert [e.id for e in page.items] == ["e0", "e1"]
    assert page.next_page_token == "2"
    assert [e.id for e in client.audit.all()] == ["e0", "e1", "e2", "e3", "e4"]
    assert [e.id for e in client.audit.all(page_size=3, page_token="1")] == ["e1", "e2", "e3", "e4"]


def test_training_wait(client: mimirsdk.Client) -> None:
    seen = []
    job = client.training.wait("j-ok", interval=0.01, on_progress=lambda j: seen.append(j.status))
    assert job.status == mimirsdk.JOB_STATUS_SUCCEEDED
    assert seen == [mimirsdk.JOB_STATUS_RUNNING, mimirsdk.JOB_STATUS_SUCCEEDED]

    with pytest.raises(mimirsdk.JobError) as info:
        client.training.wait("j-fail", interval=0.01)
    assert info.value.job.error == "out of memory"
    assert str(info.value) == "mimirsdk: training run j-fail failed: out of memory"


def test_wait_timeout(client: mimirsdk.Client, server_url: str) -> None:
    with pytest.raises(TimeoutError):
        client.training.wait("j-ok", interval=5, timeout=0.1)


def test_datasets_upload(client: mimirsdk.Client, tmp_path) -> None:
    res = client.datasets.upload_csv("churn", b"a,b\n1,2\n3,4\n", target="b")
    assert (res.dataset.name, res.dataset.rows, res.dataset.target) == ("churn", 3, "b")
    assert res.dataset.kind == mimirsdk.DATASET_KIND_TABLE

    path = tmp_path / "photos.zip"
    path.write_bytes(b"PK" + b"\x00" * 10)
    res = client.datasets.upload_photos("cats", path)
    assert res.dataset.kind == mimirsdk.DATASET_KIND_PHOTOS
    assert res.dataset.size_bytes == 12
    with open(path, "rb") as f:
        assert client.datasets.upload_sounds("s", f).dataset.size_bytes == 12


def test_documents_ask(client: mimirsdk.Client) -> None:
    answer = client.documents.ask_text(collection_id="c1", messages=[mimirsdk.user_message("returns")])
    assert answer.text == "About returns: yes [1]."
    assert [s.document_name for s in answer.sources] == ["policy.pdf"]
    assert answer.finished and answer.generated_tokens == 4


def test_scoring_download(client: mimirsdk.Client, tmp_path) -> None:
    buf = io.BytesIO()
    n = client.scorings.download("s1", buf)
    assert buf.getvalue() == b"plan,predicted,confidence,problem\nmonthly,yes,0.9,\n"
    assert n == len(buf.getvalue())
    path = tmp_path / "scored.csv"
    assert client.scorings.download("s1", path) == n
    assert path.read_bytes() == buf.getvalue()
    with pytest.raises(mimirsdk.NotFoundError, match="no scoring"):
        client.scorings.download("nope", io.BytesIO())


def test_raw_call_and_stream(client: mimirsdk.Client) -> None:
    res = client.call("mimir.v1.ModelService.GetModel", id="m1")
    assert res.model.name == "churn"
    res = client.call("/mimir.v1.ModelService/GetModel", {"id": "m2"})
    assert res.model.name == "llama"
    pieces = client.stream("mimir.v1.PredictService/Chat", model_id="m2", messages=[{"role": "user", "content": "z"}])
    assert "".join(p.text for p in pieces) == "You said: z"
    with pytest.raises(ValueError, match="no procedure"):
        client.call("mimir.v1.ModelService.Nope")


def test_unimplemented(client: mimirsdk.Client) -> None:
    with pytest.raises(mimirsdk.UnimplementedError):
        client.teams.list()


def test_timeout(server_url: str) -> None:
    class Slow(httpx.BaseTransport):
        def handle_request(self, request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("slow", request=request)

    with mimirsdk.Client(server_url, api_key="k", http_client=httpx.Client(transport=Slow())) as c:
        with pytest.raises(mimirsdk.DeadlineExceededError):
            c.models.list()


def test_bad_base_urls() -> None:
    for bad, msg in [
        ("localhost:8080", "not a server address"),
        ("ftp://x", "must start with http"),
        ("http://", "not a server address"),
        ("http://u:p@x", "username or password"),
        ("http://x/?a=1", "query or fragment"),
        ("nonsense", "not a server address"),
    ]:
        with pytest.raises(ValueError, match=msg):
            mimirsdk.Client(bad)
    with pytest.raises(ValueError, match="spaces or line breaks"):
        mimirsdk.Client("http://x", api_key="a b")
    assert mimirsdk.Client(" https://x.example/mimir/ ").base_url == "https://x.example/mimir"


def test_from_env(monkeypatch) -> None:
    monkeypatch.delenv(mimirsdk.ENV_URL, raising=False)
    with pytest.raises(ValueError, match="MIMIR_URL"):
        mimirsdk.Client.from_env()
    monkeypatch.setenv(mimirsdk.ENV_URL, "http://localhost:8080")
    monkeypatch.setenv(mimirsdk.ENV_API_KEY, "mimir_x")
    c = mimirsdk.Client.from_env()
    assert c.base_url == "http://localhost:8080"
    assert c.openai_base_url == "http://localhost:8080/v1"
    assert c._t.api_key == "mimir_x"
    assert mimirsdk.Client.from_env(api_key="other")._t.api_key == "other"


def test_access_helpers() -> None:
    a = mimirsdk.all_models(mimirsdk.ROLE_EDITOR)
    assert a.all_models and a.role == mimirsdk.ROLE_EDITOR
    s = mimirsdk.some_models(mimirsdk.ROLE_VIEWER, "m1", "m2")
    assert list(s.model_ids) == ["m1", "m2"] and not s.all_models
