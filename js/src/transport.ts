import type {
  DescMessage,
  DescMethodServerStreaming,
  DescMethodUnary,
  MessageInitShape,
  MessageShape,
} from "@bufbuild/protobuf";
import { MethodOptions_IdempotencyLevel } from "@bufbuild/protobuf/wkt";
import { ConnectError, Code as ConnectCode, type Interceptor, type Transport } from "@connectrpc/connect";
import { createAsyncIterable } from "@connectrpc/connect/protocol";
import { createConnectTransport } from "@connectrpc/connect-web";
import { codeFromHTTP, errorFor, MimirError, parseCode, retryAfterOf, wrapError } from "./errors.js";
import { VERSION } from "./version.js";

export const DEFAULT_TIMEOUT_MS = 60_000;
export const DEFAULT_RETRIES = 3;
export const DEFAULT_RETRY_BACKOFF_MS = 250;
export const DEFAULT_MAX_RETRY_WAIT_MS = 30_000;

/** How a Client talks to the server. */
export interface ClientOptions {
  /** An API key (mimir_...), sent as "Authorization: Bearer". */
  apiKey?: string;
  /**
   * Bounds each call that returns one response, retries included, in
   * milliseconds; 0 means no bound. Streamed calls (chat, generateStream,
   * documents.ask) are bounded only by their signal. The default is 60
   * seconds.
   */
  timeoutMs?: number;
  /** How many times a failed call may be tried again; 0 turns retries off.
   * The default is 3. */
  retries?: number;
  /** The wait before the first retry; each later retry waits twice as long,
   * with jitter, up to maxRetryWaitMs. The default is 250 ms. */
  retryBackoffMs?: number;
  /** A Retry-After from the server replaces the backoff, and a call whose
   * Retry-After is longer than this is not retried. The default is 30
   * seconds. */
  maxRetryWaitMs?: number;
  /** Put ahead of the SDK's own User-Agent, like "my-app/1.2". Browsers
   * don't let pages set User-Agent, so there it is sent as
   * X-User-Agent instead. */
  userAgent?: string;
  /** Headers to add to every request, such as one a proxy in front of the
   * server needs. */
  headers?: Record<string, string>;
  /** Send requests through this fetch instead of the global one. */
  fetch?: typeof globalThis.fetch;
  /** More Connect interceptors, run after the SDK's own. */
  interceptors?: Interceptor[];
  /** Send JSON instead of binary protobuf, which is easier to read in a
   * browser's network tab. */
  useJson?: boolean;
}

/** Per-call options: an AbortSignal to stop the call, a timeout that
 * replaces the client's, and headers for this call only. */
export interface CallOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
  headers?: Record<string, string>;
}

interface Config {
  apiKey: string;
  timeoutMs: number;
  retries: number;
  backoffMs: number;
  maxRetryWaitMs: number;
  userAgent: string;
  headers: Record<string, string>;
  fetch: typeof globalThis.fetch;
}

const inBrowser = typeof (globalThis as { document?: unknown }).document !== "undefined";

function procedureOf(method: { parent: { typeName: string }; name: string }): string {
  return `/${method.parent.typeName}/${method.name}`;
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(signal.reason);
      return;
    }
    const t = setTimeout(() => {
      signal?.removeEventListener("abort", onAbort);
      resolve();
    }, ms);
    const onAbort = () => {
      clearTimeout(t);
      reject(signal?.reason);
    };
    signal?.addEventListener("abort", onAbort, { once: true });
  });
}

/** The SDK's Connect transport, with sign-in, retries and timeouts, and
 * plain HTTP for the uploads and downloads next to the RPCs. */
export class Caller {
  readonly transport: Transport;
  private readonly cfg: Config;

  constructor(
    readonly baseUrl: string,
    opts: ClientOptions,
  ) {
    const apiKey = opts.apiKey ?? "";
    if (/[\r\n ]/.test(apiKey)) {
      throw new Error("mimirsdk: the API key has spaces or line breaks in it");
    }
    let ua = `mimir-server-sdk-js/${VERSION}`;
    const proc = (globalThis as { process?: { versions?: { node?: string } } }).process;
    if (proc?.versions?.node) ua += ` (Node.js ${proc.versions.node})`;
    if (opts.userAgent) ua = `${opts.userAgent} ${ua}`;
    const fetchFn = opts.fetch ?? globalThis.fetch.bind(globalThis);
    this.cfg = {
      apiKey,
      timeoutMs: Math.max(opts.timeoutMs ?? DEFAULT_TIMEOUT_MS, 0),
      retries: Math.max(opts.retries ?? DEFAULT_RETRIES, 0),
      backoffMs: opts.retryBackoffMs && opts.retryBackoffMs > 0 ? opts.retryBackoffMs : DEFAULT_RETRY_BACKOFF_MS,
      maxRetryWaitMs:
        opts.maxRetryWaitMs && opts.maxRetryWaitMs > 0 ? opts.maxRetryWaitMs : DEFAULT_MAX_RETRY_WAIT_MS,
      userAgent: ua,
      headers: { ...(opts.headers ?? {}) },
      fetch: fetchFn,
    };
    this.transport = createConnectTransport({
      baseUrl,
      useBinaryFormat: !opts.useJson,
      fetch: fetchFn,
      interceptors: [this.interceptor(), ...(opts.interceptors ?? [])],
    });
  }

  /** The headers every request carries. */
  headers(extra?: Record<string, string>): Headers {
    const h = new Headers(this.cfg.headers);
    h.set(inBrowser ? "X-User-Agent" : "User-Agent", this.cfg.userAgent);
    if (this.cfg.apiKey) h.set("Authorization", `Bearer ${this.cfg.apiKey}`);
    for (const [k, v] of Object.entries(extra ?? {})) h.set(k, v);
    return h;
  }

  private interceptor(): Interceptor {
    return (next) => async (req) => {
      for (const [k, v] of this.headers()) {
        if (!req.header.has(k)) req.header.set(k, v);
      }
      if (req.stream) {
        try {
          return await next(req);
        } catch (err) {
          throw unreachable(err);
        }
      }
      const level = req.method.idempotency;
      const retrySafe =
        level === MethodOptions_IdempotencyLevel.NO_SIDE_EFFECTS ||
        level === MethodOptions_IdempotencyLevel.IDEMPOTENT;
      for (let attempt = 0; ; attempt++) {
        try {
          return await next(req);
        } catch (caught) {
          const err = unreachable(caught);
          if (attempt >= this.cfg.retries || req.signal.aborted) throw err;
          const wait = this.retryWait(err, retrySafe, attempt);
          if (wait === undefined) throw err;
          try {
            await sleep(wait, req.signal);
          } catch {
            throw err;
          }
        }
      }
    };
  }

  /**
   * How long to wait before trying a failed call again, or undefined to
   * give up. A Retry-After means the server refused the call before doing
   * anything, so any call may be retried after it. An unavailable server
   * may have done the work before the reply was lost, so only calls without
   * side effects are retried then.
   */
  private retryWait(err: unknown, retrySafe: boolean, attempt: number): number | undefined {
    if (!(err instanceof ConnectError)) return undefined;
    const ra = retryAfterOf(err.metadata) * 1000;
    if (ra > 0) return ra <= this.cfg.maxRetryWaitMs ? ra : undefined;
    if (err.code !== ConnectCode.Unavailable || !retrySafe) return undefined;
    const d = Math.min(this.cfg.backoffMs * 2 ** attempt, this.cfg.maxRetryWaitMs);
    // Full jitter in the upper half, so many clients don't retry at once.
    return d / 2 + Math.random() * (d / 2);
  }

  async unary<I extends DescMessage, O extends DescMessage>(
    method: DescMethodUnary<I, O>,
    input: MessageInitShape<I>,
    opts?: CallOptions,
  ): Promise<MessageShape<O>> {
    const timeout = opts?.timeoutMs ?? this.cfg.timeoutMs;
    try {
      const res = await this.transport.unary(
        method,
        opts?.signal,
        timeout > 0 ? timeout : undefined,
        opts?.headers,
        input,
      );
      return res.message;
    } catch (err) {
      throw wrapError(procedureOf(method), err);
    }
  }

  /** Yield each message of a server stream. Leaving the loop early stops
   * the stream, which stops the server's work. */
  async *serverStream<I extends DescMessage, O extends DescMessage>(
    method: DescMethodServerStreaming<I, O>,
    input: MessageInitShape<I>,
    opts?: CallOptions,
  ): AsyncGenerator<MessageShape<O>, void, undefined> {
    const stop = new AbortController();
    const onAbort = () => stop.abort(opts?.signal?.reason);
    if (opts?.signal?.aborted) onAbort();
    opts?.signal?.addEventListener("abort", onAbort, { once: true });
    try {
      const timeout = opts?.timeoutMs;
      const res = await this.transport.stream(
        method,
        stop.signal,
        timeout && timeout > 0 ? timeout : undefined,
        opts?.headers,
        createAsyncIterable([input]),
      );
      for await (const msg of res.message) {
        yield msg;
      }
    } catch (err) {
      throw wrapError(procedureOf(method), err);
    } finally {
      opts?.signal?.removeEventListener("abort", onAbort);
      stop.abort();
    }
  }

  /** POST a body to a plain HTTP endpoint and read its JSON answer. */
  async upload(path: string, body: BodyInit, opts?: CallOptions): Promise<unknown> {
    const headers = this.headers(opts?.headers);
    headers.set("Content-Type", "application/octet-stream");
    const init: RequestInit & { duplex?: "half" } = { method: "POST", body, headers, signal: opts?.signal };
    if (typeof ReadableStream !== "undefined" && body instanceof ReadableStream) init.duplex = "half";
    const res = await this.fetch(path, init);
    const text = await res.text();
    if (res.status !== 200) throw httpError(res.status, text, path);
    try {
      return JSON.parse(text);
    } catch {
      throw errorFor({ code: "internal", message: `the server's answer isn't JSON: ${text.slice(0, 200)}`, procedure: path });
    }
  }

  /** GET a file from a plain HTTP endpoint, as a stream. */
  async download(path: string, opts?: CallOptions): Promise<ReadableStream<Uint8Array>> {
    const res = await this.fetch(path, { method: "GET", headers: this.headers(opts?.headers), signal: opts?.signal });
    if (res.status !== 200) throw httpError(res.status, await res.text(), path);
    if (!res.body) return new Blob([]).stream();
    return res.body;
  }

  private async fetch(path: string, init: RequestInit): Promise<Response> {
    try {
      return await this.cfg.fetch(this.baseUrl + path, init);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") throw err;
      throw errorFor({
        code: "unavailable",
        message: err instanceof Error ? err.message : String(err),
        procedure: path,
        cause: err,
      });
    }
  }
}

/** A request fetch couldn't send at all (connection refused, DNS, TLS)
 * becomes Unavailable, as connect-go calls it, so reads are retried. */
function unreachable(err: unknown): unknown {
  const ce = err instanceof ConnectError ? err : undefined;
  const cause = ce ? ce.cause : err;
  if ((ce === undefined || ce.code === ConnectCode.Unknown) && cause instanceof TypeError) {
    return new ConnectError(cause.message, ConnectCode.Unavailable, undefined, undefined, cause);
  }
  return err;
}

/** Read the Connect-shaped error ({"code": ..., "message": ...}) the server
 * answers a failed upload or download with. */
function httpError(status: number, text: string, procedure: string): MimirError {
  let code = undefined;
  let message = "";
  try {
    const body = JSON.parse(text) as { code?: unknown; message?: unknown };
    code = parseCode(body.code);
    message = typeof body.message === "string" ? body.message : "";
  } catch {
    // Not Connect-shaped: a proxy's answer, say.
  }
  return errorFor({ code: code ?? codeFromHTTP(status), message: message || text.trim().slice(0, 500), procedure });
}
