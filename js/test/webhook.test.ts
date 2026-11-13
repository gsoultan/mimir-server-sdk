import { describe, expect, it } from "vitest";
import {
  BadSignatureError,
  ExpiredError,
  NoSignatureError,
  TRAINING_FINISHED,
  WebhookError,
  parse,
  sign,
  verify,
} from "../src/webhook.js";

const SECRET = "whsec_test";
const BODY = JSON.stringify({
  id: "ev1",
  type: "training.finished",
  time: "2026-11-13T06:47:47.123456789Z",
  data: { id: "j1", status: "succeeded", model_id: "m1", accuracy: 0.91 },
});

describe("webhook", () => {
  it("signs and parses", async () => {
    const ev = await parse(SECRET, await sign(SECRET, BODY), BODY);
    expect([ev.id, ev.type]).toEqual(["ev1", TRAINING_FINISHED]);
    expect(ev.time?.toISOString()).toBe("2026-11-13T06:47:47.123Z");
    expect(ev.job().model_id).toBe("m1");
    expect(() => ev.model()).toThrow(/has no model data/);
  });

  it("matches the Go SDK's signature", async () => {
    // Made by the Go SDK: webhook.Sign("whsec_vector", time.Unix(1700000000, 0), body).
    const body = new TextEncoder().encode('{"id":"ev1","type":"test"}');
    const want = "t=1700000000,v1=af13c1a596443d96473d576831bd5071fefc03a5783ea085d3653b8d2208f76e";
    expect(await sign("whsec_vector", body, 1700000000)).toBe(want);
    await verify("whsec_vector", want, body, 1e10);
  });

  it("rejects what isn't genuine", async () => {
    const now = Date.now() / 1000;
    await expect(verify(SECRET, null, BODY)).rejects.toBeInstanceOf(NoSignatureError);
    await expect(verify(SECRET, "  ", BODY)).rejects.toBeInstanceOf(NoSignatureError);
    await expect(verify("other", await sign(SECRET, BODY), BODY)).rejects.toBeInstanceOf(BadSignatureError);
    await expect(verify(SECRET, await sign(SECRET, BODY), BODY + " ")).rejects.toBeInstanceOf(BadSignatureError);
    await expect(verify(SECRET, "t=abc,v1=00", BODY)).rejects.toBeInstanceOf(BadSignatureError);
    await expect(verify(SECRET, `t=${Math.floor(now)}`, BODY)).rejects.toBeInstanceOf(BadSignatureError);
    await expect(verify(SECRET, await sign(SECRET, BODY, now - 3600), BODY)).rejects.toBeInstanceOf(ExpiredError);
    await verify(SECRET, await sign(SECRET, BODY, now - 3600), BODY, 7200);
  });

  it("takes any of several signatures", async () => {
    const [ts, v1] = (await sign(SECRET, BODY)).split(",");
    await verify(SECRET, `${ts},v1=deadbeef,${v1}`, BODY);
  });

  it("says when the body isn't JSON", async () => {
    await expect(parse(SECRET, await sign(SECRET, "nope"), "nope")).rejects.toBeInstanceOf(WebhookError);
  });
});
