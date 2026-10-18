from typing import List, Tuple
import logging

from models.device_model import Device, VPCConfig
from models.interface_model import Interface
from models.intent_model import BlueprintIntent, BlueprintResolution
from models.vlan_model import VLAN
from models.l3_models import SVI
from core.vlan_validator import VLANValidator

logger = logging.getLogger(__name__)


class IntentEngine:
    def __init__(self, catalog_loader=None):
        from core.catalog_loader import CatalogLoader
        self.catalog = catalog_loader or CatalogLoader()
        self.vlan_validator = VLANValidator(self.catalog)

    def resolve(self, intent: BlueprintIntent) -> Tuple[Device, BlueprintResolution]:
        role = intent.role.lower().strip()
        if role not in {"access", "leaf", "spine"}:
            raise ValueError("Intent role must be access, leaf, or spine.")

        # Get model-aware VLAN constraints
        vlan_start = intent.overrides.base_access_vlan
        vlan_count = intent.overrides.access_vlan_count
        
        # Validate and adjust VLAN range based on hardware constraints
        constraints = self.vlan_validator.get_constraints(intent.model)
        valid, msg = self.vlan_validator.validate_vlan_range(intent.model, vlan_start, vlan_count)
        if not valid:
            # Suggest valid range if validation fails
            suggested_start, suggested_end = self.vlan_validator.suggest_vlan_range(
                intent.model, vlan_count, vlan_start
            )
            logger.warning(f"VLAN validation failed for {intent.model}: {msg}. Using suggested range [{suggested_start}-{suggested_end}]")
            vlan_start = suggested_start
            vlan_count = suggested_end - suggested_start + 1
        
        vlans = self._build_vlans(role, vlan_start, vlan_count, constraints)
        interfaces = self._build_interfaces(role, intent.overrides.interface_count, vlan_start, intent.uplink_ports, constraints)
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

    def _build_vlans(self, role: str, start: int, count: int, constraints) -> List[VLAN]:
        if role == "access":
            prefix = "USER"
        elif role == "leaf":
            prefix = "FABRIC"
        else:
            prefix = "TRANSIT"
        
        # Build VLANs respecting constraints
        vlans = []
        for i in range(count):
            vlan_id = start + i
            # Skip reserved VLANs
            if constraints.is_vlan_reserved(vlan_id):
                logger.warning(f"Skipping reserved VLAN {vlan_id} in range")
                continue
            if not constraints.is_vlan_valid(vlan_id):
                logger.warning(f"Skipping invalid VLAN {vlan_id} in range")
                continue
            vlans.append(VLAN(id=vlan_id, name=f"{prefix}_{vlan_id}"))
        
        return vlans

    def _eth_sort_key(self, name: str) -> tuple:
        parts = name.replace("Ethernet", "").split("/")
        try:
            return tuple(int(p) for p in parts)
        except ValueError:
            return (0, 0)

    def _build_interfaces(self, role: str, count: int, access_vlan: int, uplink_ports: List[str], constraints) -> List[Interface]:
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
                # Use first valid VLAN from constraints if base VLAN is invalid
                vlan_to_use = access_vlan
                if not constraints.is_vlan_valid(access_vlan):
                    vlan_to_use = constraints.default_vlan_start
            else:
                desc = f"Routed_Port_{idx}"
                vlan_to_use = None
            interfaces.append(
                Interface(
                    name=name,
                    mode=intf_mode,
                    vlan=vlan_to_use if intf_mode == "access" else None,
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
