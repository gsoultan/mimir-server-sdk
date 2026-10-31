# mimir-server-sdk

The Go client for [mimir-server](https://github.com/gsoultan/mimir-server).
Sign in with an API key, then manage models, datasets, training runs,
webhooks and people, and ask models questions, including chats streamed as
the model writes them.

```sh
go get github.com/gsoultan/mimir-server-sdk
```

It needs Go 1.27 or later.

## Quickstart

Make an API key in the console under **API keys**, then:

```go
package main

import (
	"context"
	"fmt"
	"log"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func main() {
	ctx := context.Background()
	client, err := mimirsdk.New("http://localhost:8080", mimirsdk.WithAPIKey("mimir_..."))
	if err != nil {
		log.Fatal(err)
	}

	models, err := client.Models.List(ctx)
	if err != nil {
		log.Fatal(err)
	}
	for _, m := range models {
		fmt.Println(m.GetName(), m.GetId())
	}

	answer, err := client.Models.PredictFields(ctx, models[0].GetId(), map[string]string{
		"plan": "monthly", "tenure": "3",
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(answer.GetGuesses()[0].GetLabel())
}
```

`mimirsdk.NewFromEnv()` does the same with the address in `$MIMIR_URL` and
the key in `$MIMIR_API_KEY`.

## What it covers

| Service | What it does |
| --- | --- |
| `client.Models` | list, get, upload (`.mim`, ONNX, GGUF, streamed so files can be larger than memory), update, delete; `SaveArchitecture` and `DeleteArchitecture` for model types written in your own code; `Predict`, `PredictFields`, `PredictPhoto`; `Explain` and `ExplainModel` for why a table model answers as it does; `Generate`, `GenerateStream`, `Chat`, `ChatText` for language models; `SendFeedback` and `Quality` for how a model does in use; `Versions` and `UseVersion` to roll back |
| `client.Datasets` | `UploadCSV`, `UploadPhotos`, `UploadSounds`, `UploadBoxes`, `UploadText`, `Create` from a database query, a bucket or a template, with `TestQuery` and `TestBucket` to look first; get, refresh, check, delete |
| `client.Training` | `Start`, `Wait` (with progress), get, list, cancel, resume, delete, `Compare` (runs side by side), `KeepLearning` (on an interval, optionally waiting for new rows) |
| `client.Scorings` | `ScoreCSV`, `ScoreQuery` (on a schedule), `Create` from storage or a dataset; `Wait`, `Download` the results, run again, cancel, delete |
| `client.Documents` | Collections of your files: `AddFile`, `WaitDocument`, `Search`, `Ask` and `AskText` with the passages cited |
| `client.Benchmarks` | `Freeze` a test from a dataset, `Create` from test rows of your own, `Score` models, `WaitForScores`, `Leader`, get the leaderboard, list, delete |
| `client.Webhooks` | create, update, delete, `SendTest`, `Deliveries` (paged), `Redeliver` |
| `client.APIKeys` | list, create, revoke the caller's keys |
| `client.Auth` | `WhoAmI`, `SignIn` and `VerifySecondFactor` for a password sign-in; `ChangePassword`; `StartTwoFactor`, `EnableTwoFactor`, `DisableTwoFactor`; `Sessions`, `RevokeSession`, `RevokeOtherSessions`; `SetupState`, `CheckDatabase` and `Setup` for first-run setup |
| `client.SignIn` | sign-in with Google, GitHub or your own OpenID Connect provider: `Options`, `Providers`, `SaveProvider`, `DeleteProvider` |
| `client.Users`, `client.Teams` | manage people and teams (admins and owners) |
| `client.Audit` | `All` walks the audit log page by page |
| `client.Workers` | list, get, choices, create, delete, `ReplaceToken`, `SetTasks` (train, serve or both), rented cloud GPU settings |
| `client.Settings` | usage, limits, where training runs, alerts (`UpdateAlerts`, `SendTestAlert`), retention, security (who must use two-step verification), `DatabaseInfo`, and `Backup` of the database |
| `client.Templates` | the template gallery and its example data |
| `webhook` package | check `Mimir-Signature` and decode events on the receiving end |

Anything else the server offers is on `client.Raw()`: the generated Connect
client for every service, sharing the same API key, retries and timeout.
Request and response types are the server's own, re-exported under the same
names (`mimirsdk.Model`, `mimirsdk.ChatRequest`, ...), so the SDK is the only
import you need.

## Streaming chat

`Chat` and `GenerateStream` return an iterator. Each piece holds the next
bit of text; the last has `Done` set and the token counts. Breaking out of
the loop stops the model.

```go
req := &mimirsdk.ChatRequest{
	ModelId:  llamaID,
	Messages: []*mimirsdk.ChatMessage{mimirsdk.UserMessage("Write a haiku about Go.")},
}
for piece, err := range client.Models.Chat(ctx, req) {
	if err != nil {
		return err
	}
	fmt.Print(piece.GetText())
}
```

`ChatText` waits for the whole answer instead. Apps written for OpenAI can
also talk to language models through the server's OpenAI-compatible API at
`client.OpenAIBaseURL()` with a mimir API key.

## Training

```go
created, err := client.Datasets.UploadCSV(ctx, "churn", "churned", file)
job, err := client.Training.Start(ctx, &mimirsdk.CreateJobRequest{
	Name:         "churn",
	Architecture: created.GetDataset().GetArchitectures()[0],
	DatasetId:    created.GetDataset().GetId(),
})
job, err = client.Training.Wait(ctx, job.GetId(), mimirsdk.WaitOptions{
	OnProgress: func(j *mimirsdk.Job) { fmt.Println("epoch", j.GetEpoch()) },
})
```

`Wait` returns a `*mimirsdk.JobError` when the run fails or is cancelled. A
finished run carries its full report: `job.GetReport()` has the share of
right answers, the per-label scores and the confusion table, or the average
miss and R² for a number model.

## Scoring a whole list

`client.Scorings` answers every row of a table with one model at once, in
the background on the server, and keeps the rows with each answer next to
them as a CSV.

```go
sc, err := client.Scorings.ScoreCSV(ctx, modelID, "October customers", csvBytes)
sc, err = client.Scorings.Wait(ctx, sc.GetId(), mimirsdk.ScoringWaitOptions{})
f, _ := os.Create("scored.csv")
defer f.Close()
_, err = client.Scorings.Download(ctx, sc.GetId(), f)
```

The rows need at least one column the model reads, and no answer column.
The results have the rows' own columns, then `predicted`, `confidence`
(or `suggestions` for a ranking model) and `problem`, which says why a row
couldn't be answered. `ScoreQuery` scores a database query's rows, and
with an interval of an hour or more scores them again on a schedule.

## Asking your documents

`client.Documents` answers questions from your own files. The server
reads each file into passages in the background and answers from the ones
that best match, citing them as [1], [2]:

```go
col, err := client.Documents.CreateCollection(ctx, &mimirsdk.CreateCollectionRequest{
	Name: "Shop handbook", EmbeddingModelId: modelID,
})
doc, err := client.Documents.AddFile(ctx, col.GetId(), "returns-policy.pdf")
_, err = client.Documents.WaitDocument(ctx, doc.GetId(), 0)

answer, err := client.Documents.AskText(ctx, &mimirsdk.AskRequest{
	CollectionId: col.GetId(),
	Messages:     []*mimirsdk.ChatMessage{mimirsdk.UserMessage("Can a customer return a used item?")},
})
fmt.Println(answer.Text)
for i, p := range answer.Sources {
	fmt.Printf("[%d] %s, passage %d\n", i+1, p.GetDocumentName(), p.GetNumber())
}
```

`Ask` streams the answer instead, with the sources in its first message,
and `Search` returns the matching passages without an answer. Apps that
speak the OpenAI API can ask the collection too, by its `ApiName`.

## Benchmarks

An accuracy from a run says how a model did on the examples that run kept
aside, which is a different test for every run. A benchmark is one fixed
test every model takes the same way. Its rows are frozen from a dataset and
left out of training on it, so no model learns the answers to its own test.

```go
test, err := client.Benchmarks.Freeze(ctx, "churn test", datasetID, 0.2)
_, err = client.Benchmarks.Score(ctx, test.GetId(), modelA, modelB)
scores, err := client.Benchmarks.WaitForScores(ctx, test.GetId(), mimirsdk.ScoreWaitOptions{})
for _, s := range scores {
	fmt.Println(s.GetRank(), s.GetModelName(), s.GetHeadline())
}
```

The leaderboard comes back best first, by the share of right answers, by
the balanced score when one answer is rare, or by the average miss for a
number model, where less is better. `Benchmark.GetMetric()` says which, and
`GetLowerIsBetter()` which way round. A model that finishes training on the
benchmark's dataset is scored on its own.

## Why it answered that

For a model taught on a table, `Explain` gives each column's effect on one
answer compared with a typical row, and `ExplainModel` which columns
matter most overall:

```go
why, err := client.Models.Explain(ctx, modelID, fields, "") // "" explains the answer it gave
fmt.Printf("chance of %s: %.0f%% (typical row %.0f%%)\n", why.GetLabel(), why.GetValue()*100, why.GetTypical()*100)
for _, c := range why.GetContributions() {
	fmt.Printf("  %s = %s: %+.0f points\n", c.GetColumn(), c.GetValue(), c.GetEffect()*100)
}

cols, err := client.Models.ExplainModel(ctx, modelID)
for _, c := range cols.GetColumns() {
	fmt.Printf("%s: %.0f%% of the effect\n", c.GetColumn(), c.GetShare()*100)
}
```

For a model that answers with a number, `GetNumber()` is true and the
effects are in its units. Models that rank, and models of photos, sound or
text, are refused with `ErrInvalidArgument`.

## Feedback and versions

Every answer comes with a `PredictionId`. Once your app learns what the
right answer was, send it back, and the model page shows how often the
model gets it right in use:

```go
answer, err := client.Models.PredictFields(ctx, modelID, fields)
// ... later, when the customer stays or leaves:
right, err := client.Models.SendFeedback(ctx, answer.GetPredictionId(), "stayed")
// For a model that answers with a number:
right, err = client.Models.SendFeedbackValue(ctx, answer.GetPredictionId(), 41.5)

q, err := client.Models.Quality(ctx, modelID, 30)
fmt.Printf("%.0f%% right this week\n", q.GetWeekAccuracy()*100)
```

Answers are kept for feedback for 30 days. When a model gets clearly fewer
right than when it was trained, the server sends a
`webhook.AccuracyDropped` event, and `ev.Accuracy()` decodes it.

Each upload, training run and keep-learning pass stores a new version of
the model. `Versions` lists them and `UseVersion` makes an earlier one live
again:

```go
versions, err := client.Models.Versions(ctx, modelID)
model, err := client.Models.UseVersion(ctx, modelID, versions[1].GetId())
```

## Errors

Every error the server returns is a `*mimirsdk.Error` with a `Code`, a
`Message` written for people, and `RetryAfter` when the server asked to wait.
Test for kinds with `errors.Is`:

```go
_, err := client.Models.Get(ctx, id)
switch {
case errors.Is(err, mimirsdk.ErrNotFound):
	// no such model, or not one this key may see
case errors.Is(err, mimirsdk.ErrUnauthenticated):
	// the API key is wrong or revoked
case errors.Is(err, mimirsdk.ErrResourceExhausted):
	// a limit: the message says which, and when it resets
}
```

Context errors come back unchanged, so `errors.Is(err, context.DeadlineExceeded)`
works too.

## Retries and timeouts

- Calls that only read (list, get, who am I) are retried when the server is
  briefly unavailable, with exponential backoff and jitter.
- Any call the server turns down with a `Retry-After` (the per-minute
  prediction limit) is retried after that wait, unless the wait is longer
  than the cap (`DefaultMaxRetryWait`, 30 seconds); then the error is
  returned with `RetryAfter` set.
- Calls that change something are never retried after they may have reached
  the server.
- Each call that returns one response is bounded by `WithTimeout` (60
  seconds by default) when its context has no deadline. Streamed chats are
  bounded only by their context.

```go
client, err := mimirsdk.New(url,
	mimirsdk.WithAPIKey(key),
	mimirsdk.WithTimeout(2*time.Minute), // big uploads
	mimirsdk.WithRetries(5),
	mimirsdk.WithRetryBackoff(500*time.Millisecond, 10*time.Second),
	mimirsdk.WithUserAgent("my-app/1.0"),
)
```

`WithHTTPClient` swaps the HTTP client (a proxy, custom TLS, a cookie jar for
password sign-in), `WithHeader` adds headers, and `WithConnectOptions`
passes options straight to Connect.

## Paged lists

The audit log and webhook deliveries come in pages. `All` and `Deliveries`
walk every page, fetching the next only when the loop gets there;
`ListPage` and `DeliveriesPage` return one page and its `NextPageToken`.

```go
for ev, err := range client.Audit.All(ctx, mimirsdk.ListOptions{PageSize: 100}) {
	if err != nil {
		return err
	}
	fmt.Println(ev.GetActor(), ev.GetAction(), ev.GetTarget())
}
```

## Receiving webhooks

```go
import "github.com/gsoultan/mimir-server-sdk/webhook"

http.Handle("POST /hooks/mimir", webhook.Handler(secret, func(ctx context.Context, ev *webhook.Event) error {
	if ev.Type == webhook.TrainingFinished {
		job, err := ev.Job()
		if err != nil {
			return err
		}
		log.Printf("%s is ready: model %s", job.Name, job.ModelID)
	}
	return nil
}))
```

The handler answers 401 to anything not signed with the webhook's secret,
or signed more than five minutes from now, and 500 when your function
returns an error, so the server tries again later. Deliveries are retried
for about a day, so the same event can arrive twice; `ev.ID` is the same
each time. `webhook.Verify` and `webhook.Parse` do the check by hand.

## Examples

Runnable programs in [examples](examples):

- [quickstart](examples/quickstart): list models and ask one a question
- [chat](examples/chat): a terminal chat with a language model, streamed
- [train](examples/train): upload a CSV, train, wait and predict
- [webhook-receiver](examples/webhook-receiver): check and print deliveries

```sh
export MIMIR_URL=http://localhost:8080 MIMIR_API_KEY=mimir_...
go run ./examples/train data.csv
```

## Versions

The SDK follows semantic versioning; the API may change between 0.x
releases. Each release names the mimir-server release it is built against:

| SDK | mimir-server |
| --- | --- |
| v0.3.x | v0.3.1 and later 0.3 releases |
| v0.2.x | v0.3.0 and later 0.3 releases |
| v0.1.x | v0.1.3 |

## Development

```sh
go vet ./...
go test -race ./...
```

The tests run against a fake server built from the server's generated
handlers. A release is a `v*` tag: the release workflow checks that
`version.go` matches the tag, runs the tests and publishes the notes with
GoReleaser.
