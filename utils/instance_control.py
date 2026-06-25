"""Single-instance helpers: PID file, port ownership, graceful stop."""

from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
from typing import List, Optional

from utils.app_dirs import get_logs_dir

DEFAULT_PORT = 9000
PID_FILENAME = "nxos_configurator.pid"


def pid_file_path() -> str:
    return os.path.join(get_logs_dir(), PID_FILENAME)


def write_pid_file() -> None:
    path = pid_file_path()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(str(os.getpid()))


def read_pid_file() -> Optional[int]:
    path = pid_file_path()
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return int(fh.read().strip())
    except (OSError, ValueError):
        return None


def remove_pid_file() -> None:
    path = pid_file_path()
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass


def is_process_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        return str(pid) in (result.stdout or "")
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def pids_listening_on_port(port: int) -> List[int]:
    pids: List[int] = []
    if sys.platform == "win32":
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            check=False,
        )
        needle = f":{port}"
        for line in (result.stdout or "").splitlines():
            if "LISTENING" not in line.upper():
                continue
            if needle not in line:
                continue
            parts = line.split()
            if not parts:
                continue
            try:
                pid = int(parts[-1])
            except ValueError:
                continue
            if pid > 0 and pid not in pids:
                pids.append(pid)
        return pids

    result = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}"],
        capture_output=True,
        text=True,
        check=False,
    )
    for token in (result.stdout or "").split():
        try:
            pids.append(int(token))
        except ValueError:
            continue
    return pids


def terminate_pid(pid: int) -> bool:
    if not is_process_running(pid):
        return True
    if sys.platform == "win32":
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    try:
        os.kill(pid, signal.SIGTERM)
        return True
    except OSError:
        return False


def stop_listeners_on_port(port: int = DEFAULT_PORT) -> List[int]:
    """Terminate processes listening on *port*. Returns PIDs that were targeted."""
    stopped: List[int] = []
    for pid in pids_listening_on_port(port):
        if terminate_pid(pid):
            stopped.append(pid)
    remove_pid_file()
    return stopped


def describe_port_conflict(port: int = DEFAULT_PORT) -> str:
    pids = pids_listening_on_port(port)
    pid_file = read_pid_file()
    lines = [
        f"Port {port} is already in use.",
    ]
    if pids:
        lines.append(f"Listening process PID(s): {', '.join(str(p) for p in pids)}")
    if pid_file:
        lines.append(f"PID file: {pid_file_path()} (pid {pid_file})")
    lines.append(
        "Close the console window, click Stop in the web UI, or run: "
        "scripts\\stop_configurator.ps1"
    )
    lines.append(
        f"To replace the running instance: re-launch with --replace"
    )
    return "\n".join(lines)


def process_name_for_pid(pid: int) -> str:
    if sys.platform != "win32":
        return ""
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    line = (result.stdout or "").strip()
    if not line or "No tasks" in line:
        return ""
    match = re.match(r'"([^"]+)"', line)
    return match.group(1) if match else line.split(",")[0].strip('"')
