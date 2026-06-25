"""NX-OS version train comparison for wizard UI (C8)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.catalog_loader import CatalogLoader


def compare_versions(from_id: str, to_id: str, catalog: Optional[CatalogLoader] = None) -> Dict[str, Any]:
    cat = catalog or CatalogLoader()
    src = cat.get_version(from_id) or {}
    dst = cat.get_version(to_id) or {}
    if not src or not dst:
        return {"from": from_id, "to": to_id, "changes": [], "warning": "Unknown version id"}

    src_feat = src.get("features") or {}
    dst_feat = dst.get("features") or {}
    changes: List[Dict[str, str]] = []

    if src.get("template") != dst.get("template"):
        changes.append(
            {
                "level": "warn",
                "text": f"Template switches from {src.get('template')} to {dst.get('template')} — lab-test output.",
            }
        )

    for key in sorted(set(src_feat) | set(dst_feat)):
        a, b = src_feat.get(key), dst_feat.get(key)
        if a == b:
            continue
        if key == "vpc_peer_gateway" and not b:
            changes.append({"level": "warn", "text": "peer-gateway may be omitted on this train."})
        elif key == "vpc_auto_recovery" and not b:
            changes.append({"level": "warn", "text": "vPC auto-recovery / orphan-suspend not supported."})
        else:
            changes.append({"level": "info", "text": f"Feature '{key}': {a} → {b}"})

    legacy = (dst.get("template") or "") == "nxos_legacy.j2"
    if legacy:
        changes.append({"level": "warn", "text": "Legacy 7.x template — no VXLAN, NX-API, or BFD blocks."})

    return {
        "from": from_id,
        "to": to_id,
        "from_label": src.get("label", from_id),
        "to_label": dst.get("label", to_id),
        "changes": changes,
    }
