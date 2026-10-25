package mimirsdk

import (
	"context"
	"iter"

	"connectrpc.com/connect"
)

// call sends one request and unwraps its response, turning errors into
// *Error. A nil req sends an empty message.
func call[Req, Res any](ctx context.Context, procedure string, fn func(context.Context, *connect.Request[Req]) (*connect.Response[Res], error), req *Req) (*Res, error) {
	if req == nil {
		req = new(Req)
	}
	res, err := fn(ctx, connect.NewRequest(req))
	if err != nil {
		return nil, wrapError(procedure, err)
	}
	return res.Msg, nil
}

// stream yields each message of a server stream. Stopping the loop early
// closes the stream.
func stream[Req, Res any](ctx context.Context, procedure string, fn func(context.Context, *connect.Request[Req]) (*connect.ServerStreamForClient[Res], error), req *Req) iter.Seq2[*Res, error] {
	return func(yield func(*Res, error) bool) {
		if req == nil {
			req = new(Req)
		}
		s, err := fn(ctx, connect.NewRequest(req))
		if err != nil {
			yield(nil, wrapError(procedure, err))
			return
		}
		defer s.Close()
		for s.Receive() {
			if !yield(s.Msg(), nil) {
				return
			}
		}
		if err := s.Err(); err != nil {
			yield(nil, wrapError(procedure, err))
		}
	}
}

// Page is one page of a paged list.
type Page[T any] struct {
	Items []T
	// NextPageToken fetches the next page; empty on the last one.
	NextPageToken string
}

// paginate walks every page fetch returns, starting from token, until a
// page has no next token.
func paginate[T any](ctx context.Context, token string, fetch func(ctx context.Context, token string) (*Page[T], error)) iter.Seq2[T, error] {
	return func(yield func(T, error) bool) {
		for {
			page, err := fetch(ctx, token)
			if err != nil {
				var zero T
				yield(zero, err)
				return
			}
			for _, item := range page.Items {
				if !yield(item, nil) {
					return
				}
			}
			if page.NextPageToken == "" || page.NextPageToken == token {
				return
			}
			token = page.NextPageToken
		}
	}
}
