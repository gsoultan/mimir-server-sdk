package mimirsdk

import (
	"context"
	"slices"
	"time"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// BenchmarkService keeps the fixed tests models are ranked on. A
// benchmark's rows are frozen from a dataset and left out of training on
// it, so every model answers examples it never learned from, and the same
// ones.
type BenchmarkService struct {
	raw mimirv1connect.BenchmarkServiceClient
}

// List returns every benchmark the caller may see.
func (s *BenchmarkService) List(ctx context.Context) ([]*Benchmark, error) {
	res, err := call(ctx, mimirv1connect.BenchmarkServiceListBenchmarksProcedure, s.raw.ListBenchmarks, nil)
	return res.GetBenchmarks(), err
}

// ListForDataset returns the benchmarks frozen from one dataset.
func (s *BenchmarkService) ListForDataset(ctx context.Context, datasetID string) ([]*Benchmark, error) {
	res, err := call(ctx, mimirv1connect.BenchmarkServiceListBenchmarksProcedure, s.raw.ListBenchmarks, &mimirv1.ListBenchmarksRequest{DatasetId: datasetID})
	return res.GetBenchmarks(), err
}

// Get returns a benchmark with its leaderboard, best first, and the
// models that could still take it.
func (s *BenchmarkService) Get(ctx context.Context, id string) (*GetBenchmarkResponse, error) {
	return call(ctx, mimirv1connect.BenchmarkServiceGetBenchmarkProcedure, s.raw.GetBenchmark, &mimirv1.GetBenchmarkRequest{Id: id})
}

// Create makes a benchmark. Share is the part of the dataset's rows to
// keep aside, from 0.05 to 0.5, or 0 for a fifth; Csv instead holds test
// rows of your own, with the dataset's columns.
func (s *BenchmarkService) Create(ctx context.Context, req *CreateBenchmarkRequest) (*Benchmark, error) {
	res, err := call(ctx, mimirv1connect.BenchmarkServiceCreateBenchmarkProcedure, s.raw.CreateBenchmark, req)
	return res.GetBenchmark(), err
}

// Freeze makes a benchmark that keeps share of a dataset's rows aside;
// share of 0 keeps a fifth.
func (s *BenchmarkService) Freeze(ctx context.Context, name, datasetID string, share float64) (*Benchmark, error) {
	return s.Create(ctx, &mimirv1.CreateBenchmarkRequest{Name: name, DatasetId: datasetID, Share: share})
}

// Delete removes a benchmark, its rows and its scores. The models stay.
func (s *BenchmarkService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.BenchmarkServiceDeleteBenchmarkProcedure, s.raw.DeleteBenchmark, &mimirv1.DeleteBenchmarkRequest{Id: id})
	return err
}

// Score puts models on a benchmark's leaderboard. Scoring runs on the
// server; the scores come back queued, and WaitForScores follows them. A
// model scored before is scored again with the weights it has now.
func (s *BenchmarkService) Score(ctx context.Context, benchmarkID string, modelIDs ...string) ([]*BenchmarkScore, error) {
	res, err := call(ctx, mimirv1connect.BenchmarkServiceScoreModelsProcedure, s.raw.ScoreModels, &mimirv1.ScoreModelsRequest{BenchmarkId: benchmarkID, ModelIds: modelIDs})
	return res.GetScores(), err
}

// ScoreWaitOptions change how WaitForScores follows a benchmark.
type ScoreWaitOptions struct {
	// Interval is how often to look; 0 means 2 seconds.
	Interval time.Duration
	// OnProgress, when set, sees the leaderboard each time it looks.
	OnProgress func([]*BenchmarkScore)
}

// WaitForScores follows a benchmark until no score on it is still queued
// or running, and returns the leaderboard, best first. Bound the wait
// with ctx. A score that failed is in the list with its reason, and is
// not an error here.
func (s *BenchmarkService) WaitForScores(ctx context.Context, benchmarkID string, opts ScoreWaitOptions) ([]*BenchmarkScore, error) {
	interval := opts.Interval
	if interval <= 0 {
		interval = 2 * time.Second
	}
	t := time.NewTicker(interval)
	defer t.Stop()
	for {
		res, err := s.Get(ctx, benchmarkID)
		if err != nil {
			return nil, err
		}
		scores := res.GetScores()
		if opts.OnProgress != nil {
			opts.OnProgress(scores)
		}
		if !slices.ContainsFunc(scores, scoring) {
			return scores, nil
		}
		select {
		case <-ctx.Done():
			return scores, ctx.Err()
		case <-t.C:
		}
	}
}

// Leader returns the best finished score on a benchmark, and false when
// none has finished.
func (s *BenchmarkService) Leader(ctx context.Context, benchmarkID string) (*BenchmarkScore, bool, error) {
	res, err := s.Get(ctx, benchmarkID)
	if err != nil {
		return nil, false, err
	}
	for _, sc := range res.GetScores() {
		if sc.GetRank() == 1 {
			return sc, true, nil
		}
	}
	return nil, false, nil
}

// scoring reports whether a score is still being worked out.
func scoring(s *BenchmarkScore) bool {
	return s.GetStatus() == JobStatusQueued || s.GetStatus() == JobStatusRunning
}
