// Copyright (c) 2026 Gembit Soultan Shirazi
// SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 OR PolyForm-Small-Business-1.0.0 OR LicenseRef-Commercial
//
// This file is part of mimir-server-sdk, the Go client for mimir-server,
// created and owned by Gembit Soultan Shirazi.
// It is free to use for personal and other noncommercial purposes, for
// nonprofits, and for companies with fewer than 100 people and under
// 1,000,000 USD in yearly revenue, under the PolyForm Noncommercial and
// PolyForm Small Business licenses. Any other use needs a commercial
// license from Gembit Soultan Shirazi. See the LICENSE and LICENSING.md files
// at the root of this repository.

package mimirsdk

import (
	"context"
	"errors"
	"math/rand/v2"
	"net/http"
	"runtime"
	"time"

	"connectrpc.com/connect"
)

// interceptor signs requests in, names the SDK in User-Agent, bounds unary
// calls by the configured timeout and retries the ones that may be retried.
type interceptor struct {
	cfg config
}

var _ connect.Interceptor = (*interceptor)(nil)

func (i *interceptor) userAgent() string {
	ua := "mimir-server-sdk-go/" + Version + " (" + runtime.Version() + ")"
	if i.cfg.userAgent != "" {
		ua = i.cfg.userAgent + " " + ua
	}
	return ua
}

func (i *interceptor) setHeaders(h http.Header) {
	for k, vs := range i.cfg.header {
		for _, v := range vs {
			h.Add(k, v)
		}
	}
	h.Set("User-Agent", i.userAgent())
	if i.cfg.apiKey != "" {
		h.Set("Authorization", "Bearer "+i.cfg.apiKey)
	}
}

func (i *interceptor) WrapUnary(next connect.UnaryFunc) connect.UnaryFunc {
	return func(ctx context.Context, req connect.AnyRequest) (connect.AnyResponse, error) {
		i.setHeaders(req.Header())
		if _, ok := ctx.Deadline(); !ok && i.cfg.timeout > 0 {
			var cancel context.CancelFunc
			ctx, cancel = context.WithTimeout(ctx, i.cfg.timeout)
			defer cancel()
		}
		readOnly := req.Spec().IdempotencyLevel == connect.IdempotencyNoSideEffects ||
			req.Spec().IdempotencyLevel == connect.IdempotencyIdempotent
		for attempt := 0; ; attempt++ {
			res, err := next(ctx, req)
			if err == nil || attempt >= i.cfg.retries {
				return res, err
			}
			wait, ok := i.retryWait(err, readOnly, attempt)
			if !ok {
				return res, err
			}
			t := time.NewTimer(wait)
			select {
			case <-ctx.Done():
				t.Stop()
				return nil, err
			case <-t.C:
			}
		}
	}
}

// retryWait says whether a failed call should be tried again, and after
// how long. A Retry-After means the server refused the call before doing
// anything, so any call may be retried after it. An unavailable server may
// have done the work before the reply was lost, so only calls without
// side effects are retried then.
func (i *interceptor) retryWait(err error, readOnly bool, attempt int) (time.Duration, bool) {
	var ce *connect.Error
	if !errors.As(err, &ce) {
		return 0, false
	}
	if ra := retryAfter(ce); ra > 0 {
		return ra, ra <= i.cfg.maxRetryWait
	}
	if ce.Code() != connect.CodeUnavailable || !readOnly {
		return 0, false
	}
	d := i.cfg.backoff << attempt
	if d <= 0 || d > i.cfg.maxRetryWait {
		d = i.cfg.maxRetryWait
	}
	// Full jitter in the upper half, so many clients don't retry at once.
	d = d/2 + rand.N(d/2+1)
	return d, true
}

func (i *interceptor) WrapStreamingClient(next connect.StreamingClientFunc) connect.StreamingClientFunc {
	return func(ctx context.Context, spec connect.Spec) connect.StreamingClientConn {
		conn := next(ctx, spec)
		i.setHeaders(conn.RequestHeader())
		return conn
	}
}

func (i *interceptor) WrapStreamingHandler(next connect.StreamingHandlerFunc) connect.StreamingHandlerFunc {
	return next
}
