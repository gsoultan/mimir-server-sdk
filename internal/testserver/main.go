// Command testserver is a small stand-in for mimir-server that the Python
// and JavaScript SDKs' tests talk to. It serves the real Connect handlers
// generated from the server's protos, so the tests check the SDKs against
// the same wire format the server speaks, with canned answers.
//
//	go run ./internal/testserver
//
// It prints "listening on http://127.0.0.1:<port>" and serves until its
// standard input closes. Calls need "Authorization: Bearer mimir_test_key",
// except GetSetupState.
//
// Tests that count calls send X-Test-Run with a name of their own and read
// the counts back from GET /test/count?run=<name>&procedure=<procedure>.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"

	"connectrpc.com/connect"
	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

const testKey = "mimir_test_key"

func main() {
	addr := "127.0.0.1:0"
	if len(os.Args) > 1 {
		addr = os.Args[1]
	}
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatal(err)
	}
	s := &server{counts: map[string]int{}}
	srv := &http.Server{Handler: s.routes()}
	go func() {
		// Stop when the test that started us goes away.
		_, _ = io.Copy(io.Discard, os.Stdin)
		_ = srv.Close()
	}()
	fmt.Printf("listening on http://%s\n", ln.Addr())
	if err := srv.Serve(ln); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatal(err)
	}
}

type server struct {
	mimirv1connect.UnimplementedModelServiceHandler
	mimirv1connect.UnimplementedPredictServiceHandler
	mimirv1connect.UnimplementedAuthServiceHandler
	mimirv1connect.UnimplementedAuditServiceHandler
	mimirv1connect.UnimplementedTrainingServiceHandler
	mimirv1connect.UnimplementedDatasetServiceHandler
	mimirv1connect.UnimplementedDocumentServiceHandler
	mimirv1connect.UnimplementedScoringServiceHandler

	mu     sync.Mutex
	counts map[string]int
}

func (s *server) routes() http.Handler {
	mux := http.NewServeMux()
	opts := connect.WithInterceptors(s)
	mux.Handle(mimirv1connect.NewModelServiceHandler(s, opts))
	mux.Handle(mimirv1connect.NewPredictServiceHandler(s, opts))
	mux.Handle(mimirv1connect.NewAuthServiceHandler(s, opts))
	mux.Handle(mimirv1connect.NewAuditServiceHandler(s, opts))
	mux.Handle(mimirv1connect.NewTrainingServiceHandler(s, opts))
	mux.Handle(mimirv1connect.NewDatasetServiceHandler(s, opts))
	mux.Handle(mimirv1connect.NewDocumentServiceHandler(s, opts))
	mux.Handle(mimirv1connect.NewScoringServiceHandler(s, opts))
	mux.HandleFunc("POST /api/uploads", s.upload)
	mux.HandleFunc("GET /api/scorings/{id}/results", s.results)
	mux.HandleFunc("GET /test/count", s.count)
	return mux
}

// count records a call and returns how many times this run has made it.
func (s *server) record(h http.Header, procedure string) int {
	s.mu.Lock()
	defer s.mu.Unlock()
	k := h.Get("X-Test-Run") + " " + procedure
	s.counts[k]++
	return s.counts[k]
}

func (s *server) count(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	n := s.counts[r.URL.Query().Get("run")+" "+r.URL.Query().Get("procedure")]
	s.mu.Unlock()
	_ = json.NewEncoder(w).Encode(map[string]int{"count": n})
}

func authorized(h http.Header) bool {
	return h.Get("Authorization") == "Bearer "+testKey
}

// The interceptor checks the API key and counts calls.

func (s *server) WrapUnary(next connect.UnaryFunc) connect.UnaryFunc {
	return func(ctx context.Context, req connect.AnyRequest) (connect.AnyResponse, error) {
		s.record(req.Header(), req.Spec().Procedure)
		if req.Spec().Procedure != mimirv1connect.AuthServiceGetSetupStateProcedure && !authorized(req.Header()) {
			return nil, connect.NewError(connect.CodeUnauthenticated, errors.New("sign in first"))
		}
		return next(ctx, req)
	}
}

func (s *server) WrapStreamingClient(next connect.StreamingClientFunc) connect.StreamingClientFunc {
	return next
}

func (s *server) WrapStreamingHandler(next connect.StreamingHandlerFunc) connect.StreamingHandlerFunc {
	return func(ctx context.Context, conn connect.StreamingHandlerConn) error {
		s.record(conn.RequestHeader(), conn.Spec().Procedure)
		if !authorized(conn.RequestHeader()) {
			return connect.NewError(connect.CodeUnauthenticated, errors.New("sign in first"))
		}
		return next(ctx, conn)
	}
}

// Models.

var models = []*mimirv1.Model{
	{Id: "m1", Name: "churn", Architecture: "mim", Status: mimirv1.ModelStatus_MODEL_STATUS_READY, SizeBytes: 1 << 40},
	{Id: "m2", Name: "llama", Architecture: "llama", Status: mimirv1.ModelStatus_MODEL_STATUS_READY},
}

func (s *server) ListModels(context.Context, *connect.Request[mimirv1.ListModelsRequest]) (*connect.Response[mimirv1.ListModelsResponse], error) {
	return connect.NewResponse(&mimirv1.ListModelsResponse{Models: models}), nil
}

func (s *server) GetModel(_ context.Context, req *connect.Request[mimirv1.GetModelRequest]) (*connect.Response[mimirv1.GetModelResponse], error) {
	for _, m := range models {
		if m.GetId() == req.Msg.GetId() {
			return connect.NewResponse(&mimirv1.GetModelResponse{Model: m}), nil
		}
	}
	return nil, connect.NewError(connect.CodeNotFound, fmt.Errorf("no model %q", req.Msg.GetId()))
}

// ListArchitectures fails as unavailable the first two times each run asks,
// so tests can see reads retried.
func (s *server) ListArchitectures(_ context.Context, req *connect.Request[mimirv1.ListArchitecturesRequest]) (*connect.Response[mimirv1.ListArchitecturesResponse], error) {
	n := s.record(req.Header(), "attempt ListArchitectures")
	if n <= 2 {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("starting up"))
	}
	return connect.NewResponse(&mimirv1.ListArchitecturesResponse{Architectures: []*mimirv1.Architecture{
		{Name: "mim", Description: "attempt " + strconv.Itoa(n)},
	}}), nil
}

// DeleteModel of "unavailable" always fails as unavailable: it has side
// effects, so it must not be retried.
func (s *server) DeleteModel(_ context.Context, req *connect.Request[mimirv1.DeleteModelRequest]) (*connect.Response[mimirv1.DeleteModelResponse], error) {
	if req.Msg.GetId() == "unavailable" {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("lost the reply"))
	}
	return connect.NewResponse(&mimirv1.DeleteModelResponse{}), nil
}

func (s *server) CreateModel(_ context.Context, req *connect.Request[mimirv1.CreateModelRequest]) (*connect.Response[mimirv1.CreateModelResponse], error) {
	m := &mimirv1.Model{Id: "m-new", Name: req.Msg.GetName(), Architecture: req.Msg.GetArchitecture()}
	switch {
	case req.Msg.GetUpload() != "":
		m.Description = "upload " + req.Msg.GetUpload()
	default:
		m.Description = "weights " + strconv.Itoa(len(req.Msg.GetWeights()))
	}
	return connect.NewResponse(&mimirv1.CreateModelResponse{Model: m}), nil
}

func (s *server) upload(w http.ResponseWriter, r *http.Request) {
	if !authorized(r.Header) {
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write([]byte(`{"code":"unauthenticated","message":"sign in first"}`))
		return
	}
	n, err := io.Copy(io.Discard, r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	if n == 0 {
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte(`{"code":"invalid_argument","message":"the file is empty"}`))
		return
	}
	_ = json.NewEncoder(w).Encode(map[string]string{"upload": fmt.Sprintf("u-%d-%d", n, r.ContentLength)})
}

// Predictions.

func (s *server) Predict(_ context.Context, req *connect.Request[mimirv1.PredictRequest]) (*connect.Response[mimirv1.PredictResponse], error) {
	res := &mimirv1.PredictResponse{PredictionId: "p1", DurationMicros: 1500}
	switch {
	case len(req.Msg.GetFields()) > 0:
		res.Guesses = []*mimirv1.Guess{{Label: req.Msg.GetFields()["plan"] + "!", Probability: 0.75}}
	case len(req.Msg.GetPhoto()) > 0:
		res.Guesses = []*mimirv1.Guess{{Label: "photo " + strconv.Itoa(len(req.Msg.GetPhoto())), Probability: 1}}
	default:
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("give fields or a photo"))
	}
	return connect.NewResponse(res), nil
}

func (s *server) SendFeedback(_ context.Context, req *connect.Request[mimirv1.SendFeedbackRequest]) (*connect.Response[mimirv1.SendFeedbackResponse], error) {
	return connect.NewResponse(&mimirv1.SendFeedbackResponse{Correct: req.Msg.GetLabel() == "yes!"}), nil
}

// Chat echoes the last message back in three pieces. Model "boom" fails
// after the first piece.
func (s *server) Chat(_ context.Context, req *connect.Request[mimirv1.ChatRequest], st *connect.ServerStream[mimirv1.ChatResponse]) error {
	msgs := req.Msg.GetMessages()
	if len(msgs) == 0 {
		return connect.NewError(connect.CodeInvalidArgument, errors.New("send at least one message"))
	}
	last := msgs[len(msgs)-1]
	pieces := []string{"You said", ": ", last.GetContent()}
	for i, p := range pieces {
		if err := st.Send(&mimirv1.ChatResponse{Text: p}); err != nil {
			return err
		}
		if i == 0 && req.Msg.GetModelId() == "boom" {
			return connect.NewError(connect.CodeResourceExhausted, errors.New("out of tokens"))
		}
	}
	return st.Send(&mimirv1.ChatResponse{
		Done: true, Finished: true, PromptTokens: int32(len(msgs)), GeneratedTokens: int32(len(pieces)), DurationMicros: 42,
	})
}

// Sign-in.

func (s *server) GetSetupState(context.Context, *connect.Request[mimirv1.GetSetupStateRequest]) (*connect.Response[mimirv1.GetSetupStateResponse], error) {
	return connect.NewResponse(&mimirv1.GetSetupStateResponse{}), nil
}

// WhoAmI answers with the request's User-Agent as the user's name, so tests
// can see what the SDK sent.
func (s *server) WhoAmI(_ context.Context, req *connect.Request[mimirv1.WhoAmIRequest]) (*connect.Response[mimirv1.WhoAmIResponse], error) {
	return connect.NewResponse(&mimirv1.WhoAmIResponse{
		User:        &mimirv1.User{Email: "test@example.com", Name: req.Header().Get("User-Agent")},
		Permissions: []string{req.Header().Get("X-Extra")},
	}), nil
}

// ListAuditEvents pages through five events.
func (s *server) ListAuditEvents(_ context.Context, req *connect.Request[mimirv1.ListAuditEventsRequest]) (*connect.Response[mimirv1.ListAuditEventsResponse], error) {
	const total = 5
	start, _ := strconv.Atoi(req.Msg.GetPageToken())
	size := int(req.Msg.GetPageSize())
	if size <= 0 {
		size = 2
	}
	res := &mimirv1.ListAuditEventsResponse{}
	for i := start; i < total && i < start+size; i++ {
		res.Events = append(res.Events, &mimirv1.AuditEvent{Id: "e" + strconv.Itoa(i), Action: "model.created"})
	}
	if start+size < total {
		res.NextPageToken = strconv.Itoa(start + size)
	}
	return connect.NewResponse(res), nil
}

// Training.

// CreateJob refuses a run named "busy" once with a Retry-After of a second,
// and one named "very-busy" always, with a Retry-After of two minutes.
func (s *server) CreateJob(_ context.Context, req *connect.Request[mimirv1.CreateJobRequest]) (*connect.Response[mimirv1.CreateJobResponse], error) {
	n := s.record(req.Header(), "attempt CreateJob")
	busy := func(secs string) error {
		err := connect.NewError(connect.CodeResourceExhausted, errors.New("too many runs"))
		err.Meta().Set("Retry-After", secs)
		return err
	}
	switch {
	case req.Msg.GetName() == "busy" && n == 1:
		return nil, busy("1")
	case req.Msg.GetName() == "very-busy":
		return nil, busy("120")
	}
	return connect.NewResponse(&mimirv1.CreateJobResponse{Job: &mimirv1.Job{
		Id: "j-ok", Name: req.Msg.GetName(), Status: mimirv1.JobStatus_JOB_STATUS_QUEUED,
	}}), nil
}

// GetJob says "j-ok" is running the first time each run asks and has
// succeeded after; "j-fail" has failed.
func (s *server) GetJob(_ context.Context, req *connect.Request[mimirv1.GetJobRequest]) (*connect.Response[mimirv1.GetJobResponse], error) {
	n := s.record(req.Header(), "attempt GetJob "+req.Msg.GetId())
	job := &mimirv1.Job{Id: req.Msg.GetId(), Epoch: int32(n)}
	switch {
	case req.Msg.GetId() == "j-fail":
		job.Status, job.Error = mimirv1.JobStatus_JOB_STATUS_FAILED, "out of memory"
	case n == 1:
		job.Status = mimirv1.JobStatus_JOB_STATUS_RUNNING
	default:
		job.Status = mimirv1.JobStatus_JOB_STATUS_SUCCEEDED
	}
	return connect.NewResponse(&mimirv1.GetJobResponse{Job: job}), nil
}

// Datasets.

func (s *server) CreateDataset(_ context.Context, req *connect.Request[mimirv1.CreateDatasetRequest]) (*connect.Response[mimirv1.CreateDatasetResponse], error) {
	m := req.Msg
	rows := int64(strings.Count(string(m.GetCsv()), "\n"))
	return connect.NewResponse(&mimirv1.CreateDatasetResponse{Dataset: &mimirv1.Dataset{
		Id: "d1", Name: m.GetName(), Kind: m.GetKind(), Rows: rows, Target: m.GetTarget(),
		SizeBytes: int64(len(m.GetCsv()) + len(m.GetArchive()) + len(m.GetText())),
	}}), nil
}

// Documents.

func (s *server) Ask(_ context.Context, req *connect.Request[mimirv1.AskRequest], st *connect.ServerStream[mimirv1.AskResponse]) error {
	q := ""
	if msgs := req.Msg.GetMessages(); len(msgs) > 0 {
		q = msgs[len(msgs)-1].GetContent()
	}
	src := []*mimirv1.Passage{{Id: "p1", DocumentName: "policy.pdf", Number: 1, Text: "Returns within 30 days.", Score: 0.9}}
	for _, r := range []*mimirv1.AskResponse{
		{Sources: src},
		{Text: "About " + q + ": "},
		{Text: "yes [1]."},
		{Done: true, Finished: true, PromptTokens: 10, GeneratedTokens: 4, DurationMicros: 7},
	} {
		if err := st.Send(r); err != nil {
			return err
		}
	}
	return nil
}

// Scorings.

func (s *server) results(w http.ResponseWriter, r *http.Request) {
	if !authorized(r.Header) {
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write([]byte(`{"code":"unauthenticated","message":"sign in first"}`))
		return
	}
	if r.PathValue("id") != "s1" {
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write([]byte(`{"code":"not_found","message":"no scoring"}`))
		return
	}
	w.Header().Set("Content-Type", "text/csv")
	_, _ = w.Write([]byte("plan,predicted,confidence,problem\nmonthly,yes,0.9,\n"))
}
