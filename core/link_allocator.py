"""Port-channel and member port allocation, conflict detection, suggestions (A1/A3)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from core.po_map_store import next_free_po, role_for_po


def _parse_ports(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(p).strip() for p in raw if str(p).strip()]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    return []


def _eth_key(name: str) -> tuple:
    parts = name.replace("Ethernet", "").split("/")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0)


def build_reserved_inventory(
    *,
    model: str,
    peer_link_interfaces: Optional[List[str]] = None,
    keepalive_interfaces: Optional[List[str]] = None,
    port_channels: Optional[List[Dict[str, Any]]] = None,
    link_rows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Aggregate used Po IDs and member ports from wizard state."""
    po_map: Dict[int, Dict[str, Any]] = {}
    members: Dict[str, int] = {}

    def register_po(po_id: int, label: str, po_members: List[str], kind: str = "fabric") -> None:
        if po_id <= 0:
            return
        po_map[po_id] = {"label": label, "members": po_members, "kind": kind}

    register_po(1, "vPC peer-link", list(peer_link_interfaces or []), "peer_link")
    register_po(2, "vPC keepalive", list(keepalive_interfaces or []), "keepalive")

    for po in port_channels or []:
        num = int(po.get("number", po.get("po_id", 0)))
        register_po(
            num,
            po.get("description", f"Port-channel{num}"),
            _parse_ports(po.get("member_interfaces") or po.get("members")),
            po.get("kind", "device"),
        )

    for row in link_rows or []:
        if not row.get("enabled", True):
            continue
        po_id = int(row.get("po_id", 0))
        label = row.get("description") or row.get("label") or f"Fabric link {po_id}"
        register_po(po_id, label, _parse_ports(row.get("members")), row.get("link_kind", "fabric"))

    for po_id, meta in po_map.items():
        for port in meta.get("members") or []:
            members[port] = po_id

    return {"po_map": po_map, "members": members, "used_po_ids": sorted(po_map.keys())}


def validate_link_row(
    row: Dict[str, Any],
    inventory: Dict[str, Any],
    model: str,
    *,
    exclude_self_po: Optional[int] = None,
) -> Dict[str, Any]:
    """Return conflicts and suggestions for one fabric link row."""
    po_id = int(row.get("po_id", 0))
    members = _parse_ports(row.get("members"))
    po_map: Dict[int, Dict] = inventory.get("po_map") or {}
    member_map: Dict[str, int] = inventory.get("members") or {}
    conflicts: List[Dict[str, str]] = []

    if po_id > 0:
        existing = po_map.get(po_id)
        if existing and po_id != exclude_self_po:
            conflicts.append(
                {
                    "type": "po_id",
                    "message": f"Po{po_id} already used by {existing.get('label', 'another bundle')}",
                    "existing_label": str(existing.get("label", "")),
                }
            )

    for port in members:
        owner = member_map.get(port)
        if owner and owner != po_id and owner != exclude_self_po:
            conflicts.append(
                {
                    "type": "member",
                    "message": f"{port} is member of Po{owner}",
                    "port": port,
                    "existing_po": str(owner),
                }
            )

    role = role_for_po(po_id, model) if po_id else None
    suggestions: Dict[str, Any] = {}
    if conflicts:
        used = list(po_map.keys())
        kind = row.get("link_kind", "uplink")
        pref = "downlink" if kind == "downlink" else "uplink" if kind == "uplink" else "planner"
        suggestions["next_po_id"] = next_free_po(used, model, pref)
        suggestions["role_hint"] = role

    return {
        "valid": len(conflicts) == 0,
        "conflicts": conflicts,
        "suggestions": suggestions,
        "po_role": role,
    }


def suggest_members(
    *,
    hw_profile: Dict[str, Any],
    pool: str,
    count: int = 2,
    inventory: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Suggest free member ports from hardware pool (A3)."""
    inv = inventory or {"members": {}}
    used_members: Set[str] = set((inv.get("members") or {}).keys())
    reserved: Set[str] = set()
    for key in ("vpc_peer_link", "vpc_keepalive"):
        for p in hw_profile.get(key) or []:
            reserved.add(str(p))
    used_members.update(reserved)

    candidates: List[str] = []
    if pool == "fiber":
        for grp in hw_profile.get("port_groups") or []:
            if int(grp.get("start", 0)) < 49:
                continue
            end = int(grp.get("end", grp.get("start", 0)))
            for i in range(int(grp["start"]), end + 1):
                name = f"Ethernet1/{i}"
                if name not in used_members:
                    candidates.append(name)
    elif pool == "core":
        total = int(hw_profile.get("total_ports") or 0)
        for i in range(total, 0, -1):
            name = f"Ethernet1/{i}"
            if name not in used_members:
                candidates.append(name)
    else:
        total = int(hw_profile.get("total_ports") or 48)
        for i in range(1, total + 1):
            name = f"Ethernet1/{i}"
            if name not in used_members and name not in reserved:
                candidates.append(name)

    candidates.sort(key=_eth_key)
    return candidates[:count]


def port_budget(hw_profile: Dict[str, Any], inventory: Dict[str, Any]) -> Dict[str, Any]:
    """Capacity summary for I3."""
    total = int(hw_profile.get("total_ports") or 0)
    used = set((inventory.get("members") or {}).keys())
    reserved = set()
    for key in ("vpc_peer_link", "vpc_keepalive"):
        for p in hw_profile.get(key) or []:
            reserved.add(str(p))
    free = []
    if total:
        for i in range(1, total + 1):
            name = f"Ethernet1/{i}"
            if name not in used and name not in reserved:
                free.append(name)
    fiber = suggest_members(hw_profile=hw_profile, pool="fiber", count=99, inventory=inventory)
    return {
        "total_ports": total,
        "used_count": len(used),
        "reserved_count": len(reserved),
        "free_ports": free[:20],
        "free_count": len(free),
        "fiber_uplink_available": fiber,
        "po_used": inventory.get("used_po_ids") or [],
    }
