"""Load and persist Po allocation map (bundled defaults + user overrides)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from utils.app_dirs import get_app_dir


def _bundle_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "data" / "po_allocation_map.yaml"
    return Path(__file__).resolve().parent.parent / "data" / "po_allocation_map.yaml"


def _user_path() -> Path:
    return Path(get_app_dir()) / "configs" / "po_allocation_map.yaml"


def load_po_map() -> Dict[str, Any]:
    path = _bundle_path()
    data: Dict[str, Any] = {}
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    user = _user_path()
    if user.exists():
        with open(user, encoding="utf-8") as fh:
            override = yaml.safe_load(fh) or {}
        if override.get("models"):
            data.setdefault("models", {}).update(override["models"])
        if override.get("default_ranges"):
            data["default_ranges"] = override["default_ranges"]
    return data


def save_po_map(updates: Dict[str, Any]) -> Dict[str, Any]:
    current = load_po_map()
    if updates.get("default_ranges"):
        current["default_ranges"] = updates["default_ranges"]
    if updates.get("models"):
        current.setdefault("models", {})
        current["models"].update(updates["models"])
    dest = _user_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        yaml.safe_dump(current, fh, default_flow_style=False, sort_keys=False)
    return current


def ranges_for_model(model: str) -> Dict[str, List[int]]:
    data = load_po_map()
    defaults = data.get("default_ranges") or {}
    models = data.get("models") or {}
    merged = dict(defaults)
    for key, profile in models.items():
        if key == model or model in key:
            merged.update(profile)
            break
    return {k: list(v) if isinstance(v, list) else v for k, v in merged.items()}


def po_in_range(po_id: int, range_pair: List[int]) -> bool:
    if not range_pair or len(range_pair) < 2:
        return False
    return int(range_pair[0]) <= po_id <= int(range_pair[1])


def role_for_po(po_id: int, model: str) -> Optional[str]:
    for role, rng in ranges_for_model(model).items():
        if isinstance(rng, list) and len(rng) >= 2 and po_in_range(po_id, rng):
            return role
    return None


def next_free_po(used: List[int], model: str, preferred_role: str = "planner") -> int:
    ranges = ranges_for_model(model)
    rng = ranges.get(preferred_role) or ranges.get("planner") or [10, 99]
    start, end = int(rng[0]), int(rng[1])
    used_set = set(used)
    for n in range(start, end + 1):
        if n not in used_set:
            return n
    for n in range(1, 4096):
        if n not in used_set:
            return n
    return start
