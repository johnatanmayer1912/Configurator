"""Resolve fabric link presets (downlinks/uplinks) from hardware profiles and operator overrides."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set


def _eth_sort_key(name: str) -> tuple:
    parts = name.replace("Ethernet", "").split("/")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0)


def _parse_port_list(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(p).strip() for p in raw if str(p).strip()]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    return []


def reserved_vpc_ports(hw_profile: Dict[str, Any]) -> Set[str]:
    excluded: Set[str] = set()
    for key in ("vpc_peer_link", "vpc_keepalive"):
        for port in hw_profile.get(key) or []:
            excluded.add(str(port))
    return excluded


def fiber_uplink_pool(hw_profile: Dict[str, Any]) -> List[str]:
    """QSFP/SFP+ uplink candidates (Eth1/49+), excluding vPC peer-link and keepalive."""
    excluded = reserved_vpc_ports(hw_profile)
    pool: List[str] = []
    for grp in hw_profile.get("port_groups") or []:
        start = int(grp.get("start", 0))
        if start < 49:
            continue
        end = int(grp.get("end", start))
        for idx in range(start, end + 1):
            name = f"Ethernet1/{idx}"
            if name not in excluded:
                pool.append(name)
    pool.sort(key=_eth_sort_key)
    return pool


def core_uplink_pool(hw_profile: Dict[str, Any], *, count: int = 2) -> List[str]:
    """40G core uplink candidates — highest ports not used by vPC wiring."""
    excluded = reserved_vpc_ports(hw_profile)
    total = int(hw_profile.get("total_ports") or 0)
    candidates: List[str] = []
    if total > 0:
        for idx in range(total, 0, -1):
            name = f"Ethernet1/{idx}"
            if name in excluded:
                continue
            candidates.append(name)
            if len(candidates) >= count:
                break
    candidates.sort(key=_eth_sort_key)
    return candidates


def resolve_link_members(preset: Dict[str, Any], hw_profile: Dict[str, Any]) -> List[str]:
    explicit = _parse_port_list(preset.get("members"))
    if explicit:
        return explicit
    source = preset.get("members_from", "")
    if source == "fiber_pool":
        pool = fiber_uplink_pool(hw_profile)
        return pool[:2]
    if source == "fiber_pool_secondary":
        pool = fiber_uplink_pool(hw_profile)
        return pool[2:4]
    if source == "core_pool":
        return core_uplink_pool(hw_profile, count=2)
    return []


def resolve_link_plans(
    *,
    scenario_id: str,
    defaults: Dict[str, Any],
    catalog,
    hw_profile: Dict[str, Any],
    kind: str,
    deployment_switches: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Resolve downlink or uplink preset list for a scenario."""
    explicit_key = "downlinks" if kind == "downlink" else "uplinks"
    explicit = defaults.get(explicit_key)
    if isinstance(explicit, list) and explicit and isinstance(explicit[0], dict):
        if any("members" in item or "po_id" in item for item in explicit):
            return [_normalize_link_entry(item, hw_profile) for item in explicit if item.get("enabled", True)]

    row = catalog.get_matrix_row(scenario_id) or {}
    preset_key = "downlink_presets" if kind == "downlink" else "uplink_presets"
    allowed_raw = row.get(preset_key)
    allowed_list = list(allowed_raw) if allowed_raw is not None else None
    options_key = "downlink_options" if kind == "downlink" else "uplink_options"
    options = defaults.get(options_key) or {}

    if kind == "downlink":
        presets = {p["id"]: p for p in catalog.list_downlink_presets()}
    else:
        presets = {p["id"]: p for p in catalog.list_uplink_presets()}

    resolved: List[Dict[str, Any]] = []
    for preset_id, preset in presets.items():
        if allowed_list is not None:
            if preset_id not in allowed_list:
                enabled = bool(options.get(preset_id, False))
            else:
                enabled = bool(options.get(preset_id, preset.get("default", False)))
        else:
            enabled = bool(options.get(preset_id, preset.get("default", False)))
        if not enabled:
            continue
        entry = _normalize_link_entry(preset, hw_profile)
        entry["id"] = preset_id
        entry["enabled"] = True
        if kind == "downlink":
            entry["link_kind"] = "downlink"
        else:
            entry["link_kind"] = "uplink"
        
        # Replace generic preset descriptions with actual hostnames in multi-switch deployments
        if deployment_switches and entry.get("description"):
            entry["description"] = _replace_preset_description_with_hostnames(
                entry["description"], 
                preset_id, 
                deployment_switches, 
                kind,
                catalog
            )
        
        resolved.append(entry)

    return resolved


def _replace_preset_description_with_hostnames(
    description: str, 
    preset_id: str, 
    deployment_switches: List[Dict[str, Any]], 
    kind: str,
    catalog
) -> str:
    """Replace generic preset descriptions with actual switch hostnames."""
    # For downlink presets, replace generic leaf references with actual hostnames
    if kind == "downlink":
        if "NET_LEAF_10G" in description:
            # Find 10G leaf switches
            leaf_10g = [s for s in deployment_switches if s.model and catalog.get_hardware_profile(s.model) and catalog.get_hardware_profile(s.model).get("device_class") == "leaf_10g"]
            if leaf_10g:
                hostnames = " + ".join([s.hostname for s in leaf_10g])
                return description.replace("NET_LEAF_10G_SW1+SW2", hostnames)
        elif "NET_LEAF_1G" in description:
            # Find 1G leaf switches
            leaf_1g = [s for s in deployment_switches if s.model and catalog.get_hardware_profile(s.model) and catalog.get_hardware_profile(s.model).get("device_class") == "leaf_1g"]
            if leaf_1g:
                hostnames = " + ".join([s.hostname for s in leaf_1g])
                return description.replace("NET_LEAF_1G_SW1+SW2", hostnames)
    
    # For uplink presets, replace generic spine references with actual hostnames
    if kind == "uplink":
        if "SPINE" in description:
            # Find spine switches (handle both spine and core device classes)
            spine = [s for s in deployment_switches if s.model and catalog.get_hardware_profile(s.model) and catalog.get_hardware_profile(s.model).get("device_class") in ["spine", "core"]]
            if spine:
                hostnames = " + ".join([s.hostname for s in spine])
                return description.replace("SPINE_PAIR", hostnames).replace("SPINE", hostnames)
    
    return description


def _normalize_link_entry(item: Dict[str, Any], hw_profile: Dict[str, Any]) -> Dict[str, Any]:
    members = _parse_port_list(item.get("members"))
    if not members:
        members = resolve_link_members(item, hw_profile)
    po_id = int(item.get("po_id", item.get("port_channel", 0)))
    vpc_id = item.get("vpc_id")
    if vpc_id is None:
        vpc_id = po_id
    return {
        "id": item.get("id", ""),
        "enabled": bool(item.get("enabled", True)),
        "po_id": po_id,
        "vpc_id": int(vpc_id) if vpc_id is not None else None,
        "description": str(item.get("description", f"Fabric_Link_{po_id}")),
        "members": members,
        "mode": str(item.get("mode", "trunk")),
        "mtu": item.get("mtu"),
        "link_kind": item.get("link_kind", "downlink" if "leaf" in str(item.get("id", "")).lower() else "uplink"),
    }
