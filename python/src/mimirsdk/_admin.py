from __future__ import annotations

import builtins
from typing import Any, Iterator, Mapping, Union

from . import types as t
from ._base import Page, Service, paginate
from ._scorings import Dest, download_to
from ._transport import to_message

# What a worker may be told to take, for WorkerService.set_tasks.
WORKER_TASKS_ALL = "all"  # training runs and predictions
WORKER_TASKS_TRAIN = "train"  # training runs only
WORKER_TASKS_SERVE = "serve"  # predictions only

# Alert channels, for SettingsService.send_test_alert.
ALERT_CHANNEL_EMAIL = "email"
ALERT_CHANNEL_TELEGRAM = "telegram"


class WebhookService(Service):
    """Manages the addresses the server tells about changes. Check
    deliveries on the receiving end with ``mimirsdk.webhook``."""

    def list(self) -> builtins.list[t.Webhook]:
        """The caller's team's webhooks."""
        return list(self._call("mimir.v1.WebhookService.ListWebhooks", t.ListWebhooksRequest()).webhooks)

    def event_types(self) -> builtins.list[str]:
        """Every event a webhook can subscribe to."""
        return list(self._call("mimir.v1.WebhookService.ListWebhooks", t.ListWebhooksRequest()).event_types)

    def create(
        self, request: Union[t.CreateWebhookRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.CreateWebhookResponse:
        """Add a webhook. Its signing ``secret`` is in the response only
        this once: give it to ``webhook.verify`` on the receiving end."""
        return self._call("mimir.v1.WebhookService.CreateWebhook", to_message(t.CreateWebhookRequest, request, fields))

    def update(
        self, request: Union[t.UpdateWebhookRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.Webhook:
        """Change a webhook's name, address or events, or turn it off."""
        req = to_message(t.UpdateWebhookRequest, request, fields)
        return self._call("mimir.v1.WebhookService.UpdateWebhook", req).webhook

    def delete(self, id: str) -> None:
        """Remove a webhook."""
        self._call("mimir.v1.WebhookService.DeleteWebhook", t.DeleteWebhookRequest(id=id))

    def send_test(self, id: str) -> t.Delivery:
        """Send a "test" event to a webhook now."""
        return self._call("mimir.v1.WebhookService.SendTestEvent", t.SendTestEventRequest(id=id)).delivery

    def redeliver(self, delivery_id: str) -> t.Delivery:
        """Send a past delivery again, now."""
        return self._call("mimir.v1.WebhookService.Redeliver", t.RedeliverRequest(id=delivery_id)).delivery

    def deliveries_page(self, webhook_id: str, *, page_size: int = 0, page_token: str = "") -> Page[t.Delivery]:
        """One page of a webhook's deliveries, newest first."""
        req = t.ListDeliveriesRequest(webhook_id=webhook_id, page_size=page_size, page_token=page_token)
        res = self._call("mimir.v1.WebhookService.ListDeliveries", req)
        return Page(items=list(res.deliveries), next_page_token=res.next_page_token)

    def deliveries(self, webhook_id: str, *, page_size: int = 0, page_token: str = "") -> Iterator[t.Delivery]:
        """Every delivery of a webhook, newest first, fetching pages as the
        loop needs them."""
        return paginate(
            page_token, lambda token: self.deliveries_page(webhook_id, page_size=page_size, page_token=token)
        )


class WorkerService(Service):
    """Reads the machines that answer and teach models for the server."""

    def list(self) -> builtins.list[t.Worker]:
        """Every worker."""
        return list(self._call("mimir.v1.WorkerService.ListWorkers", t.ListWorkersRequest()).workers)

    def get(self, id: str, hours: int = 0) -> t.GetWorkerResponse:
        """A worker with its last ``hours`` of samples and its tasks; 0 lets
        the server choose."""
        return self._call("mimir.v1.WorkerService.GetWorker", t.GetWorkerRequest(id=id, hours=hours))

    def choices(self) -> builtins.list[t.Worker]:
        """The workers a model or training run may be placed on."""
        return list(self._call("mimir.v1.WorkerService.ListWorkerChoices", t.ListWorkerChoicesRequest()).workers)

    def create(self, name: str) -> t.CreateWorkerResponse:
        """Add a worker and return the token it joins with, shown only
        once."""
        return self._call("mimir.v1.WorkerService.CreateWorker", t.CreateWorkerRequest(name=name))

    def set_tasks(self, id: str, tasks: str) -> t.Worker:
        """Tell a worker what to take: WORKER_TASKS_ALL, WORKER_TASKS_TRAIN
        or WORKER_TASKS_SERVE, or "" to leave it to the worker's own -tasks
        flag. It applies at once to a connected worker."""
        req = t.SetWorkerTasksRequest(id=id, tasks=tasks)
        return self._call("mimir.v1.WorkerService.SetWorkerTasks", req).worker

    def cloud_gpu(self) -> t.GetCloudGpuResponse:
        """How training runs rent a GPU when they wait, whether one is
        running now, and which providers and GPUs can be picked."""
        return self._call("mimir.v1.WorkerService.GetCloudGpu", t.GetCloudGpuRequest())

    def update_cloud_gpu(
        self, request: Union[t.UpdateCloudGpuRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.CloudGpu:
        """Set up renting a GPU for waiting training runs, change it, or
        turn it off. Turning it on the first time adds a worker for it,
        which only trains."""
        req = to_message(t.UpdateCloudGpuRequest, request, fields)
        return self._call("mimir.v1.WorkerService.UpdateCloudGpu", req).cloud_gpu

    def stop_cloud_gpu(self) -> t.CloudGpu:
        """Stop the rented GPU now. Runs on it go back in the queue and
        resume from their checkpoints."""
        return self._call("mimir.v1.WorkerService.StopCloudGpu", t.StopCloudGpuRequest()).cloud_gpu

    def replace_token(self, id: str) -> str:
        """Make a new token for a worker, shown only once. The old token
        stops working at once and the worker is disconnected until it joins
        again with the new one."""
        return self._call("mimir.v1.WorkerService.ReplaceWorkerToken", t.ReplaceWorkerTokenRequest(id=id)).token

    def delete(self, id: str) -> None:
        """Remove a worker."""
        self._call("mimir.v1.WorkerService.DeleteWorker", t.DeleteWorkerRequest(id=id))


class SettingsService(Service):
    """Reads and changes server-wide settings. It needs an owner, except
    ``usage``, which shows each caller their own."""

    def get(self) -> t.GetSettingsResponse:
        """The alert, retention, security, limit and training settings."""
        return self._call("mimir.v1.SettingsService.GetSettings", t.GetSettingsRequest())

    def usage(self, month: str = "") -> t.GetUsageResponse:
        """How many predictions were asked in a month ("YYYY-MM"; "" means
        this month), by person and API key."""
        return self._call("mimir.v1.SettingsService.GetUsage", t.GetUsageRequest(month=month))

    def update_alerts(
        self,
        email: Union[t.EmailAlerts, Mapping[str, Any], None] = None,
        telegram: Union[t.TelegramAlerts, Mapping[str, Any], None] = None,
    ) -> t.UpdateAlertsResponse:
        """Change where alerts go: email through an SMTP server, Telegram,
        or both. A channel left out is left as it is; an empty password or
        bot token keeps the stored one."""
        body: dict[str, Any] = {}
        if email is not None:
            body["email"] = email
        if telegram is not None:
            body["telegram"] = telegram
        return self._call("mimir.v1.SettingsService.UpdateAlerts", to_message(t.UpdateAlertsRequest, body, {}))

    def send_test_alert(self, channel: str) -> None:
        """Send "This is a test" through ALERT_CHANNEL_EMAIL or
        ALERT_CHANNEL_TELEGRAM now."""
        self._call("mimir.v1.SettingsService.SendTestAlert", t.SendTestAlertRequest(channel=channel))

    def update_retention(self, retention: Union[t.Retention, Mapping[str, Any]]) -> t.Retention:
        """Change how long the audit log and webhook delivery history are
        kept."""
        req = to_message(t.UpdateRetentionRequest, {"retention": retention}, {})
        return self._call("mimir.v1.SettingsService.UpdateRetention", req).retention

    def update_security(self, security: Union[t.Security, Mapping[str, Any]]) -> t.Security:
        """Change the security policy, such as whether everyone must use
        two-step verification."""
        req = to_message(t.UpdateSecurityRequest, {"security": security}, {})
        return self._call("mimir.v1.SettingsService.UpdateSecurity", req).security

    def update_limits(self, limits: Union[t.Limits, Mapping[str, Any]]) -> t.Limits:
        """Change the prediction and training limits."""
        req = to_message(t.UpdateLimitsRequest, {"limits": limits}, {})
        return self._call("mimir.v1.SettingsService.UpdateLimits", req).limits

    def update_training(
        self, request: Union[t.UpdateTrainingRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.Training:
        """Say whether a standalone console trains runs in its own process
        when no worker takes them, and, when ``group_workers`` is set, on how
        many workers one run may train together."""
        req = to_message(t.UpdateTrainingRequest, request, fields)
        return self._call("mimir.v1.SettingsService.UpdateTraining", req).training

    def database_info(self) -> t.GetDatabaseInfoResponse:
        """The server's database: its size, schema version, how many records
        it holds and when history was last trimmed."""
        return self._call("mimir.v1.SettingsService.GetDatabaseInfo", t.GetDatabaseInfoRequest())

    def backup(self, dest: Dest) -> int:
        """Write a pg_dump of the server's database to ``dest``, a path or a
        binary file object, in pg_dump's custom format (restore it with
        pg_restore), and return how many bytes it wrote. The server allows it
        only for an admin signed in with a password, not an API key, and only
        where pg_dump is installed."""
        return download_to(self._t, "/api/backup", dest)


class TemplateService(Service):
    """Lists ready-made starting points for common questions."""

    def list(self) -> tuple[list[t.Template], list[t.TemplateCategory]]:
        """Every template, with the categories they belong to."""
        res = self._call("mimir.v1.TemplateService.ListTemplates", t.ListTemplatesRequest())
        return list(res.templates), list(res.categories)

    def example(self, template_id: str) -> tuple[str, bytes]:
        """A template's made-up example data, a CSV or a ZIP, with a file
        name to save it under."""
        req = t.GetTemplateExampleRequest(template_id=template_id)
        res = self._call("mimir.v1.TemplateService.GetTemplateExample", req)
        return res.file_name, res.data
