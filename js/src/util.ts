import type { DescMessage, MessageInitShape } from "@bufbuild/protobuf";
import type { CallOptions } from "./transport.js";

/** A request: the message, or a plain object with any of its fields. */
export type Init<S extends DescMessage> = MessageInitShape<S>;

/** One page of a paged list. */
export interface Page<T> {
  items: T[];
  /** Fetches the next page; empty on the last one. */
  nextPageToken: string;
}

/** Options for a paged list. */
export interface ListOptions extends CallOptions {
  /** How many to fetch per request; 0 lets the server choose. */
  pageSize?: number;
  /** Start from a page an earlier call returned. */
  pageToken?: string;
}

/** Walk every page fetch returns, starting from token, until a page has no
 * next token. */
export async function* paginate<T>(token: string, fetch: (token: string) => Promise<Page<T>>): AsyncGenerator<T> {
  for (;;) {
    const page = await fetch(token);
    yield* page.items;
    if (!page.nextPageToken || page.nextPageToken === token) return;
    token = page.nextPageToken;
  }
}

/** Options for the wait methods. */
export interface WaitOptions<T> {
  /** How often to look, in milliseconds; the default is 2 seconds (1 for
   * documents). */
  intervalMs?: number;
  /** Stops waiting; the wait then throws the signal's reason. */
  signal?: AbortSignal;
  /** Sees the item each time the wait looks. */
  onProgress?: (item: T) => void;
}

/** Call get every interval until done says so, and return the last value. */
export async function poll<T>(
  get: () => Promise<T>,
  done: (v: T) => boolean,
  opts: WaitOptions<T> | undefined,
  defaultInterval: number,
): Promise<T> {
  const interval = opts?.intervalMs && opts.intervalMs > 0 ? opts.intervalMs : defaultInterval;
  for (;;) {
    opts?.signal?.throwIfAborted();
    const v = await get();
    opts?.onProgress?.(v);
    if (done(v)) return v;
    await new Promise<void>((resolve, reject) => {
      const t = setTimeout(() => {
        opts?.signal?.removeEventListener("abort", onAbort);
        resolve();
      }, interval);
      const onAbort = () => {
        clearTimeout(t);
        reject(opts?.signal?.reason);
      };
      opts?.signal?.addEventListener("abort", onAbort, { once: true });
    });
  }
}

/** Every byte of a stream, in one array. */
export async function readAll(stream: ReadableStream<Uint8Array>): Promise<Uint8Array> {
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

/**
 * Import a Node.js built-in at run time. The specifier is hidden from
 * bundlers, so a browser build of an app that never calls the file helpers
 * doesn't try to bundle node:fs.
 */
export function nodeImport<T>(specifier: string): Promise<T> {
  return import(/* webpackIgnore: true */ /* @vite-ignore */ specifier) as Promise<T>;
}

/** Write a stream to a file on disk (Node.js, Deno and Bun). Returns how
 * many bytes it wrote. */
export async function writeFile(stream: ReadableStream<Uint8Array>, path: string): Promise<number> {
  const fs = await nodeImport<typeof import("node:fs")>("node:fs");
  const { Writable } = await nodeImport<typeof import("node:stream")>("node:stream");
  let n = 0;
  const counted = stream.pipeThrough(
    new TransformStream<Uint8Array, Uint8Array>({
      transform(chunk, controller) {
        n += chunk.byteLength;
        controller.enqueue(chunk);
      },
    }),
  );
  await counted.pipeTo(Writable.toWeb(fs.createWriteStream(path)) as WritableStream<Uint8Array>);
  return n;
}

/** Read a file on disk (Node.js, Deno and Bun). */
export async function readFile(path: string): Promise<Uint8Array> {
  const fs = await nodeImport<typeof import("node:fs/promises")>("node:fs/promises");
  return new Uint8Array(await fs.readFile(path));
}

/** A file's name without its folder. */
export function baseName(path: string): string {
  return path.split(/[\\/]/).pop() ?? path;
}
