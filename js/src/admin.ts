import {
  SettingsService as SettingsRPC,
  type EmailAlertsSchema,
  type GetDatabaseInfoResponse,
  type GetSettingsResponse,
  type GetUsageResponse,
  type Limits,
  type LimitsSchema,
  type Retention,
  type RetentionSchema,
  type Security,
  type SecuritySchema,
  type TelegramAlertsSchema,
  type Training,
  type UpdateAlertsResponse,
  type UpdateTrainingRequestSchema,
} from "./gen/mimir/v1/settings_pb.js";
import { TemplateService as TemplateRPC, type Template, type TemplateCategory } from "./gen/mimir/v1/template_pb.js";
import {
  WebhookService as WebhookRPC,
  type CreateWebhookRequestSchema,
  type CreateWebhookResponse,
  type Delivery,
  type UpdateWebhookRequestSchema,
  type Webhook,
} from "./gen/mimir/v1/webhook_pb.js";
import {
  WorkerService as WorkerRPC,
  type CloudGpu,
  type CreateWorkerResponse,
  type GetCloudGpuResponse,
  type GetWorkerResponse,
  type UpdateCloudGpuRequestSchema,
  type Worker,
} from "./gen/mimir/v1/worker_pb.js";
import type { Caller, CallOptions } from "./transport.js";
import { paginate, writeFile, type Init, type ListOptions, type Page } from "./util.js";

/** What a worker may be told to take, for WorkerService.setTasks. */
export const WorkerTasks = {
  /** Training runs and predictions. */
  All: "all",
  /** Training runs only. */
  Train: "train",
  /** Predictions only. */
  Serve: "serve",
} as const;

/** Alert channels, for SettingsService.sendTestAlert. */
export const AlertChannel = {
  Email: "email",
  Telegram: "telegram",
} as const;

/** Manages the addresses the server tells about changes. Check deliveries
 * on the receiving end with mimir-server-sdk/webhook. */
export class WebhookService {
  constructor(private readonly c: Caller) {}

  /** The caller's team's webhooks. */
  async list(opts?: CallOptions): Promise<Webhook[]> {
    return (await this.c.unary(WebhookRPC.method.listWebhooks, {}, opts)).webhooks;
  }

  /** Every event a webhook can subscribe to. */
  async eventTypes(opts?: CallOptions): Promise<string[]> {
    return (await this.c.unary(WebhookRPC.method.listWebhooks, {}, opts)).eventTypes;
  }

  /** Add a webhook. Its signing secret is in the response only this once:
   * give it to verify on the receiving end. */
  async create(req: Init<typeof CreateWebhookRequestSchema>, opts?: CallOptions): Promise<CreateWebhookResponse> {
    return this.c.unary(WebhookRPC.method.createWebhook, req, opts);
  }

  /** Change a webhook's name, address or events, or turn it off. */
  async update(req: Init<typeof UpdateWebhookRequestSchema>, opts?: CallOptions): Promise<Webhook> {
    return (await this.c.unary(WebhookRPC.method.updateWebhook, req, opts)).webhook!;
  }

  /** Remove a webhook. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(WebhookRPC.method.deleteWebhook, { id }, opts);
  }

  /** Send a "test" event to a webhook now. */
  async sendTest(id: string, opts?: CallOptions): Promise<Delivery> {
    return (await this.c.unary(WebhookRPC.method.sendTestEvent, { id }, opts)).delivery!;
  }

  /** Send a past delivery again, now. */
  async redeliver(deliveryId: string, opts?: CallOptions): Promise<Delivery> {
    return (await this.c.unary(WebhookRPC.method.redeliver, { id: deliveryId }, opts)).delivery!;
  }

  /** One page of a webhook's deliveries, newest first. */
  async deliveriesPage(webhookId: string, opts: ListOptions = {}): Promise<Page<Delivery>> {
    const { pageSize = 0, pageToken = "", ...call } = opts;
    const res = await this.c.unary(WebhookRPC.method.listDeliveries, { webhookId, pageSize, pageToken }, call);
    return { items: res.deliveries, nextPageToken: res.nextPageToken };
  }

  /** Every delivery of a webhook, newest first, fetching pages as the loop
   * needs them. */
  deliveries(webhookId: string, opts: ListOptions = {}): AsyncGenerator<Delivery> {
    return paginate(opts.pageToken ?? "", (pageToken) => this.deliveriesPage(webhookId, { ...opts, pageToken }));
  }
}

/** Reads the machines that answer and teach models for the server. */
export class WorkerService {
  constructor(private readonly c: Caller) {}

  /** Every worker. */
  async list(opts?: CallOptions): Promise<Worker[]> {
    return (await this.c.unary(WorkerRPC.method.listWorkers, {}, opts)).workers;
  }

  /** A worker with its last hours of samples and its tasks; 0 lets the
   * server choose. */
  async get(id: string, hours = 0, opts?: CallOptions): Promise<GetWorkerResponse> {
    return this.c.unary(WorkerRPC.method.getWorker, { id, hours }, opts);
  }

  /** The workers a model or training run may be placed on. */
  async choices(opts?: CallOptions): Promise<Worker[]> {
    return (await this.c.unary(WorkerRPC.method.listWorkerChoices, {}, opts)).workers;
  }

  /** Add a worker and return the token it joins with, shown only once. */
  async create(name: string, opts?: CallOptions): Promise<CreateWorkerResponse> {
    return this.c.unary(WorkerRPC.method.createWorker, { name }, opts);
  }

  /** Tell a worker what to take: WorkerTasks.All, Train or Serve, or "" to
   * leave it to the worker's own -tasks flag. */
  async setTasks(id: string, tasks: string, opts?: CallOptions): Promise<Worker> {
    return (await this.c.unary(WorkerRPC.method.setWorkerTasks, { id, tasks }, opts)).worker!;
  }

  /** How training runs rent a GPU when they wait, whether one is running
   * now, and which providers and GPUs can be picked. */
  async cloudGPU(opts?: CallOptions): Promise<GetCloudGpuResponse> {
    return this.c.unary(WorkerRPC.method.getCloudGpu, {}, opts);
  }

  /** Set up renting a GPU for waiting training runs, change it, or turn it
   * off. */
  async updateCloudGPU(req: Init<typeof UpdateCloudGpuRequestSchema>, opts?: CallOptions): Promise<CloudGpu> {
    return (await this.c.unary(WorkerRPC.method.updateCloudGpu, req, opts)).cloudGpu!;
  }

  /** Stop the rented GPU now. Runs on it go back in the queue. */
  async stopCloudGPU(opts?: CallOptions): Promise<CloudGpu> {
    return (await this.c.unary(WorkerRPC.method.stopCloudGpu, {}, opts)).cloudGpu!;
  }

  /** Make a new token for a worker, shown only once. The old token stops
   * working at once. */
  async replaceToken(id: string, opts?: CallOptions): Promise<string> {
    return (await this.c.unary(WorkerRPC.method.replaceWorkerToken, { id }, opts)).token;
  }

  /** Remove a worker. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(WorkerRPC.method.deleteWorker, { id }, opts);
  }
}

/** Reads and changes server-wide settings. It needs an owner, except usage,
 * which shows each caller their own. */
export class SettingsService {
  constructor(private readonly c: Caller) {}

  /** The alert, retention, security, limit and training settings. */
  async get(opts?: CallOptions): Promise<GetSettingsResponse> {
    return this.c.unary(SettingsRPC.method.getSettings, {}, opts);
  }

  /** How many predictions were asked in a month ("YYYY-MM"; "" means this
   * month), by person and API key. */
  async usage(month = "", opts?: CallOptions): Promise<GetUsageResponse> {
    return this.c.unary(SettingsRPC.method.getUsage, { month }, opts);
  }

  /** Change where alerts go. A channel left out is left as it is; an empty
   * password or bot token keeps the stored one. */
  async updateAlerts(
    channels: { email?: Init<typeof EmailAlertsSchema>; telegram?: Init<typeof TelegramAlertsSchema> },
    opts?: CallOptions,
  ): Promise<UpdateAlertsResponse> {
    return this.c.unary(SettingsRPC.method.updateAlerts, channels, opts);
  }

  /** Send "This is a test" through AlertChannel.Email or Telegram now. */
  async sendTestAlert(channel: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(SettingsRPC.method.sendTestAlert, { channel }, opts);
  }

  /** Change how long the audit log and webhook delivery history are kept. */
  async updateRetention(retention: Init<typeof RetentionSchema>, opts?: CallOptions): Promise<Retention> {
    return (await this.c.unary(SettingsRPC.method.updateRetention, { retention }, opts)).retention!;
  }

  /** Change the security policy, such as whether everyone must use
   * two-step verification. */
  async updateSecurity(security: Init<typeof SecuritySchema>, opts?: CallOptions): Promise<Security> {
    return (await this.c.unary(SettingsRPC.method.updateSecurity, { security }, opts)).security!;
  }

  /** Change the prediction and training limits. */
  async updateLimits(limits: Init<typeof LimitsSchema>, opts?: CallOptions): Promise<Limits> {
    return (await this.c.unary(SettingsRPC.method.updateLimits, { limits }, opts)).limits!;
  }

  /** Say whether a standalone console trains runs in its own process when
   * no worker takes them, and on how many workers one run may train
   * together. */
  async updateTraining(req: Init<typeof UpdateTrainingRequestSchema>, opts?: CallOptions): Promise<Training> {
    return (await this.c.unary(SettingsRPC.method.updateTraining, req, opts)).training!;
  }

  /** The server's database: its size, schema version, how many records it
   * holds and when history was last trimmed. */
  async databaseInfo(opts?: CallOptions): Promise<GetDatabaseInfoResponse> {
    return this.c.unary(SettingsRPC.method.getDatabaseInfo, {}, opts);
  }

  /** A pg_dump of the server's database as a stream, in pg_dump's custom
   * format. The server allows it only for an admin signed in with a
   * password, not an API key. */
  async backup(opts?: CallOptions): Promise<ReadableStream<Uint8Array>> {
    return this.c.download("/api/backup", opts);
  }

  /** backup, written to a file on disk (Node.js, Deno and Bun). */
  async backupToFile(path: string, opts?: CallOptions): Promise<number> {
    return writeFile(await this.backup(opts), path);
  }
}

/** Lists ready-made starting points for common questions. */
export class TemplateService {
  constructor(private readonly c: Caller) {}

  /** Every template, with the categories they belong to. */
  async list(opts?: CallOptions): Promise<{ templates: Template[]; categories: TemplateCategory[] }> {
    const res = await this.c.unary(TemplateRPC.method.listTemplates, {}, opts);
    return { templates: res.templates, categories: res.categories };
  }

  /** A template's made-up example data, a CSV or a ZIP, with a file name to
   * save it under. */
  async example(templateId: string, opts?: CallOptions): Promise<{ fileName: string; data: Uint8Array }> {
    const res = await this.c.unary(TemplateRPC.method.getTemplateExample, { templateId }, opts);
    return { fileName: res.fileName, data: res.data };
  }
}
