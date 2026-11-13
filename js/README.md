# mimir-server-sdk for JavaScript and TypeScript

The JavaScript and TypeScript client for
[mimir-server](https://github.com/gsoultan/mimir-server). Sign in with an API
key, then manage models, datasets, training runs, webhooks and people, and
ask models questions, including chats streamed as the model writes them. It
covers the same calls as the [Go SDK](https://github.com/gsoultan/mimir-server-sdk).

It runs on Node.js 20 or later, Deno, Bun and in browsers, and is written in
TypeScript, with types for every request and answer. It speaks the server's
Connect protocol through `fetch`, with
[connect-es](https://github.com/connectrpc/connect-es).

```sh
npm install mimir-server-sdk
```

Until it is published, build it from the repository: `npm ci && npm pack`
in `js/`, then `npm install ./mimir-server-sdk-0.1.0.tgz`.

## Quickstart

Make an API key in the console under **API keys**, then:

```ts
import { Client } from "mimir-server-sdk";

const client = new Client("http://localhost:8080", { apiKey: "mimir_..." });

for (const m of await client.models.list()) {
  console.log(m.name, m.id);
}

const answer = await client.models.predictFields(modelId, { plan: "monthly", tenure: 3 });
console.log(answer.guesses[0]?.label);
```

`Client.fromEnv()` does the same with the address in `$MIMIR_URL` and the
key in `$MIMIR_API_KEY`.

## What it covers

| Service | What it does |
| --- | --- |
| `client.models` | `list`, `get`, `upload` (bytes, a Blob or a stream, sent as it is read) and `uploadFile`, `update`, `delete`; `saveArchitecture`, `deleteArchitecture`; `predict`, `predictFields`, `predictPhoto`; `explain`, `explainModel`; `generate`, `generateStream`, `chat`, `chatText` for language models; `sendFeedback` and `quality`; `versions` and `useVersion` to roll back |
| `client.datasets` | `uploadCSV`, `uploadPhotos`, `uploadSounds`, `uploadBoxes`, `uploadText`, `create` from a database query, a bucket or a template, with `testQuery` and `testBucket` to look first; `get`, `refresh`, `check`, `delete` |
| `client.training` | `start`, `wait` (with progress), `get`, `list`, `cancel`, `resume`, `delete`, `compare`, `keepLearning` |
| `client.scorings` | `scoreCSV`, `scoreQuery` (on a schedule), `create`; `wait`, `download` and `downloadToFile`, `run`, `cancel`, `setRepeat`, `delete` |
| `client.documents` | collections of your files: `addFile`, `waitDocument`, `search`, `ask` and `askText` with the passages cited |
| `client.benchmarks` | `freeze`, `create`, `score`, `waitForScores`, `leader`, `get`, `list`, `delete` |
| `client.webhooks` | `create`, `update`, `delete`, `sendTest`, `deliveries` (paged), `redeliver` |
| `client.apiKeys` | `list`, `create`, `revoke` the caller's keys |
| `client.auth` | `whoAmI`, `signIn` and `verifySecondFactor`; `changePassword`; two-step verification; sessions; first-run `setup` |
| `client.signIn` | sign-in with Google, GitHub or OpenID Connect: `options`, `providers`, `saveProvider`, `deleteProvider` |
| `client.users`, `client.teams` | manage people and teams |
| `client.audit` | `all` walks the audit log page by page |
| `client.workers` | `list`, `get`, `choices`, `create`, `delete`, `replaceToken`, `setTasks`, rented cloud GPU settings |
| `client.settings` | usage, limits, training, alerts, retention, security, `databaseInfo`, `backup` |
| `client.templates` | the template gallery and its example data |
| `mimir-server-sdk/webhook` | check `Mimir-Signature` and decode events on the receiving end |

Every message, enum and service of the server's API is exported under the
server's own names (`Model`, `ChatRequest`, `JobStatus`, `ModelService`,
...), generated with [protobuf-es](https://github.com/bufbuild/protobuf-es).
Requests are plain objects with any of the message's fields; 64-bit numbers
such as `sizeBytes` are `bigint`.

Every method takes a last, optional `{ signal, timeoutMs, headers }` to stop
a call with an `AbortSignal`, change its timeout or add headers.
Anything the services don't wrap is on `client.raw`: the generated Connect
clients, sharing the API key and retries.

## Streaming chat

`chat` and `generateStream` return an async iterator. Each piece holds the
next bit of text; the last has `done` set and the token counts. Leaving the
loop early stops the model.

```ts
import { userMessage } from "mimir-server-sdk";

for await (const piece of client.models.chat({ modelId: llamaId, messages: [userMessage("Write a haiku.")] })) {
  process.stdout.write(piece.text);
}
```

`chatText` waits for the whole answer instead. Apps written for OpenAI can
also talk to language models through the server's OpenAI-compatible API at
`client.openaiBaseUrl` with a mimir API key.

## Training

```ts
const created = await client.datasets.uploadCSV("churn", await readFile("churn.csv"), "churned");
let job = await client.training.start({
  name: "churn",
  architecture: created.dataset!.architectures[0],
  datasetId: created.dataset!.id,
});
job = await client.training.wait(job.id, { onProgress: (j) => console.log("epoch", j.epoch) });
```

`wait` throws a `JobError` when the run fails or is cancelled, with the run
on `err.job`; stop waiting with `signal`.

## Scoring a whole list

```ts
let sc = await client.scorings.scoreCSV(modelId, csvText, "October customers");
sc = await client.scorings.wait(sc.id);
await client.scorings.downloadToFile(sc.id, "scored.csv"); // or download() for a stream
```

## Asking your documents

```ts
const answer = await client.documents.askText({
  collectionId,
  messages: [userMessage("Can I return a used item?")],
});
console.log(answer.text, answer.sources.map((s) => s.documentName));
```

## Errors

A call the server turns down throws a `MimirError`, or the subclass for its
code: `NotFoundError`, `InvalidArgumentError`, `PermissionDeniedError`,
`UnauthenticatedError`, `ResourceExhaustedError`, `UnavailableError` and so
on. Each has `code` (like `"not_found"`), the server's `rawMessage`, the
`procedure` that failed and `retryAfter` in seconds.

```ts
import { NotFoundError } from "mimir-server-sdk";

try {
  await client.models.get(modelId);
} catch (err) {
  if (err instanceof NotFoundError) { /* ... */ }
  throw err;
}
```

Calls that read are retried when the server is unavailable, and any call is
retried after a `Retry-After` of up to 30 seconds. Set `retries: 0` to turn
that off, and `timeoutMs` (60 seconds by default, retries included) to bound
each call. Streamed calls are bounded only by their `signal`.

## Webhooks

```ts
import { parse, SIGNATURE_HEADER, TRAINING_FINISHED, WebhookError } from "mimir-server-sdk/webhook";

const event = await parse(secret, request.headers.get(SIGNATURE_HEADER), rawBody);
if (event.type === TRAINING_FINISHED) console.log(event.job().model_id);
```

`parse` rejects with a `WebhookError` (`NoSignatureError`,
`BadSignatureError` or `ExpiredError`) for a delivery that isn't genuine;
answer those with 401. It uses Web Crypto, so it also runs in edge
functions.

## In a browser

The client works in a browser too. On a page the console itself serves,
it is signed in with the session cookie of whoever uses the console; a page
on another origin needs an API key and the server to allow that origin
(CORS). Browsers don't
let pages set `User-Agent`, so the SDK names itself in `X-User-Agent`
there. `uploadFile`, `downloadToFile` and `backupToFile` need Node.js,
Deno or Bun; the rest don't.

## Versions

The message types come from mimir-server v0.3.1, the same version the Go SDK
is built against. `scripts/gen.sh` at the top of the repository writes them
again after the Go SDK's `go.mod` moves to a newer server.

## Development

```sh
npm ci
npm test            # builds and starts internal/testserver, so it needs Go
npm run typecheck
npm run build
```
