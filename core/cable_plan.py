"""Cable plan export — human-readable wiring sheet for installers (D5)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _parse_members(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(p) for p in raw if p]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    return []


def build_cable_plan(
    *,
    hostname: str,
    model: str,
    site_name: str,
    scenario_name: str,
    port_channels: List[Dict[str, Any]],
    pair_hostname: Optional[str] = None,
) -> Dict[str, Any]:
    """Build structured cable plan from device port-channel list."""
    rows: List[Dict[str, str]] = []
    for po in port_channels:
        po_id = po.get("number", po.get("po_id"))
        desc = po.get("description", "")
        members = _parse_members(po.get("member_interfaces") or po.get("members"))
        role = "peer-link" if po.get("vpc_peer_link") else "keepalive" if po.get("vpc_keepalive") else "fabric"
        if "SPINE" in desc.upper() or po.get("link_kind") == "uplink":
            role = "uplink"
        if "LEAF" in desc.upper() or po.get("link_kind") == "downlink":
            role = "downlink"
        remote = pair_hostname if role in {"peer-link", "keepalive"} else _guess_remote(desc, role)
        for port in members:
            rows.append(
                {
                    "local_device": hostname,
                    "local_port": port,
                    "local_po": f"port-channel{po_id}",
                    "role": role,
                    "description": desc,
                    "remote_device": remote,
                    "remote_port": "— (label during install)",
                    "cable_type": _cable_hint(model, port, role),
                }
            )

    return {
        "schema_version": 1,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "site": site_name,
        "hostname": hostname,
        "model": model,
        "scenario": scenario_name,
        "pair_hostname": pair_hostname,
        "rows": rows,
    }


def _guess_remote(desc: str, role: str) -> str:
    if role == "uplink":
        return "SPINE_PAIR (both switches)"
    if role == "downlink":
        return "LEAF_PAIR (dual-homed)"
    return "PEER" if "PEER" in desc.upper() else "TBD"


def _cable_hint(model: str, port: str, role: str) -> str:
    try:
        num = int(port.replace("Ethernet1/", ""))
    except ValueError:
        return "Check optics"
    if num >= 49:
        return "SFP+/QSFP per model (fiber)"
    if "9336" in model:
        return "QSFP28 DAC/AOC (40G)"
    return "DAC/AOC per site standard"


def render_cable_plan_md(plan: Dict[str, Any]) -> str:
    lines = [
        f"# Cable Plan — {plan.get('hostname', 'switch')}",
        "",
        f"**Site:** {plan.get('site', '')}  ",
        f"**Model:** {plan.get('model', '')}  ",
        f"**Scenario:** {plan.get('scenario', '')}  ",
        f"**Generated:** {plan.get('generated', '')}  ",
    ]
    if plan.get("pair_hostname"):
        lines.append(f"**vPC peer:** {plan['pair_hostname']}  ")
    lines.extend(
        [
            "",
            "## Instructions",
            "",
            "1. Label both ends of each cable before rack install.",
            "2. Peer-link and keepalive connect only between the two vPC switches.",
            "3. Uplinks go to the spine pair; downlinks to dual-homed leaf/access pairs.",
            "4. Fill in **Remote port** on site copy when patched.",
            "",
            "## Wiring table",
            "",
            "| Local device | Local port | Port-channel | Role | Remote device | Remote port | Cable |",
            "|--------------|------------|--------------|------|---------------|-------------|-------|",
        ]
    )
    for row in plan.get("rows") or []:
        lines.append(
            f"| {row['local_device']} | {row['local_port']} | {row['local_po']} | {row['role']} | "
            f"{row['remote_device']} | {row['remote_port']} | {row['cable_type']} |"
        )
    lines.extend(["", "## Post-patch verification", "", "```", "show interface status", "show port-channel summary", "show vpc brief", "```"])
    return "\n".join(lines)
