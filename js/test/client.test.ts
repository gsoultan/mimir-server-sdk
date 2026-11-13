import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { beforeEach, describe, expect, inject, it } from "vitest";
import {
  Client,
  DatasetKind,
  DeadlineExceededError,
  InvalidArgumentError,
  JobError,
  JobStatus,
  MimirError,
  ModelStatus,
  NotFoundError,
  ResourceExhaustedError,
  Role,
  UnauthenticatedError,
  UnavailableError,
  UnimplementedError,
  VERSION,
  allModels,
  assistantMessage,
  someModels,
  userMessage,
} from "../src/index.js";

const KEY = "mimir_test_key";
const url = inject("serverUrl");
let run = "";
let client: Client;

beforeEach(() => {
  run = randomUUID();
  client = new Client(url, { apiKey: KEY, retryBackoffMs: 10, headers: { "X-Test-Run": run } });
});

async function count(procedure: string): Promise<number> {
  const res = await fetch(`${url}/test/count?run=${run}&procedure=${procedure}`);
  return ((await res.json()) as { count: number }).count;
}

async function collect<T>(it: AsyncIterable<T>): Promise<T[]> {
  const out: T[] = [];
  for await (const x of it) out.push(x);
  return out;
}

describe("models", () => {
  it("lists and gets", async () => {
    const models = await client.models.list();
    expect(models.map((m) => m.name)).toEqual(["churn", "llama"]);
    expect(models[0]!.sizeBytes).toBe(1n << 40n);
    expect(models[0]!.status).toBe(ModelStatus.READY);
    expect((await client.models.get("m2")).architecture).toBe("llama");
  });

  it("turns errors into typed MimirErrors", async () => {
    const err = await client.models.get("nope").catch((e: unknown) => e);
    expect(err).toBeInstanceOf(NotFoundError);
    expect(err).toBeInstanceOf(MimirError);
    const e = err as MimirError;
    expect(e.code).toBe("not_found");
    expect(e.rawMessage).toBe('no model "nope"');
    expect(e.procedure).toBe("/mimir.v1.ModelService/GetModel");
    expect(e.message).toBe('mimirsdk: ModelService/GetModel: not_found: no model "nope"');
    expect(e.retryable).toBe(false);
  });

  it("predicts and takes feedback", async () => {
    const res = await client.models.predictFields("m1", { plan: "monthly", tenure: 3 });
    expect(res.guesses[0]!.label).toBe("monthly!");
    expect(res.guesses[0]!.probability).toBeCloseTo(0.75);
    expect(await client.models.sendFeedback(res.predictionId, "yes!")).toBe(true);
    const photo = await client.models.predictPhoto("m1", new Uint8Array(8));
    expect(photo.guesses[0]!.label).toBe("photo 8");
    await expect(client.models.predict({ modelId: "m1" })).rejects.toBeInstanceOf(InvalidArgumentError);
  });

  it("creates with weights", async () => {
    const m = await client.models.create({ name: "w", architecture: "mim", weights: new Uint8Array([0, 1, 2]) });
    expect(m.description).toBe("weights 3");
  });

  it("uploads bytes, blobs, streams and files", async () => {
    expect((await client.models.upload("a", "mim", new Uint8Array(3))).description).toBe("upload u-3-3");
    expect((await client.models.upload("b", "mim", new Blob(["hello"]))).description).toBe("upload u-5-5");
    const stream = new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(new Uint8Array(4));
        c.enqueue(new Uint8Array(3));
        c.close();
      },
    });
    expect((await client.models.upload("c", "mim", stream)).description).toBe("upload u-7--1");

    const dir = mkdtempSync(join(tmpdir(), "mimir-"));
    const path = join(dir, "net.mim");
    writeFileSync(path, new Uint8Array(3_000_000));
    const m = await client.models.uploadFile(path, "mim");
    expect(m.name).toBe("net");
    expect(m.description).toBe("upload u-3000000--1");

    await expect(client.models.upload("e", "mim", new Uint8Array(0))).rejects.toThrow(/the file is empty/);
    await expect(client.models.uploadFile(join(dir, "missing.mim"), "mim")).rejects.toThrow(/ENOENT/);
  });

  it("needs an API key for uploads", async () => {
    const anon = new Client(url);
    await expect(anon.models.upload("x", "mim", new Uint8Array(3))).rejects.toBeInstanceOf(UnauthenticatedError);
  });
});

describe("chat", () => {
  it("streams", async () => {
    const pieces = await collect(client.models.chat({ modelId: "m2", messages: [userMessage("hi there")] }));
    expect(pieces.map((p) => p.text)).toEqual(["You said", ": ", "hi there", ""]);
    expect(pieces.at(-1)!.done).toBe(true);
  });

  it("collects the whole answer", async () => {
    const reply = await client.models.chatText({
      modelId: "m2",
      messages: [{ role: "user", content: "a" }, assistantMessage("b"), userMessage("c")],
    });
    expect(reply).toEqual({
      text: "You said: c",
      promptTokens: 3,
      generatedTokens: 3,
      finished: true,
      durationMicros: 42n,
    });
  });

  it("fails mid-stream with a typed error", async () => {
    const got: string[] = [];
    const err = await (async () => {
      for await (const p of client.models.chat({ modelId: "boom", messages: [userMessage("x")] })) got.push(p.text);
    })().catch((e: unknown) => e);
    expect(got).toEqual(["You said"]);
    expect(err).toBeInstanceOf(ResourceExhaustedError);
    expect((err as MimirError).rawMessage).toBe("out of tokens");
    expect((err as MimirError).procedure).toBe("/mimir.v1.PredictService/Chat");
  });

  it("stops early", async () => {
    for await (const p of client.models.chat({ modelId: "m2", messages: [userMessage("x")] })) {
      expect(p.text).toBe("You said");
      break;
    }
    expect((await client.models.get("m1")).name).toBe("churn");
  });

  it("can be aborted", async () => {
    const ac = new AbortController();
    ac.abort(new Error("stop"));
    await expect(collect(client.models.chat({ modelId: "m2", messages: [userMessage("x")] }, { signal: ac.signal })))
      .rejects.toThrow();
  });

  it("needs an API key", async () => {
    const anon = new Client(url);
    await expect(collect(anon.models.chat({ modelId: "m2", messages: [userMessage("x")] }))).rejects.toBeInstanceOf(
      UnauthenticatedError,
    );
  });
});

describe("transport", () => {
  it("lets anyone check setup but needs a key for the rest", async () => {
    const anon = new Client(url);
    await anon.auth.setupState();
    await expect(anon.models.list()).rejects.toBeInstanceOf(UnauthenticatedError);
  });

  it("sends the User-Agent and headers", async () => {
    const c = new Client(url, { apiKey: KEY, userAgent: "my-app/1.2", headers: { "X-Extra": "hello" } });
    const me = await c.auth.whoAmI();
    expect(me.user!.email).toBe("test@example.com");
    expect(me.user!.name).toBe(`my-app/1.2 mimir-server-sdk-js/${VERSION} (Node.js ${process.versions.node})`);
    expect(me.permissions).toEqual(["hello"]);
  });

  it("retries reads when the server is unavailable", async () => {
    const archs = await client.models.architectures();
    expect(archs[0]!.description).toBe("attempt 3");
    expect(await count("/mimir.v1.ModelService/ListArchitectures")).toBe(3);
  });

  it("can turn retries off", async () => {
    const c = new Client(url, { apiKey: KEY, retries: 0, headers: { "X-Test-Run": run } });
    const err = await c.models.architectures().catch((e: unknown) => e);
    expect(err).toBeInstanceOf(UnavailableError);
    expect((err as MimirError).retryable).toBe(true);
  });

  it("doesn't retry writes when the server is unavailable", async () => {
    await expect(client.models.delete("unavailable")).rejects.toBeInstanceOf(UnavailableError);
    expect(await count("/mimir.v1.ModelService/DeleteModel")).toBe(1);
  });

  it("waits out a Retry-After", async () => {
    const start = Date.now();
    const job = await client.training.start({ name: "busy", architecture: "mim", datasetId: "d1" });
    expect(job.id).toBe("j-ok");
    expect(Date.now() - start).toBeGreaterThanOrEqual(900);
    expect(await count("/mimir.v1.TrainingService/CreateJob")).toBe(2);
  });

  it("doesn't wait out a long Retry-After", async () => {
    const err = (await client.training.start({ name: "very-busy" }).catch((e: unknown) => e)) as MimirError;
    expect(err).toBeInstanceOf(ResourceExhaustedError);
    expect(err.retryAfter).toBe(120);
    expect(err.retryable).toBe(true);
    expect(await count("/mimir.v1.TrainingService/CreateJob")).toBe(1);
  });

  it("calls a refused connection unavailable", async () => {
    const c = new Client("http://127.0.0.1:9", { apiKey: "k", retries: 1, retryBackoffMs: 10 });
    await expect(c.models.list()).rejects.toBeInstanceOf(UnavailableError);
  });

  it("times out", async () => {
    const slow: typeof fetch = (_input, init) =>
      new Promise((_, reject) => {
        init?.signal?.addEventListener("abort", () => reject(init.signal!.reason));
      });
    const c = new Client(url, { apiKey: KEY, timeoutMs: 50, fetch: slow });
    await expect(c.models.list()).rejects.toBeInstanceOf(DeadlineExceededError);
  });

  it("speaks JSON too", async () => {
    const c = new Client(url, { apiKey: KEY, useJson: true });
    expect((await c.models.list())[0]!.sizeBytes).toBe(1n << 40n);
    expect((await c.models.chatText({ modelId: "m2", messages: [userMessage("j")] })).text).toBe("You said: j");
  });

  it("says when a service isn't there", async () => {
    await expect(client.teams.list()).rejects.toBeInstanceOf(UnimplementedError);
  });

  it("gives the raw Connect clients", async () => {
    const res = await client.raw.models.getModel({ id: "m1" });
    expect(res.model!.name).toBe("churn");
  });
});

describe("lists and waits", () => {
  it("pages through the audit log", async () => {
    const page = await client.audit.listPage({ pageSize: 2 });
    expect(page.items.map((e) => e.id)).toEqual(["e0", "e1"]);
    expect(page.nextPageToken).toBe("2");
    expect((await collect(client.audit.all())).map((e) => e.id)).toEqual(["e0", "e1", "e2", "e3", "e4"]);
    expect((await collect(client.audit.all({ pageSize: 3, pageToken: "1" }))).map((e) => e.id)).toEqual([
      "e1",
      "e2",
      "e3",
      "e4",
    ]);
  });

  it("waits for a training run", async () => {
    const seen: JobStatus[] = [];
    const job = await client.training.wait("j-ok", { intervalMs: 10, onProgress: (j) => seen.push(j.status) });
    expect(job.status).toBe(JobStatus.SUCCEEDED);
    expect(seen).toEqual([JobStatus.RUNNING, JobStatus.SUCCEEDED]);
    const err = (await client.training.wait("j-fail", { intervalMs: 10 }).catch((e: unknown) => e)) as JobError;
    expect(err).toBeInstanceOf(JobError);
    expect(err.job.error).toBe("out of memory");
    expect(err.message).toBe("mimirsdk: training run j-fail failed: out of memory");
  });

  it("stops waiting when aborted", async () => {
    const ac = new AbortController();
    const p = client.training.wait("j-ok", { intervalMs: 10_000, signal: ac.signal });
    setTimeout(() => ac.abort(new Error("gave up")), 20);
    await expect(p).rejects.toThrow("gave up");
  });
});

describe("data", () => {
  it("uploads datasets", async () => {
    const res = await client.datasets.uploadCSV("churn", "a,b\n1,2\n3,4\n", "b");
    expect([res.dataset!.name, res.dataset!.rows, res.dataset!.target]).toEqual(["churn", 3n, "b"]);
    expect(res.dataset!.kind).toBe(DatasetKind.TABLE);
    const zip = await client.datasets.uploadPhotos("cats", new Blob([new Uint8Array(12)]));
    expect(zip.dataset!.kind).toBe(DatasetKind.PHOTOS);
    expect(zip.dataset!.sizeBytes).toBe(12n);
  });

  it("asks documents", async () => {
    const answer = await client.documents.askText({ collectionId: "c1", messages: [userMessage("returns")] });
    expect(answer.text).toBe("About returns: yes [1].");
    expect(answer.sources.map((s) => s.documentName)).toEqual(["policy.pdf"]);
    expect(answer.finished).toBe(true);
  });

  it("downloads scoring results", async () => {
    const text = await new Response(await client.scorings.download("s1")).text();
    expect(text).toBe("plan,predicted,confidence,problem\nmonthly,yes,0.9,\n");
    const path = join(mkdtempSync(join(tmpdir(), "mimir-")), "scored.csv");
    expect(await client.scorings.downloadToFile("s1", path)).toBe(text.length);
    expect(readFileSync(path, "utf8")).toBe(text);
    await expect(client.scorings.download("nope")).rejects.toBeInstanceOf(NotFoundError);
  });
});

describe("setup", () => {
  it("checks the server address", () => {
    for (const [bad, msg] of [
      ["localhost:8080", /not a server address/],
      ["ftp://x", /must start with http/],
      ["http://", /not a server address/],
      ["http://u:p@x", /username or password/],
      ["http://x/?a=1", /query or fragment/],
      ["nonsense", /not a server address/],
    ] as const) {
      expect(() => new Client(bad), bad).toThrow(msg);
    }
    expect(() => new Client("http://x", { apiKey: "a b" })).toThrow(/spaces or line breaks/);
    const c = new Client(" https://x.example/mimir/ ");
    expect(c.baseUrl).toBe("https://x.example/mimir");
    expect(c.openaiBaseUrl).toBe("https://x.example/mimir/v1");
  });

  it("reads the environment", () => {
    const old = { ...process.env };
    try {
      delete process.env.MIMIR_URL;
      expect(() => Client.fromEnv()).toThrow(/MIMIR_URL/);
      process.env.MIMIR_URL = "http://localhost:8080";
      process.env.MIMIR_API_KEY = "mimir_x";
      expect(Client.fromEnv().baseUrl).toBe("http://localhost:8080");
    } finally {
      process.env = old;
    }
  });

  it("builds access", () => {
    const a = allModels(Role.EDITOR);
    expect(a.allModels).toBe(true);
    expect(someModels(Role.VIEWER, "m1", "m2").modelIds).toEqual(["m1", "m2"]);
  });
});
