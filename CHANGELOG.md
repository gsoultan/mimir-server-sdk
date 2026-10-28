# Changelog

## Unreleased

Needs the next mimir-server release (the one after v0.2.0).

- `client.Scorings`: answer every row of a table with one model at once,
  from a CSV (`ScoreCSV`), a database query on a schedule (`ScoreQuery`),
  storage or a dataset (`Create`); `Wait` follows it, `Download` streams
  the results CSV, and `Run`, `Cancel`, `SetRepeat` and `Delete` manage
  it. `*ScoringError` says why one failed.
- `client.Documents`: answer questions from your own files. Make a
  collection, `AddFile` PDFs, Word, Markdown, web pages or text, follow
  them with `WaitDocument`, then `Ask` (streamed, sources first) or
  `AskText`, or `Search` for the matching passages.
- `Models.Explain`: why a table model gave its answer, as each column's
  effect against a typical row; `Models.ExplainModel`: which columns
  matter most to it overall.

## v0.1.0 (unreleased)

The first release, built against mimir-server v0.2.0.

- `mimirsdk.New` and `NewFromEnv`, with options for the API key, HTTP
  client, timeout, retries, User-Agent and headers.
- Services for models (upload, predict, generate, streamed chat), datasets,
  training (with `Wait`), webhooks, API keys, sign-in, users, teams, the
  audit log, workers, settings and templates; `Raw` for the rest.
- `*Error` with `errors.Is` sentinels and `RetryAfter`; retries for reads
  when the server is unavailable and for any call refused with a
  Retry-After.
- Iterators over paged lists and streamed answers.
- `Models.Upload` and `UploadFile` stream the file to `/api/uploads`, so a
  model can be larger than memory.
- `Training.KeepLearning` can wait for a number of new rows,
  `Settings.UpdateTraining` says where runs train, and `Workers.SetTasks`
  and the cloud GPU calls (`CloudGPU`, `UpdateCloudGPU`, `StopCloudGPU`)
  manage workers.
- `client.Benchmarks`: a fixed test frozen from a dataset that every model
  takes the same way, with a leaderboard, `Score`, `WaitForScores` and
  `Leader`. Training on the dataset leaves the test rows out.
- `Training.Compare` puts two to six runs side by side, and a finished run
  carries its full report (`Job.GetReport()`).
- The `webhook` package: signature checks, event decoding and an
  `http.Handler`.
- `Datasets.UploadSounds` (a ZIP of WAV folders), `UploadBoxes` (a ZIP of
  photos and a boxes.csv) and `UploadText` (writing for a language model),
  with the `DatasetKindSounds`, `DatasetKindBoxes` and `DatasetKindText`
  kinds.
- `Models.SendFeedback` and `SendFeedbackValue` send the right answer for
  a prediction, by its `PredictionId`; `Models.Quality` returns how a model
  does in use; `webhook.AccuracyDropped` and `Event.Accuracy` for the
  alert.
- `Models.Versions` and `UseVersion` list a model's versions and roll back
  or forward.
