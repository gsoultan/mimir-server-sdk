// Package mimirsdk is the Go client for mimir-server: sign in with an API
// key, then manage models, datasets, training runs, webhooks and people,
// and ask models questions, including chats streamed as they are written.
//
//	client, err := mimirsdk.New("https://mimir.example.com", mimirsdk.WithAPIKey("mimir_..."))
//	if err != nil {
//		return err
//	}
//	models, err := client.Models.List(ctx)
//
// Every call takes a context. Calls that read without changing anything are
// retried when the server is briefly unavailable, and any call the server
// refuses with a Retry-After (a rate limit) is retried after that wait, up
// to WithRetries attempts. Errors from the server are *Error values: test
// them with errors.Is against ErrNotFound, ErrPermissionDenied and the other
// sentinels, or read Code and Message.
//
// The services cover what apps need most. For anything else, Raw returns
// the generated Connect clients for every service the server has, sharing
// the same API key, retries and timeouts.
//
// Request and response types are the server's own (package
// github.com/gsoultan/mimir-server/gen/mimir/v1), re-exported here under
// the same names, so one import is enough.
package mimirsdk
