"""
app_dirs.py — Resolves runtime output directories relative to the executable location.

When running as a PyInstaller bundle, sys.executable points to the .exe file.
When running from source, it points to the Python interpreter — in that case
we use the project root instead.

All output (configs, logs, checkpoints) is written next to the executable so
files persist after the process exits and are easy to find.
"""

import os
import sys


def get_app_dir() -> str:
    """Return the directory that contains the running executable (or project root from source)."""
    if getattr(sys, "frozen", False):
        # PyInstaller bundle — exe lives here
        return os.path.dirname(sys.executable)
    else:
        # Running from source — use project root (parent of utils/)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_output_dir(subdir: str) -> str:
    """Return an absolute path to *subdir* inside the app directory, creating it if needed."""
    path = os.path.join(get_app_dir(), subdir)
    os.makedirs(path, exist_ok=True)
    return path


def get_history_dir() -> str:
    return get_output_dir("configs/history")


def get_checkpoints_dir() -> str:
    return get_output_dir("configs/checkpoints")


def get_logs_dir() -> str:
    return get_output_dir("logs")


def get_vault_dir() -> str:
    return get_output_dir("configs/vault")
