import {
  BenchmarkService as BenchmarkRPC,
  type Benchmark,
  type BenchmarkScore,
  type CreateBenchmarkRequestSchema,
  type GetBenchmarkResponse,
} from "./gen/mimir/v1/benchmark_pb.js";
import { JobStatus } from "./gen/mimir/v1/training_pb.js";
import type { Caller, CallOptions } from "./transport.js";
import { poll, type Init, type WaitOptions } from "./util.js";

function scoring(s: BenchmarkScore): boolean {
  return s.status === JobStatus.QUEUED || s.status === JobStatus.RUNNING;
}

/** Keeps the fixed tests models are ranked on. A benchmark's rows are
 * frozen from a dataset and left out of training on it, so every model
 * answers examples it never learned from, and the same ones. */
export class BenchmarkService {
  constructor(private readonly c: Caller) {}

  /** Every benchmark the caller may see, or those frozen from one dataset. */
  async list(datasetId = "", opts?: CallOptions): Promise<Benchmark[]> {
    return (await this.c.unary(BenchmarkRPC.method.listBenchmarks, { datasetId }, opts)).benchmarks;
  }

  /** A benchmark with its leaderboard, best first, and the models that
   * could still take it. */
  async get(id: string, opts?: CallOptions): Promise<GetBenchmarkResponse> {
    return this.c.unary(BenchmarkRPC.method.getBenchmark, { id }, opts);
  }

  /** Make a benchmark. share is the part of the dataset's rows to keep
   * aside, from 0.05 to 0.5, or 0 for a fifth; csv instead holds test rows
   * of your own, with the dataset's columns. */
  async create(req: Init<typeof CreateBenchmarkRequestSchema>, opts?: CallOptions): Promise<Benchmark> {
    return (await this.c.unary(BenchmarkRPC.method.createBenchmark, req, opts)).benchmark!;
  }

  /** Make a benchmark that keeps share of a dataset's rows aside; 0 keeps a
   * fifth. */
  async freeze(name: string, datasetId: string, share = 0, opts?: CallOptions): Promise<Benchmark> {
    return this.create({ name, datasetId, share }, opts);
  }

  /** Remove a benchmark, its rows and its scores. The models stay. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(BenchmarkRPC.method.deleteBenchmark, { id }, opts);
  }

  /** Put models on a benchmark's leaderboard. The scores come back queued,
   * and waitForScores follows them. */
  async score(benchmarkId: string, modelIds: string[], opts?: CallOptions): Promise<BenchmarkScore[]> {
    return (await this.c.unary(BenchmarkRPC.method.scoreModels, { benchmarkId, modelIds }, opts)).scores;
  }

  /** Follow a benchmark until no score on it is still queued or running,
   * and return the leaderboard, best first. A score that failed is in the
   * list with its reason, and is not an error here. */
  async waitForScores(benchmarkId: string, opts?: WaitOptions<BenchmarkScore[]>): Promise<BenchmarkScore[]> {
    return poll(
      async () => (await this.get(benchmarkId, { signal: opts?.signal })).scores,
      (scores) => !scores.some(scoring),
      opts,
      2000,
    );
  }

  /** The best finished score on a benchmark, or undefined when none has
   * finished. */
  async leader(benchmarkId: string, opts?: CallOptions): Promise<BenchmarkScore | undefined> {
    return (await this.get(benchmarkId, opts)).scores.find((s) => s.rank === 1);
  }
}
