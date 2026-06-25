"""Instance control and shutdown behavior."""

import os
import subprocess
import sys
import time

import httpx
import pytest

from utils.instance_control import (
    is_process_running,
    pids_listening_on_port,
    read_pid_file,
    remove_pid_file,
    write_pid_file,
)


@pytest.mark.parametrize("port", [9000])
def test_pids_listening_on_port_returns_list(port):
    result = pids_listening_on_port(port)
    assert isinstance(result, list)


def test_pid_file_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("utils.instance_control.get_logs_dir", lambda: str(tmp_path))
    write_pid_file()
    assert read_pid_file() == os.getpid()
    remove_pid_file()
    assert read_pid_file() is None


@pytest.mark.release_blocker
def test_shutdown_works_without_auth_token():
    """Stop must work from any localhost tab (no session token in URL)."""
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    proc = subprocess.Popen(
        [sys.executable, "web_launcher.py", "--no-browser"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    try:
        for _ in range(30):
            time.sleep(0.5)
            try:
                httpx.get("http://127.0.0.1:9000/version", timeout=1.0)
                break
            except httpx.HTTPError:
                continue
        else:
            pytest.fail("Server did not start in time")

        res = httpx.post("http://127.0.0.1:9000/system/shutdown", timeout=5.0)
        assert res.status_code == 200
        assert res.json().get("status") == "shutdown_initiated"

        for _ in range(15):
            time.sleep(0.5)
            if proc.poll() is not None:
                return
        pytest.fail("Process still running after shutdown")
    finally:
        if proc.poll() is None:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
            else:
                proc.terminate()


def test_is_process_running_current_pid():
    assert is_process_running(os.getpid()) is True
    assert is_process_running(999999) is False
