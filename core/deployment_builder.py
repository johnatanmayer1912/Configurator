"""
Deployment build helpers — export paths, uplink wiring, and build-phase utilities.

Extracted from api/main.py generate_deployment for testability and maintainability.
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

from models.interface_model import Interface

if TYPE_CHECKING:
    from models.device_model import Device


def resolve_deployment_export_base(
    output_dir: Optional[str],
    history_dir: Path,
    preview: bool,
) -> Path:
    """Resolve batch export directory; optional output_dir must stay under history vault."""
    batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_dir and str(output_dir).strip():
        candidate = Path(output_dir).expanduser().resolve()
        history_root = history_dir.resolve()
        if not str(candidate).startswith(str(history_root)):
            raise ValueError(
                f"output_dir must be under the configuration vault ({history_root})"
            )
        export_base = candidate / batch_timestamp
    else:
        export_base = history_dir / batch_timestamp
    if not preview:
        os.makedirs(export_base, exist_ok=True)
    return export_base


def parse_port_list(ports: str) -> List[str]:
    """Parse E1/5-6, E1/5,E1/6, or Ethernet1/5 style lists."""
    ports = (ports or "").strip()
    if not ports:
        return []
    if "," in ports:
        return [p.strip() for p in ports.split(",") if p.strip()]
    if "-" in ports:
        parts = ports.split("-")
        if len(parts) == 2:
            left = parts[0].strip()
            base = re.sub(r"\d+$", "", left)
            try:
                start_num = int(left.split("/")[-1])
                end_num = int(parts[1].strip())
                return [f"{base}{i}" for i in range(start_num, end_num + 1)]
            except ValueError:
                pass
    return [ports]


def normalize_port_name(port: str) -> str:
    port = port.strip()
    if port.startswith("E") and not port.startswith("Ethernet"):
        return "Ethernet" + port[1:]
    return port


def apply_custom_uplinks_for_switch(
    device: "Device",
    switch_hostname: str,
    uplinks: List[Any],
    all_hostnames: Set[str],
) -> None:
    """Apply deployment uplink definitions to one switch (source or destination)."""
    device.uplink_config = device.uplink_config or []

    for uplink in uplinks:
        if hasattr(uplink, "from_switch"):
            uplink_from = uplink.from_switch
            uplink_to = uplink.to_switch
            port_spec = uplink.ports_for(switch_hostname)
            po_id = uplink.po_id
        else:
            uplink_from = uplink.get("from")
            uplink_to = uplink.get("to")
            if switch_hostname == uplink_from:
                port_spec = uplink.get("from_ports") or uplink.get("ports", "")
            elif switch_hostname == uplink_to:
                port_spec = uplink.get("to_ports") or uplink.get("ports", "")
            else:
                continue
            po_id = uplink.get("po_id")

        is_source = uplink_from == switch_hostname
        is_destination = uplink_to == switch_hostname
        if not is_source and not is_destination:
            continue

        peer = uplink_to if is_source else uplink_from
        if peer not in all_hostnames:
            continue

        port_list = parse_port_list(port_spec)
        if not port_list:
            continue

        for port in port_list:
            full_port = normalize_port_name(port)
            short_port = port if port.startswith("E") else port.replace("Ethernet", "E")

            device.uplink_config.append({
                "interface": short_port,
                "description": f"to {peer}",
                "mode": "trunk",
                "port_channel": po_id,
            })

            iface_found = False
            for iface in device.interfaces:
                if iface.name == full_port or iface.name == port:
                    iface.description = f"to {peer}"
                    if po_id:
                        iface.channel_group = int(po_id)
                        iface.channel_mode = "active"
                    iface.mode = "trunk"
                    iface_found = True
                    break

            if not iface_found:
                new_iface = Interface(
                    name=full_port,
                    description=f"to {peer}",
                    mode="trunk",
                    shutdown=False,
                )
                if po_id:
                    new_iface.channel_group = int(po_id)
                    new_iface.channel_mode = "active"
                device.interfaces.append(new_iface)


def switches_blocked_by_vpc_errors(
    vpc_errors: List[str],
    vpc_pairs: List[Any],
) -> Set[str]:
    """Hostnames that must not export when their vPC pair failed validation."""
    if not vpc_errors:
        return set()
    blocked: Set[str] = set()
    for pair in vpc_pairs:
        domain = str(getattr(pair, "domain", None) or pair.get("domain", ""))
        if any(domain in err for err in vpc_errors):
            primary = getattr(pair, "primary", None) or pair.get("primary")
            secondary = getattr(pair, "secondary", None) or pair.get("secondary")
            if primary:
                blocked.add(primary)
            if secondary:
                blocked.add(secondary)
    return blocked
