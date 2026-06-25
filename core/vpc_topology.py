"""Build vPC port-channels, LAG members, and spare ports from hardware + scenario defaults."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from models.device_model import Device, VPCConfig
from models.interface_model import Interface
from models.port_channel_model import PortChannel


def _parse_port_list(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(p).strip() for p in raw if str(p).strip()]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.split(",") if p.strip()]
    return []


def _eth_sort_key(name: str) -> tuple:
    parts = name.replace("Ethernet", "").split("/")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0)


def _role_priority(vpc: VPCConfig, defaults: Dict[str, Any]) -> int:
    if vpc.role == "secondary":
        return int(defaults.get("vpc_role_priority_secondary", defaults.get("role_priority_secondary", 2000)))
    return int(defaults.get("vpc_role_priority_primary", defaults.get("role_priority_primary", vpc.role_priority)))


def apply_vpc_topology(
    device: Device,
    defaults: Dict[str, Any],
    hw_profile: Dict[str, Any],
    *,
    peer_hostname: Optional[str] = None,
) -> None:
    """Populate port-channels and interface list for institutional vPC designs."""
    if not device.vpc:
        return

    vpc = device.vpc
    peer_links = list(vpc.peer_link_interfaces)
    keepalive_ports = list(vpc.keepalive_interfaces)
    if not keepalive_ports:
        keepalive_ports = list(hw_profile.get("vpc_keepalive") or [])

    vpc.role_priority = _role_priority(vpc, defaults)
    vpc.peer_switch = bool(defaults.get("vpc_peer_switch", defaults.get("peer_switch", False)))
    if defaults.get("vpc_delay_restore") is not None:
        vpc.delay_restore = int(defaults["vpc_delay_restore"])
    elif defaults.get("delay_restore") is not None:
        vpc.delay_restore = int(defaults["delay_restore"])

    port_channels: List[PortChannel] = []
    used_ports: Set[str] = set()

    pl_desc = defaults.get(
        "peer_link_description",
        f"Connected_To_{peer_hostname or 'PEER'}_Peer-Link",
    )
    port_channels.append(
        PortChannel(
            number=vpc.peer_link_id,
            description=pl_desc,
            vpc_peer_link=True,
            spanning_tree_network=True,
            member_interfaces=peer_links,
        )
    )
    used_ports.update(peer_links)

    ka_po_id = int(defaults.get("keepalive_po_id", defaults.get("vpc_keepalive_po_id", vpc.keepalive_po_id)))
    vpc.keepalive_po_id = ka_po_id
    ka_desc = defaults.get(
        "keepalive_description",
        f"Connected_To_{peer_hostname or 'PEER'}_Peer-Keepalive",
    )
    local_ka_ip = vpc.local_keepalive_ip
    if "/" not in local_ka_ip:
        local_ka_ip = f"{local_ka_ip}/24"
    port_channels.append(
        PortChannel(
            number=ka_po_id,
            description=ka_desc,
            mode="l3",
            vpc_keepalive=True,
            vrf=vpc.keepalive_vrf,
            ip_address=local_ka_ip,
            member_interfaces=keepalive_ports,
        )
    )
    used_ports.update(keepalive_ports)

    # Optional downlink bundles (core → 10G / 1G leaf pairs)
    downlinks = defaults.get("downlinks") or []
    enabled_downlinks = []
    for item in downlinks:
        if isinstance(item, dict):
            if item.get("enabled", True):
                enabled_downlinks.append(item)
        elif isinstance(item, str):
            enabled_downlinks.append({"id": item, "enabled": True})

    downlink_overrides = defaults.get("downlink_options") or {}
    for item in enabled_downlinks:
        dl_id = item.get("id", "")
        if dl_id and dl_id in downlink_overrides and not downlink_overrides[dl_id]:
            continue
        po_id = int(item.get("po_id", item.get("port_channel", 0)))
        vpc_id = int(item.get("vpc_id", po_id))
        members = _parse_port_list(item.get("members") or item.get("interfaces"))
        if not members:
            continue
        mtu = item.get("mtu", defaults.get("downlink_mtu", 9216))
        port_channels.append(
            PortChannel(
                number=po_id,
                description=item.get("description", f"vPC_Downlink_{vpc_id}"),
                vpc_id=vpc_id,
                mtu=int(mtu) if mtu else None,
                member_interfaces=members,
            )
        )
        used_ports.update(members)

    _apply_fabric_uplink_bundles(port_channels, used_ports, defaults)
    device.port_channels = port_channels
    device.interfaces = _build_lag_and_spare_interfaces(
        device,
        used_ports,
        hw_profile,
        defaults,
        peer_hostname=peer_hostname,
    )


def apply_vpc_leaf_topology(
    device: Device,
    defaults: Dict[str, Any],
    hw_profile: Dict[str, Any],
    *,
    peer_hostname: Optional[str] = None,
) -> None:
    """Add vPC peer-link/keepalive (and optional downlinks) while preserving access/uplink ports."""
    if not device.vpc:
        return

    vpc = device.vpc
    peer_links = list(vpc.peer_link_interfaces)
    keepalive_ports = list(vpc.keepalive_interfaces)
    if not keepalive_ports:
        keepalive_ports = list(hw_profile.get("vpc_keepalive") or [])

    vpc.role_priority = _role_priority(vpc, defaults)
    vpc.peer_switch = bool(defaults.get("vpc_peer_switch", defaults.get("peer_switch", False)))
    if defaults.get("vpc_delay_restore") is not None:
        vpc.delay_restore = int(defaults["vpc_delay_restore"])
    elif defaults.get("delay_restore") is not None:
        vpc.delay_restore = int(defaults["delay_restore"])

    port_channels: List[PortChannel] = []
    used_ports: Set[str] = set()
    peer_label = peer_hostname or "SW2"

    pl_desc = defaults.get(
        "peer_link_description",
        f"Connected_To_{peer_label}_Peer-Link",
    )
    port_channels.append(
        PortChannel(
            number=vpc.peer_link_id,
            description=pl_desc,
            vpc_peer_link=True,
            spanning_tree_network=True,
            member_interfaces=peer_links,
        )
    )
    used_ports.update(peer_links)

    ka_po_id = int(defaults.get("keepalive_po_id", defaults.get("vpc_keepalive_po_id", vpc.keepalive_po_id)))
    vpc.keepalive_po_id = ka_po_id
    ka_desc = defaults.get(
        "keepalive_description",
        f"Connected_To_{peer_label}_Peer-Keepalive",
    )
    local_ka_ip = vpc.local_keepalive_ip
    if "/" not in local_ka_ip:
        local_ka_ip = f"{local_ka_ip}/24"
    port_channels.append(
        PortChannel(
            number=ka_po_id,
            description=ka_desc,
            mode="l3",
            vpc_keepalive=True,
            vrf=vpc.keepalive_vrf,
            ip_address=local_ka_ip,
            member_interfaces=keepalive_ports,
        )
    )
    used_ports.update(keepalive_ports)

    downlinks = defaults.get("downlinks") or []
    downlink_overrides = defaults.get("downlink_options") or {}
    for item in downlinks:
        if isinstance(item, dict):
            if not item.get("enabled", True):
                continue
            dl_id = item.get("id", "")
            if dl_id and dl_id in downlink_overrides and not downlink_overrides[dl_id]:
                continue
            po_id = int(item.get("po_id", item.get("port_channel", 0)))
            vpc_id = int(item.get("vpc_id", po_id))
            members = _parse_port_list(item.get("members") or item.get("interfaces"))
            if not members:
                continue
            mtu = item.get("mtu", defaults.get("downlink_mtu", 9216))
            port_channels.append(
                PortChannel(
                    number=po_id,
                    description=item.get("description", f"vPC_Downlink_{vpc_id}"),
                    vpc_id=vpc_id,
                    mtu=int(mtu) if mtu else None,
                    member_interfaces=members,
                )
            )
            used_ports.update(members)

    _apply_fabric_uplink_bundles(port_channels, used_ports, defaults)

    device.port_channels = port_channels
    device.interfaces = _merge_vpc_into_interfaces(
        device.interfaces,
        port_channels,
        used_ports,
        hw_profile,
        defaults,
        peer_hostname=peer_hostname,
    )


def _apply_fabric_uplink_bundles(
    port_channels: List[PortChannel],
    used_ports: Set[str],
    defaults: Dict[str, Any],
) -> None:
    """Add spine/uplink port-channels after peer-link, keepalive, and downlinks."""
    for item in defaults.get("uplinks") or []:
        if not isinstance(item, dict) or not item.get("enabled", True):
            continue
        members = _parse_port_list(item.get("members") or item.get("interfaces"))
        if not members:
            continue
        po_id = int(item.get("po_id", item.get("port_channel", 0)))
        vpc_id = item.get("vpc_id")
        if vpc_id is None:
            vpc_id = po_id
        mtu = item.get("mtu")
        port_channels.append(
            PortChannel(
                number=po_id,
                description=item.get("description", f"Connected_to_SPINE_{po_id}"),
                mode=str(item.get("mode", "trunk")),
                vpc_id=int(vpc_id) if vpc_id is not None else None,
                mtu=int(mtu) if mtu else None,
                member_interfaces=members,
            )
        )
        used_ports.update(members)


def _merge_vpc_into_interfaces(
    existing: List[Interface],
    port_channels: List[PortChannel],
    used_ports: Set[str],
    hw_profile: Dict[str, Any],
    defaults: Dict[str, Any],
    *,
    peer_hostname: Optional[str] = None,
) -> List[Interface]:
    by_name: Dict[str, Interface] = {intf.name: intf for intf in existing}
    peer_label = peer_hostname or "SW2"

    for po in port_channels:
        for port in po.member_interfaces:
            desc = _member_description(po, port, peer_label)
            mode = "trunk" if po.mode == "trunk" or po.vpc_peer_link else "routed"
            by_name[port] = Interface(
                name=port,
                mode=mode,
                description=desc,
                shutdown=False,
                channel_group=po.number,
                channel_mode="active",
                mtu=po.mtu,
            )

    if defaults.get("bring_up_spare_ports", True):
        total = int(hw_profile.get("total_ports") or 0)
        if total > 0:
            for idx in range(1, total + 1):
                name = f"Ethernet1/{idx}"
                if name in used_ports or name in by_name:
                    continue
                by_name[name] = Interface(name=name, mode="bare", shutdown=False)

    merged = list(by_name.values())
    merged.sort(key=lambda i: _eth_sort_key(i.name))
    return merged


def _build_lag_and_spare_interfaces(
    device: Device,
    used_ports: Set[str],
    hw_profile: Dict[str, Any],
    defaults: Dict[str, Any],
    *,
    peer_hostname: Optional[str] = None,
) -> List[Interface]:
    interfaces: List[Interface] = []
    peer_label = peer_hostname or "SW2"

    for po in device.port_channels:
        for port in po.member_interfaces:
            desc = _member_description(po, port, peer_label)
            intf = Interface(
                name=port,
                mode="trunk" if po.mode == "trunk" else "routed",
                description=desc,
                shutdown=False,
                channel_group=po.number,
                channel_mode="active",
                mtu=po.mtu,
            )
            if po.vpc_peer_link:
                intf.mode = "trunk"
            interfaces.append(intf)

    if defaults.get("bring_up_spare_ports", True):
        total = int(hw_profile.get("total_ports") or 0)
        if total > 0:
            for idx in range(1, total + 1):
                name = f"Ethernet1/{idx}"
                if name in used_ports:
                    continue
                if any(i.name == name for i in interfaces):
                    continue
                interfaces.append(Interface(name=name, mode="bare", shutdown=False))

    interfaces.sort(key=lambda i: _eth_sort_key(i.name))
    return interfaces


def _member_description(po: PortChannel, port: str, peer_label: str) -> str:
    if po.vpc_peer_link:
        return f"Part_Of_Vpc_PEERLINK_To_{peer_label}"
    if po.vpc_keepalive:
        return f"Part_Of_Vpc_KEEPALIVE_To_{peer_label}"
    if po.vpc_id:
        desc_upper = (po.description or "").upper()
        if "SPINE" in desc_upper or "UPLINK" in desc_upper:
            return f"Part_Of_VPC{po.vpc_id}_Uplink"
        return f"Part_Of_VPC{po.vpc_id}_Downlink"
    return f"Part_Of_Port-Channel{po.number}"
