import { Code as ConnectCode, ConnectError } from "@connectrpc/connect";
import { JobStatus, type Job } from "./gen/mimir/v1/training_pb.js";
import type { Scoring } from "./gen/mimir/v1/scoring_pb.js";
import type { Document } from "./gen/mimir/v1/document_pb.js";

/** What kind of failure a MimirError is: Connect's error codes. */
export type Code =
  | "canceled"
  | "unknown"
  | "invalid_argument"
  | "deadline_exceeded"
  | "not_found"
  | "already_exists"
  | "permission_denied"
  | "resource_exhausted"
  | "failed_precondition"
  | "aborted"
  | "out_of_range"
  | "unimplemented"
  | "internal"
  | "unavailable"
  | "data_loss"
  | "unauthenticated";

const codes: Record<ConnectCode, Code> = {
  [ConnectCode.Canceled]: "canceled",
  [ConnectCode.Unknown]: "unknown",
  [ConnectCode.InvalidArgument]: "invalid_argument",
  [ConnectCode.DeadlineExceeded]: "deadline_exceeded",
  [ConnectCode.NotFound]: "not_found",
  [ConnectCode.AlreadyExists]: "already_exists",
  [ConnectCode.PermissionDenied]: "permission_denied",
  [ConnectCode.ResourceExhausted]: "resource_exhausted",
  [ConnectCode.FailedPrecondition]: "failed_precondition",
  [ConnectCode.Aborted]: "aborted",
  [ConnectCode.OutOfRange]: "out_of_range",
  [ConnectCode.Unimplemented]: "unimplemented",
  [ConnectCode.Internal]: "internal",
  [ConnectCode.Unavailable]: "unavailable",
  [ConnectCode.DataLoss]: "data_loss",
  [ConnectCode.Unauthenticated]: "unauthenticated",
};

const allCodes = new Set<string>(Object.values(codes));

export interface MimirErrorInit {
  code: Code;
  message: string;
  procedure?: string;
  retryAfter?: number;
  cause?: unknown;
}

/**
 * A call the server, or the way to it, turned down. `code` says what kind
 * of failure it is, `rawMessage` is the server's explanation, written to
 * show to people, `procedure` the call that failed (like
 * "/mimir.v1.ModelService/GetModel") and `retryAfter` how many seconds the
 * server asked to wait before trying again (0 when it didn't say). Catch a
 * subclass, such as NotFoundError, for one code.
 */
export class MimirError extends Error {
  override name = "MimirError";
  readonly code: Code;
  readonly rawMessage: string;
  readonly procedure: string;
  readonly retryAfter: number;

  constructor(init: MimirErrorInit) {
    let text = "mimirsdk: ";
    if (init.procedure) text += init.procedure.replace(/^\/mimir\.v1\./, "") + ": ";
    text += init.code;
    if (init.message) text += ": " + init.message;
    super(text, init.cause === undefined ? undefined : { cause: init.cause });
    this.code = init.code;
    this.rawMessage = init.message;
    this.procedure = init.procedure ?? "";
    this.retryAfter = init.retryAfter ?? 0;
  }

  /** The same call may succeed if tried again later. */
  get retryable(): boolean {
    return this.code === "unavailable" || this.retryAfter > 0;
  }
}

function errorClass(code: Code, name: string): typeof MimirError {
  const cls = class extends MimirError {
    override name = name;
    constructor(init: Omit<MimirErrorInit, "code"> & { code?: Code }) {
      super({ ...init, code });
    }
  };
  Object.defineProperty(cls, "name", { value: name });
  return cls as unknown as typeof MimirError;
}

type ErrorClass = new (init: Omit<MimirErrorInit, "code"> & { code?: Code }) => MimirError;

export const CanceledError = errorClass("canceled", "CanceledError") as ErrorClass;
export const InvalidArgumentError = errorClass("invalid_argument", "InvalidArgumentError") as ErrorClass;
export const DeadlineExceededError = errorClass("deadline_exceeded", "DeadlineExceededError") as ErrorClass;
export const NotFoundError = errorClass("not_found", "NotFoundError") as ErrorClass;
export const AlreadyExistsError = errorClass("already_exists", "AlreadyExistsError") as ErrorClass;
export const PermissionDeniedError = errorClass("permission_denied", "PermissionDeniedError") as ErrorClass;
export const ResourceExhaustedError = errorClass("resource_exhausted", "ResourceExhaustedError") as ErrorClass;
export const FailedPreconditionError = errorClass("failed_precondition", "FailedPreconditionError") as ErrorClass;
export const UnimplementedError = errorClass("unimplemented", "UnimplementedError") as ErrorClass;
export const InternalError = errorClass("internal", "InternalError") as ErrorClass;
export const UnavailableError = errorClass("unavailable", "UnavailableError") as ErrorClass;
export const UnauthenticatedError = errorClass("unauthenticated", "UnauthenticatedError") as ErrorClass;

const byCode: Partial<Record<Code, ErrorClass>> = {
  canceled: CanceledError,
  invalid_argument: InvalidArgumentError,
  deadline_exceeded: DeadlineExceededError,
  not_found: NotFoundError,
  already_exists: AlreadyExistsError,
  permission_denied: PermissionDeniedError,
  resource_exhausted: ResourceExhaustedError,
  failed_precondition: FailedPreconditionError,
  unimplemented: UnimplementedError,
  internal: InternalError,
  unavailable: UnavailableError,
  unauthenticated: UnauthenticatedError,
};

/** The MimirError subclass for a code. */
export function errorFor(init: MimirErrorInit): MimirError {
  const cls = byCode[init.code];
  return cls ? new cls(init) : new MimirError(init);
}

/** The code for a Connect error code. */
export function codeOf(c: ConnectCode): Code {
  return codes[c] ?? "unknown";
}

/** Parse a code name the server sent, such as "not_found". */
export function parseCode(v: unknown): Code | undefined {
  return typeof v === "string" && allCodes.has(v) ? (v as Code) : undefined;
}

/** The nearest code for an HTTP status, for answers that aren't
 * Connect-shaped (a proxy's, say). */
export function codeFromHTTP(status: number): Code {
  switch (status) {
    case 400:
      return "invalid_argument";
    case 401:
      return "unauthenticated";
    case 403:
      return "permission_denied";
    case 404:
      return "unimplemented";
    case 408:
      return "deadline_exceeded";
    case 409:
      return "aborted";
    case 412:
      return "failed_precondition";
    case 413:
    case 429:
    case 431:
      return "resource_exhausted";
    case 502:
    case 503:
    case 504:
      return "unavailable";
    default:
      return "unknown";
  }
}

/** Seconds from a Retry-After header, 0 when there is none. */
export function retryAfterOf(headers: Headers | undefined): number {
  const v = headers?.get("retry-after")?.trim();
  if (!v || !/^\d+$/.test(v)) return 0;
  return Number(v);
}

/**
 * Turn an error from a Connect client into a MimirError. An abort the
 * caller asked for passes through as it is.
 */
export function wrapError(procedure: string, err: unknown): unknown {
  if (err instanceof MimirError) return err;
  if (isAbortError(err)) return err;
  const ce = ConnectError.from(err);
  if (ce.code === ConnectCode.Canceled && isAbortError(ce.cause)) return ce.cause;
  return errorFor({
    code: codeOf(ce.code),
    message: ce.rawMessage,
    procedure,
    retryAfter: retryAfterOf(ce.metadata),
    cause: err,
  });
}

function isAbortError(err: unknown): boolean {
  return err instanceof Error && err.name === "AbortError";
}

function statusName(status: JobStatus): string {
  return (JobStatus[status] ?? String(status)).toLowerCase();
}

/** A training run that failed or was cancelled. `job` is the run as it
 * ended. */
export class JobError extends Error {
  override name = "JobError";
  constructor(readonly job: Job) {
    super(`mimirsdk: training run ${job.id} ${statusName(job.status)}` + (job.error ? `: ${job.error}` : ""));
  }
}

/** A scoring that failed or was cancelled. `scoring` is the scoring as it
 * ended. */
export class ScoringError extends Error {
  override name = "ScoringError";
  constructor(readonly scoring: Scoring) {
    super(
      `mimirsdk: scoring ${scoring.id} ${statusName(scoring.status)}` + (scoring.error ? `: ${scoring.error}` : ""),
    );
  }
}

/** A document the server couldn't read. `document` is the document as it
 * ended. */
export class DocumentError extends Error {
  override name = "DocumentError";
  constructor(readonly document: Document) {
    super(`mimirsdk: document ${document.name} not read` + (document.error ? `: ${document.error}` : ""));
  }
}
