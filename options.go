package mimirsdk

import (
	"net/http"
	"time"

	"connectrpc.com/connect"
)

// Defaults for the options below.
const (
	DefaultTimeout      = 60 * time.Second
	DefaultRetries      = 3
	DefaultRetryBackoff = 250 * time.Millisecond
	DefaultMaxRetryWait = 30 * time.Second
)

// Option changes how a Client talks to the server.
type Option func(*config)

type config struct {
	apiKey       string
	httpClient   connect.HTTPClient
	timeout      time.Duration
	retries      int
	backoff      time.Duration
	maxRetryWait time.Duration
	userAgent    string
	header       http.Header
	connectOpts  []connect.ClientOption
}

func defaultConfig() config {
	return config{
		httpClient:   http.DefaultClient,
		timeout:      DefaultTimeout,
		retries:      DefaultRetries,
		backoff:      DefaultRetryBackoff,
		maxRetryWait: DefaultMaxRetryWait,
		header:       http.Header{},
	}
}

// WithAPIKey signs every request in with an API key (mimir_...), sent as
// "Authorization: Bearer". Create keys in the console under API keys, or
// with APIKeys.Create.
func WithAPIKey(key string) Option {
	return func(c *config) { c.apiKey = key }
}

// WithHTTPClient sends requests through client instead of
// http.DefaultClient. Give it a cookie jar to sign in with a password
// (Auth.SignIn) instead of an API key. Don't set client.Timeout: it would
// cut streamed chats short. Use WithTimeout or a context deadline instead.
func WithHTTPClient(client connect.HTTPClient) Option {
	return func(c *config) {
		if client != nil {
			c.httpClient = client
		}
	}
}

// WithTimeout bounds each call that returns one response, retries
// included, when its context has no deadline of its own. 0 means no bound.
// Streamed calls (Chat, GenerateStream) are bounded only by their context.
// The default is DefaultTimeout.
func WithTimeout(d time.Duration) Option {
	return func(c *config) { c.timeout = max(d, 0) }
}

// WithRetries sets how many times a failed call may be tried again. 0
// turns retries off. The default is DefaultRetries.
func WithRetries(n int) Option {
	return func(c *config) { c.retries = max(n, 0) }
}

// WithRetryBackoff sets the wait before the first retry; each later retry
// waits twice as long, with jitter, up to maxWait. A Retry-After from the
// server replaces the backoff, and a call whose Retry-After is longer than
// maxWait is not retried. The defaults are DefaultRetryBackoff and
// DefaultMaxRetryWait.
func WithRetryBackoff(base, maxWait time.Duration) Option {
	return func(c *config) {
		if base > 0 {
			c.backoff = base
		}
		if maxWait > 0 {
			c.maxRetryWait = maxWait
		}
	}
}

// WithUserAgent puts product (like "my-app/1.2") ahead of the SDK's own
// User-Agent.
func WithUserAgent(product string) Option {
	return func(c *config) { c.userAgent = product }
}

// WithHeader adds a header to every request, such as one a proxy in front
// of the server needs.
func WithHeader(key, value string) Option {
	return func(c *config) { c.header.Add(key, value) }
}

// WithConnectOptions passes options to the underlying Connect clients, such
// as connect.WithGRPC() or extra interceptors.
func WithConnectOptions(opts ...connect.ClientOption) Option {
	return func(c *config) { c.connectOpts = append(c.connectOpts, opts...) }
}
