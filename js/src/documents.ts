import {
  DocumentService as DocumentRPC,
  type AskRequestSchema,
  type AskResponse,
  type Collection,
  type CreateCollectionRequestSchema,
  type Document,
  type GetCollectionResponse,
  type Passage,
  type UpdateCollectionRequestSchema,
} from "./gen/mimir/v1/document_pb.js";
import { JobStatus } from "./gen/mimir/v1/training_pb.js";
import { DocumentError } from "./errors.js";
import { ended } from "./training.js";
import type { Caller, CallOptions } from "./transport.js";
import { baseName, poll, readFile, type Init, type WaitOptions } from "./util.js";

/** A whole answer from a collection, as askText collects it. */
export interface Answer {
  text: string;
  sources: Passage[];
  /** False when the answer stopped at the most tokens it may write. */
  finished: boolean;
  promptTokens: number;
  generatedTokens: number;
  durationMicros: bigint;
}

/** Answers questions from a team's own files. A collection holds documents
 * (PDF, Word, Markdown, web pages or text); the server reads each into
 * passages in the background, and ask answers from the passages that best
 * match a question, citing them as [1], [2]. */
export class DocumentService {
  constructor(private readonly c: Caller) {}

  /** The collections the caller may see, by name. */
  async listCollections(opts?: CallOptions): Promise<Collection[]> {
    return (await this.c.unary(DocumentRPC.method.listCollections, {}, opts)).collections;
  }

  /** A collection with its documents, newest first. */
  async getCollection(id: string, opts?: CallOptions): Promise<GetCollectionResponse> {
    return this.c.unary(DocumentRPC.method.getCollection, { id }, opts);
  }

  /** Make a collection. embeddingModelId reads the documents and can't
   * change later; languageModelId writes the answers and defaults to the
   * same model. */
  async createCollection(req: Init<typeof CreateCollectionRequestSchema>, opts?: CallOptions): Promise<Collection> {
    return (await this.c.unary(DocumentRPC.method.createCollection, req, opts)).collection!;
  }

  /** Change a collection's name, language model and instructions. */
  async updateCollection(req: Init<typeof UpdateCollectionRequestSchema>, opts?: CallOptions): Promise<Collection> {
    return (await this.c.unary(DocumentRPC.method.updateCollection, req, opts)).collection!;
  }

  /** Remove a collection with its documents. */
  async deleteCollection(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(DocumentRPC.method.deleteCollection, { id }, opts);
  }

  /** Add a file's contents to a collection; name's extension (.pdf, .docx,
   * .md, .html, .txt) says how to read it. waitDocument follows it. */
  async add(collectionId: string, name: string, data: Uint8Array, opts?: CallOptions): Promise<Document> {
    return (await this.c.unary(DocumentRPC.method.addDocument, { collectionId, name, data }, opts)).document!;
  }

  /** add for a file on disk (Node.js, Deno and Bun). */
  async addFile(collectionId: string, path: string, opts?: CallOptions): Promise<Document> {
    return this.add(collectionId, baseName(path), await readFile(path), opts);
  }

  /** One document. */
  async getDocument(id: string, opts?: CallOptions): Promise<Document> {
    return (await this.c.unary(DocumentRPC.method.getDocument, { id }, opts)).document!;
  }

  /** Remove a document and its passages. One being read can't be deleted
   * until it's done. */
  async deleteDocument(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(DocumentRPC.method.deleteDocument, { id }, opts);
  }

  /** Follow a document until it is read or fails. One that fails throws
   * DocumentError, which holds the document. */
  async waitDocument(id: string, opts?: WaitOptions<Document>): Promise<Document> {
    const doc = await poll(() => this.getDocument(id, { signal: opts?.signal }), ended, opts, 1000);
    if (doc.status !== JobStatus.SUCCEEDED) throw new DocumentError(doc);
    return doc;
  }

  /** Up to limit passages that best match query, best first; 0 means 5. */
  async search(collectionId: string, query: string, limit = 0, opts?: CallOptions): Promise<Passage[]> {
    return (await this.c.unary(DocumentRPC.method.search, { collectionId, query, limit }, opts)).passages;
  }

  /** Answer the last question of a chat from a collection's documents,
   * yielding the answer as it is written. The first message carries the
   * sources the answer cites as [1], [2] and so on; the last has done set. */
  ask(req: Init<typeof AskRequestSchema>, opts?: CallOptions): AsyncGenerator<AskResponse, void, undefined> {
    return this.c.serverStream(DocumentRPC.method.ask, req, opts);
  }

  /** ask, waiting for the whole answer. */
  async askText(req: Init<typeof AskRequestSchema>, opts?: CallOptions): Promise<Answer> {
    const a: Answer = {
      text: "",
      sources: [],
      finished: false,
      promptTokens: 0,
      generatedTokens: 0,
      durationMicros: 0n,
    };
    const parts: string[] = [];
    for await (const piece of this.ask(req, opts)) {
      if (piece.sources.length > 0) a.sources = piece.sources;
      parts.push(piece.text);
      if (piece.done) {
        a.finished = piece.finished;
        a.promptTokens = piece.promptTokens;
        a.generatedTokens = piece.generatedTokens;
        a.durationMicros = piece.durationMicros;
      }
    }
    a.text = parts.join("");
    return a;
  }
}
