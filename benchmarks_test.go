package mimirsdk_test

import (
	"context"
	"testing"
	"time"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func TestWaitForScores(t *testing.T) {
	// The first look has one score still running; the second has the
	// leaderboard finished.
	running := &mimirv1.GetBenchmarkResponse{
		Benchmark: &mimirv1.Benchmark{Id: "b1", Kind: "class", Metric: "right answers"},
		Scores: []*mimirv1.BenchmarkScore{
			{ModelId: "m1", Status: mimirv1.JobStatus_JOB_STATUS_SUCCEEDED, Headline: 0.9, Rank: 1},
			{ModelId: "m2", Status: mimirv1.JobStatus_JOB_STATUS_RUNNING},
		},
	}
	done := &mimirv1.GetBenchmarkResponse{
		Benchmark: running.Benchmark,
		Scores: []*mimirv1.BenchmarkScore{
			{ModelId: "m2", Status: mimirv1.JobStatus_JOB_STATUS_SUCCEEDED, Headline: 0.95, Rank: 1},
			{ModelId: "m1", Status: mimirv1.JobStatus_JOB_STATUS_SUCCEEDED, Headline: 0.9, Rank: 2},
		},
	}
	f := &fake{getBench: func(n int) (*mimirv1.GetBenchmarkResponse, error) {
		if n == 1 {
			return running, nil
		}
		return done, nil
	}}
	c := start(t, f)

	var seen int
	scores, err := c.Benchmarks.WaitForScores(context.Background(), "b1", mimirsdk.ScoreWaitOptions{
		Interval:   time.Millisecond,
		OnProgress: func([]*mimirsdk.BenchmarkScore) { seen++ },
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(scores) != 2 || scores[0].GetModelId() != "m2" || seen != 2 {
		t.Fatalf("scores %v, looked %d times", scores, seen)
	}

	// Leader is the finished score in first place.
	top, ok, err := c.Benchmarks.Leader(context.Background(), "b1")
	if err != nil || !ok || top.GetModelId() != "m2" {
		t.Fatalf("leader %v, %v, %v", top, ok, err)
	}
}

func TestWaitForScoresStopsWithTheContext(t *testing.T) {
	f := &fake{getBench: func(int) (*mimirv1.GetBenchmarkResponse, error) {
		return &mimirv1.GetBenchmarkResponse{
			Benchmark: &mimirv1.Benchmark{Id: "b1"},
			Scores:    []*mimirv1.BenchmarkScore{{ModelId: "m1", Status: mimirv1.JobStatus_JOB_STATUS_QUEUED}},
		}, nil
	}}
	c := start(t, f)
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Millisecond)
	defer cancel()
	if _, err := c.Benchmarks.WaitForScores(ctx, "b1", mimirsdk.ScoreWaitOptions{Interval: time.Millisecond}); err == nil {
		t.Fatal("waited forever on a score that never finishes")
	}

	// Nothing has finished, so there is no leader.
	if _, ok, err := c.Benchmarks.Leader(context.Background(), "b1"); ok || err != nil {
		t.Fatalf("leader %v, %v", ok, err)
	}
}
