"""Apply manual VLAN/interface overrides from the wizard advanced section."""

from typing import Any, Dict, List, Optional

from models.device_model import Device
from models.interface_model import Interface
from models.vlan_model import VLAN
from models.l3_models import SVI


def apply_manual_overrides(device: Device, overrides: Optional[Dict[str, Any]]) -> None:
    """Merge optional custom VLANs, SVIs, and interfaces from UI overrides."""
    if not overrides:
        return

    extra_vlans = overrides.get("custom_vlans") or overrides.get("vlans")
    if isinstance(extra_vlans, list) and extra_vlans:
        existing_ids = {v.id for v in device.vlans}
        for item in extra_vlans:
            vid = int(item.get("id") or item.get("vlan_id", 0))
            if vid and 1 <= vid <= 4094 and vid not in existing_ids:
                device.vlans.append(VLAN(vid, item.get("name") or f"VLAN_{vid}"))
                existing_ids.add(vid)

    extra_svis = overrides.get("custom_svis") or overrides.get("svis")
    if isinstance(extra_svis, list) and extra_svis:
        existing_svi = {s.vlan_id for s in device.svis}
        for item in extra_svis:
            vid = int(item.get("vlan_id") or item.get("id", 0))
            ip = item.get("ip_address") or item.get("ip")
            if vid and 1 <= vid <= 4094 and ip and vid not in existing_svi:
                device.svis.append(SVI(vlan_id=vid, ip_address=ip, description=item.get("description")))

    extra_ints = overrides.get("custom_interfaces") or overrides.get("interfaces")
    if isinstance(extra_ints, list) and extra_ints:
        existing_names = {i.name for i in device.interfaces}
        for item in extra_ints:
            name = (item.get("name") or "").strip()
            if not name or name in existing_names:
                continue
            device.interfaces.append(
                Interface(
                    name=name,
                    mode=item.get("mode", "access"),
                    vlan=item.get("vlan"),
                    description=item.get("description"),
                    shutdown=item.get("shutdown", False),
                    vpc_id=item.get("vpc_id"),
                )
            )
            existing_names.add(name)

    # Plain-text interface lines: "Ethernet1/1" or "Ethernet1/1 mode access vlan 10"
    raw_lines = overrides.get("interface_lines")
    if isinstance(raw_lines, str) and raw_lines.strip():
        existing_names = {i.name for i in device.interfaces}
        for line in raw_lines.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            name = parts[0]
            if name in existing_names:
                continue
            mode, vlan = "access", None
            if "trunk" in line.lower():
                mode = "trunk"
            elif "routed" in line.lower():
                mode = "routed"
            for i, p in enumerate(parts):
                if p.lower() == "vlan" and i + 1 < len(parts):
                    try:
                        vlan = int(parts[i + 1])
                    except ValueError:
                        pass
            device.interfaces.append(Interface(name=name, mode=mode, vlan=vlan, description="MANUAL_OVERRIDE"))
            existing_names.add(name)
