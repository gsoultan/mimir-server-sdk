# Changelog

## v0.1.0 (unreleased)

The first release, built against mimir-server v0.1.2.

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
