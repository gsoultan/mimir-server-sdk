package mimirsdk

import mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"

// The server's types, under the names the server gives them. See the
// server's proto files (proto/mimir/v1) for what each field means.
type (
	Role                       = mimirv1.Role
	Access                     = mimirv1.Access
	User                       = mimirv1.User
	Session                    = mimirv1.Session
	APIKey                     = mimirv1.ApiKey
	AuditEvent                 = mimirv1.AuditEvent
	Architecture               = mimirv1.Architecture
	Column                     = mimirv1.Column
	ModelStatus                = mimirv1.ModelStatus
	Model                      = mimirv1.Model
	LanguageSettings           = mimirv1.LanguageSettings
	Tensor                     = mimirv1.Tensor
	Guess                      = mimirv1.Guess
	ChatMessage                = mimirv1.ChatMessage
	Limits                     = mimirv1.Limits
	UsageRow                   = mimirv1.UsageRow
	Team                       = mimirv1.Team
	TemplateCategory           = mimirv1.TemplateCategory
	TemplateColumn             = mimirv1.TemplateColumn
	Template                   = mimirv1.Template
	DataCheck                  = mimirv1.DataCheck
	DatasetKind                = mimirv1.DatasetKind
	Dataset                    = mimirv1.Dataset
	StorageSource              = mimirv1.StorageSource
	Row                        = mimirv1.Row
	Bucket                     = mimirv1.Bucket
	Connection                 = mimirv1.Connection
	JobStatus                  = mimirv1.JobStatus
	TrainingSettings           = mimirv1.TrainingSettings
	Layer                      = mimirv1.Layer
	EpochResult                = mimirv1.EpochResult
	Job                        = mimirv1.Job
	Webhook                    = mimirv1.Webhook
	DeliveryStatus             = mimirv1.DeliveryStatus
	Delivery                   = mimirv1.Delivery
	Worker                     = mimirv1.Worker
	Stats                      = mimirv1.Stats
	CreateModelRequest         = mimirv1.CreateModelRequest
	UpdateModelRequest         = mimirv1.UpdateModelRequest
	SaveArchitectureRequest    = mimirv1.SaveArchitectureRequest
	PredictRequest             = mimirv1.PredictRequest
	PredictResponse            = mimirv1.PredictResponse
	GenerateRequest            = mimirv1.GenerateRequest
	GenerateResponse           = mimirv1.GenerateResponse
	GenerateStreamRequest      = mimirv1.GenerateStreamRequest
	GenerateStreamResponse     = mimirv1.GenerateStreamResponse
	ChatRequest                = mimirv1.ChatRequest
	ChatResponse               = mimirv1.ChatResponse
	GetDeviceModelResponse     = mimirv1.GetDeviceModelResponse
	CreateDatasetRequest       = mimirv1.CreateDatasetRequest
	CreateDatasetResponse      = mimirv1.CreateDatasetResponse
	GetDatasetResponse         = mimirv1.GetDatasetResponse
	CheckDatasetRequest        = mimirv1.CheckDatasetRequest
	CheckDatasetResponse       = mimirv1.CheckDatasetResponse
	TestQueryResponse          = mimirv1.TestQueryResponse
	TestBucketRequest          = mimirv1.TestBucketRequest
	TestBucketResponse         = mimirv1.TestBucketResponse
	CreateJobRequest           = mimirv1.CreateJobRequest
	SignInResponse             = mimirv1.SignInResponse
	VerifySecondFactorResponse = mimirv1.VerifySecondFactorResponse
	WhoAmIResponse             = mimirv1.WhoAmIResponse
	GetSetupStateResponse      = mimirv1.GetSetupStateResponse
	CreateUserRequest          = mimirv1.CreateUserRequest
	UpdateUserRequest          = mimirv1.UpdateUserRequest
	CreateAPIKeyRequest        = mimirv1.CreateApiKeyRequest
	CreateAPIKeyResponse       = mimirv1.CreateApiKeyResponse
	CreateWebhookRequest       = mimirv1.CreateWebhookRequest
	CreateWebhookResponse      = mimirv1.CreateWebhookResponse
	UpdateWebhookRequest       = mimirv1.UpdateWebhookRequest
	GetWorkerResponse          = mimirv1.GetWorkerResponse
	CreateWorkerResponse       = mimirv1.CreateWorkerResponse
	GetUsageResponse           = mimirv1.GetUsageResponse
	GetSettingsResponse        = mimirv1.GetSettingsResponse
)

// Role values.
const (
	RoleViewer = mimirv1.Role_ROLE_VIEWER
	RoleEditor = mimirv1.Role_ROLE_EDITOR
	RoleAdmin  = mimirv1.Role_ROLE_ADMIN
	RoleOwner  = mimirv1.Role_ROLE_OWNER
)

// ModelStatus values.
const (
	ModelStatusReady  = mimirv1.ModelStatus_MODEL_STATUS_READY
	ModelStatusFailed = mimirv1.ModelStatus_MODEL_STATUS_FAILED
)

// JobStatus values.
const (
	JobStatusQueued    = mimirv1.JobStatus_JOB_STATUS_QUEUED
	JobStatusRunning   = mimirv1.JobStatus_JOB_STATUS_RUNNING
	JobStatusSucceeded = mimirv1.JobStatus_JOB_STATUS_SUCCEEDED
	JobStatusFailed    = mimirv1.JobStatus_JOB_STATUS_FAILED
	JobStatusCancelled = mimirv1.JobStatus_JOB_STATUS_CANCELLED
)

// DatasetKind values.
const (
	DatasetKindTable      = mimirv1.DatasetKind_DATASET_KIND_TABLE
	DatasetKindMnist      = mimirv1.DatasetKind_DATASET_KIND_MNIST
	DatasetKindPhotos     = mimirv1.DatasetKind_DATASET_KIND_PHOTOS
	DatasetKindPhotoTable = mimirv1.DatasetKind_DATASET_KIND_PHOTO_TABLE
)

// DeliveryStatus values.
const (
	DeliveryStatusPending   = mimirv1.DeliveryStatus_DELIVERY_STATUS_PENDING
	DeliveryStatusDelivered = mimirv1.DeliveryStatus_DELIVERY_STATUS_DELIVERED
	DeliveryStatusFailed    = mimirv1.DeliveryStatus_DELIVERY_STATUS_FAILED
)
