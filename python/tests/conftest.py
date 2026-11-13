"""Starts the Go test server (internal/testserver) the tests talk to. It
serves the server's real Connect handlers, so the tests check the wire
format too. Needs Go; set MIMIR_TESTSERVER to a built binary to skip the
build."""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import uuid
from typing import Iterator

import pytest

import mimirsdk

ROOT = pathlib.Path(__file__).resolve().parents[2]
KEY = "mimir_test_key"


@pytest.fixture(scope="session")
def server_url() -> Iterator[str]:
    binary = os.environ.get("MIMIR_TESTSERVER")
    tmp = None
    if not binary:
        tmp = tempfile.TemporaryDirectory()
        binary = os.path.join(tmp.name, "testserver")
        subprocess.run(["go", "build", "-o", binary, "./internal/testserver"], cwd=ROOT, check=True)
    proc = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    line = proc.stdout.readline().strip()
    assert line.startswith("listening on "), line
    try:
        yield line.removeprefix("listening on ")
    finally:
        assert proc.stdin is not None
        proc.stdin.close()
        proc.wait(timeout=10)
        if tmp is not None:
            tmp.cleanup()


@pytest.fixture
def run() -> str:
    """A name for this test's calls, so the server counts them apart."""
    return uuid.uuid4().hex


@pytest.fixture
def client(server_url: str, run: str) -> Iterator[mimirsdk.Client]:
    with mimirsdk.Client(server_url, api_key=KEY, retry_backoff=0.01, headers={"X-Test-Run": run}) as c:
        yield c
