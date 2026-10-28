package mimirsdk

import (
	"errors"
	"fmt"
	"net/url"
	"os"
	"strings"

	"connectrpc.com/connect"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// Environment variables NewFromEnv reads.
const (
	EnvURL    = "MIMIR_URL"
	EnvAPIKey = "MIMIR_API_KEY"
)

// Client talks to one mimir-server. It is safe for concurrent use; make one
// and share it.
type Client struct {
	baseURL string
	raw     *RawClients

	Auth       *AuthService
	APIKeys    *APIKeyService
	Users      *UserService
	Teams      *TeamService
	Audit      *AuditService
	Models     *ModelService
	Datasets   *DatasetService
	Training   *TrainingService
	Webhooks   *WebhookService
	Workers    *WorkerService
	Settings   *SettingsService
	Templates  *TemplateService
	Benchmarks *BenchmarkService
	Scorings   *ScoringService
	Documents  *DocumentService
}

// RawClients are the generated Connect clients for every service. Use them
// for calls the services on Client don't wrap.
type RawClients struct {
	Auth       mimirv1connect.AuthServiceClient
	Users      mimirv1connect.UserServiceClient
	APIKeys    mimirv1connect.ApiKeyServiceClient
	Audit      mimirv1connect.AuditServiceClient
	Teams      mimirv1connect.TeamServiceClient
	Models     mimirv1connect.ModelServiceClient
	Predict    mimirv1connect.PredictServiceClient
	Datasets   mimirv1connect.DatasetServiceClient
	Training   mimirv1connect.TrainingServiceClient
	Webhooks   mimirv1connect.WebhookServiceClient
	Workers    mimirv1connect.WorkerServiceClient
	Settings   mimirv1connect.SettingsServiceClient
	Templates  mimirv1connect.TemplateServiceClient
	Benchmarks mimirv1connect.BenchmarkServiceClient
	Scorings   mimirv1connect.ScoringServiceClient
	Documents  mimirv1connect.DocumentServiceClient
}

// New returns a client for the server at baseURL, such as
// "https://mimir.example.com" or "http://localhost:8080".
func New(baseURL string, opts ...Option) (*Client, error) {
	base, err := parseBaseURL(baseURL)
	if err != nil {
		return nil, err
	}
	cfg := defaultConfig()
	for _, opt := range opts {
		opt(&cfg)
	}
	if strings.ContainsAny(cfg.apiKey, "\r\n ") {
		return nil, errors.New("mimirsdk: the API key has spaces or line breaks in it")
	}

	ic := &interceptor{cfg: cfg}
	copts := append([]connect.ClientOption{
		connect.WithInterceptors(ic),
	}, cfg.connectOpts...)
	h := cfg.httpClient
	raw := &RawClients{
		Auth:       mimirv1connect.NewAuthServiceClient(h, base, copts...),
		Users:      mimirv1connect.NewUserServiceClient(h, base, copts...),
		APIKeys:    mimirv1connect.NewApiKeyServiceClient(h, base, copts...),
		Audit:      mimirv1connect.NewAuditServiceClient(h, base, copts...),
		Teams:      mimirv1connect.NewTeamServiceClient(h, base, copts...),
		Models:     mimirv1connect.NewModelServiceClient(h, base, copts...),
		Predict:    mimirv1connect.NewPredictServiceClient(h, base, copts...),
		Datasets:   mimirv1connect.NewDatasetServiceClient(h, base, copts...),
		Training:   mimirv1connect.NewTrainingServiceClient(h, base, copts...),
		Webhooks:   mimirv1connect.NewWebhookServiceClient(h, base, copts...),
		Workers:    mimirv1connect.NewWorkerServiceClient(h, base, copts...),
		Settings:   mimirv1connect.NewSettingsServiceClient(h, base, copts...),
		Templates:  mimirv1connect.NewTemplateServiceClient(h, base, copts...),
		Benchmarks: mimirv1connect.NewBenchmarkServiceClient(h, base, copts...),
		Scorings:   mimirv1connect.NewScoringServiceClient(h, base, copts...),
		Documents:  mimirv1connect.NewDocumentServiceClient(h, base, copts...),
	}
	return &Client{
		baseURL:    base,
		raw:        raw,
		Auth:       &AuthService{raw: raw.Auth},
		APIKeys:    &APIKeyService{raw: raw.APIKeys},
		Users:      &UserService{raw: raw.Users},
		Teams:      &TeamService{raw: raw.Teams},
		Audit:      &AuditService{raw: raw.Audit},
		Models:     &ModelService{raw: raw.Models, predict: raw.Predict, uploads: &uploader{http: h, url: base + uploadPath, ic: ic}},
		Datasets:   &DatasetService{raw: raw.Datasets},
		Training:   &TrainingService{raw: raw.Training},
		Webhooks:   &WebhookService{raw: raw.Webhooks},
		Workers:    &WorkerService{raw: raw.Workers},
		Settings:   &SettingsService{raw: raw.Settings},
		Templates:  &TemplateService{raw: raw.Templates},
		Benchmarks: &BenchmarkService{raw: raw.Benchmarks},
		Scorings:   &ScoringService{raw: raw.Scorings, http: h, base: base, download: ic},
		Documents:  &DocumentService{raw: raw.Documents},
	}, nil
}

// NewFromEnv is New with the server address from $MIMIR_URL and the API key
// from $MIMIR_API_KEY. Options given here win over the environment.
func NewFromEnv(opts ...Option) (*Client, error) {
	base := os.Getenv(EnvURL)
	if base == "" {
		return nil, fmt.Errorf("mimirsdk: set %s to the server's address, like http://localhost:8080", EnvURL)
	}
	if key := os.Getenv(EnvAPIKey); key != "" {
		opts = append([]Option{WithAPIKey(key)}, opts...)
	}
	return New(base, opts...)
}

// BaseURL is the server address the client was made with, without a
// trailing slash.
func (c *Client) BaseURL() string { return c.baseURL }

// OpenAIBaseURL is where the server's OpenAI-compatible API lives
// (/v1/chat/completions, /v1/completions, /v1/models). Point an OpenAI
// client library at it with a mimir API key to chat with language models.
func (c *Client) OpenAIBaseURL() string { return c.baseURL + "/v1" }

// Raw returns the generated Connect clients behind the services. They share
// the client's API key, retries and timeout, but return *connect.Error
// rather than *Error.
func (c *Client) Raw() *RawClients { return c.raw }

func parseBaseURL(raw string) (string, error) {
	raw = strings.TrimSpace(raw)
	u, err := url.Parse(raw)
	if err != nil || u.Host == "" {
		return "", fmt.Errorf("mimirsdk: %q is not a server address; use one like https://mimir.example.com", raw)
	}
	if u.Scheme != "http" && u.Scheme != "https" {
		return "", fmt.Errorf("mimirsdk: the server address must start with http:// or https://, not %q", u.Scheme+"://")
	}
	if u.User != nil {
		return "", errors.New("mimirsdk: don't put a username or password in the server address; use WithAPIKey")
	}
	if u.RawQuery != "" || u.Fragment != "" {
		return "", errors.New("mimirsdk: the server address can't have a query or fragment")
	}
	return strings.TrimRight(u.String(), "/"), nil
}
