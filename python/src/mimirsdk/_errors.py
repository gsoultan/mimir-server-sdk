from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .types import Document, Job, Scoring


class Code(str, enum.Enum):
    """What kind of failure a MimirError is: Connect's error codes."""

    CANCELED = "canceled"
    UNKNOWN = "unknown"
    INVALID_ARGUMENT = "invalid_argument"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    FAILED_PRECONDITION = "failed_precondition"
    ABORTED = "aborted"
    OUT_OF_RANGE = "out_of_range"
    UNIMPLEMENTED = "unimplemented"
    INTERNAL = "internal"
    UNAVAILABLE = "unavailable"
    DATA_LOSS = "data_loss"
    UNAUTHENTICATED = "unauthenticated"

    @classmethod
    def parse(cls, value: object) -> Optional[Code]:
        try:
            return cls(str(value))
        except ValueError:
            return None


class MimirError(Exception):
    """A call the server, or the way to it, turned down.

    ``code`` says what kind of failure it is, ``message`` is the server's
    explanation, written to show to people, ``procedure`` the call that
    failed (like ``/mimir.v1.ModelService/GetModel``) and ``retry_after``
    how many seconds the server asked to wait before trying again (0 when
    it didn't say). Catch a subclass, such as NotFoundError, for one code.
    """

    code: Code = Code.UNKNOWN

    def __init__(
        self,
        message: str = "",
        *,
        code: Optional[Code] = None,
        procedure: str = "",
        retry_after: float = 0.0,
    ) -> None:
        if code is not None:
            self.code = code
        self.message = message
        self.procedure = procedure
        self.retry_after = retry_after
        super().__init__(str(self))

    def __str__(self) -> str:
        out = "mimirsdk: "
        if self.procedure:
            out += self.procedure.removeprefix("/mimir.v1.") + ": "
        out += self.code.value
        if self.message:
            out += ": " + self.message
        return out

    @property
    def retryable(self) -> bool:
        """The same call may succeed if tried again later."""
        return self.code == Code.UNAVAILABLE or self.retry_after > 0


class CanceledError(MimirError):
    code = Code.CANCELED


class InvalidArgumentError(MimirError):
    code = Code.INVALID_ARGUMENT


class DeadlineExceededError(MimirError):
    code = Code.DEADLINE_EXCEEDED


class NotFoundError(MimirError):
    code = Code.NOT_FOUND


class AlreadyExistsError(MimirError):
    code = Code.ALREADY_EXISTS


class PermissionDeniedError(MimirError):
    code = Code.PERMISSION_DENIED


class ResourceExhaustedError(MimirError):
    code = Code.RESOURCE_EXHAUSTED


class FailedPreconditionError(MimirError):
    code = Code.FAILED_PRECONDITION


class UnimplementedError(MimirError):
    code = Code.UNIMPLEMENTED


class InternalError(MimirError):
    code = Code.INTERNAL


class UnavailableError(MimirError):
    code = Code.UNAVAILABLE


class UnauthenticatedError(MimirError):
    code = Code.UNAUTHENTICATED


_BY_CODE = {
    cls.code: cls
    for cls in (
        CanceledError,
        InvalidArgumentError,
        DeadlineExceededError,
        NotFoundError,
        AlreadyExistsError,
        PermissionDeniedError,
        ResourceExhaustedError,
        FailedPreconditionError,
        UnimplementedError,
        InternalError,
        UnavailableError,
        UnauthenticatedError,
    )
}


def error_for(code: Code, message: str, procedure: str, retry_after: float = 0.0) -> MimirError:
    """Make the MimirError subclass for code."""
    cls = _BY_CODE.get(code, MimirError)
    return cls(message, code=code, procedure=procedure, retry_after=retry_after)


def code_from_http(status: int) -> Code:
    """The nearest code for an HTTP status, for answers that aren't
    Connect-shaped (a proxy's, say)."""
    return {
        400: Code.INVALID_ARGUMENT,
        401: Code.UNAUTHENTICATED,
        403: Code.PERMISSION_DENIED,
        404: Code.UNIMPLEMENTED,
        408: Code.DEADLINE_EXCEEDED,
        409: Code.ABORTED,
        412: Code.FAILED_PRECONDITION,
        413: Code.RESOURCE_EXHAUSTED,
        415: Code.INTERNAL,
        429: Code.RESOURCE_EXHAUSTED,
        431: Code.RESOURCE_EXHAUSTED,
        502: Code.UNAVAILABLE,
        503: Code.UNAVAILABLE,
        504: Code.UNAVAILABLE,
    }.get(status, Code.UNKNOWN)


def _status(value: int, prefix: str) -> str:
    from .types import JobStatus

    name = JobStatus.Name(value) if value in JobStatus.values() else str(value)
    return name.removeprefix(prefix).lower()


class JobError(Exception):
    """A training run that failed or was cancelled. ``job`` is the run as
    it ended."""

    def __init__(self, job: Job) -> None:
        self.job = job
        status = _status(job.status, "JOB_STATUS_")
        msg = f"mimirsdk: training run {job.id} {status}"
        if job.error:
            msg += f": {job.error}"
        super().__init__(msg)


class ScoringError(Exception):
    """A scoring that failed or was cancelled. ``scoring`` is the scoring
    as it ended."""

    def __init__(self, scoring: Scoring) -> None:
        self.scoring = scoring
        status = _status(scoring.status, "JOB_STATUS_")
        msg = f"mimirsdk: scoring {scoring.id} {status}"
        if scoring.error:
            msg += f": {scoring.error}"
        super().__init__(msg)


class DocumentError(Exception):
    """A document the server couldn't read. ``document`` is the document
    as it ended."""

    def __init__(self, document: Document) -> None:
        self.document = document
        msg = f"mimirsdk: document {document.name} not read"
        if document.error:
            msg += f": {document.error}"
        super().__init__(msg)
