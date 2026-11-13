import {
  DatasetKind,
  DatasetService as DatasetRPC,
  JobStatus,
  TrainingService as TrainingRPC,
  type CheckDatasetRequestSchema,
  type CheckDatasetResponse,
  type CompareJobsResponse,
  type ConnectionSchema,
  type CreateDatasetRequestSchema,
  type CreateDatasetResponse,
  type CreateJobRequestSchema,
  type Dataset,
  type GetDatasetResponse,
  type Job,
  type TestBucketRequestSchema,
  type TestBucketResponse,
  type TestQueryResponse,
} from "./gen/mimir/v1/training_pb.js";
import { JobError } from "./errors.js";
import type { Caller, CallOptions } from "./transport.js";
import { poll, readAll, type Init, type WaitOptions } from "./util.js";

/** A file's contents: bytes, a Blob or a stream. */
export type FileBody = Uint8Array | ArrayBuffer | Blob | ReadableStream<Uint8Array> | string;

/** The bytes of a file body. A string is sent as UTF-8 text. */
export async function bytesOf(body: FileBody): Promise<Uint8Array> {
  if (body instanceof Uint8Array) return body;
  if (typeof body === "string") return new TextEncoder().encode(body);
  if (body instanceof ArrayBuffer) return new Uint8Array(body);
  if (typeof Blob !== "undefined" && body instanceof Blob) return new Uint8Array(await body.arrayBuffer());
  return readAll(body as ReadableStream<Uint8Array>);
}

/** Whether a run, scoring or document has ended. */
export function ended(item: { status: JobStatus }): boolean {
  return (
    item.status === JobStatus.SUCCEEDED || item.status === JobStatus.FAILED || item.status === JobStatus.CANCELLED
  );
}

/** Keeps the examples models learn from. */
export class DatasetService {
  constructor(private readonly c: Caller) {}

  /** Every dataset the caller may see. */
  async list(opts?: CallOptions): Promise<Dataset[]> {
    return (await this.c.unary(DatasetRPC.method.listDatasets, {}, opts)).datasets;
  }

  /** A dataset with its first few rows. */
  async get(id: string, opts?: CallOptions): Promise<GetDatasetResponse> {
    return this.c.unary(DatasetRPC.method.getDataset, { id }, opts);
  }

  /** Store a dataset: a CSV, a ZIP of photos, a database query, files in a
   * bucket, or a template's example data. The response says how well the
   * data fits. */
  async create(req: Init<typeof CreateDatasetRequestSchema>, opts?: CallOptions): Promise<CreateDatasetResponse> {
    return this.c.unary(DatasetRPC.method.createDataset, req, opts);
  }

  /** Store a table with a header row. target is the column to predict; ""
   * means the last one. A string is the CSV's text. */
  async uploadCSV(name: string, csv: FileBody, target = "", opts?: CallOptions): Promise<CreateDatasetResponse> {
    return this.create({ name, kind: DatasetKind.TABLE, csv: await bytesOf(csv), target }, opts);
  }

  /** Store a ZIP of photos, with one folder per answer. */
  async uploadPhotos(name: string, zip: FileBody, opts?: CallOptions): Promise<CreateDatasetResponse> {
    return this.create({ name, kind: DatasetKind.PHOTOS, archive: await bytesOf(zip) }, opts);
  }

  /** Store a ZIP of WAV sounds, with one folder per answer. */
  async uploadSounds(name: string, zip: FileBody, opts?: CallOptions): Promise<CreateDatasetResponse> {
    return this.create({ name, kind: DatasetKind.SOUNDS, archive: await bytesOf(zip) }, opts);
  }

  /** Store a ZIP of photos and a boxes.csv saying where the things in them
   * are: one row per thing, with the columns photo, what, left, top, width
   * and height (or right and bottom), in pixels. */
  async uploadBoxes(name: string, zip: FileBody, opts?: CallOptions): Promise<CreateDatasetResponse> {
    return this.create({ name, kind: DatasetKind.BOXES, archive: await bytesOf(zip) }, opts);
  }

  /** Store writing for a language model to learn from: plain text, or JSON
   * Lines of chats, prompts and completions. */
  async uploadText(name: string, text: FileBody, opts?: CallOptions): Promise<CreateDatasetResponse> {
    return this.create({ name, kind: DatasetKind.TEXT, text: await bytesOf(text) }, opts);
  }

  /** Run a database query and return its columns, a few rows and how many
   * rows it has, so the answer column can be picked before a dataset is
   * made from it. */
  async testQuery(
    connection: Init<typeof ConnectionSchema>,
    query: string,
    opts?: CallOptions,
  ): Promise<TestQueryResponse> {
    return this.c.unary(DatasetRPC.method.testQuery, { connection, query }, opts);
  }

  /** Read a file, or a folder ending in a slash, from S3-compatible storage
   * and say what is there. */
  async testBucket(req: Init<typeof TestBucketRequestSchema>, opts?: CallOptions): Promise<TestBucketResponse> {
    return this.c.unary(DatasetRPC.method.testBucket, req, opts);
  }

  /** Run a database dataset's query again and replace its rows. */
  async refresh(id: string, opts?: CallOptions): Promise<Dataset> {
    return (await this.c.unary(DatasetRPC.method.refreshDataset, { id }, opts)).dataset!;
  }

  /** Check a dataset against a template, and with apply keep the match. */
  async check(req: Init<typeof CheckDatasetRequestSchema>, opts?: CallOptions): Promise<CheckDatasetResponse> {
    return this.c.unary(DatasetRPC.method.checkDataset, req, opts);
  }

  /** Remove a dataset. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(DatasetRPC.method.deleteDataset, { id }, opts);
  }
}

/** Teaches models and follows their progress. */
export class TrainingService {
  constructor(private readonly c: Caller) {}

  /** Every training run the caller may see. */
  async list(opts?: CallOptions): Promise<Job[]> {
    return (await this.c.unary(TrainingRPC.method.listJobs, {}, opts)).jobs;
  }

  /** One training run with its progress. */
  async get(id: string, opts?: CallOptions): Promise<Job> {
    return (await this.c.unary(TrainingRPC.method.getJob, { id }, opts)).job!;
  }

  /** Queue a training run. wait follows it to the end. */
  async start(req: Init<typeof CreateJobRequestSchema>, opts?: CallOptions): Promise<Job> {
    return (await this.c.unary(TrainingRPC.method.createJob, req, opts)).job!;
  }

  /** Stop a queued or running run, keeping its progress. */
  async cancel(id: string, opts?: CallOptions): Promise<Job> {
    return (await this.c.unary(TrainingRPC.method.cancelJob, { id }, opts)).job!;
  }

  /** Queue a cancelled or failed run again, from its last finished epoch. */
  async resume(id: string, opts?: CallOptions): Promise<Job> {
    return (await this.c.unary(TrainingRPC.method.resumeJob, { id }, opts)).job!;
  }

  /** Remove a run. The model it made stays. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(TrainingRPC.method.deleteJob, { id }, opts);
  }

  /** Two to six runs side by side, with every pass of each, what their
   * settings differ in, and the id of the best of them. */
  async compare(ids: string[], opts?: CallOptions): Promise<CompareJobsResponse> {
    return this.c.unary(TrainingRPC.method.compareJobs, { ids }, opts);
  }

  /** Make a run learn again from fresh examples every everySeconds; 0 stops
   * it. minNewRows above 0 makes each pass wait until the source has that
   * many new rows; 0 starts a pass every interval. */
  async keepLearning(id: string, everySeconds: number, minNewRows = 0, opts?: CallOptions): Promise<Job> {
    const req = { id, repeatSeconds: BigInt(Math.floor(everySeconds)), minNewRows: BigInt(minNewRows) };
    return (await this.c.unary(TrainingRPC.method.setRepeat, req, opts)).job!;
  }

  /** Follow a run until it succeeds, fails or is cancelled, and return it
   * as it ended. A run that fails or is cancelled throws JobError, which
   * holds the run. Stop waiting with opts.signal. */
  async wait(id: string, opts?: WaitOptions<Job>): Promise<Job> {
    const job = await poll(() => this.get(id, { signal: opts?.signal }), ended, opts, 2000);
    if (job.status !== JobStatus.SUCCEEDED) throw new JobError(job);
    return job;
  }
}
