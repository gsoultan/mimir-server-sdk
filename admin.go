package mimirsdk

import (
	"context"
	"io"
	"iter"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// WebhookService manages the addresses the server tells about changes.
// Check deliveries on the receiving end with the webhook package.
type WebhookService struct {
	raw mimirv1connect.WebhookServiceClient
}

// List returns the caller's team's webhooks.
func (s *WebhookService) List(ctx context.Context) ([]*Webhook, error) {
	res, err := call(ctx, mimirv1connect.WebhookServiceListWebhooksProcedure, s.raw.ListWebhooks, nil)
	return res.GetWebhooks(), err
}

// EventTypes lists every event a webhook can subscribe to.
func (s *WebhookService) EventTypes(ctx context.Context) ([]string, error) {
	res, err := call(ctx, mimirv1connect.WebhookServiceListWebhooksProcedure, s.raw.ListWebhooks, nil)
	return res.GetEventTypes(), err
}

// Create adds a webhook. Its signing Secret is in the response only this
// once: give it to webhook.Verify on the receiving end.
func (s *WebhookService) Create(ctx context.Context, req *CreateWebhookRequest) (*CreateWebhookResponse, error) {
	return call(ctx, mimirv1connect.WebhookServiceCreateWebhookProcedure, s.raw.CreateWebhook, req)
}

// Update changes a webhook's name, address or events, or turns it off.
func (s *WebhookService) Update(ctx context.Context, req *UpdateWebhookRequest) (*Webhook, error) {
	res, err := call(ctx, mimirv1connect.WebhookServiceUpdateWebhookProcedure, s.raw.UpdateWebhook, req)
	return res.GetWebhook(), err
}

// Delete removes a webhook.
func (s *WebhookService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.WebhookServiceDeleteWebhookProcedure, s.raw.DeleteWebhook, &mimirv1.DeleteWebhookRequest{Id: id})
	return err
}

// SendTest sends a "test" event to a webhook now.
func (s *WebhookService) SendTest(ctx context.Context, id string) (*Delivery, error) {
	res, err := call(ctx, mimirv1connect.WebhookServiceSendTestEventProcedure, s.raw.SendTestEvent, &mimirv1.SendTestEventRequest{Id: id})
	return res.GetDelivery(), err
}

// Redeliver sends a past delivery again, now.
func (s *WebhookService) Redeliver(ctx context.Context, deliveryID string) (*Delivery, error) {
	res, err := call(ctx, mimirv1connect.WebhookServiceRedeliverProcedure, s.raw.Redeliver, &mimirv1.RedeliverRequest{Id: deliveryID})
	return res.GetDelivery(), err
}

// DeliveriesPage returns one page of a webhook's deliveries, newest first.
func (s *WebhookService) DeliveriesPage(ctx context.Context, webhookID string, opts ListOptions) (*Page[*Delivery], error) {
	res, err := call(ctx, mimirv1connect.WebhookServiceListDeliveriesProcedure, s.raw.ListDeliveries,
		&mimirv1.ListDeliveriesRequest{WebhookId: webhookID, PageSize: opts.PageSize, PageToken: opts.PageToken})
	if err != nil {
		return nil, err
	}
	return &Page[*Delivery]{Items: res.GetDeliveries(), NextPageToken: res.GetNextPageToken()}, nil
}

// Deliveries walks every delivery of a webhook, newest first, fetching
// pages as the loop needs them.
func (s *WebhookService) Deliveries(ctx context.Context, webhookID string, opts ListOptions) iter.Seq2[*Delivery, error] {
	return paginate(ctx, opts.PageToken, func(ctx context.Context, token string) (*Page[*Delivery], error) {
		return s.DeliveriesPage(ctx, webhookID, ListOptions{PageSize: opts.PageSize, PageToken: token})
	})
}

// WorkerService reads the machines that answer and teach models for the
// server.
type WorkerService struct {
	raw mimirv1connect.WorkerServiceClient
}

// List returns every worker.
func (s *WorkerService) List(ctx context.Context) ([]*Worker, error) {
	res, err := call(ctx, mimirv1connect.WorkerServiceListWorkersProcedure, s.raw.ListWorkers, nil)
	return res.GetWorkers(), err
}

// Get returns a worker with its last hours of samples and its tasks.
// hours of 0 lets the server choose.
func (s *WorkerService) Get(ctx context.Context, id string, hours int32) (*GetWorkerResponse, error) {
	return call(ctx, mimirv1connect.WorkerServiceGetWorkerProcedure, s.raw.GetWorker, &mimirv1.GetWorkerRequest{Id: id, Hours: hours})
}

// Choices returns the workers a model or training run may be placed on.
func (s *WorkerService) Choices(ctx context.Context) ([]*Worker, error) {
	res, err := call(ctx, mimirv1connect.WorkerServiceListWorkerChoicesProcedure, s.raw.ListWorkerChoices, nil)
	return res.GetWorkers(), err
}

// Create adds a worker and returns the token it joins with, shown only
// once.
func (s *WorkerService) Create(ctx context.Context, name string) (*CreateWorkerResponse, error) {
	return call(ctx, mimirv1connect.WorkerServiceCreateWorkerProcedure, s.raw.CreateWorker, &mimirv1.CreateWorkerRequest{Name: name})
}

// What a worker may be told to take, for SetTasks.
const (
	WorkerTasksAll   = "all"   // training runs and predictions
	WorkerTasksTrain = "train" // training runs only
	WorkerTasksServe = "serve" // predictions only
)

// SetTasks tells a worker what to take: WorkerTasksAll, WorkerTasksTrain
// or WorkerTasksServe, or "" to leave it to the worker's own -tasks flag.
// It applies at once to a connected worker.
func (s *WorkerService) SetTasks(ctx context.Context, id, tasks string) (*Worker, error) {
	res, err := call(ctx, mimirv1connect.WorkerServiceSetWorkerTasksProcedure, s.raw.SetWorkerTasks, &mimirv1.SetWorkerTasksRequest{Id: id, Tasks: tasks})
	return res.GetWorker(), err
}

// CloudGPU says how training runs rent a GPU when they wait, whether one
// is running now, and which providers and GPUs can be picked.
func (s *WorkerService) CloudGPU(ctx context.Context) (*GetCloudGpuResponse, error) {
	return call(ctx, mimirv1connect.WorkerServiceGetCloudGpuProcedure, s.raw.GetCloudGpu, nil)
}

// UpdateCloudGPU sets up renting a GPU for waiting training runs, changes
// it, or turns it off. Turning it on the first time adds a worker for it,
// which only trains.
func (s *WorkerService) UpdateCloudGPU(ctx context.Context, req *UpdateCloudGpuRequest) (*CloudGpu, error) {
	res, err := call(ctx, mimirv1connect.WorkerServiceUpdateCloudGpuProcedure, s.raw.UpdateCloudGpu, req)
	return res.GetCloudGpu(), err
}

// StopCloudGPU stops the rented GPU now. Runs on it go back in the queue
// and resume from their checkpoints.
func (s *WorkerService) StopCloudGPU(ctx context.Context) (*CloudGpu, error) {
	res, err := call(ctx, mimirv1connect.WorkerServiceStopCloudGpuProcedure, s.raw.StopCloudGpu, nil)
	return res.GetCloudGpu(), err
}

// ReplaceToken makes a new token for a worker, shown only once. The old
// token stops working at once and the worker is disconnected until it
// joins again with the new one.
func (s *WorkerService) ReplaceToken(ctx context.Context, id string) (string, error) {
	res, err := call(ctx, mimirv1connect.WorkerServiceReplaceWorkerTokenProcedure, s.raw.ReplaceWorkerToken, &mimirv1.ReplaceWorkerTokenRequest{Id: id})
	return res.GetToken(), err
}

// Delete removes a worker.
func (s *WorkerService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.WorkerServiceDeleteWorkerProcedure, s.raw.DeleteWorker, &mimirv1.DeleteWorkerRequest{Id: id})
	return err
}

// SettingsService reads and changes server-wide settings. It needs an
// owner, except Usage, which shows each caller their own.
type SettingsService struct {
	raw mimirv1connect.SettingsServiceClient
	dl  *downloader
}

// Get returns the alert, retention, security, limit and training settings.
func (s *SettingsService) Get(ctx context.Context) (*GetSettingsResponse, error) {
	return call(ctx, mimirv1connect.SettingsServiceGetSettingsProcedure, s.raw.GetSettings, nil)
}

// Usage returns how many predictions were asked in a month ("YYYY-MM"; ""
// means this month), by person and API key.
func (s *SettingsService) Usage(ctx context.Context, month string) (*GetUsageResponse, error) {
	return call(ctx, mimirv1connect.SettingsServiceGetUsageProcedure, s.raw.GetUsage, &mimirv1.GetUsageRequest{Month: month})
}

// UpdateAlerts changes where alerts go: email through an SMTP server,
// Telegram, or both. A nil channel is left as it is; an empty password or
// bot token keeps the stored one.
func (s *SettingsService) UpdateAlerts(ctx context.Context, email *EmailAlerts, telegram *TelegramAlerts) (*UpdateAlertsResponse, error) {
	return call(ctx, mimirv1connect.SettingsServiceUpdateAlertsProcedure, s.raw.UpdateAlerts, &mimirv1.UpdateAlertsRequest{Email: email, Telegram: telegram})
}

// Alert channels, for SendTestAlert.
const (
	AlertChannelEmail    = "email"
	AlertChannelTelegram = "telegram"
)

// SendTestAlert sends "This is a test" through AlertChannelEmail or
// AlertChannelTelegram now.
func (s *SettingsService) SendTestAlert(ctx context.Context, channel string) error {
	_, err := call(ctx, mimirv1connect.SettingsServiceSendTestAlertProcedure, s.raw.SendTestAlert, &mimirv1.SendTestAlertRequest{Channel: channel})
	return err
}

// UpdateRetention changes how long the audit log and webhook delivery
// history are kept.
func (s *SettingsService) UpdateRetention(ctx context.Context, retention *Retention) (*Retention, error) {
	res, err := call(ctx, mimirv1connect.SettingsServiceUpdateRetentionProcedure, s.raw.UpdateRetention, &mimirv1.UpdateRetentionRequest{Retention: retention})
	return res.GetRetention(), err
}

// UpdateSecurity changes the security policy, such as whether everyone
// must use two-step verification.
func (s *SettingsService) UpdateSecurity(ctx context.Context, security *Security) (*Security, error) {
	res, err := call(ctx, mimirv1connect.SettingsServiceUpdateSecurityProcedure, s.raw.UpdateSecurity, &mimirv1.UpdateSecurityRequest{Security: security})
	return res.GetSecurity(), err
}

// DatabaseInfo describes the server's database: its size, schema version,
// how many records it holds and when history was last trimmed.
func (s *SettingsService) DatabaseInfo(ctx context.Context) (*GetDatabaseInfoResponse, error) {
	return call(ctx, mimirv1connect.SettingsServiceGetDatabaseInfoProcedure, s.raw.GetDatabaseInfo, nil)
}

// Backup writes a pg_dump of the server's database to w, in pg_dump's
// custom format (restore it with pg_restore), and returns how many bytes
// it wrote. The server allows it only for an admin signed in with a
// password, not an API key, and only where pg_dump is installed.
func (s *SettingsService) Backup(ctx context.Context, w io.Writer) (int64, error) {
	return s.dl.get(ctx, backupPath, "download backup", w)
}

// UpdateLimits changes the prediction and training limits.
func (s *SettingsService) UpdateLimits(ctx context.Context, limits *Limits) (*Limits, error) {
	res, err := call(ctx, mimirv1connect.SettingsServiceUpdateLimitsProcedure, s.raw.UpdateLimits, &mimirv1.UpdateLimitsRequest{Limits: limits})
	return res.GetLimits(), err
}

// UpdateTraining says whether a standalone console trains runs in its own
// process when no worker takes them, and, when GroupWorkers is set, on how
// many workers one run may train together.
func (s *SettingsService) UpdateTraining(ctx context.Context, req *UpdateTrainingRequest) (*Training, error) {
	res, err := call(ctx, mimirv1connect.SettingsServiceUpdateTrainingProcedure, s.raw.UpdateTraining, req)
	return res.GetTraining(), err
}

// TemplateService lists ready-made starting points for common questions.
type TemplateService struct {
	raw mimirv1connect.TemplateServiceClient
}

// List returns every template, with the categories they belong to.
func (s *TemplateService) List(ctx context.Context) ([]*Template, []*TemplateCategory, error) {
	res, err := call(ctx, mimirv1connect.TemplateServiceListTemplatesProcedure, s.raw.ListTemplates, nil)
	return res.GetTemplates(), res.GetCategories(), err
}

// Example returns a template's made-up example data, a CSV or a ZIP, with
// a file name to save it under.
func (s *TemplateService) Example(ctx context.Context, templateID string) (fileName string, data []byte, err error) {
	res, err := call(ctx, mimirv1connect.TemplateServiceGetTemplateExampleProcedure, s.raw.GetTemplateExample, &mimirv1.GetTemplateExampleRequest{TemplateId: templateID})
	return res.GetFileName(), res.GetData(), err
}
