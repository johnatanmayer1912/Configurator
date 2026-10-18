"""
Saved deployment / wizard templates on disk (operator UX).
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.app_dirs import get_app_dir

TEMPLATE_DIR_NAME = "saved_templates"
_SAFE_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,120}$")


def templates_dir() -> Path:
    root = Path(get_app_dir()) / "data" / TEMPLATE_DIR_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def list_templates() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path in sorted(templates_dir().glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            out.append({
                "id": path.stem,
                "name": data.get("name", path.stem),
                "description": data.get("description", ""),
                "switch_count": len(data.get("switches", data.get("deployment", {}).get("switches", []))),
                "updated_at": data.get("updated_at", ""),
                "path": str(path),
            })
        except Exception:
            continue
    return out


def save_template(name: str, payload: Dict[str, Any], description: str = "") -> Dict[str, Any]:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", name.strip())[:120] or str(uuid.uuid4())[:8]
    if not _SAFE_NAME.match(safe):
        safe = f"template_{uuid.uuid4().hex[:8]}"
    record = {
        "name": name.strip() or safe,
        "description": description.strip(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    path = templates_dir() / f"{safe}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return {"id": safe, "path": str(path), "name": record["name"]}


def load_template(template_id: str) -> Optional[Dict[str, Any]]:
    if not _SAFE_NAME.match(template_id):
        return None
    path = templates_dir() / f"{template_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
