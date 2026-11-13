"""The Connect protocol over HTTP, with the SDK's sign-in, retries and
timeouts. See https://connectrpc.com/docs/protocol."""

from __future__ import annotations

import json
import platform
import random
import struct
import time
from typing import Any, Callable, Iterator, Mapping, Optional, TypeVar, Union

import httpx
from google.protobuf import descriptor_pool, json_format, message_factory
from google.protobuf.descriptor import MethodDescriptor
from google.protobuf.message import DecodeError, Message

from . import _gen  # noqa: F401  (registers every message with the pool)
from ._errors import Code, MimirError, UnavailableError, code_from_http, error_for
from ._version import __version__

M = TypeVar("M", bound=Message)

DEFAULT_TIMEOUT = 60.0
DEFAULT_RETRIES = 3
DEFAULT_RETRY_BACKOFF = 0.25
DEFAULT_MAX_RETRY_WAIT = 30.0

# MethodOptions.IdempotencyLevel: NO_SIDE_EFFECTS and IDEMPOTENT.
_RETRY_SAFE_LEVELS = (1, 2)

_FLAG_COMPRESSED = 0x01
_FLAG_END_STREAM = 0x02
_MAX_MESSAGE_BYTES = 256 << 20


def method(name: str) -> MethodDescriptor:
    """The method descriptor for a procedure, given as
    ``mimir.v1.ModelService.ListModels``, ``mimir.v1.ModelService/ListModels``
    or ``/mimir.v1.ModelService/ListModels``."""
    full = name.strip("/").replace("/", ".")
    try:
        return descriptor_pool.Default().FindMethodByName(full)
    except KeyError:
        raise ValueError(f"mimirsdk: the server has no procedure {name!r}") from None


def procedure_of(m: MethodDescriptor) -> str:
    return f"/{m.containing_service.full_name}/{m.name}"


def output_class(m: MethodDescriptor) -> type[Message]:
    return message_factory.GetMessageClass(m.output_type)


def input_class(m: MethodDescriptor) -> type[Message]:
    return message_factory.GetMessageClass(m.input_type)


class Transport:
    def __init__(
        self,
        base_url: str,
        *,
        api_key: str = "",
        http_client: Optional[httpx.Client] = None,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        max_retry_wait: float = DEFAULT_MAX_RETRY_WAIT,
        user_agent: str = "",
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        if any(c in api_key for c in "\r\n "):
            raise ValueError("mimirsdk: the API key has spaces or line breaks in it")
        self.base_url = base_url
        self.api_key = api_key
        self._own_http = http_client is None
        # No overall timeout on the client: streamed chats run as long as the
        # model writes. Unary calls get their own deadline below.
        self.http = http_client or httpx.Client(timeout=httpx.Timeout(None, connect=30.0))
        self.timeout = timeout if timeout and timeout > 0 else None
        self.retries = max(retries, 0)
        self.retry_backoff = retry_backoff if retry_backoff > 0 else DEFAULT_RETRY_BACKOFF
        self.max_retry_wait = max_retry_wait if max_retry_wait > 0 else DEFAULT_MAX_RETRY_WAIT
        ua = f"mimir-server-sdk-python/{__version__} (Python {platform.python_version()})"
        self.user_agent = f"{user_agent} {ua}" if user_agent else ua
        self.extra_headers = dict(headers or {})

    def close(self) -> None:
        if self._own_http:
            self.http.close()

    def headers(self) -> dict[str, str]:
        h = dict(self.extra_headers)
        h["User-Agent"] = self.user_agent
        if self.api_key:
            h["Authorization"] = "Bearer " + self.api_key
        return h

    # Unary calls.

    def unary(self, m: MethodDescriptor, request: Message) -> Message:
        procedure = procedure_of(m)
        body = request.SerializeToString()
        retry_safe = m.GetOptions().idempotency_level in _RETRY_SAFE_LEVELS
        deadline = time.monotonic() + self.timeout if self.timeout else None
        attempt = 0
        while True:
            try:
                return self._unary_once(m, procedure, body, deadline)
            except MimirError as err:
                if attempt >= self.retries:
                    raise
                wait = self._retry_wait(err, retry_safe, attempt)
                if wait is None:
                    raise
                if deadline is not None and time.monotonic() + wait >= deadline:
                    raise
                time.sleep(wait)
                attempt += 1

    def _unary_once(self, m: MethodDescriptor, procedure: str, body: bytes, deadline: Optional[float]) -> Message:
        headers = self.headers()
        headers["Content-Type"] = "application/proto"
        headers["Connect-Protocol-Version"] = "1"
        timeout: Optional[float] = None
        if deadline is not None:
            timeout = deadline - time.monotonic()
            if timeout <= 0:
                raise error_for(Code.DEADLINE_EXCEEDED, "the call ran out of time", procedure)
            headers["Connect-Timeout-Ms"] = str(max(int(timeout * 1000), 1))
        try:
            res = self.http.post(
                self.base_url + procedure,
                content=body,
                headers=headers,
                timeout=httpx.Timeout(timeout, connect=min(timeout or 30.0, 30.0)),
            )
        except httpx.TimeoutException:
            raise error_for(Code.DEADLINE_EXCEEDED, "the call ran out of time", procedure) from None
        except httpx.TransportError as e:
            raise UnavailableError(str(e) or type(e).__name__, procedure=procedure) from e
        if res.status_code != 200:
            raise _unary_error(res, procedure)
        try:
            return output_class(m).FromString(res.content)
        except DecodeError as e:
            raise error_for(Code.INTERNAL, f"the server's answer isn't readable: {e}", procedure) from e

    def _retry_wait(self, err: MimirError, retry_safe: bool, attempt: int) -> Optional[float]:
        """How long to wait before trying a failed call again, or None to
        give up. A Retry-After means the server refused the call before doing
        anything, so any call may be retried after it. An unavailable server
        may have done the work before the reply was lost, so only calls
        without side effects are retried then."""
        if err.retry_after > 0:
            return err.retry_after if err.retry_after <= self.max_retry_wait else None
        if err.code != Code.UNAVAILABLE or not retry_safe:
            return None
        d = min(self.retry_backoff * (2**attempt), self.max_retry_wait)
        # Full jitter in the upper half, so many clients don't retry at once.
        return d / 2 + random.uniform(0, d / 2)

    # Server streams.

    def server_stream(self, m: MethodDescriptor, request: Message) -> Iterator[Message]:
        """Yield each message of a server stream. Closing the iterator
        (breaking out of a for loop over it) closes the stream, which stops
        the server's work."""
        procedure = procedure_of(m)
        out = output_class(m)
        payload = request.SerializeToString()
        headers = self.headers()
        headers["Content-Type"] = "application/connect+proto"
        headers["Connect-Protocol-Version"] = "1"
        body = struct.pack(">BI", 0, len(payload)) + payload
        try:
            cm = self.http.stream(
                "POST",
                self.base_url + procedure,
                content=body,
                headers=headers,
                timeout=httpx.Timeout(None, connect=30.0),
            )
            res = cm.__enter__()
        except httpx.TransportError as e:
            raise UnavailableError(str(e) or type(e).__name__, procedure=procedure) from e
        try:
            if res.status_code != 200:
                res.read()
                raise _unary_error(res, procedure)
            if res.headers.get("connect-content-encoding", "identity") not in ("", "identity"):
                raise error_for(Code.INTERNAL, "the server compressed the stream", procedure)
            for flags, data in _envelopes(res.iter_bytes(), procedure):
                if flags & _FLAG_COMPRESSED:
                    raise error_for(Code.INTERNAL, "the server compressed a message", procedure)
                if flags & _FLAG_END_STREAM:
                    _raise_end_stream(data, res.headers, procedure)
                    return
                try:
                    yield out.FromString(data)
                except DecodeError as e:
                    raise error_for(Code.INTERNAL, f"the server's answer isn't readable: {e}", procedure) from e
            raise error_for(Code.INTERNAL, "the stream ended without an end message", procedure)
        except httpx.TimeoutException:
            raise error_for(Code.DEADLINE_EXCEEDED, "the stream ran out of time", procedure) from None
        except httpx.TransportError as e:
            raise UnavailableError(str(e) or type(e).__name__, procedure=procedure) from e
        finally:
            cm.__exit__(None, None, None)

    # Plain HTTP endpoints next to the RPCs: uploads and downloads.

    def upload(self, path: str, chunks: Union[bytes, Iterator[bytes]], size: int = -1) -> dict[str, Any]:
        headers = self.headers()
        headers["Content-Type"] = "application/octet-stream"
        if size >= 0:
            headers["Content-Length"] = str(size)
        try:
            res = self.http.post(
                self.base_url + path, content=chunks, headers=headers, timeout=httpx.Timeout(None, connect=30.0)
            )
        except httpx.TransportError as e:
            raise UnavailableError(str(e) or type(e).__name__, procedure=path) from e
        if res.status_code != 200:
            raise _http_error(res.status_code, res.content, path)
        try:
            return json.loads(res.content)
        except ValueError:
            raise error_for(
                Code.INTERNAL, f"the server's answer isn't JSON: {res.text.strip()[:200]!r}", path
            ) from None

    def download(self, path: str, write: Callable[[bytes], Any]) -> int:
        headers = self.headers()
        n = 0
        try:
            with self.http.stream(
                "GET", self.base_url + path, headers=headers, timeout=httpx.Timeout(None, connect=30.0)
            ) as res:
                if res.status_code != 200:
                    raise _http_error(res.status_code, res.read(), path)
                for chunk in res.iter_bytes():
                    write(chunk)
                    n += len(chunk)
        except httpx.TransportError as e:
            raise UnavailableError(str(e) or type(e).__name__, procedure=path) from e
        return n


def _envelopes(chunks: Iterator[bytes], procedure: str) -> Iterator[tuple[int, bytes]]:
    buf = bytearray()
    for chunk in chunks:
        buf += chunk
        while len(buf) >= 5:
            flags, length = struct.unpack(">BI", bytes(buf[:5]))
            if length > _MAX_MESSAGE_BYTES:
                raise error_for(Code.RESOURCE_EXHAUSTED, f"a message of {length} bytes is too large", procedure)
            if len(buf) < 5 + length:
                break
            data = bytes(buf[5 : 5 + length])
            del buf[: 5 + length]
            yield flags, data
    if buf:
        raise error_for(Code.INTERNAL, "the stream ended in the middle of a message", procedure)


def _retry_after(headers: Mapping[str, str]) -> float:
    v = (headers.get("retry-after") or "").strip()
    if not v:
        return 0.0
    try:
        secs = int(v)
    except ValueError:
        return 0.0
    return float(secs) if secs >= 0 else 0.0


def _unary_error(res: httpx.Response, procedure: str) -> MimirError:
    err = _http_error(res.status_code, res.content, procedure)
    err.retry_after = _retry_after(res.headers)
    return err


def _http_error(status: int, data: bytes, procedure: str) -> MimirError:
    """Read the Connect-shaped error ({"code": ..., "message": ...}) the
    server answers a failed call with."""
    code: Optional[Code] = None
    message = ""
    try:
        body = json.loads(data)
        if isinstance(body, dict):
            code = Code.parse(body.get("code"))
            message = str(body.get("message") or "")
    except ValueError:
        pass
    if code is None:
        code = code_from_http(status)
    if not message:
        message = data.decode("utf-8", "replace").strip()[:500]
    return error_for(code, message, procedure)


def _raise_end_stream(data: bytes, headers: Mapping[str, str], procedure: str) -> None:
    try:
        end = json.loads(data or b"{}")
    except ValueError:
        raise error_for(Code.INTERNAL, "the stream's end message isn't JSON", procedure) from None
    err = end.get("error") if isinstance(end, dict) else None
    if not err:
        return
    code = Code.parse(err.get("code")) or Code.UNKNOWN
    meta = {k.lower(): (v[0] if isinstance(v, list) and v else v) for k, v in (end.get("metadata") or {}).items()}
    raise error_for(code, str(err.get("message") or ""), procedure, _retry_after(meta))


def to_message(cls: type[M], request: Union[M, Mapping[str, Any], None], fields: Mapping[str, Any]) -> M:
    """A request message from a message, a dict of its fields or keyword
    arguments. Keyword arguments set fields on top of the others. Dicts may
    use the proto field names (model_id) or their JSON names (modelId)."""
    if request is None:
        msg = cls()
    elif isinstance(request, Message):
        if request.DESCRIPTOR is not cls.DESCRIPTOR:
            raise TypeError(f"mimirsdk: expected a {cls.DESCRIPTOR.name}, got a {request.DESCRIPTOR.name}")
        msg = cls()
        msg.CopyFrom(request)
    elif isinstance(request, Mapping):
        msg = json_format.ParseDict(_jsonable(request), cls())
    else:
        raise TypeError(f"mimirsdk: expected a {cls.DESCRIPTOR.name} or a dict, got {type(request).__name__}")
    if fields:
        msg.MergeFrom(json_format.ParseDict(_jsonable(fields), cls()))
    return msg


def _jsonable(v: Any) -> Any:
    """Prepare a dict for ParseDict: messages become dicts, bytes become
    base64, so callers can mix them freely."""
    import base64

    if isinstance(v, Message):
        return json_format.MessageToDict(v, preserving_proto_field_name=True)
    if isinstance(v, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(v)).decode("ascii")
    if isinstance(v, Mapping):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    return v
