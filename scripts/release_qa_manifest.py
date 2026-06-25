"""Load and validate data/release_qa_manifest.yaml for QA gate runners."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "release_qa_manifest.yaml"


def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"Missing QA manifest: {MANIFEST_PATH}")
    with MANIFEST_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data


def stages_for_trigger(trigger: str) -> List[Dict[str, Any]]:
    manifest = load_manifest()
    out: List[Dict[str, Any]] = []
    for stage in manifest.get("stages", []):
        triggers = stage.get("triggers") or []
        if trigger in triggers:
            out.append(stage)
    return out


def validate_manifest_files() -> List[str]:
    """Return list of errors (empty if manifest and referenced paths are valid)."""
    errors: List[str] = []
    try:
        manifest = load_manifest()
    except Exception as exc:
        return [str(exc)]

    if not manifest.get("schema_version"):
        errors.append("manifest: schema_version is required")

    stage_ids: List[str] = []
    for stage in manifest.get("stages", []):
        sid = stage.get("id")
        if not sid:
            errors.append("manifest: stage missing id")
            continue
        if sid in stage_ids:
            errors.append(f"manifest: duplicate stage id {sid}")
        stage_ids.append(sid)

        stype = stage.get("type")
        if stype == "pytest":
            for rel in stage.get("paths") or []:
                path = ROOT / rel
                if not path.exists():
                    errors.append(f"manifest: missing pytest path {rel}")
        elif stype == "script":
            for rel in stage.get("command") or []:
                path = ROOT / rel
                if not path.is_file():
                    errors.append(f"manifest: missing script {rel}")

    return errors


def pytest_args_for_trigger(trigger: str, *, exclude_full_suite_duplicates: bool = True) -> List[str]:
    """Collect pytest file paths for a trigger (deduped, order preserved)."""
    seen: set[str] = set()
    paths: List[str] = []
    full_suite = False

    for stage in stages_for_trigger(trigger):
        if stage.get("type") != "pytest":
            continue
        for rel in stage.get("paths") or []:
            norm = rel.replace("\\", "/")
            if norm == "tests/" or norm == "tests":
                full_suite = True
                continue
            if norm not in seen:
                seen.add(norm)
                paths.append(norm)

    if full_suite and exclude_full_suite_duplicates:
        return ["tests/"]
    return paths
