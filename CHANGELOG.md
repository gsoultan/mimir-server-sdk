# Changelog

## v0.3.0

Built against mimir-server v0.3.1. Every call the server offers to people
and apps is now wrapped; only the worker's own `Link` stream is left to
`Raw()`.

- `client.SignIn`: sign-in with Google, GitHub or a company's own OpenID
  Connect provider. `Options` lists the sign-in page's buttons;
  `Providers`, `SaveProvider` and `DeleteProvider` manage them, with the
  rules that decide which team someone new lands in. `SignInKind` and its
  values are re-exported, and `RawClients` has the `SignIn` client.
- `Auth.ChangePassword`, `StartTwoFactor`, `EnableTwoFactor` and
  `DisableTwoFactor` for the signed-in person's password and two-step
  verification; `Sessions`, `RevokeSession` and `RevokeOtherSessions` for
  where they are signed in.
- `Auth.CheckDatabase` and `Auth.Setup` finish first-run setup with the
  setup token.
- `Settings.UpdateAlerts`, `SendTestAlert`, `UpdateRetention`,
  `UpdateSecurity` (with the `TwoFactorOptional`, `TwoFactorAdmins` and
  `TwoFactorEveryone` policies), `DatabaseInfo`, and `Backup`, which
  downloads a pg_dump of the database for an admin signed in with a
  password.
- `Datasets.TestQuery` and `TestBucket` show what a database query or a
  bucket holds before a dataset is made from it.
- `Models.SaveArchitecture` and `DeleteArchitecture` describe model types
  written in your own code.
- `Workers.ReplaceToken` gives a worker a new token.
- The `webhook` package knows `scoring.finished` and `scoring.failed`
  (`ScoringFinished`, `ScoringFailed`), and `Event.Scoring` decodes them.
- `OpenAIBaseURL` mentions `/v1/embeddings`, which the server serves too.

## v0.2.0

Built against mimir-server v0.3.0, and needs it for scorings, documents
and explanations.

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
- `client.Benchmarks`: a fixed test frozen from a dataset that every model
  takes the same way, with a leaderboard, `Score`, `WaitForScores` and
  `Leader`. Training on the dataset leaves the test rows out.
- `Training.Compare` puts two to six runs side by side, and a finished run
  carries its full report (`Job.GetReport()`).
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

## v0.1.0

The first release, built against mimir-server v0.1.3.

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
- The `webhook` package: signature checks, event decoding and an
  `http.Handler`.
