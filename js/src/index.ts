/**
 * The JavaScript and TypeScript client for mimir-server.
 *
 *     import { Client, userMessage } from "mimir-server-sdk";
 *
 *     const client = new Client("http://localhost:8080", { apiKey: "mimir_..." });
 *     for (const m of await client.models.list()) console.log(m.name, m.id);
 *
 * Every message, enum and service descriptor of the server's API is
 * exported under the server's own names (Model, ChatRequest, JobStatus,
 * ...). Requests take plain objects with any of a message's fields.
 */

export { Client, ENV_API_KEY, ENV_URL, type RawClients } from "./client.js";
export {
  DEFAULT_MAX_RETRY_WAIT_MS,
  DEFAULT_RETRIES,
  DEFAULT_RETRY_BACKOFF_MS,
  DEFAULT_TIMEOUT_MS,
  type CallOptions,
  type ClientOptions,
} from "./transport.js";
export {
  AlreadyExistsError,
  CanceledError,
  DeadlineExceededError,
  DocumentError,
  FailedPreconditionError,
  InternalError,
  InvalidArgumentError,
  JobError,
  MimirError,
  NotFoundError,
  PermissionDeniedError,
  ResourceExhaustedError,
  ScoringError,
  UnauthenticatedError,
  UnavailableError,
  UnimplementedError,
  type Code,
} from "./errors.js";
export { assistantMessage, userMessage, type ChatReply, type UploadBody } from "./models.js";
export type { Answer } from "./documents.js";
export type { FileBody } from "./training.js";
export { allModels, someModels } from "./access.js";
export { AlertChannel, WorkerTasks } from "./admin.js";
export type { Init, ListOptions, Page, WaitOptions } from "./util.js";
export { SERVER_VERSION, VERSION } from "./version.js";

export * from "./gen/mimir/v1/access_pb.js";
export * from "./gen/mimir/v1/benchmark_pb.js";
export * from "./gen/mimir/v1/document_pb.js";
export * from "./gen/mimir/v1/model_pb.js";
export * from "./gen/mimir/v1/scoring_pb.js";
export * from "./gen/mimir/v1/settings_pb.js";
export * from "./gen/mimir/v1/signin_pb.js";
export * from "./gen/mimir/v1/team_pb.js";
export * from "./gen/mimir/v1/template_pb.js";
export * from "./gen/mimir/v1/training_pb.js";
export * from "./gen/mimir/v1/webhook_pb.js";
export * from "./gen/mimir/v1/worker_pb.js";
