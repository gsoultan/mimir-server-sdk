package mimirsdk_test

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"connectrpc.com/connect"
	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

const testKey = "mimir_test_key"

// fake is a stand-in server. Each test sets the hooks it needs; the rest
// answer Unimplemented.
type fake struct {
	mimirv1connect.UnimplementedModelServiceHandler
	mimirv1connect.UnimplementedPredictServiceHandler
	mimirv1connect.UnimplementedAuditServiceHandler
	mimirv1connect.UnimplementedTrainingServiceHandler
	mimirv1connect.UnimplementedApiKeyServiceHandler
	mimirv1connect.UnimplementedBenchmarkServiceHandler
	mimirv1connect.UnimplementedDatasetServiceHandler
	mimirv1connect.UnimplementedScoringServiceHandler

	mu      sync.Mutex
	headers []http.Header

	listModels  func(n int) (*mimirv1.ListModelsResponse, error)
	createModel func(n int, req *mimirv1.CreateModelRequest) (*mimirv1.CreateModelResponse, error)
	getModel    func(id string) (*mimirv1.GetModelResponse, error)
	predict     func(req *mimirv1.PredictRequest) (*mimirv1.PredictResponse, error)
	chat        func(req *mimirv1.ChatRequest, send func(*mimirv1.ChatResponse) error) error
	audit       func(req *mimirv1.ListAuditEventsRequest) (*mimirv1.ListAuditEventsResponse, error)
	getJob      func(n int) (*mimirv1.GetJobResponse, error)
	getBench    func(n int) (*mimirv1.GetBenchmarkResponse, error)
	dataset     func(req *mimirv1.CreateDatasetRequest) (*mimirv1.CreateDatasetResponse, error)
	versions    func(req *mimirv1.ListModelVersionsRequest) (*mimirv1.ListModelVersionsResponse, error)
	useVersion  func(req *mimirv1.UseModelVersionRequest) (*mimirv1.UseModelVersionResponse, error)
	quality     func(req *mimirv1.GetModelQualityRequest) (*mimirv1.GetModelQualityResponse, error)
	feedback    func(req *mimirv1.SendFeedbackRequest) (*mimirv1.SendFeedbackResponse, error)
	upload      http.Handler
	getScoring  func(n int) (*mimirv1.GetScoringResponse, error)
	results     http.Handler

	calls atomic.Int32
}

func (f *fake) record(h http.Header) int {
	f.mu.Lock()
	f.headers = append(f.headers, h.Clone())
	f.mu.Unlock()
	return int(f.calls.Add(1))
}

func (f *fake) lastHeader() http.Header {
	f.mu.Lock()
	defer f.mu.Unlock()
	return f.headers[len(f.headers)-1]
}

func (f *fake) ListModels(_ context.Context, req *connect.Request[mimirv1.ListModelsRequest]) (*connect.Response[mimirv1.ListModelsResponse], error) {
	n := f.record(req.Header())
	res, err := f.listModels(n)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) CreateModel(_ context.Context, req *connect.Request[mimirv1.CreateModelRequest]) (*connect.Response[mimirv1.CreateModelResponse], error) {
	n := f.record(req.Header())
	res, err := f.createModel(n, req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) GetModel(_ context.Context, req *connect.Request[mimirv1.GetModelRequest]) (*connect.Response[mimirv1.GetModelResponse], error) {
	f.record(req.Header())
	res, err := f.getModel(req.Msg.GetId())
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) Predict(_ context.Context, req *connect.Request[mimirv1.PredictRequest]) (*connect.Response[mimirv1.PredictResponse], error) {
	f.record(req.Header())
	res, err := f.predict(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) Chat(_ context.Context, req *connect.Request[mimirv1.ChatRequest], s *connect.ServerStream[mimirv1.ChatResponse]) error {
	f.record(req.Header())
	return f.chat(req.Msg, s.Send)
}

func (f *fake) ListAuditEvents(_ context.Context, req *connect.Request[mimirv1.ListAuditEventsRequest]) (*connect.Response[mimirv1.ListAuditEventsResponse], error) {
	f.record(req.Header())
	res, err := f.audit(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) GetJob(_ context.Context, req *connect.Request[mimirv1.GetJobRequest]) (*connect.Response[mimirv1.GetJobResponse], error) {
	n := f.record(req.Header())
	res, err := f.getJob(n)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) GetScoring(_ context.Context, req *connect.Request[mimirv1.GetScoringRequest]) (*connect.Response[mimirv1.GetScoringResponse], error) {
	n := f.record(req.Header())
	res, err := f.getScoring(n)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) GetBenchmark(_ context.Context, req *connect.Request[mimirv1.GetBenchmarkRequest]) (*connect.Response[mimirv1.GetBenchmarkResponse], error) {
	n := f.record(req.Header())
	res, err := f.getBench(n)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

// start serves f and returns a client for it. Retries wait at most a few
// milliseconds so the tests stay quick.
func (f *fake) CreateDataset(_ context.Context, req *connect.Request[mimirv1.CreateDatasetRequest]) (*connect.Response[mimirv1.CreateDatasetResponse], error) {
	f.record(req.Header())
	res, err := f.dataset(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func start(t *testing.T, f *fake, opts ...mimirsdk.Option) *mimirsdk.Client {
	t.Helper()
	mux := http.NewServeMux()
	mux.Handle(mimirv1connect.NewModelServiceHandler(f))
	mux.Handle(mimirv1connect.NewPredictServiceHandler(f))
	mux.Handle(mimirv1connect.NewAuditServiceHandler(f))
	mux.Handle(mimirv1connect.NewTrainingServiceHandler(f))
	mux.Handle(mimirv1connect.NewApiKeyServiceHandler(f))
	mux.Handle(mimirv1connect.NewBenchmarkServiceHandler(f))
	mux.Handle(mimirv1connect.NewDatasetServiceHandler(f))
	mux.Handle(mimirv1connect.NewScoringServiceHandler(f))
	if f.results != nil {
		mux.Handle("GET /api/scorings/{id}/results", f.results)
	}
	if f.upload != nil {
		mux.Handle("POST /api/uploads", f.upload)
	}
	srv := httptest.NewServer(mux)
	t.Cleanup(srv.Close)
	opts = append([]mimirsdk.Option{
		mimirsdk.WithAPIKey(testKey),
		mimirsdk.WithRetryBackoff(time.Millisecond, 2*time.Second),
	}, opts...)
	c, err := mimirsdk.New(srv.URL+"/", opts...)
	if err != nil {
		t.Fatal(err)
	}
	return c
}

func unavailable() error {
	return connect.NewError(connect.CodeUnavailable, errors.New("The server is starting."))
}

func rateLimited(secs int) error {
	err := connect.NewError(connect.CodeResourceExhausted, errors.New("Too many questions at once."))
	err.Meta().Set("Retry-After", fmt.Sprint(secs))
	return err
}

func TestSendsKeyAndUserAgent(t *testing.T) {
	f := &fake{listModels: func(int) (*mimirv1.ListModelsResponse, error) {
		return &mimirv1.ListModelsResponse{Models: []*mimirv1.Model{{Id: "m1", Name: "digits"}}}, nil
	}}
	c := start(t, f, mimirsdk.WithUserAgent("my-app/1.0"), mimirsdk.WithHeader("X-Team", "blue"))

	models, err := c.Models.List(t.Context())
	if err != nil {
		t.Fatal(err)
	}
	if len(models) != 1 || models[0].GetName() != "digits" {
		t.Fatalf("models = %v", models)
	}
	h := f.lastHeader()
	if got := h.Get("Authorization"); got != "Bearer "+testKey {
		t.Errorf("Authorization = %q", got)
	}
	if ua := h.Get("User-Agent"); !strings.HasPrefix(ua, "my-app/1.0 mimir-server-sdk-go/"+mimirsdk.Version) {
		t.Errorf("User-Agent = %q", ua)
	}
	if got := h.Get("X-Team"); got != "blue" {
		t.Errorf("X-Team = %q", got)
	}
}

func TestTypedErrors(t *testing.T) {
	f := &fake{getModel: func(id string) (*mimirv1.GetModelResponse, error) {
		return nil, connect.NewError(connect.CodeNotFound, fmt.Errorf("There's no model %s.", id))
	}}
	c := start(t, f)

	_, err := c.Models.Get(t.Context(), "nope")
	if !errors.Is(err, mimirsdk.ErrNotFound) {
		t.Fatalf("err = %v, want ErrNotFound", err)
	}
	if errors.Is(err, mimirsdk.ErrPermissionDenied) {
		t.Error("a not-found error matched ErrPermissionDenied")
	}
	var apiErr *mimirsdk.Error
	if !errors.As(err, &apiErr) {
		t.Fatalf("err is %T, want *mimirsdk.Error", err)
	}
	if apiErr.Code != mimirsdk.CodeNotFound || apiErr.Message != "There's no model nope." {
		t.Errorf("code %v, message %q", apiErr.Code, apiErr.Message)
	}
	if apiErr.Procedure != mimirv1connect.ModelServiceGetModelProcedure {
		t.Errorf("procedure = %q", apiErr.Procedure)
	}
	if want := "mimirsdk: ModelService/GetModel: not_found: There's no model nope."; err.Error() != want {
		t.Errorf("Error() = %q, want %q", err.Error(), want)
	}
	if f.calls.Load() != 1 {
		t.Errorf("a not-found call was tried %d times", f.calls.Load())
	}
}

func TestRetriesReadsWhenUnavailable(t *testing.T) {
	f := &fake{listModels: func(n int) (*mimirv1.ListModelsResponse, error) {
		if n < 3 {
			return nil, unavailable()
		}
		return &mimirv1.ListModelsResponse{}, nil
	}}
	c := start(t, f)

	if _, err := c.Models.List(t.Context()); err != nil {
		t.Fatal(err)
	}
	if n := f.calls.Load(); n != 3 {
		t.Errorf("calls = %d, want 3", n)
	}
}

func TestGivesUpAfterRetries(t *testing.T) {
	f := &fake{listModels: func(int) (*mimirv1.ListModelsResponse, error) { return nil, unavailable() }}
	c := start(t, f, mimirsdk.WithRetries(2))

	_, err := c.Models.List(t.Context())
	if !errors.Is(err, mimirsdk.ErrUnavailable) {
		t.Fatalf("err = %v", err)
	}
	if n := f.calls.Load(); n != 3 {
		t.Errorf("calls = %d, want 1 try and 2 retries", n)
	}
}

func TestDoesNotRetryChangesWhenUnavailable(t *testing.T) {
	f := &fake{createModel: func(int, *mimirv1.CreateModelRequest) (*mimirv1.CreateModelResponse, error) {
		return nil, unavailable()
	}}
	c := start(t, f)

	_, err := c.Models.Create(t.Context(), &mimirsdk.CreateModelRequest{Name: "x"})
	if !errors.Is(err, mimirsdk.ErrUnavailable) {
		t.Fatalf("err = %v", err)
	}
	if n := f.calls.Load(); n != 1 {
		t.Errorf("an upload that may have landed was sent %d times", n)
	}
}

func TestRetriesAfterRetryAfter(t *testing.T) {
	f := &fake{createModel: func(n int, req *mimirv1.CreateModelRequest) (*mimirv1.CreateModelResponse, error) {
		if n == 1 {
			return nil, rateLimited(1)
		}
		return &mimirv1.CreateModelResponse{Model: &mimirv1.Model{Id: "m1", Name: req.GetName()}}, nil
	}}
	c := start(t, f)

	began := time.Now()
	m, err := c.Models.Create(t.Context(), &mimirsdk.CreateModelRequest{Name: "digits"})
	if err != nil {
		t.Fatal(err)
	}
	if m.GetName() != "digits" {
		t.Errorf("model = %v", m)
	}
	if waited := time.Since(began); waited < time.Second {
		t.Errorf("retried after %v, before the server's Retry-After", waited)
	}
}

func TestLongRetryAfterIsReturned(t *testing.T) {
	f := &fake{predict: func(*mimirv1.PredictRequest) (*mimirv1.PredictResponse, error) {
		return nil, rateLimited(60)
	}}
	c := start(t, f)

	_, err := c.Models.PredictFields(t.Context(), "m1", map[string]string{"age": "40"})
	var apiErr *mimirsdk.Error
	if !errors.As(err, &apiErr) || !errors.Is(err, mimirsdk.ErrResourceExhausted) {
		t.Fatalf("err = %v", err)
	}
	if apiErr.RetryAfter != time.Minute || !apiErr.Retryable() {
		t.Errorf("RetryAfter = %v, Retryable = %v", apiErr.RetryAfter, apiErr.Retryable())
	}
	if n := f.calls.Load(); n != 1 {
		t.Errorf("calls = %d; a wait past the cap should not be retried", n)
	}
}

func TestTimeout(t *testing.T) {
	f := &fake{getModel: func(string) (*mimirv1.GetModelResponse, error) {
		time.Sleep(200 * time.Millisecond)
		return &mimirv1.GetModelResponse{}, nil
	}}
	c := start(t, f, mimirsdk.WithTimeout(20*time.Millisecond))

	_, err := c.Models.Get(t.Context(), "m1")
	if !errors.Is(err, context.DeadlineExceeded) {
		t.Fatalf("err = %v, want context.DeadlineExceeded", err)
	}
}

func TestChatStream(t *testing.T) {
	f := &fake{chat: func(req *mimirv1.ChatRequest, send func(*mimirv1.ChatResponse) error) error {
		if got := req.GetMessages()[0].GetContent(); got != "Hi" {
			return connect.NewError(connect.CodeInvalidArgument, fmt.Errorf("got %q", got))
		}
		for _, piece := range []string{"Hel", "lo", "!"} {
			if err := send(&mimirv1.ChatResponse{Text: piece}); err != nil {
				return err
			}
		}
		return send(&mimirv1.ChatResponse{Done: true, PromptTokens: 3, GeneratedTokens: 2, Finished: true})
	}}
	c := start(t, f)
	req := &mimirsdk.ChatRequest{ModelId: "llm", Messages: []*mimirsdk.ChatMessage{mimirsdk.UserMessage("Hi")}}

	var text strings.Builder
	var last *mimirsdk.ChatResponse
	for piece, err := range c.Models.Chat(t.Context(), req) {
		if err != nil {
			t.Fatal(err)
		}
		text.WriteString(piece.GetText())
		last = piece
	}
	if text.String() != "Hello!" || !last.GetDone() || last.GetGeneratedTokens() != 2 {
		t.Errorf("text %q, last %v", text.String(), last)
	}
	if got := f.lastHeader().Get("Authorization"); got != "Bearer "+testKey {
		t.Errorf("stream Authorization = %q", got)
	}

	reply, err := c.Models.ChatText(t.Context(), req)
	if err != nil {
		t.Fatal(err)
	}
	if reply.Text != "Hello!" || reply.PromptTokens != 3 || !reply.Finished {
		t.Errorf("reply = %+v", reply)
	}
}

func TestChatStreamError(t *testing.T) {
	f := &fake{chat: func(_ *mimirv1.ChatRequest, send func(*mimirv1.ChatResponse) error) error {
		if err := send(&mimirv1.ChatResponse{Text: "Hel"}); err != nil {
			return err
		}
		return connect.NewError(connect.CodeResourceExhausted, errors.New("The model ran out of memory."))
	}}
	c := start(t, f)

	_, err := c.Models.ChatText(t.Context(), &mimirsdk.ChatRequest{ModelId: "llm"})
	if !errors.Is(err, mimirsdk.ErrResourceExhausted) {
		t.Fatalf("err = %v", err)
	}
}

func TestChatStopsEarly(t *testing.T) {
	stopped := make(chan struct{})
	f := &fake{chat: func(_ *mimirv1.ChatRequest, send func(*mimirv1.ChatResponse) error) error {
		defer close(stopped)
		for {
			if err := send(&mimirv1.ChatResponse{Text: "la "}); err != nil {
				return err
			}
			time.Sleep(time.Millisecond)
		}
	}}
	c := start(t, f)

	n := 0
	for _, err := range c.Models.Chat(t.Context(), &mimirsdk.ChatRequest{ModelId: "llm"}) {
		if err != nil {
			t.Fatal(err)
		}
		if n++; n == 3 {
			break
		}
	}
	select {
	case <-stopped:
	case <-time.After(5 * time.Second):
		t.Fatal("the server kept writing after the loop stopped")
	}
}

func TestAuditPages(t *testing.T) {
	pages := map[string]*mimirv1.ListAuditEventsResponse{
		"":   {Events: []*mimirv1.AuditEvent{{Id: "1"}, {Id: "2"}}, NextPageToken: "p2"},
		"p2": {Events: []*mimirv1.AuditEvent{{Id: "3"}}, NextPageToken: "p3"},
		"p3": {Events: []*mimirv1.AuditEvent{{Id: "4"}}},
	}
	f := &fake{audit: func(req *mimirv1.ListAuditEventsRequest) (*mimirv1.ListAuditEventsResponse, error) {
		if req.GetPageSize() != 2 {
			return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("page size"))
		}
		return pages[req.GetPageToken()], nil
	}}
	c := start(t, f)

	var ids []string
	for ev, err := range c.Audit.All(t.Context(), mimirsdk.ListOptions{PageSize: 2}) {
		if err != nil {
			t.Fatal(err)
		}
		ids = append(ids, ev.GetId())
	}
	if got := strings.Join(ids, ","); got != "1,2,3,4" {
		t.Errorf("ids = %s", got)
	}

	// Stopping early fetches no more pages than it needs.
	f.calls.Store(0)
	for range c.Audit.All(t.Context(), mimirsdk.ListOptions{PageSize: 2}) {
		break
	}
	if n := f.calls.Load(); n != 1 {
		t.Errorf("fetched %d pages for one event", n)
	}
}

func TestWaitForTraining(t *testing.T) {
	statuses := []mimirv1.JobStatus{mimirsdk.JobStatusQueued, mimirsdk.JobStatusRunning, mimirsdk.JobStatusSucceeded}
	f := &fake{getJob: func(n int) (*mimirv1.GetJobResponse, error) {
		return &mimirv1.GetJobResponse{Job: &mimirv1.Job{Id: "j1", Status: statuses[min(n, len(statuses))-1], ModelId: "m9"}}, nil
	}}
	c := start(t, f)

	seen := 0
	job, err := c.Training.Wait(t.Context(), "j1", mimirsdk.WaitOptions{
		Interval:   time.Millisecond,
		OnProgress: func(*mimirsdk.Job) { seen++ },
	})
	if err != nil {
		t.Fatal(err)
	}
	if job.GetModelId() != "m9" || seen != 3 {
		t.Errorf("job %v, progress calls %d", job, seen)
	}
}

func TestWaitForFailedTraining(t *testing.T) {
	f := &fake{getJob: func(int) (*mimirv1.GetJobResponse, error) {
		return &mimirv1.GetJobResponse{Job: &mimirv1.Job{Id: "j1", Status: mimirsdk.JobStatusFailed, Error: "The data has no rows."}}, nil
	}}
	c := start(t, f)

	job, err := c.Training.Wait(t.Context(), "j1", mimirsdk.WaitOptions{Interval: time.Millisecond})
	var jobErr *mimirsdk.JobError
	if !errors.As(err, &jobErr) || job == nil {
		t.Fatalf("err = %v", err)
	}
	if want := "mimirsdk: training run j1 failed: The data has no rows."; err.Error() != want {
		t.Errorf("Error() = %q", err.Error())
	}
}

func TestNew(t *testing.T) {
	for _, bad := range []string{"", "localhost:8080", "ftp://x", "https://u:p@x", "https://x?y=1"} {
		if _, err := mimirsdk.New(bad); err == nil {
			t.Errorf("New(%q) took a bad address", bad)
		}
	}
	if _, err := mimirsdk.New("https://x", mimirsdk.WithAPIKey("mimir_a\nb")); err == nil {
		t.Error("New took a key with a line break")
	}
	c, err := mimirsdk.New(" https://mimir.example.com/base/ ")
	if err != nil {
		t.Fatal(err)
	}
	if c.BaseURL() != "https://mimir.example.com/base" || c.OpenAIBaseURL() != "https://mimir.example.com/base/v1" {
		t.Errorf("BaseURL %q, OpenAIBaseURL %q", c.BaseURL(), c.OpenAIBaseURL())
	}
}

func TestNewFromEnv(t *testing.T) {
	t.Setenv(mimirsdk.EnvURL, "")
	if _, err := mimirsdk.NewFromEnv(); err == nil {
		t.Error("NewFromEnv worked without MIMIR_URL")
	}

	f := &fake{listModels: func(int) (*mimirv1.ListModelsResponse, error) { return &mimirv1.ListModelsResponse{}, nil }}
	mux := http.NewServeMux()
	mux.Handle(mimirv1connect.NewModelServiceHandler(f))
	srv := httptest.NewServer(mux)
	defer srv.Close()
	t.Setenv(mimirsdk.EnvURL, srv.URL)
	t.Setenv(mimirsdk.EnvAPIKey, "mimir_from_env")

	c, err := mimirsdk.NewFromEnv()
	if err != nil {
		t.Fatal(err)
	}
	if _, err := c.Models.List(t.Context()); err != nil {
		t.Fatal(err)
	}
	if got := f.lastHeader().Get("Authorization"); got != "Bearer mimir_from_env" {
		t.Errorf("Authorization = %q", got)
	}
}

func TestRawShareAuth(t *testing.T) {
	f := &fake{listModels: func(int) (*mimirv1.ListModelsResponse, error) { return &mimirv1.ListModelsResponse{}, nil }}
	c := start(t, f)

	if _, err := c.Raw().Models.ListModels(t.Context(), connect.NewRequest(&mimirv1.ListModelsRequest{})); err != nil {
		t.Fatal(err)
	}
	if got := f.lastHeader().Get("Authorization"); got != "Bearer "+testKey {
		t.Errorf("Authorization = %q", got)
	}
}

func TestUnimplemented(t *testing.T) {
	c := start(t, &fake{})
	_, err := c.APIKeys.List(t.Context())
	if !errors.Is(err, mimirsdk.ErrUnimplemented) {
		t.Fatalf("err = %v", err)
	}
}

func TestUploadStreamsTheFile(t *testing.T) {
	weights := strings.Repeat("w", 3<<20)
	f := &fake{}
	f.upload = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		f.record(r.Header)
		b, _ := io.ReadAll(r.Body)
		if string(b) != weights || r.ContentLength != int64(len(weights)) {
			http.Error(w, "wrong body", http.StatusBadRequest)
			return
		}
		fmt.Fprintf(w, `{"upload":"up1","size":%d}`, len(b))
	})
	f.createModel = func(_ int, req *mimirv1.CreateModelRequest) (*mimirv1.CreateModelResponse, error) {
		if req.GetUpload() != "up1" || len(req.GetWeights()) != 0 {
			return nil, connect.NewError(connect.CodeInvalidArgument, fmt.Errorf("upload %q, %d bytes of weights", req.GetUpload(), len(req.GetWeights())))
		}
		return &mimirv1.CreateModelResponse{Model: &mimirv1.Model{Id: "m1", Name: req.GetName()}}, nil
	}
	c := start(t, f)

	path := filepath.Join(t.TempDir(), "digits.mim")
	if err := os.WriteFile(path, []byte(weights), 0o600); err != nil {
		t.Fatal(err)
	}
	m, err := c.Models.UploadFile(t.Context(), path, "", "mim")
	if err != nil {
		t.Fatal(err)
	}
	if m.GetName() != "digits" {
		t.Errorf("model = %v", m)
	}
	f.mu.Lock()
	h := f.headers[0]
	f.mu.Unlock()
	if got := h.Get("Authorization"); got != "Bearer "+testKey {
		t.Errorf("upload Authorization = %q", got)
	}
}

func TestUploadError(t *testing.T) {
	f := &fake{upload: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusRequestEntityTooLarge)
		fmt.Fprint(w, `{"code":"resource_exhausted","message":"This file is larger than the 512 MB this server takes."}`)
	})}
	c := start(t, f)

	_, err := c.Models.Upload(t.Context(), "big", "mim", strings.NewReader("x"))
	var apiErr *mimirsdk.Error
	if !errors.As(err, &apiErr) || !errors.Is(err, mimirsdk.ErrResourceExhausted) {
		t.Fatalf("err = %v", err)
	}
	if apiErr.Message != "This file is larger than the 512 MB this server takes." {
		t.Errorf("message = %q", apiErr.Message)
	}
}

func TestUploadsSayTheirKind(t *testing.T) {
	var got []*mimirv1.CreateDatasetRequest
	f := &fake{dataset: func(req *mimirv1.CreateDatasetRequest) (*mimirv1.CreateDatasetResponse, error) {
		got = append(got, req)
		return &mimirv1.CreateDatasetResponse{Dataset: &mimirv1.Dataset{Id: "d1", Kind: req.GetKind()}}, nil
	}}
	c := start(t, f)
	ctx := t.Context()
	uploads := []struct {
		kind   mimirsdk.DatasetKind
		upload func() (*mimirsdk.CreateDatasetResponse, error)
	}{
		{mimirsdk.DatasetKindSounds, func() (*mimirsdk.CreateDatasetResponse, error) {
			return c.Datasets.UploadSounds(ctx, "calls", strings.NewReader("sounds zip"))
		}},
		{mimirsdk.DatasetKindBoxes, func() (*mimirsdk.CreateDatasetResponse, error) {
			return c.Datasets.UploadBoxes(ctx, "shelves", strings.NewReader("boxes zip"))
		}},
		{mimirsdk.DatasetKindText, func() (*mimirsdk.CreateDatasetResponse, error) {
			return c.Datasets.UploadText(ctx, "letters", strings.NewReader("Dear reader,"))
		}},
	}
	for i, u := range uploads {
		res, err := u.upload()
		if err != nil {
			t.Fatal(err)
		}
		req := got[i]
		if req.GetKind() != u.kind || res.GetDataset().GetKind() != u.kind {
			t.Errorf("%v upload sent kind %v", u.kind, req.GetKind())
		}
		if u.kind == mimirsdk.DatasetKindText {
			if string(req.GetText()) != "Dear reader," || len(req.GetArchive()) != 0 {
				t.Errorf("text sent as text %q, archive %q", req.GetText(), req.GetArchive())
			}
		} else if len(req.GetArchive()) == 0 || len(req.GetText()) != 0 {
			t.Errorf("%v sent archive %q, text %q", u.kind, req.GetArchive(), req.GetText())
		}
	}
}
