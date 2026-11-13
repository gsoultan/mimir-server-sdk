from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import IO, Any, Callable, Generic, Iterator, Optional, TypeVar, Union

from google.protobuf.message import Message

from ._transport import Transport, method

T = TypeVar("T")

# A file's contents: bytes, a binary file object, or a path to a file.
Source = Union[bytes, bytearray, memoryview, IO[bytes], "os.PathLike[str]", str]


class Service:
    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def _call(self, procedure: str, request: Message) -> Any:
        return self._t.unary(method(procedure), request)

    def _stream(self, procedure: str, request: Message) -> Iterator[Any]:
        return self._t.server_stream(method(procedure), request)


@dataclass
class Page(Generic[T]):
    """One page of a paged list."""

    items: list[T] = field(default_factory=list)
    # Fetches the next page; empty on the last one.
    next_page_token: str = ""


def paginate(token: str, fetch: Callable[[str], Page[T]]) -> Iterator[T]:
    """Walk every page fetch returns, starting from token, until a page has
    no next token."""
    while True:
        page = fetch(token)
        yield from page.items
        if not page.next_page_token or page.next_page_token == token:
            return
        token = page.next_page_token


def read_source(source: Source) -> bytes:
    """The bytes of a file given as bytes, a binary file object or a
    path."""
    if isinstance(source, (bytes, bytearray, memoryview)):
        return bytes(source)
    if isinstance(source, (str, os.PathLike)):
        with open(source, "rb") as f:
            return f.read()
    data = source.read()
    if isinstance(data, str):
        raise TypeError("mimirsdk: open the file in binary mode ('rb')")
    return data


def poll(
    get: Callable[[], T],
    done: Callable[[T], bool],
    interval: float,
    timeout: Optional[float],
    on_progress: Optional[Callable[[T], Any]] = None,
) -> T:
    """Call get every interval seconds until done says so, and return the
    last value. Raises TimeoutError after timeout seconds (None waits for
    ever)."""
    deadline = time.monotonic() + timeout if timeout is not None else None
    while True:
        value = get()
        if on_progress is not None:
            on_progress(value)
        if done(value):
            return value
        if deadline is not None and time.monotonic() + interval > deadline:
            raise TimeoutError(f"mimirsdk: still not done after {timeout:g} seconds")
        time.sleep(interval)
