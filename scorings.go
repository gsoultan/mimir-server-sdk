package mimirsdk

import (
	"context"
	"fmt"
	"io"
	"net/url"
	"strings"
	"time"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// scoringResultsPath is where a scoring's results download from, with
// %s for its id.
const scoringResultsPath = "/api/scorings/%s/results"

// ScoringService answers every row of a table with one model at once: a
// CSV, a database query, files in storage or a dataset. The server
// scores in the background and keeps the rows with each answer next to
// them as a CSV, which Download fetches.
type ScoringService struct {
	raw mimirv1connect.ScoringServiceClient
	dl  *downloader
}

// List returns every scoring the caller may see, newest first.
func (s *ScoringService) List(ctx context.Context) ([]*Scoring, error) {
	res, err := call(ctx, mimirv1connect.ScoringServiceListScoringsProcedure, s.raw.ListScorings, nil)
	return res.GetScorings(), err
}

// ListForModel returns one model's scorings, newest first.
func (s *ScoringService) ListForModel(ctx context.Context, modelID string) ([]*Scoring, error) {
	res, err := call(ctx, mimirv1connect.ScoringServiceListScoringsProcedure, s.raw.ListScorings, &mimirv1.ListScoringsRequest{ModelId: modelID})
	return res.GetScorings(), err
}

// Get returns a scoring with the first rows of its results.
func (s *ScoringService) Get(ctx context.Context, id string) (*GetScoringResponse, error) {
	return call(ctx, mimirv1connect.ScoringServiceGetScoringProcedure, s.raw.GetScoring, &mimirv1.GetScoringRequest{Id: id})
}

// Create queues a scoring. Give the rows one way: Csv, Connection and
// Query, Bucket and Path, or DatasetId. Wait follows it to the end.
func (s *ScoringService) Create(ctx context.Context, req *CreateScoringRequest) (*Scoring, error) {
	res, err := call(ctx, mimirv1connect.ScoringServiceCreateScoringProcedure, s.raw.CreateScoring, req)
	return res.GetScoring(), err
}

// ScoreCSV queues a scoring of a CSV with a header row; it needs no
// answer column. An empty name lets the server choose one.
func (s *ScoringService) ScoreCSV(ctx context.Context, modelID, name string, csv []byte) (*Scoring, error) {
	return s.Create(ctx, &mimirv1.CreateScoringRequest{ModelId: modelID, Name: name, Csv: csv})
}

// ScoreQuery queues a scoring of a database query's rows, run again
// every so often when every is at least an hour; 0 runs it once. It
// needs an admin.
func (s *ScoringService) ScoreQuery(ctx context.Context, modelID, name string, conn *Connection, query string, every time.Duration) (*Scoring, error) {
	return s.Create(ctx, &mimirv1.CreateScoringRequest{ModelId: modelID, Name: name, Connection: conn, Query: query, RepeatSeconds: int64(every / time.Second)})
}

// Run queues a finished, failed or cancelled scoring again now, fetching
// its rows afresh.
func (s *ScoringService) Run(ctx context.Context, id string) (*Scoring, error) {
	res, err := call(ctx, mimirv1connect.ScoringServiceRunScoringProcedure, s.raw.RunScoring, &mimirv1.RunScoringRequest{Id: id})
	return res.GetScoring(), err
}

// Cancel stops a queued or running scoring.
func (s *ScoringService) Cancel(ctx context.Context, id string) (*Scoring, error) {
	res, err := call(ctx, mimirv1connect.ScoringServiceCancelScoringProcedure, s.raw.CancelScoring, &mimirv1.CancelScoringRequest{Id: id})
	return res.GetScoring(), err
}

// SetRepeat changes how often a scoring from a database or storage runs
// again, from an hour to 30 days; 0 stops it.
func (s *ScoringService) SetRepeat(ctx context.Context, id string, every time.Duration) (*Scoring, error) {
	res, err := call(ctx, mimirv1connect.ScoringServiceSetScoringRepeatProcedure, s.raw.SetScoringRepeat, &mimirv1.SetScoringRepeatRequest{Id: id, RepeatSeconds: int64(every / time.Second)})
	return res.GetScoring(), err
}

// Delete removes a scoring and its results. A running one must be
// cancelled first.
func (s *ScoringService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.ScoringServiceDeleteScoringProcedure, s.raw.DeleteScoring, &mimirv1.DeleteScoringRequest{Id: id})
	return err
}

// ScoringWaitOptions change how Wait follows a scoring.
type ScoringWaitOptions struct {
	// Interval is how often to look; 0 means 2 seconds.
	Interval time.Duration
	// OnProgress, when set, sees the scoring each time Wait looks.
	OnProgress func(*Scoring)
}

// Wait follows a scoring until it succeeds, fails or is cancelled, and
// returns it as it ended. One that fails or is cancelled returns a
// *ScoringError along with it. Bound the wait with ctx.
func (s *ScoringService) Wait(ctx context.Context, id string, opts ScoringWaitOptions) (*Scoring, error) {
	interval := opts.Interval
	if interval <= 0 {
		interval = 2 * time.Second
	}
	t := time.NewTicker(interval)
	defer t.Stop()
	for {
		res, err := s.Get(ctx, id)
		if err != nil {
			return nil, err
		}
		sc := res.GetScoring()
		if opts.OnProgress != nil {
			opts.OnProgress(sc)
		}
		switch sc.GetStatus() {
		case JobStatusSucceeded:
			return sc, nil
		case JobStatusFailed, JobStatusCancelled:
			return sc, &ScoringError{Scoring: sc}
		}
		select {
		case <-ctx.Done():
			return sc, ctx.Err()
		case <-t.C:
		}
	}
}

// Download writes a scoring's latest results to w: a CSV of every row,
// in order, with the model's answer after it (predicted, then confidence
// or suggestions, and problem, which says why a row couldn't be
// answered). It returns how many bytes it wrote.
func (s *ScoringService) Download(ctx context.Context, id string, w io.Writer) (int64, error) {
	return s.dl.get(ctx, fmt.Sprintf(scoringResultsPath, url.PathEscape(id)), "download results", w)
}

// ScoringError is what Wait returns for a scoring that failed or was
// cancelled.
type ScoringError struct {
	Scoring *Scoring
}

func (e *ScoringError) Error() string {
	status := strings.ToLower(strings.TrimPrefix(e.Scoring.GetStatus().String(), "JOB_STATUS_"))
	if msg := e.Scoring.GetError(); msg != "" {
		return fmt.Sprintf("mimirsdk: scoring %s %s: %s", e.Scoring.GetId(), status, msg)
	}
	return fmt.Sprintf("mimirsdk: scoring %s %s", e.Scoring.GetId(), status)
}
