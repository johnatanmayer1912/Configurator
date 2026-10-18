"""
Shared fixtures for Playwright E2E tests.

Starts the NX-OS Configurator web server on 127.0.0.1:9000 when not already
running, so browser tests can run without manual server startup.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "http://127.0.0.1:9000"
DEFAULT_PORT = 9000


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0


def _wait_for_server(host: str = "127.0.0.1", port: int = DEFAULT_PORT, timeout: float = 45.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _port_open(host, port):
            return True
        time.sleep(0.5)
    return False


@pytest.fixture(scope="session", autouse=True)
def web_server():
    """Ensure the configurator API/UI is reachable for every E2E test session."""
    if _port_open("127.0.0.1", DEFAULT_PORT):
        yield None
        return

    proc = subprocess.Popen(
        [sys.executable, "web_launcher.py", "--no-browser"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_server():
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        pytest.fail(f"Web server did not start on port {DEFAULT_PORT} within timeout")

    yield proc

    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
