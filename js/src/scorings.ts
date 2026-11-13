import { JobStatus } from "./gen/mimir/v1/training_pb.js";
import type { ConnectionSchema } from "./gen/mimir/v1/training_pb.js";
import {
  ScoringService as ScoringRPC,
  type CreateScoringRequestSchema,
  type GetScoringResponse,
  type Scoring,
} from "./gen/mimir/v1/scoring_pb.js";
import { ScoringError } from "./errors.js";
import { bytesOf, ended, type FileBody } from "./training.js";
import type { Caller, CallOptions } from "./transport.js";
import { poll, writeFile, type Init, type WaitOptions } from "./util.js";

/** Answers every row of a table with one model at once: a CSV, a database
 * query, files in storage or a dataset. The server scores in the background
 * and keeps the rows with each answer next to them as a CSV, which download
 * fetches. */
export class ScoringService {
  constructor(private readonly c: Caller) {}

  /** Every scoring the caller may see, or one model's, newest first. */
  async list(modelId = "", opts?: CallOptions): Promise<Scoring[]> {
    return (await this.c.unary(ScoringRPC.method.listScorings, { modelId }, opts)).scorings;
  }

  /** A scoring with the first rows of its results. */
  async get(id: string, opts?: CallOptions): Promise<GetScoringResponse> {
    return this.c.unary(ScoringRPC.method.getScoring, { id }, opts);
  }

  /** Queue a scoring. Give the rows one way: csv, connection and query,
   * bucket and path, or datasetId. wait follows it to the end. */
  async create(req: Init<typeof CreateScoringRequestSchema>, opts?: CallOptions): Promise<Scoring> {
    return (await this.c.unary(ScoringRPC.method.createScoring, req, opts)).scoring!;
  }

  /** Queue a scoring of a CSV with a header row; it needs no answer column.
   * An empty name lets the server choose one. */
  async scoreCSV(modelId: string, csv: FileBody, name = "", opts?: CallOptions): Promise<Scoring> {
    return this.create({ modelId, name, csv: await bytesOf(csv) }, opts);
  }

  /** Queue a scoring of a database query's rows, run again every
   * everySeconds when that is at least an hour; 0 runs it once. It needs an
   * admin. */
  async scoreQuery(
    modelId: string,
    connection: Init<typeof ConnectionSchema>,
    query: string,
    { name = "", everySeconds = 0, ...opts }: CallOptions & { name?: string; everySeconds?: number } = {},
  ): Promise<Scoring> {
    return this.create({ modelId, name, connection, query, repeatSeconds: BigInt(Math.floor(everySeconds)) }, opts);
  }

  /** Queue a finished, failed or cancelled scoring again now. */
  async run(id: string, opts?: CallOptions): Promise<Scoring> {
    return (await this.c.unary(ScoringRPC.method.runScoring, { id }, opts)).scoring!;
  }

  /** Stop a queued or running scoring. */
  async cancel(id: string, opts?: CallOptions): Promise<Scoring> {
    return (await this.c.unary(ScoringRPC.method.cancelScoring, { id }, opts)).scoring!;
  }

  /** Change how often a scoring from a database or storage runs again, from
   * an hour to 30 days; 0 stops it. */
  async setRepeat(id: string, everySeconds: number, opts?: CallOptions): Promise<Scoring> {
    const req = { id, repeatSeconds: BigInt(Math.floor(everySeconds)) };
    return (await this.c.unary(ScoringRPC.method.setScoringRepeat, req, opts)).scoring!;
  }

  /** Remove a scoring and its results. A running one must be cancelled
   * first. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(ScoringRPC.method.deleteScoring, { id }, opts);
  }

  /** Follow a scoring until it succeeds, fails or is cancelled. One that
   * fails or is cancelled throws ScoringError, which holds the scoring. */
  async wait(id: string, opts?: WaitOptions<Scoring>): Promise<Scoring> {
    const sc = await poll(async () => (await this.get(id, { signal: opts?.signal })).scoring!, ended, opts, 2000);
    if (sc.status !== JobStatus.SUCCEEDED) throw new ScoringError(sc);
    return sc;
  }

  /** A scoring's latest results as a stream: a CSV of every row, in order,
   * with the model's answer after it (predicted, then confidence or
   * suggestions, and problem, which says why a row couldn't be answered). */
  async download(id: string, opts?: CallOptions): Promise<ReadableStream<Uint8Array>> {
    return this.c.download(`/api/scorings/${encodeURIComponent(id)}/results`, opts);
  }

  /** download, written to a file on disk (Node.js, Deno and Bun). Returns
   * how many bytes it wrote. */
  async downloadToFile(id: string, path: string, opts?: CallOptions): Promise<number> {
    return writeFile(await this.download(id, opts), path);
  }
}
