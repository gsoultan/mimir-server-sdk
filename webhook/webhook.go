// Package webhook checks and reads the events mimir-server sends to
// webhooks.
//
// Each delivery is a JSON POST signed with the webhook's secret in a
// Mimir-Signature header ("t=<unix seconds>,v1=<hex HMAC-SHA256 of
// "<t>.<body>">"). Mount Handler to have that checked for you:
//
//	http.Handle("/hooks/mimir", webhook.Handler(secret, func(ctx context.Context, ev *webhook.Event) error {
//		if ev.Type == webhook.TrainingFinished {
//			job, err := ev.Job()
//			...
//		}
//		return nil
//	}))
//
// The server retries a delivery for about a day until it gets a 2xx, so
// the same event can arrive more than once: use Event.ID to skip repeats.
package webhook

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"
)

// SignatureHeader is the header that carries a delivery's signature.
const SignatureHeader = "Mimir-Signature"

// DefaultTolerance is how far a delivery's signed time may be from now.
const DefaultTolerance = 5 * time.Minute

// MaxBodyBytes is the largest body ParseRequest reads.
const MaxBodyBytes = 1 << 20

// Event types.
const (
	ModelCreated     = "model.created"
	ModelUpdated     = "model.updated"
	ModelDeleted     = "model.deleted"
	TrainingQueued   = "training.queued"
	TrainingFinished = "training.finished"
	TrainingFailed   = "training.failed"
	UserCreated      = "user.created"
	UserDeleted      = "user.deleted"
	Test             = "test"
)

// Reasons Verify turns a delivery down.
var (
	ErrNoSignature  = errors.New("webhook: no Mimir-Signature header")
	ErrBadSignature = errors.New("webhook: the signature doesn't match the body")
	ErrExpired      = errors.New("webhook: the signature is too old or from the future")
)

// Sign returns the Mimir-Signature header value for body at time t, as the
// server makes it. It is for tests of a receiver.
func Sign(secret string, t time.Time, body []byte) string {
	ts := strconv.FormatInt(t.Unix(), 10)
	return "t=" + ts + ",v1=" + hex.EncodeToString(mac(secret, ts, body))
}

func mac(secret, ts string, body []byte) []byte {
	m := hmac.New(sha256.New, []byte(secret))
	m.Write([]byte(ts))
	m.Write([]byte("."))
	m.Write(body)
	return m.Sum(nil)
}

// Verify checks a Mimir-Signature header against the raw body, allowing
// the signed time to be up to tolerance from now (0 means
// DefaultTolerance). It returns nil for a genuine delivery.
func Verify(secret, header string, body []byte, tolerance time.Duration) error {
	if strings.TrimSpace(header) == "" {
		return ErrNoSignature
	}
	if tolerance <= 0 {
		tolerance = DefaultTolerance
	}
	var ts string
	var sigs [][]byte
	for part := range strings.SplitSeq(header, ",") {
		k, v, _ := strings.Cut(strings.TrimSpace(part), "=")
		switch k {
		case "t":
			ts = v
		case "v1":
			if sig, err := hex.DecodeString(v); err == nil {
				sigs = append(sigs, sig)
			}
		}
	}
	sec, err := strconv.ParseInt(ts, 10, 64)
	if err != nil || len(sigs) == 0 {
		return ErrBadSignature
	}
	if d := time.Since(time.Unix(sec, 0)); d > tolerance || d < -tolerance {
		return ErrExpired
	}
	want := mac(secret, ts, body)
	for _, sig := range sigs {
		if hmac.Equal(want, sig) {
			return nil
		}
	}
	return ErrBadSignature
}

// Event is one delivery's body.
type Event struct {
	// ID is the same for every retry of one event.
	ID   string    `json:"id"`
	Type string    `json:"type"`
	Time time.Time `json:"time"`
	// Data depends on Type; Model, Job and User decode it.
	Data json.RawMessage `json:"data"`
}

// Parse verifies a delivery's signature and decodes its body.
func Parse(secret, header string, body []byte, tolerance time.Duration) (*Event, error) {
	if err := Verify(secret, header, body, tolerance); err != nil {
		return nil, err
	}
	var ev Event
	if err := json.Unmarshal(body, &ev); err != nil {
		return nil, fmt.Errorf("webhook: decode the event: %w", err)
	}
	return &ev, nil
}

// ParseRequest is Parse on an incoming request, with DefaultTolerance.
func ParseRequest(r *http.Request, secret string) (*Event, error) {
	body, err := io.ReadAll(io.LimitReader(r.Body, MaxBodyBytes+1))
	if err != nil {
		return nil, fmt.Errorf("webhook: read the body: %w", err)
	}
	if len(body) > MaxBodyBytes {
		return nil, errors.New("webhook: the body is larger than MaxBodyBytes")
	}
	return Parse(secret, r.Header.Get(SignatureHeader), body, DefaultTolerance)
}

// Handler serves webhook deliveries: it checks each one and passes it to
// handle. A delivery that fails the check gets 401 and isn't handled; one
// handle returns an error for gets 500, so the server sends it again later.
func Handler(secret string, handle func(context.Context, *Event) error) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.Header().Set("Allow", http.MethodPost)
			http.Error(w, "use POST", http.StatusMethodNotAllowed)
			return
		}
		ev, err := ParseRequest(r, secret)
		switch {
		case errors.Is(err, ErrNoSignature), errors.Is(err, ErrBadSignature), errors.Is(err, ErrExpired):
			http.Error(w, err.Error(), http.StatusUnauthorized)
			return
		case err != nil:
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		if err := handle(r.Context(), ev); err != nil {
			http.Error(w, "the receiver couldn't handle the event", http.StatusInternalServerError)
			return
		}
		w.WriteHeader(http.StatusNoContent)
	})
}

// ModelEvent is the data of model.created, model.updated and
// model.deleted.
type ModelEvent struct {
	Model struct {
		ID           string `json:"id"`
		Name         string `json:"name"`
		Architecture string `json:"architecture"`
		SizeBytes    int64  `json:"size_bytes"`
	} `json:"model"`
	// Actor is who made the change: an email, or "key <name> (<email>)"
	// for an API key. Empty for a model a training run made.
	Actor string `json:"actor"`
}

// JobEvent is the data of training.queued, training.finished and
// training.failed.
type JobEvent struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	Architecture string `json:"architecture"`
	Dataset      string `json:"dataset"`
	// Status is "queued", "running", "succeeded", "failed" or "cancelled".
	Status   string  `json:"status"`
	Epoch    int32   `json:"epoch"`
	Epochs   int32   `json:"epochs"`
	Accuracy float64 `json:"accuracy"`
	ModelID  string  `json:"model_id"`
	Error    string  `json:"error"`
}

// UserEvent is the data of user.created and user.deleted.
type UserEvent struct {
	User struct {
		ID    string `json:"id"`
		Email string `json:"email"`
		Name  string `json:"name"`
	} `json:"user"`
	Actor string `json:"actor"`
}

// Model decodes a model event's data.
func (e *Event) Model() (*ModelEvent, error) {
	return decode[ModelEvent](e, "model.")
}

// Job decodes a training event's data.
func (e *Event) Job() (*JobEvent, error) {
	return decode[JobEvent](e, "training.")
}

// User decodes a user event's data.
func (e *Event) User() (*UserEvent, error) {
	return decode[UserEvent](e, "user.")
}

func decode[T any](e *Event, prefix string) (*T, error) {
	if !strings.HasPrefix(e.Type, prefix) {
		return nil, fmt.Errorf("webhook: a %s event has no %s data", e.Type, strings.TrimSuffix(prefix, "."))
	}
	var v T
	if err := json.Unmarshal(e.Data, &v); err != nil {
		return nil, fmt.Errorf("webhook: decode the %s data: %w", e.Type, err)
	}
	return &v, nil
}
