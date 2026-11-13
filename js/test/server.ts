// Starts the Go test server (internal/testserver) the tests talk to. It
// serves the server's real Connect handlers, so the tests check the wire
// format too. Needs Go; set MIMIR_TESTSERVER to a built binary to skip the
// build.
import { execFileSync, spawn, type ChildProcess } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { createInterface } from "node:readline";
import type { TestProject } from "vitest/node";

let proc: ChildProcess | undefined;
let tmp: string | undefined;

export async function setup(project: TestProject): Promise<void> {
  let binary = process.env.MIMIR_TESTSERVER;
  if (!binary) {
    tmp = mkdtempSync(join(tmpdir(), "mimir-testserver-"));
    binary = join(tmp, process.platform === "win32" ? "testserver.exe" : "testserver");
    execFileSync("go", ["build", "-o", binary, "./internal/testserver"], {
      cwd: resolve(import.meta.dirname, "../.."),
      stdio: "inherit",
    });
  }
  proc = spawn(binary, [], { stdio: ["pipe", "pipe", "inherit"] });
  const line = await new Promise<string>((ok, fail) => {
    const rl = createInterface({ input: proc!.stdout! });
    rl.once("line", (l) => {
      rl.close();
      ok(l);
    });
    proc!.once("exit", (code) => fail(new Error(`the test server exited with ${code}`)));
  });
  if (!line.startsWith("listening on ")) throw new Error(`unexpected first line: ${line}`);
  project.provide("serverUrl", line.slice("listening on ".length));
}

export async function teardown(): Promise<void> {
  proc?.stdin?.end();
  await new Promise((ok) => (proc && proc.exitCode === null ? proc.once("exit", ok) : ok(undefined)));
  if (tmp) rmSync(tmp, { recursive: true, force: true });
}

declare module "vitest" {
  export interface ProvidedContext {
    serverUrl: string;
  }
}
