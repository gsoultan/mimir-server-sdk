# mimir-server-sdk for Python

The Python client for [mimir-server](https://github.com/gsoultan/mimir-server).
Sign in with an API key, then manage models, datasets, training runs,
webhooks and people, and ask models questions, including chats streamed as
the model writes them. It covers the same calls as the
[Go SDK](https://github.com/gsoultan/mimir-server-sdk).

It needs Python 3.10 or later, and depends on `httpx` and `protobuf`.

```sh
pip install "mimir-server-sdk @ git+https://github.com/gsoultan/mimir-server-sdk#subdirectory=python"
```

## Quickstart

Make an API key in the console under **API keys**, then:

```python
import mimirsdk

with mimirsdk.Client("http://localhost:8080", api_key="mimir_...") as client:
    for m in client.models.list():
        print(m.name, m.id)

    answer = client.models.predict_fields(model_id, {"plan": "monthly", "tenure": 3})
    print(answer.guesses[0].label)
```

`mimirsdk.Client.from_env()` does the same with the address in `$MIMIR_URL`
and the key in `$MIMIR_API_KEY`.

## What it covers

| Service | What it does |
| --- | --- |
| `client.models` | `list`, `get`, `upload` and `upload_file` (`.mim`, ONNX, GGUF, streamed so files can be larger than memory), `update`, `delete`; `save_architecture`, `delete_architecture`; `predict`, `predict_fields`, `predict_photo`; `explain`, `explain_model`; `generate`, `generate_stream`, `chat`, `chat_text` for language models; `send_feedback` and `quality`; `versions` and `use_version` to roll back |
| `client.datasets` | `upload_csv`, `upload_photos`, `upload_sounds`, `upload_boxes`, `upload_text`, `create` from a database query, a bucket or a template, with `test_query` and `test_bucket` to look first; `get`, `refresh`, `check`, `delete` |
| `client.training` | `start`, `wait` (with progress), `get`, `list`, `cancel`, `resume`, `delete`, `compare`, `keep_learning` |
| `client.scorings` | `score_csv`, `score_query` (on a schedule), `create`; `wait`, `download` the results, `run`, `cancel`, `set_repeat`, `delete` |
| `client.documents` | collections of your files: `add_file`, `wait_document`, `search`, `ask` and `ask_text` with the passages cited |
| `client.benchmarks` | `freeze`, `create`, `score`, `wait_for_scores`, `leader`, `get`, `list`, `delete` |
| `client.webhooks` | `create`, `update`, `delete`, `send_test`, `deliveries` (paged), `redeliver` |
| `client.api_keys` | `list`, `create`, `revoke` the caller's keys |
| `client.auth` | `who_am_i`, `sign_in` and `verify_second_factor`; `change_password`; two-step verification; sessions; first-run `setup` |
| `client.sign_in` | sign-in with Google, GitHub or OpenID Connect: `options`, `providers`, `save_provider`, `delete_provider` |
| `client.users`, `client.teams` | manage people and teams |
| `client.audit` | `all` walks the audit log page by page |
| `client.workers` | `list`, `get`, `choices`, `create`, `delete`, `replace_token`, `set_tasks`, rented cloud GPU settings |
| `client.settings` | usage, limits, training, alerts, retention, security, `database_info`, `backup` |
| `client.templates` | the template gallery and its example data |
| `mimirsdk.webhook` | check `Mimir-Signature` and decode events on the receiving end |

Every message and enum of the server's API is in `mimirsdk.types` under the
server's own names, and re-exported from `mimirsdk` (`mimirsdk.Model`,
`mimirsdk.ChatRequest`, `mimirsdk.JOB_STATUS_SUCCEEDED`, ...). They are
protobuf messages: read fields as attributes, and use `HasField` to tell an
unset message field from an empty one.

Methods that take a request accept the message, a dict of its fields, or
keyword arguments, so these are the same:

```python
client.training.start(name="churn", architecture="table-auto", dataset_id=ds_id)
client.training.start({"name": "churn", "architecture": "table-auto", "dataset_id": ds_id})
client.training.start(mimirsdk.CreateJobRequest(name="churn", architecture="table-auto", dataset_id=ds_id))
```

Anything else the server offers is on `client.call` and `client.stream`,
with the same API key, retries and timeout:

```python
res = client.call("mimir.v1.ModelService.GetModel", id=model_id)
```

## Streaming chat

`chat` and `generate_stream` return an iterator. Each piece holds the next
bit of text; the last has `done` set and the token counts. Breaking out of
the loop stops the model.

```python
from mimirsdk import user_message

for piece in client.models.chat(model_id=llama_id, messages=[user_message("Write a haiku about Python.")]):
    print(piece.text, end="", flush=True)
```

`chat_text` waits for the whole answer instead. Apps written for OpenAI can
also talk to language models through the server's OpenAI-compatible API at
`client.openai_base_url` with a mimir API key:

```python
from openai import OpenAI

openai = OpenAI(base_url=client.openai_base_url, api_key="mimir_...")
```

## Training

```python
created = client.datasets.upload_csv("churn", "churn.csv", target="churned")
job = client.training.start(
    name="churn",
    architecture=created.dataset.architectures[0],
    dataset_id=created.dataset.id,
)
job = client.training.wait(job.id, on_progress=lambda j: print("epoch", j.epoch))
```

`upload_csv` and the other dataset uploads take bytes, a binary file
object, or a path. `wait` raises `mimirsdk.JobError` when the run fails or
is cancelled, with the run on `err.job`, and `TimeoutError` after
`timeout=` seconds if you give one. A finished run carries its full report
in `job.report`.

## Scoring a whole list

```python
sc = client.scorings.score_csv(model_id, "october.csv", name="October customers")
sc = client.scorings.wait(sc.id)
client.scorings.download(sc.id, "scored.csv")
```

The results have the rows' own columns, then `predicted`, `confidence` (or
`suggestions` for a ranking model) and `problem`, which says why a row
couldn't be answered.

## Asking your documents

```python
from mimirsdk import user_message

col = client.documents.create_collection(name="Policies", embedding_model_id=embedder_id, language_model_id=llama_id)
doc = client.documents.add_file(col.id, "returns.pdf")
client.documents.wait_document(doc.id)

answer = client.documents.ask_text(collection_id=col.id, messages=[user_message("Can I return a used item?")])
print(answer.text)
for s in answer.sources:
    print(f"[{s.number}] {s.document_name}")
```

## Errors

A call the server turns down raises `mimirsdk.MimirError`, or the subclass
for its code: `NotFoundError`, `InvalidArgumentError`,
`PermissionDeniedError`, `UnauthenticatedError`, `ResourceExhaustedError`,
`UnavailableError` and so on. Each has `code`, the server's `message`, the
`procedure` that failed and `retry_after` in seconds.

```python
try:
    client.models.get(model_id)
except mimirsdk.NotFoundError:
    ...
```

Calls that read are retried when the server is unavailable, and any call is
retried after a `Retry-After` of up to 30 seconds. Set `retries=0` to turn
that off, and `timeout=` (seconds, retries included, 60 by default) to bound
each call. Streamed calls aren't bounded by `timeout`.

## Webhooks

```python
from mimirsdk import webhook

event = webhook.parse(secret, request.headers.get(webhook.SIGNATURE_HEADER), raw_body)
if event.type == webhook.TRAINING_FINISHED:
    print(event.job()["model_id"])
```

`parse` raises `webhook.WebhookError` (`NoSignatureError`,
`BadSignatureError` or `ExpiredError`) for a delivery that isn't genuine;
answer those with 401. The server retries a delivery until it gets a 2xx,
so use `event.id` to skip repeats.

## Signing in with a password

Apps should use an API key. Scripts that set a server up can sign in with a
password instead: the client keeps the session cookie, so later calls are
signed in.

```python
client = mimirsdk.Client("http://localhost:8080")
client.auth.sign_in("owner@example.com", password)
key = client.api_keys.create("my-app", mimirsdk.all_models(mimirsdk.ROLE_EDITOR))
print(key.secret)  # shown only this once
```

## Versions

The message types come from mimir-server v0.3.1, the same version the Go SDK
is built against. `scripts/gen.sh` at the top of the repository writes them
again after the Go SDK's `go.mod` moves to a newer server.

## Development

```sh
uv sync
uv run pytest        # builds and starts internal/testserver, so it needs Go
uv run ruff check && uv run ruff format --check && uv run mypy
```
