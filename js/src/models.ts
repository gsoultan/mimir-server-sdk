import { create } from "@bufbuild/protobuf";
import {
  ModelService as ModelRPC,
  PredictService as PredictRPC,
  type Architecture,
  type ChatMessage,
  type ChatRequestSchema,
  type ChatResponse,
  type CreateModelRequestSchema,
  type ExplainModelResponse,
  type ExplainResponse,
  type GenerateRequestSchema,
  type GenerateResponse,
  type GenerateStreamRequestSchema,
  type GenerateStreamResponse,
  type GetDeviceModelResponse,
  type GetModelQualityResponse,
  type Model,
  type ModelVersion,
  type PredictRequestSchema,
  type PredictResponse,
  type SaveArchitectureRequestSchema,
  type UpdateModelRequestSchema,
  ChatMessageSchema,
} from "./gen/mimir/v1/model_pb.js";
import { errorFor } from "./errors.js";
import type { Caller, CallOptions } from "./transport.js";
import { baseName, nodeImport, type Init } from "./util.js";

const uploadPath = "/api/uploads";

/** A chat turn written by a person. */
export function userMessage(content: string): ChatMessage {
  return create(ChatMessageSchema, { role: "user", content });
}

/** A chat turn the model wrote earlier. */
export function assistantMessage(content: string): ChatMessage {
  return create(ChatMessageSchema, { role: "assistant", content });
}

/** A whole chat turn, as chatText collects it. */
export interface ChatReply {
  text: string;
  promptTokens: number;
  generatedTokens: number;
  /** The model ended the text itself, rather than running into the token
   * limit. */
  finished: boolean;
  durationMicros: bigint;
}

/** What a model's weights can be read from: bytes, a Blob or a stream. */
export type UploadBody = Uint8Array | ArrayBuffer | Blob | ReadableStream<Uint8Array>;

function fieldsOf(fields: Record<string, unknown>): Record<string, string> {
  return Object.fromEntries(Object.entries(fields).map(([k, v]) => [k, String(v)]));
}

/** Manages models and asks them questions. */
export class ModelService {
  constructor(private readonly c: Caller) {}

  /** Every model the caller may see, newest first. */
  async list(opts?: CallOptions): Promise<Model[]> {
    return (await this.c.unary(ModelRPC.method.listModels, {}, opts)).models;
  }

  /** One model. */
  async get(id: string, opts?: CallOptions): Promise<Model> {
    return (await this.c.unary(ModelRPC.method.getModel, { id }, opts)).model!;
  }

  /** The model types the server can build and run. */
  async architectures(opts?: CallOptions): Promise<Architecture[]> {
    return (await this.c.unary(ModelRPC.method.listArchitectures, {}, opts)).architectures;
  }

  /** Store a model from its weights held in memory (weights), or from a
   * file sent beforehand (upload). For a file, upload is simpler. */
  async create(req: Init<typeof CreateModelRequestSchema>, opts?: CallOptions): Promise<Model> {
    return (await this.c.unary(ModelRPC.method.createModel, req, opts)).model!;
  }

  /**
   * Store a model whose weights are `data`: a Mimir Model (.mim) file, or
   * an ONNX or GGUF file for the "mim" and language-model architectures,
   * which the server converts. A stream is sent as it is read, so it can be
   * larger than memory; the server's -max-model-mb caps it. The upload is
   * bounded by opts.signal, not by the client's timeout.
   */
  async upload(name: string, architecture: string, data: UploadBody, opts?: CallOptions): Promise<Model> {
    const body = data instanceof Uint8Array ? new Blob([data as Uint8Array<ArrayBuffer>]) : data;
    const out = (await this.c.upload(uploadPath, body as BodyInit, opts)) as { upload?: unknown } | null;
    const upload = out && typeof out.upload === "string" ? out.upload : "";
    if (!upload) {
      throw errorFor({
        code: "internal",
        message: `the server's answer has no upload id: ${JSON.stringify(out)}`,
        procedure: uploadPath,
      });
    }
    return this.create({ name, architecture, upload }, opts);
  }

  /** upload from a file on disk (Node.js, Deno and Bun), streamed. An empty
   * name uses the file's name without its extension. */
  async uploadFile(path: string, architecture: string, name = "", opts?: CallOptions): Promise<Model> {
    const fs = await nodeImport<typeof import("node:fs")>("node:fs");
    const { Readable } = await nodeImport<typeof import("node:stream")>("node:stream");
    if (!name) name = baseName(path).replace(/\.[^.]*$/, "");
    await fs.promises.access(path, fs.constants.R_OK);
    const stream = Readable.toWeb(fs.createReadStream(path)) as ReadableStream<Uint8Array>;
    return this.upload(name, architecture, stream, opts);
  }

  /** Describe a model type written in someone's own code and run on
   * workers, or change how one already saved is described. */
  async saveArchitecture(req: Init<typeof SaveArchitectureRequestSchema>, opts?: CallOptions): Promise<Architecture> {
    return (await this.c.unary(ModelRPC.method.saveArchitecture, req, opts)).architecture!;
  }

  /** Remove a described model type that no model uses. */
  async deleteArchitecture(name: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(ModelRPC.method.deleteArchitecture, { name }, opts);
  }

  /** Rename a model, change its description or language settings, or let it
   * run on people's devices. */
  async update(req: Init<typeof UpdateModelRequestSchema>, opts?: CallOptions): Promise<Model> {
    return (await this.c.unary(ModelRPC.method.updateModel, req, opts)).model!;
  }

  /** Remove a model and its weights. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(ModelRPC.method.deleteModel, { id }, opts);
  }

  /** Pick the worker that answers a model, or "" for automatic. */
  async setWorker(id: string, workerId: string, opts?: CallOptions): Promise<Model> {
    return (await this.c.unary(ModelRPC.method.setModelWorker, { id, workerId }, opts)).model!;
  }

  /** A model that may run on people's devices, with its stored weights. */
  async download(id: string, opts?: CallOptions): Promise<GetDeviceModelResponse> {
    return this.c.unary(ModelRPC.method.getDeviceModel, { id }, opts);
  }

  /** A model's stored versions, newest first. The live one, which answers
   * predictions, has live set. */
  async versions(modelId: string, opts?: CallOptions): Promise<ModelVersion[]> {
    return (await this.c.unary(ModelRPC.method.listModelVersions, { modelId }, opts)).versions;
  }

  /** Make one of a model's versions the live one, to roll back to an earlier
   * version or forward to a newer one. */
  async useVersion(modelId: string, versionId: string, opts?: CallOptions): Promise<Model> {
    return (await this.c.unary(ModelRPC.method.useModelVersion, { modelId, versionId }, opts)).model!;
  }

  /** How a model does in use: its answers and the feedback on them for each
   * of the last days (30 when days is 0, at most 365), the last 7 days'
   * accuracy by that feedback, and whether it has dropped well below the
   * model's score when trained. */
  async quality(modelId: string, days = 0, opts?: CallOptions): Promise<GetModelQualityResponse> {
    return this.c.unary(ModelRPC.method.getModelQuality, { modelId, days }, opts);
  }

  /** Run one example through a model: a tensor, a table row (fields) or a
   * photo, depending on what the model reads. */
  async predict(req: Init<typeof PredictRequestSchema>, opts?: CallOptions): Promise<PredictResponse> {
    return this.c.unary(PredictRPC.method.predict, req, opts);
  }

  /** Ask a model taught from a table about one row, given by column name. */
  async predictFields(modelId: string, fields: Record<string, unknown>, opts?: CallOptions): Promise<PredictResponse> {
    return this.predict({ modelId, fields: fieldsOf(fields) }, opts);
  }

  /** Ask a model that looks at photos about one JPG, PNG or GIF. */
  async predictPhoto(modelId: string, photo: Uint8Array, opts?: CallOptions): Promise<PredictResponse> {
    return this.predict({ modelId, photo }, opts);
  }

  /** Tell the server what a picking model's answer should have been:
   * predictionId is PredictResponse.predictionId, label the right answer.
   * Resolves to whether the model got it right. Answers are kept for
   * feedback for 30 days; after that it throws NotFoundError. */
  async sendFeedback(predictionId: string, label: string, opts?: CallOptions): Promise<boolean> {
    return (await this.c.unary(PredictRPC.method.sendFeedback, { predictionId, label }, opts)).correct;
  }

  /** sendFeedback for a model that answers with a number. The answer counts
   * as right within 10% of value, or 0.1 of it when value is 0. */
  async sendFeedbackValue(predictionId: string, value: number, opts?: CallOptions): Promise<boolean> {
    return (await this.c.unary(PredictRPC.method.sendFeedback, { predictionId, value }, opts)).correct;
  }

  /** Why a model taught on a table gave its answer for one row: each
   * column's effect on it, against a typical row. For a model that picks,
   * label names the answer to explain (empty for the one it gave). The
   * effects add up to value minus typical. */
  async explain(
    modelId: string,
    fields: Record<string, unknown>,
    label = "",
    opts?: CallOptions,
  ): Promise<ExplainResponse> {
    return this.c.unary(PredictRPC.method.explain, { modelId, fields: fieldsOf(fields), label }, opts);
  }

  /** Which columns matter most to a model taught on a table. */
  async explainModel(modelId: string, opts?: CallOptions): Promise<ExplainModelResponse> {
    return this.c.unary(PredictRPC.method.explainModel, { modelId }, opts);
  }

  /** Continue a prompt with a language model and return the whole text at
   * once. */
  async generate(req: Init<typeof GenerateRequestSchema>, opts?: CallOptions): Promise<GenerateResponse> {
    return this.c.unary(PredictRPC.method.generate, req, opts);
  }

  /** generate, yielding the text as the model writes it. The last piece has
   * done set and the token counts. */
  generateStream(
    req: Init<typeof GenerateStreamRequestSchema>,
    opts?: CallOptions,
  ): AsyncGenerator<GenerateStreamResponse, void, undefined> {
    return this.c.serverStream(PredictRPC.method.generateStream, req, opts);
  }

  /**
   * Write a language model's next turn in a chat, yielding the text as the
   * model writes it. The last piece has done set and the token counts.
   *
   *     for await (const piece of client.models.chat({ modelId, messages: [userMessage("Hello!")] })) {
   *       process.stdout.write(piece.text);
   *     }
   *
   * Leaving the loop early stops the model.
   */
  chat(req: Init<typeof ChatRequestSchema>, opts?: CallOptions): AsyncGenerator<ChatResponse, void, undefined> {
    return this.c.serverStream(PredictRPC.method.chat, req, opts);
  }

  /** chat, waiting for the whole answer. */
  async chatText(req: Init<typeof ChatRequestSchema>, opts?: CallOptions): Promise<ChatReply> {
    const reply: ChatReply = { text: "", promptTokens: 0, generatedTokens: 0, finished: false, durationMicros: 0n };
    const parts: string[] = [];
    for await (const piece of this.chat(req, opts)) {
      parts.push(piece.text);
      if (piece.done) {
        reply.promptTokens = piece.promptTokens;
        reply.generatedTokens = piece.generatedTokens;
        reply.finished = piece.finished;
        reply.durationMicros = piece.durationMicros;
      }
    }
    reply.text = parts.join("");
    return reply;
  }
}
