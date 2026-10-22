package webhook_test

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gsoultan/mimir-server-sdk/webhook"
)

const (
	secret = "whsec_test"
	body   = `{"id":"e1","type":"test","time":"2023-11-14T22:13:20Z","data":{"message":"hi"}}`
)

// The signature the server sends for body at 1700000000 (worked out with
// HMAC-SHA256 outside Go, so Sign and Verify can't agree on a mistake).
const serverSignature = "t=1700000000,v1=a462287eea11c6821dd500143b9e8d2d0bd08c7c39c289bdbf13c59ed58588cd"

func TestSignMatchesServer(t *testing.T) {
	if got := webhook.Sign(secret, time.Unix(1700000000, 0), []byte(body)); got != serverSignature {
		t.Fatalf("Sign = %s\nwant   %s", got, serverSignature)
	}
}

func TestVerify(t *testing.T) {
	now := time.Now()
	good := webhook.Sign(secret, now, []byte(body))
	tests := []struct {
		name   string
		secret string
		header string
		body   string
		want   error
	}{
		{"genuine", secret, good, body, nil},
		{"no header", secret, "", body, webhook.ErrNoSignature},
		{"other secret", "whsec_other", good, body, webhook.ErrBadSignature},
		{"changed body", secret, good, body + " ", webhook.ErrBadSignature},
		{"garbled", secret, "t=abc,v1=zz", body, webhook.ErrBadSignature},
		{"no v1", secret, "t=" + good[2:12], body, webhook.ErrBadSignature},
		{"old", secret, webhook.Sign(secret, now.Add(-time.Hour), []byte(body)), body, webhook.ErrExpired},
		{"future", secret, webhook.Sign(secret, now.Add(time.Hour), []byte(body)), body, webhook.ErrExpired},
		{"two signatures, one right", secret, good + ",v1=00", body, nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := webhook.Verify(tt.secret, tt.header, []byte(tt.body), 0); !errors.Is(err, tt.want) {
				t.Errorf("Verify = %v, want %v", err, tt.want)
			}
		})
	}
}

func TestParseAndDecode(t *testing.T) {
	data := `{"id":"e2","type":"training.finished","time":"2026-10-22T10:00:00Z","data":{"id":"j1","name":"churn","status":"succeeded","epoch":10,"epochs":10,"accuracy":0.91,"model_id":"m1"}}`
	ev, err := webhook.Parse(secret, webhook.Sign(secret, time.Now(), []byte(data)), []byte(data), 0)
	if err != nil {
		t.Fatal(err)
	}
	if ev.ID != "e2" || ev.Type != webhook.TrainingFinished || ev.Time.Year() != 2026 {
		t.Errorf("event = %+v", ev)
	}
	job, err := ev.Job()
	if err != nil {
		t.Fatal(err)
	}
	if job.ModelID != "m1" || job.Accuracy != 0.91 || job.Status != "succeeded" {
		t.Errorf("job = %+v", job)
	}
	if _, err := ev.Model(); err == nil {
		t.Error("a training event decoded as a model event")
	}
}

func TestHandler(t *testing.T) {
	var got *webhook.Event
	fail := false
	h := webhook.Handler(secret, func(_ context.Context, ev *webhook.Event) error {
		if fail {
			return errors.New("database down")
		}
		got = ev
		return nil
	})
	send := func(method, sig, b string) int {
		req := httptest.NewRequest(method, "/hook", strings.NewReader(b))
		if sig != "" {
			req.Header.Set(webhook.SignatureHeader, sig)
		}
		w := httptest.NewRecorder()
		h.ServeHTTP(w, req)
		return w.Code
	}

	if code := send(http.MethodPost, webhook.Sign(secret, time.Now(), []byte(body)), body); code != http.StatusNoContent {
		t.Errorf("genuine delivery: %d", code)
	}
	if got == nil || got.ID != "e1" {
		t.Errorf("handled %+v", got)
	}
	if code := send(http.MethodPost, "", body); code != http.StatusUnauthorized {
		t.Errorf("unsigned delivery: %d", code)
	}
	if code := send(http.MethodPost, webhook.Sign("whsec_other", time.Now(), []byte(body)), body); code != http.StatusUnauthorized {
		t.Errorf("forged delivery: %d", code)
	}
	if code := send(http.MethodGet, "", ""); code != http.StatusMethodNotAllowed {
		t.Errorf("GET: %d", code)
	}
	fail = true
	if code := send(http.MethodPost, webhook.Sign(secret, time.Now(), []byte(body)), body); code != http.StatusInternalServerError {
		t.Errorf("failed handler: %d", code)
	}
}
