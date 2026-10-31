package mimirsdk

import (
	"context"
	"fmt"
	"io"
	"net/http"

	"connectrpc.com/connect"
)

// backupPath is where an admin downloads a backup of the database.
const backupPath = "/api/backup"

// downloader fetches the files the server offers as plain downloads
// rather than RPCs, with the client's API key and headers.
type downloader struct {
	http connect.HTTPClient
	base string
	ic   *interceptor
}

// get streams the file at path to w and returns how many bytes it wrote.
// what names the download in errors.
func (d *downloader) get(ctx context.Context, path, what string, w io.Writer) (int64, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, d.base+path, nil)
	if err != nil {
		return 0, fmt.Errorf("mimirsdk: %s: %w", what, err)
	}
	d.ic.setHeaders(req.Header)
	res, err := d.http.Do(req)
	if err != nil {
		if ctx.Err() != nil {
			return 0, ctx.Err()
		}
		return 0, fmt.Errorf("mimirsdk: %s: %w", what, err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		data, _ := io.ReadAll(io.LimitReader(res.Body, 1<<20))
		e := uploadError(res.StatusCode, data).(*Error)
		e.Procedure = path
		return 0, e
	}
	n, err := io.Copy(w, res.Body)
	if err != nil {
		return n, fmt.Errorf("mimirsdk: %s: %w", what, err)
	}
	return n, nil
}
