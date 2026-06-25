"""Parse NX-OS running-config snippets into structured hints for the Config Builder."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


FEATURE_MAP = {
    "interface-vlan": "interface_vlan",
    "vpc": "vpc",
    "lacp": "lacp",
    "lldp": "lldp",
    "hsrp": "hsrp",
    "bfd": "bfd",
    "nxapi": "nxapi",
    "bash-shell": "bash",
    "nv overlay": "vxlan",
}

ROLE_HINTS = {
    "access": ["access", "idf", "closet", "edge"],
    "leaf": ["leaf", "tor", "rack"],
    "spine": ["spine", "core", "fabric"],
}


@dataclass
class ParsedConfig:
    hostname: str = ""
    mgmt_ip: str = ""
    mgmt_gw: str = ""
    motd: str = ""
    features: List[str] = field(default_factory=list)
    vlans: List[Dict[str, Any]] = field(default_factory=list)
    vpc_domain_id: Optional[int] = None
    vpc_peer_link_interfaces: List[str] = field(default_factory=list)
    local_keepalive_ip: str = ""
    remote_keepalive_ip: str = ""
    ntp_servers: List[str] = field(default_factory=list)
    logging_hosts: List[str] = field(default_factory=list)
    snmp_location: str = ""
    access_port_count: int = 0
    trunk_port_count: int = 0
    svi_count: int = 0
    has_hsrp: bool = False
    interface_lines: List[str] = field(default_factory=list)
    raw_line_count: int = 0

    def detect_role(self) -> str:
        host = self.hostname.lower()
        for role, tokens in ROLE_HINTS.items():
            if any(t in host for t in tokens):
                return role
        if self.vpc_domain_id or "vpc" in self.features:
            return "leaf"
        if self.svi_count >= 2 or self.has_hsrp:
            return "leaf"
        if self.access_port_count >= 12:
            return "access"
        if self.trunk_port_count > self.access_port_count:
            return "spine"
        return "access"

    @property
    def has_vpc(self) -> bool:
        return self.vpc_domain_id is not None or "vpc" in self.features

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hostname": self.hostname,
            "mgmt_ip": self.mgmt_ip,
            "mgmt_gw": self.mgmt_gw,
            "motd": self.motd,
            "features": self.features,
            "vlans": self.vlans,
            "vpc_domain_id": self.vpc_domain_id,
            "vpc_peer_link_interfaces": self.vpc_peer_link_interfaces,
            "local_keepalive_ip": self.local_keepalive_ip,
            "remote_keepalive_ip": self.remote_keepalive_ip,
            "ntp_servers": self.ntp_servers,
            "logging_hosts": self.logging_hosts,
            "snmp_location": self.snmp_location,
            "access_port_count": self.access_port_count,
            "trunk_port_count": self.trunk_port_count,
            "svi_count": self.svi_count,
            "has_hsrp": self.has_hsrp,
            "interface_lines": self.interface_lines[:20],
            "raw_line_count": self.raw_line_count,
            "detected_role": self.detect_role(),
            "has_vpc": self.has_vpc,
        }


def parse_running_config(text: str) -> ParsedConfig:
    """Best-effort parser for pasted NX-OS running-config."""
    parsed = ParsedConfig()
    if not text or not text.strip():
        return parsed

    lines = [ln.rstrip() for ln in text.splitlines()]
    parsed.raw_line_count = len(lines)

    vlan_ids: Set[int] = set()
    current_vlan: Optional[int] = None
    current_intf: Optional[str] = None
    intf_mode = ""
    peer_link_members: List[str] = []
    peer_link_po_number: Optional[int] = None
    current_po_id: Optional[int] = None

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("!"):
            continue

        if line.startswith("banner motd "):
            parsed.motd = line[12:].strip().strip("#").strip()
            continue

        if line.startswith("hostname "):
            parsed.hostname = line.split(None, 1)[1].strip()
            continue

        if line.startswith("feature "):
            feat = line[8:].strip().lower()
            for key, fid in FEATURE_MAP.items():
                if key in feat and fid not in parsed.features:
                    parsed.features.append(fid)
            continue

        if line.startswith("vlan "):
            try:
                current_vlan = int(line.split()[1])
                vlan_ids.add(current_vlan)
            except (IndexError, ValueError):
                current_vlan = None
            continue

        if current_vlan and line.startswith("name "):
            parsed.vlans.append({"id": current_vlan, "name": line[5:].strip()})
            continue

        if line.startswith("interface "):
            current_intf = line.split(None, 1)[1].strip()
            intf_mode = ""
            current_po_id = None
            if current_intf.lower().startswith("port-channel"):
                try:
                    current_po_id = int(re.sub(r"\D", "", current_intf.split()[-1]) or "0") or None
                except ValueError:
                    current_po_id = None
            continue

        if current_intf and current_intf.lower() == "mgmt0" and line.startswith("ip address "):
            parts = line.split()
            if len(parts) >= 3:
                parsed.mgmt_ip = parts[2] if "/" in parts[2] else f"{parts[2]}/{parts[4]}" if len(parts) >= 5 else parts[2]
            continue

        if line.startswith("ip route ") and "0.0.0.0/0" in line:
            parts = line.split()
            if parts:
                parsed.mgmt_gw = parts[-1]
            continue

        if line.startswith("vpc domain "):
            try:
                parsed.vpc_domain_id = int(line.split()[2])
            except (IndexError, ValueError):
                pass
            continue

        if "peer-keepalive destination" in line:
            m = re.search(r"destination\s+(\S+)", line)
            if m:
                parsed.remote_keepalive_ip = m.group(1).split("/")[0]
            m2 = re.search(r"source\s+(\S+)", line)
            if m2:
                parsed.local_keepalive_ip = m2.group(1).split("/")[0]
            continue

        if current_intf and line == "vpc peer-link":
            if current_po_id is not None:
                peer_link_po_number = current_po_id
            continue

        if current_intf and line.startswith("channel-group ") and "mode active" in line:
            m = re.match(r"channel-group\s+(\d+)", line)
            if m and peer_link_po_number and int(m.group(1)) == peer_link_po_number:
                if current_intf.lower().startswith("ethernet"):
                    peer_link_members.append(current_intf)
            continue

        if line.startswith("ntp server "):
            srv = line.split()[2]
            if srv not in parsed.ntp_servers:
                parsed.ntp_servers.append(srv)
            continue

        if line.startswith("logging server "):
            srv = line.split()[2]
            if srv not in parsed.logging_hosts:
                parsed.logging_hosts.append(srv)
            if "logging" not in parsed.features:
                parsed.features.append("logging")
            continue

        if line.startswith("snmp-server location "):
            parsed.snmp_location = line[21:].strip()
            if "snmp" not in parsed.features:
                parsed.features.append("snmp")
            continue

        if current_intf and line.startswith("switchport mode access"):
            intf_mode = "access"
            continue
        if current_intf and line.startswith("switchport mode trunk"):
            intf_mode = "trunk"
            continue

        if current_intf and line.startswith("hsrp "):
            parsed.has_hsrp = True
            if "hsrp" not in parsed.features:
                parsed.features.append("hsrp")
            continue

        if current_intf and line == "no shutdown" and current_intf.lower().startswith("ethernet"):
            if intf_mode == "access":
                parsed.access_port_count += 1
            elif intf_mode == "trunk":
                parsed.trunk_port_count += 1
            parsed.interface_lines.append(current_intf)
            current_intf = None

        if current_intf and current_intf.lower().startswith("vlan"):
            parsed.svi_count += 1

    if peer_link_members:
        parsed.vpc_peer_link_interfaces = peer_link_members
    elif parsed.vpc_domain_id:
        parsed.vpc_peer_link_interfaces = []

    for vid in sorted(vlan_ids):
        if not any(v.get("id") == vid for v in parsed.vlans):
            parsed.vlans.append({"id": vid, "name": f"VLAN_{vid}"})

    if parsed.ntp_servers and "ntp" not in parsed.features:
        parsed.features.append("ntp")

    return parsed
