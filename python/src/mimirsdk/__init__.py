"""The Python client for mimir-server.

Sign in with an API key, then manage models, datasets, training runs,
webhooks and people, and ask models questions, including chats streamed as
the model writes them::

    import mimirsdk

    with mimirsdk.Client("http://localhost:8080", api_key="mimir_...") as client:
        for m in client.models.list():
            print(m.name, m.id)

Every message and enum of the server's API is in ``mimirsdk.types`` under
the server's own names, and re-exported here.
"""

from . import types, webhook
from ._access import all_models, some_models
from ._admin import (
    ALERT_CHANNEL_EMAIL,
    ALERT_CHANNEL_TELEGRAM,
    WORKER_TASKS_ALL,
    WORKER_TASKS_SERVE,
    WORKER_TASKS_TRAIN,
)
from ._base import Page
from ._client import ENV_API_KEY, ENV_URL, Client
from ._documents import Answer
from ._errors import (
    AlreadyExistsError,
    CanceledError,
    Code,
    DeadlineExceededError,
    DocumentError,
    FailedPreconditionError,
    InternalError,
    InvalidArgumentError,
    JobError,
    MimirError,
    NotFoundError,
    PermissionDeniedError,
    ResourceExhaustedError,
    ScoringError,
    UnauthenticatedError,
    UnavailableError,
    UnimplementedError,
)
from ._models import ChatReply, assistant_message, user_message
from ._version import SERVER_VERSION, __version__
from .types import *  # noqa: F401,F403
from .types import __all__ as _types_all

__all__ = [
    "Client",
    "ENV_URL",
    "ENV_API_KEY",
    "Page",
    "ChatReply",
    "Answer",
    "user_message",
    "assistant_message",
    "all_models",
    "some_models",
    "WORKER_TASKS_ALL",
    "WORKER_TASKS_TRAIN",
    "WORKER_TASKS_SERVE",
    "ALERT_CHANNEL_EMAIL",
    "ALERT_CHANNEL_TELEGRAM",
    "Code",
    "MimirError",
    "CanceledError",
    "InvalidArgumentError",
    "DeadlineExceededError",
    "NotFoundError",
    "AlreadyExistsError",
    "PermissionDeniedError",
    "ResourceExhaustedError",
    "FailedPreconditionError",
    "UnimplementedError",
    "InternalError",
    "UnavailableError",
    "UnauthenticatedError",
    "JobError",
    "ScoringError",
    "DocumentError",
    "types",
    "webhook",
    "__version__",
    "SERVER_VERSION",
    *_types_all,
]
