"""Export path helpers — naming, validation, pair folders."""

import os
import re
from typing import Optional, Tuple


def slugify(value: str, max_len: int = 32) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]", "_", (value or "DEFAULT").strip())
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:max_len] if s else "DEFAULT")


def safe_hostname(value: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_.-]", "_", (value or "device").strip())
    return s.strip("._-") or "device"


def resolve_export_base(override: Optional[str], default_dir: str) -> str:
    """Return validated export base directory."""
    if not override or not str(override).strip():
        return default_dir
    path = os.path.abspath(str(override).strip())
    if ".." in override.replace("\\", "/"):
        raise ValueError("Export path must not contain parent directory references.")
    os.makedirs(path, exist_ok=True)
    return path


def build_file_prefix(
    site_name: str,
    scenario_slug: str,
    hostname: str,
    timestamp: str,
) -> str:
    site = slugify(site_name)
    scenario = slugify(scenario_slug)
    host = safe_hostname(hostname)
    return f"{site}_{scenario}_{host}_{timestamp}"


def pair_batch_folder(site_name: str, scenario_slug: str, timestamp: str) -> str:
    return f"{slugify(site_name)}_{slugify(scenario_slug)}_{timestamp}"


def resolve_output_directory(
    base_dir: str,
    *,
    pair_batch: bool,
    site_name: str,
    scenario_slug: str,
    timestamp: str,
) -> Tuple[str, Optional[str]]:
    """Return (absolute output dir, batch folder name if pair)."""
    if pair_batch:
        batch = pair_batch_folder(site_name, scenario_slug, timestamp)
        out = os.path.join(base_dir, batch)
        os.makedirs(out, exist_ok=True)
        return out, batch
    os.makedirs(base_dir, exist_ok=True)
    return base_dir, None
