package mimirsdk_test

import (
	"context"
	"errors"
	"net/http"
	"strings"
	"testing"
	"time"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func TestScoringWaitAndDownload(t *testing.T) {
	// The first look is still scoring; the second is done.
	f := &fake{
		getScoring: func(n int) (*mimirv1.GetScoringResponse, error) {
			if n == 1 {
				return &mimirv1.GetScoringResponse{Scoring: &mimirv1.Scoring{Id: "s1", Status: mimirv1.JobStatus_JOB_STATUS_RUNNING, Rows: 4, Done: 2}}, nil
			}
			return &mimirv1.GetScoringResponse{Scoring: &mimirv1.Scoring{Id: "s1", Status: mimirv1.JobStatus_JOB_STATUS_SUCCEEDED, Rows: 4, Done: 4}}, nil
		},
		results: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.Header.Get("Authorization") != "Bearer "+testKey || r.PathValue("id") != "s1" {
				w.WriteHeader(http.StatusUnauthorized)
				w.Write([]byte(`{"code":"unauthenticated","message":"Sign in to continue."}`))
				return
			}
			w.Write([]byte("id,width,predicted,problem\n1,1.1,apple,\n"))
		}),
	}
	c := start(t, f)

	var seen int
	sc, err := c.Scorings.Wait(context.Background(), "s1", mimirsdk.ScoringWaitOptions{
		Interval:   time.Millisecond,
		OnProgress: func(*mimirsdk.Scoring) { seen++ },
	})
	if err != nil || sc.GetDone() != 4 || seen != 2 {
		t.Fatalf("scoring %v, %v, looked %d times", sc, err, seen)
	}

	var b strings.Builder
	n, err := c.Scorings.Download(context.Background(), "s1", &b)
	if err != nil || n != int64(b.Len()) || !strings.HasPrefix(b.String(), "id,width,predicted,problem\n") {
		t.Fatalf("download %q, %d, %v", b.String(), n, err)
	}

	// A scoring that isn't there is an error with the server's reason.
	_, err = c.Scorings.Download(context.Background(), "s2", &b)
	var e *mimirsdk.Error
	if !errors.As(err, &e) || e.Code != mimirsdk.CodeUnauthenticated || e.Message != "Sign in to continue." {
		t.Fatalf("download error %v", err)
	}
}

func TestScoringWaitReportsAFailure(t *testing.T) {
	f := &fake{getScoring: func(int) (*mimirv1.GetScoringResponse, error) {
		return &mimirv1.GetScoringResponse{Scoring: &mimirv1.Scoring{Id: "s1", Status: mimirv1.JobStatus_JOB_STATUS_FAILED, Error: "The query didn't give rows."}}, nil
	}}
	c := start(t, f)
	_, err := c.Scorings.Wait(context.Background(), "s1", mimirsdk.ScoringWaitOptions{Interval: time.Millisecond})
	var se *mimirsdk.ScoringError
	if !errors.As(err, &se) || !strings.Contains(err.Error(), "failed: The query didn't give rows.") {
		t.Fatalf("wait error %v", err)
	}
}
