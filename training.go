package mimirsdk

import (
	"context"
	"fmt"
	"io"
	"time"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// DatasetService keeps the examples models learn from.
type DatasetService struct {
	raw mimirv1connect.DatasetServiceClient
}

// List returns every dataset the caller may see.
func (s *DatasetService) List(ctx context.Context) ([]*Dataset, error) {
	res, err := call(ctx, mimirv1connect.DatasetServiceListDatasetsProcedure, s.raw.ListDatasets, nil)
	return res.GetDatasets(), err
}

// Get returns a dataset with its first few rows.
func (s *DatasetService) Get(ctx context.Context, id string) (*GetDatasetResponse, error) {
	return call(ctx, mimirv1connect.DatasetServiceGetDatasetProcedure, s.raw.GetDataset, &mimirv1.GetDatasetRequest{Id: id})
}

// Create stores a dataset: a CSV, a ZIP of photos, a database query, files
// in a bucket, or a template's example data. The response says how well
// the data fits.
func (s *DatasetService) Create(ctx context.Context, req *CreateDatasetRequest) (*CreateDatasetResponse, error) {
	return call(ctx, mimirv1connect.DatasetServiceCreateDatasetProcedure, s.raw.CreateDataset, req)
}

// UploadCSV stores a table read from r, with a header row. target is the
// column to predict; "" means the last one.
func (s *DatasetService) UploadCSV(ctx context.Context, name, target string, r io.Reader) (*CreateDatasetResponse, error) {
	csv, err := io.ReadAll(r)
	if err != nil {
		return nil, fmt.Errorf("mimirsdk: read the CSV: %w", err)
	}
	return s.Create(ctx, &mimirv1.CreateDatasetRequest{Name: name, Kind: DatasetKindTable, Csv: csv, Target: target})
}

// UploadPhotos stores a ZIP of photos read from r, with one folder per
// answer.
func (s *DatasetService) UploadPhotos(ctx context.Context, name string, r io.Reader) (*CreateDatasetResponse, error) {
	zip, err := io.ReadAll(r)
	if err != nil {
		return nil, fmt.Errorf("mimirsdk: read the ZIP: %w", err)
	}
	return s.Create(ctx, &mimirv1.CreateDatasetRequest{Name: name, Kind: DatasetKindPhotos, Archive: zip})
}

// UploadSounds stores a ZIP of WAV sounds read from r, with one folder per
// answer.
func (s *DatasetService) UploadSounds(ctx context.Context, name string, r io.Reader) (*CreateDatasetResponse, error) {
	zip, err := io.ReadAll(r)
	if err != nil {
		return nil, fmt.Errorf("mimirsdk: read the ZIP: %w", err)
	}
	return s.Create(ctx, &mimirv1.CreateDatasetRequest{Name: name, Kind: DatasetKindSounds, Archive: zip})
}

// UploadBoxes stores a ZIP read from r of photos and a boxes.csv saying
// where the things in them are: one row per thing, with the columns photo,
// what, left, top, width and height (or right and bottom), in pixels.
func (s *DatasetService) UploadBoxes(ctx context.Context, name string, r io.Reader) (*CreateDatasetResponse, error) {
	zip, err := io.ReadAll(r)
	if err != nil {
		return nil, fmt.Errorf("mimirsdk: read the ZIP: %w", err)
	}
	return s.Create(ctx, &mimirv1.CreateDatasetRequest{Name: name, Kind: DatasetKindBoxes, Archive: zip})
}

// UploadText stores writing read from r for a language model to learn
// from: plain text, or JSON Lines of chats, prompts and completions.
func (s *DatasetService) UploadText(ctx context.Context, name string, r io.Reader) (*CreateDatasetResponse, error) {
	text, err := io.ReadAll(r)
	if err != nil {
		return nil, fmt.Errorf("mimirsdk: read the text: %w", err)
	}
	return s.Create(ctx, &mimirv1.CreateDatasetRequest{Name: name, Kind: DatasetKindText, Text: text})
}

// Refresh runs a database dataset's query again and replaces its rows.
func (s *DatasetService) Refresh(ctx context.Context, id string) (*Dataset, error) {
	res, err := call(ctx, mimirv1connect.DatasetServiceRefreshDatasetProcedure, s.raw.RefreshDataset, &mimirv1.RefreshDatasetRequest{Id: id})
	return res.GetDataset(), err
}

// Check checks a dataset against a template, and with Apply keeps the
// match.
func (s *DatasetService) Check(ctx context.Context, req *CheckDatasetRequest) (*CheckDatasetResponse, error) {
	return call(ctx, mimirv1connect.DatasetServiceCheckDatasetProcedure, s.raw.CheckDataset, req)
}

// Delete removes a dataset.
func (s *DatasetService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.DatasetServiceDeleteDatasetProcedure, s.raw.DeleteDataset, &mimirv1.DeleteDatasetRequest{Id: id})
	return err
}

// TrainingService teaches models and follows their progress.
type TrainingService struct {
	raw mimirv1connect.TrainingServiceClient
}

// List returns every training run the caller may see.
func (s *TrainingService) List(ctx context.Context) ([]*Job, error) {
	res, err := call(ctx, mimirv1connect.TrainingServiceListJobsProcedure, s.raw.ListJobs, nil)
	return res.GetJobs(), err
}

// Get returns one training run with its progress.
func (s *TrainingService) Get(ctx context.Context, id string) (*Job, error) {
	res, err := call(ctx, mimirv1connect.TrainingServiceGetJobProcedure, s.raw.GetJob, &mimirv1.GetJobRequest{Id: id})
	return res.GetJob(), err
}

// Start queues a training run. Wait follows it to the end.
func (s *TrainingService) Start(ctx context.Context, req *CreateJobRequest) (*Job, error) {
	res, err := call(ctx, mimirv1connect.TrainingServiceCreateJobProcedure, s.raw.CreateJob, req)
	return res.GetJob(), err
}

// Cancel stops a queued or running run, keeping its progress.
func (s *TrainingService) Cancel(ctx context.Context, id string) (*Job, error) {
	res, err := call(ctx, mimirv1connect.TrainingServiceCancelJobProcedure, s.raw.CancelJob, &mimirv1.CancelJobRequest{Id: id})
	return res.GetJob(), err
}

// Resume queues a cancelled or failed run again, from its last finished
// epoch.
func (s *TrainingService) Resume(ctx context.Context, id string) (*Job, error) {
	res, err := call(ctx, mimirv1connect.TrainingServiceResumeJobProcedure, s.raw.ResumeJob, &mimirv1.ResumeJobRequest{Id: id})
	return res.GetJob(), err
}

// Delete removes a run. The model it made stays.
func (s *TrainingService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.TrainingServiceDeleteJobProcedure, s.raw.DeleteJob, &mimirv1.DeleteJobRequest{Id: id})
	return err
}

// Compare returns two to six runs side by side, with every pass of each,
// what their settings differ in, and the id of the best of them.
func (s *TrainingService) Compare(ctx context.Context, ids ...string) (*CompareJobsResponse, error) {
	return call(ctx, mimirv1connect.TrainingServiceCompareJobsProcedure, s.raw.CompareJobs, &mimirv1.CompareJobsRequest{Ids: ids})
}

// KeepLearning makes a run learn again from fresh examples every interval;
// 0 stops it. The interval is rounded down to whole seconds. minNewRows
// above 0 makes each pass wait until the source has that many new rows,
// looking again every interval until it has; 0 starts a pass every
// interval.
func (s *TrainingService) KeepLearning(ctx context.Context, id string, every time.Duration, minNewRows int64) (*Job, error) {
	res, err := call(ctx, mimirv1connect.TrainingServiceSetRepeatProcedure, s.raw.SetRepeat, &mimirv1.SetRepeatRequest{
		Id:            id,
		RepeatSeconds: int64(every / time.Second),
		MinNewRows:    minNewRows,
	})
	return res.GetJob(), err
}

// WaitOptions change how Wait follows a run.
type WaitOptions struct {
	// Interval is how often to look; 0 means 2 seconds.
	Interval time.Duration
	// OnProgress, when set, sees the run each time Wait looks.
	OnProgress func(*Job)
}

// Wait follows a run until it succeeds, fails or is cancelled, and returns
// it as it ended. A run that fails or is cancelled returns a *JobError
// along with it. Bound the wait with ctx.
func (s *TrainingService) Wait(ctx context.Context, id string, opts WaitOptions) (*Job, error) {
	interval := opts.Interval
	if interval <= 0 {
		interval = 2 * time.Second
	}
	t := time.NewTicker(interval)
	defer t.Stop()
	for {
		job, err := s.Get(ctx, id)
		if err != nil {
			return nil, err
		}
		if opts.OnProgress != nil {
			opts.OnProgress(job)
		}
		switch job.GetStatus() {
		case JobStatusSucceeded:
			return job, nil
		case JobStatusFailed, JobStatusCancelled:
			return job, &JobError{Job: job}
		}
		select {
		case <-ctx.Done():
			return job, ctx.Err()
		case <-t.C:
		}
	}
}
