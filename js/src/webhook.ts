/**
 * Check and read the events mimir-server sends to webhooks.
 *
 * Each delivery is a JSON POST signed with the webhook's secret in a
 * Mimir-Signature header ("t=<unix seconds>,v1=<hex HMAC-SHA256 of
 * "<t>.<body>">"). Pass the raw body, before any JSON parsing, to parse:
 *
 *     import { parse, TRAINING_FINISHED } from "mimir-server-sdk/webhook";
 *
 *     app.post("/hooks/mimir", express.raw({ type: "*\/*" }), async (req, res) => {
 *       let event;
 *       try {
 *         event = await parse(SECRET, req.get("Mimir-Signature"), req.body);
 *       } catch {
 *         return res.sendStatus(401);
 *       }
 *       if (event.type === TRAINING_FINISHED) console.log(event.job().model_id);
 *       res.sendStatus(204);
 *     });
 *
 * The server retries a delivery for about a day until it gets a 2xx, so the
 * same event can arrive more than once: use Event.id to skip repeats. It
 * uses the Web Crypto API, so it works in Node.js 20+, Deno, Bun, Cloudflare
 * Workers and browsers.
 */

export const SIGNATURE_HEADER = "Mimir-Signature";
/** How far a delivery's signed time may be from now, in seconds. */
export const DEFAULT_TOLERANCE = 300;
/** The largest body worth reading. */
export const MAX_BODY_BYTES = 1 << 20;

export const MODEL_CREATED = "model.created";
export const MODEL_UPDATED = "model.updated";
export const MODEL_DELETED = "model.deleted";
/** Sent, at most once a day for each model, when a model gets clearly fewer
 * answers right in use than when trained. */
export const ACCURACY_DROPPED = "model.accuracy_dropped";
export const TRAINING_QUEUED = "training.queued";
export const TRAINING_FINISHED = "training.finished";
export const TRAINING_FAILED = "training.failed";
export const SCORING_FINISHED = "scoring.finished";
export const SCORING_FAILED = "scoring.failed";
export const USER_CREATED = "user.created";
export const USER_DELETED = "user.deleted";
export const TEST = "test";

/** A delivery that isn't genuine or can't be read. */
export class WebhookError extends Error {
  override name = "WebhookError";
}

export class NoSignatureError extends WebhookError {
  override name = "NoSignatureError";
  constructor() {
    super("webhook: no Mimir-Signature header");
  }
}

export class BadSignatureError extends WebhookError {
  override name = "BadSignatureError";
  constructor() {
    super("webhook: the signature doesn't match the body");
  }
}

export class ExpiredError extends WebhookError {
  override name = "ExpiredError";
  constructor() {
    super("webhook: the signature is too old or from the future");
  }
}

type Body = string | Uint8Array | ArrayBuffer;

function bytes(body: Body): Uint8Array {
  if (typeof body === "string") return new TextEncoder().encode(body);
  return body instanceof Uint8Array ? body : new Uint8Array(body);
}

async function mac(secret: string, ts: string, body: Uint8Array): Promise<Uint8Array> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, [
    "sign",
  ]);
  const prefix = enc.encode(ts + ".");
  const data = new Uint8Array(prefix.length + body.length);
  data.set(prefix);
  data.set(body, prefix.length);
  return new Uint8Array(await crypto.subtle.sign("HMAC", key, data));
}

function hex(b: Uint8Array): string {
  return Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
}

function unhex(s: string): Uint8Array | undefined {
  if (s.length % 2 !== 0 || !/^[0-9a-fA-F]*$/.test(s)) return undefined;
  const out = new Uint8Array(s.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(s.slice(i * 2, i * 2 + 2), 16);
  return out;
}

function equal(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a[i]! ^ b[i]!;
  return d === 0;
}

/** The Mimir-Signature header value for body at unix time at (now when
 * left out), as the server makes it. It is for tests of a receiver. */
export async function sign(secret: string, body: Body, at?: number): Promise<string> {
  const ts = String(Math.floor(at ?? Date.now() / 1000));
  return `t=${ts},v1=${hex(await mac(secret, ts, bytes(body)))}`;
}

/** Check a Mimir-Signature header against the raw body, allowing the signed
 * time to be up to tolerance seconds from now. Resolves for a genuine
 * delivery; rejects with NoSignatureError, BadSignatureError or
 * ExpiredError otherwise. */
export async function verify(
  secret: string,
  header: string | null | undefined,
  body: Body,
  tolerance = DEFAULT_TOLERANCE,
): Promise<void> {
  if (!header?.trim()) throw new NoSignatureError();
  if (tolerance <= 0) tolerance = DEFAULT_TOLERANCE;
  let ts = "";
  const sigs: Uint8Array[] = [];
  for (const part of header.split(",")) {
    const p = part.trim();
    const i = p.indexOf("=");
    const k = i < 0 ? p : p.slice(0, i);
    const v = i < 0 ? "" : p.slice(i + 1);
    if (k === "t") ts = v;
    else if (k === "v1") {
      const sig = unhex(v);
      if (sig) sigs.push(sig);
    }
  }
  if (!/^-?\d+$/.test(ts) || sigs.length === 0) throw new BadSignatureError();
  if (Math.abs(Date.now() / 1000 - Number(ts)) > tolerance) throw new ExpiredError();
  const want = await mac(secret, ts, bytes(body));
  if (!sigs.some((s) => equal(want, s))) throw new BadSignatureError();
}

export interface ModelEvent {
  model: { id: string; name: string; architecture: string; size_bytes: number };
  /** Who made the change: an email, or "key <name> (<email>)" for an API
   * key. Empty for a model a training run made. */
  actor: string;
}

export interface JobEvent {
  id: string;
  name: string;
  architecture: string;
  dataset: string;
  /** "queued", "running", "succeeded", "failed" or "cancelled". */
  status: string;
  epoch: number;
  epochs: number;
  accuracy: number;
  model_id: string;
  error: string;
}

export interface ScoringEvent {
  id: string;
  name: string;
  model_id: string;
  /** The model's name. */
  model: string;
  /** "succeeded", "failed" or "cancelled". */
  status: string;
  /** How many rows the run read, answered, and couldn't answer. */
  rows: number;
  done: number;
  failed: number;
  error: string;
}

export interface UserEvent {
  user: { id: string; email: string; name: string };
  actor: string;
}

export interface AccuracyEvent {
  model: { id: string; name: string; architecture: string; version_id: string };
  /** The last 7 days' answers, the feedback apps sent on them, and the share
   * of that feedback the model got right. */
  week: { answers: number; feedback: number; accuracy: number };
  /** The model's held-out score when trained. */
  accuracy: number;
}

/** One delivery's body. */
export class Event {
  constructor(
    /** The same for every retry of one event. */
    readonly id: string,
    readonly type: string,
    readonly time: Date | undefined,
    /** Depends on type; model(), accuracy(), job(), scoring() and user()
     * return it typed. */
    readonly data: Record<string, unknown>,
  ) {}

  private dataFor<T>(prefix: string): T {
    if (!this.type.startsWith(prefix)) {
      throw new WebhookError(`webhook: a ${this.type} event has no ${prefix.replace(/\.$/, "")} data`);
    }
    return this.data as T;
  }

  model(): ModelEvent {
    return this.dataFor("model.");
  }

  accuracy(): AccuracyEvent {
    return this.dataFor(ACCURACY_DROPPED);
  }

  job(): JobEvent {
    return this.dataFor("training.");
  }

  scoring(): ScoringEvent {
    return this.dataFor("scoring.");
  }

  user(): UserEvent {
    return this.dataFor("user.");
  }
}

/** Verify a delivery's signature and decode its body. */
export async function parse(
  secret: string,
  header: string | null | undefined,
  body: Body,
  tolerance = DEFAULT_TOLERANCE,
): Promise<Event> {
  const b = bytes(body);
  if (b.length > MAX_BODY_BYTES) throw new WebhookError("webhook: the body is larger than MAX_BODY_BYTES");
  await verify(secret, header, b, tolerance);
  let raw: unknown;
  try {
    raw = JSON.parse(new TextDecoder().decode(b));
  } catch (err) {
    throw new WebhookError(`webhook: decode the event: ${err instanceof Error ? err.message : String(err)}`);
  }
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    throw new WebhookError("webhook: decode the event: not a JSON object");
  }
  const r = raw as Record<string, unknown>;
  const time = typeof r.time === "string" && r.time ? new Date(r.time) : undefined;
  const data = r.data && typeof r.data === "object" && !Array.isArray(r.data) ? r.data : {};
  return new Event(
    String(r.id ?? ""),
    String(r.type ?? ""),
    time && !Number.isNaN(time.getTime()) ? time : undefined,
    data as Record<string, unknown>,
  );
}
