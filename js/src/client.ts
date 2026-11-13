import { createClient, type Client as ConnectClient } from "@connectrpc/connect";
import { ApiKeyService, AuditService, AuthService as AuthRPC, UserService as UserRPC } from "./gen/mimir/v1/access_pb.js";
import { BenchmarkService as BenchmarkRPC } from "./gen/mimir/v1/benchmark_pb.js";
import { DocumentService as DocumentRPC } from "./gen/mimir/v1/document_pb.js";
import { ModelService as ModelRPC, PredictService } from "./gen/mimir/v1/model_pb.js";
import { ScoringService as ScoringRPC } from "./gen/mimir/v1/scoring_pb.js";
import { SettingsService as SettingsRPC } from "./gen/mimir/v1/settings_pb.js";
import { SignInService as SignInRPC } from "./gen/mimir/v1/signin_pb.js";
import { TeamService as TeamRPC } from "./gen/mimir/v1/team_pb.js";
import { TemplateService as TemplateRPC } from "./gen/mimir/v1/template_pb.js";
import { DatasetService as DatasetRPC, TrainingService as TrainingRPC } from "./gen/mimir/v1/training_pb.js";
import { WebhookService as WebhookRPC } from "./gen/mimir/v1/webhook_pb.js";
import { WorkerService as WorkerRPC } from "./gen/mimir/v1/worker_pb.js";
import { APIKeyService, AuditService as Audit, AuthService, SignInService, TeamService, UserService } from "./access.js";
import { SettingsService, TemplateService, WebhookService, WorkerService } from "./admin.js";
import { BenchmarkService } from "./benchmarks.js";
import { DocumentService } from "./documents.js";
import { ModelService } from "./models.js";
import { ScoringService } from "./scorings.js";
import { DatasetService, TrainingService } from "./training.js";
import { Caller, type ClientOptions } from "./transport.js";

/** Environment variables Client.fromEnv reads. */
export const ENV_URL = "MIMIR_URL";
export const ENV_API_KEY = "MIMIR_API_KEY";

/** The generated Connect clients for every service. They share the
 * client's API key, retries and headers, but throw ConnectError rather than
 * MimirError, and have no default timeout. */
export interface RawClients {
  auth: ConnectClient<typeof AuthRPC>;
  users: ConnectClient<typeof UserRPC>;
  apiKeys: ConnectClient<typeof ApiKeyService>;
  audit: ConnectClient<typeof AuditService>;
  teams: ConnectClient<typeof TeamRPC>;
  models: ConnectClient<typeof ModelRPC>;
  predict: ConnectClient<typeof PredictService>;
  datasets: ConnectClient<typeof DatasetRPC>;
  training: ConnectClient<typeof TrainingRPC>;
  webhooks: ConnectClient<typeof WebhookRPC>;
  workers: ConnectClient<typeof WorkerRPC>;
  settings: ConnectClient<typeof SettingsRPC>;
  templates: ConnectClient<typeof TemplateRPC>;
  benchmarks: ConnectClient<typeof BenchmarkRPC>;
  scorings: ConnectClient<typeof ScoringRPC>;
  documents: ConnectClient<typeof DocumentRPC>;
  signIn: ConnectClient<typeof SignInRPC>;
}

/** Talks to one mimir-server. Make one and share it. */
export class Client {
  readonly baseUrl: string;
  readonly auth: AuthService;
  readonly apiKeys: APIKeyService;
  readonly users: UserService;
  readonly teams: TeamService;
  readonly audit: Audit;
  readonly models: ModelService;
  readonly datasets: DatasetService;
  readonly training: TrainingService;
  readonly webhooks: WebhookService;
  readonly workers: WorkerService;
  readonly settings: SettingsService;
  readonly templates: TemplateService;
  readonly benchmarks: BenchmarkService;
  readonly scorings: ScoringService;
  readonly documents: DocumentService;
  readonly signIn: SignInService;
  private readonly caller: Caller;
  private rawClients?: RawClients;

  /** A client for the server at baseUrl, such as
   * "https://mimir.example.com" or "http://localhost:8080". */
  constructor(baseUrl: string, opts: ClientOptions = {}) {
    this.baseUrl = parseBaseUrl(baseUrl);
    const c = new Caller(this.baseUrl, opts);
    this.caller = c;
    this.auth = new AuthService(c);
    this.apiKeys = new APIKeyService(c);
    this.users = new UserService(c);
    this.teams = new TeamService(c);
    this.audit = new Audit(c);
    this.models = new ModelService(c);
    this.datasets = new DatasetService(c);
    this.training = new TrainingService(c);
    this.webhooks = new WebhookService(c);
    this.workers = new WorkerService(c);
    this.settings = new SettingsService(c);
    this.templates = new TemplateService(c);
    this.benchmarks = new BenchmarkService(c);
    this.scorings = new ScoringService(c);
    this.documents = new DocumentService(c);
    this.signIn = new SignInService(c);
  }

  /** A client for the server at $MIMIR_URL with the API key in
   * $MIMIR_API_KEY (Node.js, Deno and Bun). Options win over the
   * environment. */
  static fromEnv(opts: ClientOptions = {}): Client {
    const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env ?? {};
    const base = env[ENV_URL];
    if (!base) throw new Error(`mimirsdk: set ${ENV_URL} to the server's address, like http://localhost:8080`);
    const key = env[ENV_API_KEY];
    return new Client(base, key ? { apiKey: key, ...opts } : opts);
  }

  /** Where the server's OpenAI-compatible API lives (/v1/chat/completions,
   * /v1/completions, /v1/embeddings, /v1/models). Point an OpenAI client
   * library at it with a mimir API key to chat with language models. */
  get openaiBaseUrl(): string {
    return this.baseUrl + "/v1";
  }

  /** The generated Connect clients for every service, for calls the
   * services here don't wrap. */
  get raw(): RawClients {
    const t = this.caller.transport;
    this.rawClients ??= {
      auth: createClient(AuthRPC, t),
      users: createClient(UserRPC, t),
      apiKeys: createClient(ApiKeyService, t),
      audit: createClient(AuditService, t),
      teams: createClient(TeamRPC, t),
      models: createClient(ModelRPC, t),
      predict: createClient(PredictService, t),
      datasets: createClient(DatasetRPC, t),
      training: createClient(TrainingRPC, t),
      webhooks: createClient(WebhookRPC, t),
      workers: createClient(WorkerRPC, t),
      settings: createClient(SettingsRPC, t),
      templates: createClient(TemplateRPC, t),
      benchmarks: createClient(BenchmarkRPC, t),
      scorings: createClient(ScoringRPC, t),
      documents: createClient(DocumentRPC, t),
      signIn: createClient(SignInRPC, t),
    };
    return this.rawClients;
  }
}

function parseBaseUrl(raw: string): string {
  raw = raw.trim();
  let u: URL;
  try {
    u = new URL(raw);
  } catch {
    throw new Error(`mimirsdk: ${JSON.stringify(raw)} is not a server address; use one like https://mimir.example.com`);
  }
  if (u.protocol !== "http:" && u.protocol !== "https:") {
    if (!u.host) {
      throw new Error(
        `mimirsdk: ${JSON.stringify(raw)} is not a server address; use one like https://mimir.example.com`,
      );
    }
    throw new Error(`mimirsdk: the server address must start with http:// or https://, not ${u.protocol}//`);
  }
  if (u.username || u.password) {
    throw new Error("mimirsdk: don't put a username or password in the server address; use apiKey");
  }
  if (u.search || u.hash || raw.includes("?") || raw.includes("#")) {
    throw new Error("mimirsdk: the server address can't have a query or fragment");
  }
  return raw.replace(/\/+$/, "");
}
