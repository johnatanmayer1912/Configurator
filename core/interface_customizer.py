"""Apply per-interface plans from the Interface Planner UI."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

from models.device_model import Device
from models.interface_model import Interface
from models.port_channel_model import PortChannel
from models.vlan_model import VLAN

VPC_PO_START = 10
_ETH_RE = re.compile(r"^Ethernet1/(\d+)$", re.IGNORECASE)


def normalize_interface_name(raw: str) -> str:
    name = (raw or "").strip()
    if not name:
        return ""
    name = name.replace("eth", "Ethernet").replace("Eth", "Ethernet")
    if name.lower().startswith("ethernet"):
        parts = name.split("/")
        if len(parts) == 2:
            try:
                return f"Ethernet1/{int(parts[1])}"
            except ValueError:
                pass
    return name


def _eth_sort_key(name: str) -> tuple:
    m = _ETH_RE.match(name)
    if m:
        return (1, int(m.group(1)))
    return (0, 0)


def _reserved_ports(device: Device) -> Set[str]:
    reserved: Set[str] = set()
    if device.vpc:
        reserved.update(device.vpc.peer_link_interfaces)
        reserved.update(device.vpc.keepalive_interfaces)
    for po in device.port_channels:
        reserved.update(po.member_interfaces)
    for intf in device.interfaces:
        if intf.mode == "trunk" and intf.trunk_vlans and intf.name not in reserved:
            if intf.description and intf.description.startswith("Uplink_"):
                reserved.add(intf.name)
    return reserved


def _used_po_numbers(device: Device) -> Set[int]:
    return {po.number for po in device.port_channels}


def _next_vpc_po_number(device: Device, start: int = VPC_PO_START) -> int:
    used = _used_po_numbers(device)
    n = start
    while n in used:
        n += 1
    return n


def _ensure_vlan(device: Device, vlan_id: int, vlan_name: Optional[str] = None) -> None:
    if not (1 <= vlan_id <= 4094):
        return
    for v in device.vlans:
        if v.id == vlan_id:
            if vlan_name and vlan_name.strip() and not v.name:
                v.name = vlan_name.strip()
            return
    device.vlans.append(VLAN(vlan_id, (vlan_name or f"VLAN_{vlan_id}").strip()))
    device.vlans.sort(key=lambda x: x.id)


def _upsert_interface(device: Device, name: str, **fields) -> Interface:
    for intf in device.interfaces:
        if intf.name == name:
            for key, val in fields.items():
                if val is not None or key in {"vlan", "trunk_vlans", "description", "custom_lines"}:
                    setattr(intf, key, val)
            return intf
    intf = Interface(name=name, shutdown=False, **fields)
    device.interfaces.append(intf)
    device.interfaces.sort(key=lambda i: _eth_sort_key(i.name))
    return intf


def _parse_custom_lines(raw: Any) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        lines = [str(x).strip() for x in raw if str(x).strip()]
    else:
        lines = [ln.strip() for ln in str(raw).splitlines() if ln.strip()]
    cleaned: List[str] = []
    for ln in lines:
        cleaned.append(re.sub(r"^\s{2}", "", ln))
    return cleaned


def _member_description(po: PortChannel, port: str) -> str:
    if po.vpc_peer_link:
        return f"Part_Of_Vpc_PEERLINK"
    if po.vpc_keepalive:
        return f"Part_Of_Vpc_KEEPALIVE"
    if po.vpc_id and po.mode == "access":
        return f"Part_Of_vPC{po.vpc_id}_Access_{port.replace('Ethernet', 'Eth')}"
    if po.vpc_id:
        return f"Part_Of_vPC{po.vpc_id}_Trunk_{port.replace('Ethernet', 'Eth')}"
    return f"Part_Of_Port-Channel{po.number}"


def apply_interface_customizations(
    device: Device,
    defaults: Optional[Dict[str, Any]],
    *,
    vpc_pair: bool = False,
    po_start: int = VPC_PO_START,
) -> None:
    """Merge interface_plans from wizard overrides onto device model."""
    if not defaults:
        return
    plans = defaults.get("interface_plans")
    if not isinstance(plans, list) or not plans:
        return

    reserved = _reserved_ports(device)
    storm = "storm_control" in (defaults.get("features") or device.enabled_features or [])

    for plan in plans:
        if not isinstance(plan, dict):
            continue
        iface = normalize_interface_name(plan.get("interface", ""))
        if not iface or iface in reserved:
            continue

        preset = str(plan.get("preset") or "custom").lower()
        user_desc = (plan.get("description") or "").strip()
        custom_lines = _parse_custom_lines(plan.get("custom_cli"))
        use_vpc_po = bool(plan.get("vpc_port_channel")) and vpc_pair and device.vpc is not None
        po_capable = preset in {"access_vlan", "trunk_all", "trunk_custom"}
        if vpc_pair and device.vpc and po_capable and plan.get("vpc_port_channel") is not False:
            use_vpc_po = True

        if preset == "custom" or (custom_lines and preset != "bring_up"):
            desc = user_desc or "Custom_Interface"
            _upsert_interface(
                device,
                iface,
                mode="bare",
                description=desc,
                vlan=None,
                trunk_vlans=None,
                channel_group=None,
                custom_lines=custom_lines or None,
            )
            continue

        if use_vpc_po:
            mode = str(plan.get("mode") or "access").lower()
            po_num = _next_vpc_po_number(device, po_start)
            vpc_id = int(plan.get("vpc_id") or po_num)

            if mode == "access":
                vlan_id = int(plan.get("vlan_id") or 0)
                if vlan_id < 1:
                    continue
                vlan_name = (plan.get("vlan_name") or "").strip()
                _ensure_vlan(device, vlan_id, vlan_name)
                po_desc = user_desc or f"vPC_Access_VLAN{vlan_id}"
                po = PortChannel(
                    number=po_num,
                    description=po_desc,
                    mode="access",
                    vpc_id=vpc_id,
                    access_vlan=vlan_id,
                    member_interfaces=[iface],
                )
            else:
                trunk_vlans = (plan.get("trunk_vlans") or "1-4094").strip()
                po_desc = user_desc or f"vPC_Trunk_{iface.replace('Ethernet', 'Eth')}"
                po = PortChannel(
                    number=po_num,
                    description=po_desc,
                    mode="trunk",
                    vpc_id=vpc_id,
                    trunk_vlans=trunk_vlans,
                    member_interfaces=[iface],
                )

            device.port_channels.append(po)
            member_mode = "trunk" if mode == "trunk" else "access"
            _upsert_interface(
                device,
                iface,
                mode=member_mode,
                description=_member_description(po, iface),
                vlan=None,
                trunk_vlans=None,
                channel_group=po_num,
                channel_mode="active",
                custom_lines=None,
            )
            continue

        if preset == "bring_up":
            _upsert_interface(
                device,
                iface,
                mode="bare",
                description=user_desc or None,
                vlan=None,
                trunk_vlans=None,
                channel_group=None,
                custom_lines=None,
            )
        elif preset == "access_vlan":
            vlan_id = int(plan.get("vlan_id") or 0)
            if vlan_id < 1:
                continue
            vlan_name = (plan.get("vlan_name") or "").strip()
            _ensure_vlan(device, vlan_id, vlan_name)
            _upsert_interface(
                device,
                iface,
                mode="access",
                vlan=vlan_id,
                description=user_desc or f"Access_VLAN{vlan_id}",
                trunk_vlans=None,
                channel_group=None,
                custom_lines=None,
            )
        elif preset in {"trunk_all", "trunk_custom"}:
            trunk_vlans = (plan.get("trunk_vlans") or "1-4094").strip()
            _upsert_interface(
                device,
                iface,
                mode="trunk",
                trunk_vlans=trunk_vlans,
                description=user_desc or "Trunk_Port",
                vlan=None,
                channel_group=None,
                custom_lines=None,
            )
        elif preset == "routed":
            _upsert_interface(
                device,
                iface,
                mode="routed",
                description=user_desc or "Routed_Port",
                vlan=None,
                trunk_vlans=None,
                channel_group=None,
                custom_lines=None,
            )

        if storm and preset == "access_vlan" and not use_vpc_po:
            pass  # storm-control rendered by template for access mode


def validate_interface_plans(
    device: Device,
    defaults: Optional[Dict[str, Any]],
    *,
    vpc_pair: bool = False,
) -> List[str]:
    """Return human-readable warnings for plans that will not be applied."""
    if not defaults:
        return []
    plans = defaults.get("interface_plans")
    if not isinstance(plans, list) or not plans:
        return []

    reserved = _reserved_ports(device)
    warnings: List[str] = []

    for plan in plans:
        if not isinstance(plan, dict):
            continue
        iface = normalize_interface_name(plan.get("interface", ""))
        if not iface:
            warnings.append("Interface Planner: port name is required for each row.")
            continue
        if iface in reserved:
            warnings.append(f"Interface Planner: {iface} is reserved (peer-link, keepalive, or downlink) — skipped.")
            continue

        preset = str(plan.get("preset") or "custom").lower()
        use_vpc_po = bool(plan.get("vpc_port_channel")) and vpc_pair and device.vpc is not None
        po_capable = preset in {"access_vlan", "trunk_all", "trunk_custom"}
        if vpc_pair and device.vpc and po_capable and plan.get("vpc_port_channel") is not False:
            use_vpc_po = True

        if use_vpc_po and str(plan.get("mode") or "access").lower() == "access":
            vlan_id = int(plan.get("vlan_id") or 0)
            if vlan_id < 1:
                warnings.append(f"Interface Planner: {iface} needs a VLAN ID for vPC port-channel access mode.")

    return warnings
