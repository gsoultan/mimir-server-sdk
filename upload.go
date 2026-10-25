package mimirsdk

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	"connectrpc.com/connect"
)

// uploadPath is where the server takes a large file ahead of CreateModel.
const uploadPath = "/api/uploads"

// uploader streams a file to POST /api/uploads, so a large model never has
// to fit in memory on either side.
type uploader struct {
	http connect.HTTPClient
	url  string
	ic   *interceptor
}

// send streams body to the server and returns the id CreateModel takes
// as CreateModelRequest.Upload. size is the body's length, or -1 when it
// isn't known.
func (u *uploader) send(ctx context.Context, body io.Reader, size int64) (string, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, u.url, body)
	if err != nil {
		return "", fmt.Errorf("mimirsdk: upload: %w", err)
	}
	req.ContentLength = size
	req.Header.Set("Content-Type", "application/octet-stream")
	u.ic.setHeaders(req.Header)
	res, err := u.http.Do(req)
	if err != nil {
		if ctx.Err() != nil {
			return "", ctx.Err()
		}
		return "", fmt.Errorf("mimirsdk: upload: %w", err)
	}
	defer res.Body.Close()
	data, err := io.ReadAll(io.LimitReader(res.Body, 1<<20))
	if err != nil {
		return "", fmt.Errorf("mimirsdk: upload: read the answer: %w", err)
	}
	if res.StatusCode != http.StatusOK {
		return "", uploadError(res.StatusCode, data)
	}
	var out struct {
		Upload string `json:"upload"`
	}
	if err := json.Unmarshal(data, &out); err != nil || out.Upload == "" {
		return "", fmt.Errorf("mimirsdk: upload: the server's answer has no upload id: %q", strings.TrimSpace(string(data)))
	}
	return out.Upload, nil
}

// uploadError reads the Connect-shaped error the server answers a failed
// upload with ({"code": "...", "message": "..."}).
func uploadError(status int, data []byte) error {
	var body struct {
		Code    string `json:"code"`
		Message string `json:"message"`
	}
	_ = json.Unmarshal(data, &body)
	var code Code
	if err := code.UnmarshalText([]byte(body.Code)); err != nil {
		code = codeFromHTTP(status)
	}
	msg := body.Message
	if msg == "" {
		msg = strings.TrimSpace(string(data))
	}
	return &Error{Code: code, Message: msg, Procedure: uploadPath}
}

// codeFromHTTP maps an HTTP status to the nearest code, for answers that
// aren't Connect-shaped (a proxy's, say).
func codeFromHTTP(status int) Code {
	switch status {
	case http.StatusBadRequest:
		return CodeInvalidArgument
	case http.StatusUnauthorized:
		return CodeUnauthenticated
	case http.StatusForbidden:
		return CodePermissionDenied
	case http.StatusNotFound:
		return CodeUnimplemented
	case http.StatusRequestEntityTooLarge, http.StatusTooManyRequests:
		return CodeResourceExhausted
	case http.StatusBadGateway, http.StatusServiceUnavailable, http.StatusGatewayTimeout:
		return CodeUnavailable
	default:
		return CodeUnknown
	}
}
