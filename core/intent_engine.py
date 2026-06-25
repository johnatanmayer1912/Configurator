from typing import List, Tuple

from models.device_model import Device, VPCConfig
from models.interface_model import Interface
from models.intent_model import BlueprintIntent, BlueprintResolution
from models.vlan_model import VLAN
from models.l3_models import SVI


class IntentEngine:
    def resolve(self, intent: BlueprintIntent) -> Tuple[Device, BlueprintResolution]:
        role = intent.role.lower().strip()
        if role not in {"access", "leaf", "spine"}:
            raise ValueError("Intent role must be access, leaf, or spine.")

        vlan_start = intent.overrides.base_access_vlan
        vlan_count = intent.overrides.access_vlan_count
        vlans = self._build_vlans(role, vlan_start, vlan_count)
        interfaces = self._build_interfaces(role, intent.overrides.interface_count, vlan_start, intent.uplink_ports)
        svis = self._build_svis(role, vlans)

        motd = intent.overrides.motd or self._default_motd(intent.site_name, role, intent.security_tier)
        admin_user = intent.overrides.admin_user or "admin"
        admin_password = intent.overrides.admin_password or ""

        device_vpc = None
        if intent.redundancy_mode.lower() == "vpc" and role in {"leaf", "spine"}:
            # Peer-link ports are assigned by ScenarioEngine from hardware profile / UI overrides.
            device_vpc = VPCConfig(
                domain_id=100,
                role="primary",
                keepalive_vrf="management",
                local_keepalive_ip="10.255.255.1",
                remote_keepalive_ip="10.255.255.2",
                peer_link_id=100,
                peer_link_interfaces=[],
            )

        device = Device(
            hostname=intent.hostname,
            mgmt_ip=intent.mgmt_ip,
            mgmt_gw=intent.mgmt_gw,
            model=intent.model,
            vlans=vlans,
            interfaces=interfaces,
            svis=svis,
            vpc=device_vpc,
            motd=motd,
            admin_user=admin_user,
            admin_password=admin_password,
        )

        resolution = BlueprintResolution(
            profile_name=f"{role.upper()}_{intent.security_tier.upper()}",
            summary_lines=[
                f"Site: {intent.site_name}",
                f"Role: {role}",
                f"Model: {intent.model}",
                f"Redundancy: {intent.redundancy_mode}",
                f"Access VLAN range: {vlans[0].id if vlans else '-'} to {vlans[-1].id if vlans else '-'}",
                f"Interfaces generated: {len(interfaces)}",
            ],
            policy_flags={
                "stp_edge_defaults": "enabled" if role == "access" else "restricted",
                "vpc_enabled": "yes" if device_vpc else "no",
                "security_tier": intent.security_tier,
            },
        )
        return device, resolution

    def _build_vlans(self, role: str, start: int, count: int) -> List[VLAN]:
        prefix = {"access": "USER", "leaf": "FABRIC", "spine": "TRANSIT"}[role]
        return [VLAN(id=start + i, name=f"{prefix}_{start + i}") for i in range(count)]

    def _eth_sort_key(self, name: str) -> tuple:
        parts = name.replace("Ethernet", "").split("/")
        try:
            return tuple(int(p) for p in parts)
        except ValueError:
            return (0, 0)

    def _build_interfaces(self, role: str, count: int, access_vlan: int, uplink_ports: List[str]) -> List[Interface]:
        interfaces: List[Interface] = []
        uplink_set = set(uplink_ports)
        access_idx = 0
        for idx in range(1, count + 1):
            name = f"Ethernet1/{idx}"
            if name in uplink_set:
                continue
            intf_mode = "access" if role != "spine" else "routed"
            if intf_mode == "access":
                access_idx += 1
                desc = f"Access_Port_{access_idx}"
            else:
                desc = f"Routed_Port_{idx}"
            interfaces.append(
                Interface(
                    name=name,
                    mode=intf_mode,
                    vlan=access_vlan if intf_mode == "access" else None,
                    description=desc,
                    shutdown=False,
                )
            )

        uplink_idx = 0
        existing = {i.name for i in interfaces}
        for name in sorted(uplink_set, key=self._eth_sort_key):
            uplink_idx += 1
            desc = f"Uplink_{uplink_idx}"
            if name in existing:
                for intf in interfaces:
                    if intf.name == name:
                        intf.mode = "trunk"
                        intf.description = desc
                        intf.vlan = None
                        intf.trunk_vlans = "1-4094"
                continue
            interfaces.append(
                Interface(
                    name=name,
                    mode="trunk",
                    description=desc,
                    trunk_vlans="1-4094",
                    shutdown=False,
                )
            )

        interfaces.sort(key=lambda i: self._eth_sort_key(i.name))
        return interfaces

    def _build_svis(self, role: str, vlans: List[VLAN]) -> List[SVI]:
        if role == "spine":
            return []
        svis: List[SVI] = []
        for vlan in vlans[:2]:
            svis.append(
                SVI(
                    vlan_id=vlan.id,
                    ip_address=f"10.{vlan.id}.0.1/24",
                    description=f"SVI_{vlan.name}",
                )
            )
        return svis

    def _default_motd(self, site_name: str, role: str, security_tier: str) -> str:
        if security_tier.lower() == "hardened":
            return f"{site_name} {role.upper()} - AUTHORIZED PERSONNEL ONLY"
        return f"{site_name} {role.upper()} - Institutional Access"
