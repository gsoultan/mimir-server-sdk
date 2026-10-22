package mimirsdk

import (
	"context"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"

	"connectrpc.com/connect"
)

// Code says what kind of failure an Error is. The values are Connect's
// codes, re-exported so callers need not import connect.
type Code = connect.Code

// The codes the server uses.
const (
	CodeCanceled           = connect.CodeCanceled
	CodeUnknown            = connect.CodeUnknown
	CodeInvalidArgument    = connect.CodeInvalidArgument
	CodeDeadlineExceeded   = connect.CodeDeadlineExceeded
	CodeNotFound           = connect.CodeNotFound
	CodeAlreadyExists      = connect.CodeAlreadyExists
	CodePermissionDenied   = connect.CodePermissionDenied
	CodeResourceExhausted  = connect.CodeResourceExhausted
	CodeFailedPrecondition = connect.CodeFailedPrecondition
	CodeAborted            = connect.CodeAborted
	CodeUnimplemented      = connect.CodeUnimplemented
	CodeInternal           = connect.CodeInternal
	CodeUnavailable        = connect.CodeUnavailable
	CodeUnauthenticated    = connect.CodeUnauthenticated
)

// Sentinels to test errors against with errors.Is. An *Error matches the
// sentinel for its code.
var (
	ErrInvalidArgument    error = codeError(CodeInvalidArgument)
	ErrNotFound           error = codeError(CodeNotFound)
	ErrAlreadyExists      error = codeError(CodeAlreadyExists)
	ErrPermissionDenied   error = codeError(CodePermissionDenied)
	ErrUnauthenticated    error = codeError(CodeUnauthenticated)
	ErrResourceExhausted  error = codeError(CodeResourceExhausted)
	ErrFailedPrecondition error = codeError(CodeFailedPrecondition)
	ErrUnimplemented      error = codeError(CodeUnimplemented)
	ErrUnavailable        error = codeError(CodeUnavailable)
	ErrInternal           error = codeError(CodeInternal)
)

type codeError Code

func (e codeError) Error() string { return "mimirsdk: " + Code(e).String() }

// Error is a call the server, or the way to it, turned down.
type Error struct {
	// Code says what kind of failure it is.
	Code Code
	// Message is the server's explanation, written to show to people.
	Message string
	// Procedure is the call that failed, like
	// "/mimir.v1.ModelService/GetModel".
	Procedure string
	// RetryAfter is how long the server asked to wait before trying again,
	// 0 when it didn't say.
	RetryAfter time.Duration

	cause *connect.Error
}

func (e *Error) Error() string {
	var b strings.Builder
	b.WriteString("mimirsdk: ")
	if e.Procedure != "" {
		b.WriteString(strings.TrimPrefix(e.Procedure, "/mimir.v1."))
		b.WriteString(": ")
	}
	b.WriteString(e.Code.String())
	if e.Message != "" {
		b.WriteString(": ")
		b.WriteString(e.Message)
	}
	return b.String()
}

// Is matches the sentinel for e's code, so errors.Is(err, ErrNotFound)
// works.
func (e *Error) Is(target error) bool {
	c, ok := target.(codeError)
	return ok && Code(c) == e.Code
}

// Unwrap returns the underlying *connect.Error.
func (e *Error) Unwrap() error { return e.cause }

// Retryable says the same call may succeed if tried again later.
func (e *Error) Retryable() bool {
	return e.Code == CodeUnavailable || e.RetryAfter > 0
}

// wrapError turns errors from the Connect clients into *Error. Context
// errors pass through as they are, so errors.Is(err, context.Canceled)
// keeps working.
func wrapError(procedure string, err error) error {
	if err == nil {
		return nil
	}
	if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
		return err
	}
	var already *Error
	if errors.As(err, &already) {
		return err
	}
	var ce *connect.Error
	if !errors.As(err, &ce) {
		return fmt.Errorf("mimirsdk: %s: %w", strings.TrimPrefix(procedure, "/mimir.v1."), err)
	}
	return &Error{
		Code:       ce.Code(),
		Message:    ce.Message(),
		Procedure:  procedure,
		RetryAfter: retryAfter(ce),
		cause:      ce,
	}
}

// retryAfter reads a Retry-After in seconds from an error's metadata.
func retryAfter(ce *connect.Error) time.Duration {
	v := ce.Meta().Get("Retry-After")
	if v == "" {
		return 0
	}
	secs, err := strconv.Atoi(strings.TrimSpace(v))
	if err != nil || secs < 0 {
		return 0
	}
	return time.Duration(secs) * time.Second
}

// JobError is returned by TrainingService.Wait when a run fails or is
// cancelled. Job is the run as it ended.
type JobError struct {
	Job *Job
}

func (e *JobError) Error() string {
	status := strings.ToLower(strings.TrimPrefix(e.Job.GetStatus().String(), "JOB_STATUS_"))
	if msg := e.Job.GetError(); msg != "" {
		return fmt.Sprintf("mimirsdk: training run %s %s: %s", e.Job.GetId(), status, msg)
	}
	return fmt.Sprintf("mimirsdk: training run %s %s", e.Job.GetId(), status)
}
