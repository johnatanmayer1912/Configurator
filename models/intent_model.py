from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IntentOverrides:
    motd: Optional[str] = None
    admin_user: Optional[str] = None
    admin_password: Optional[str] = None
    management_vrf: str = "management"
    base_access_vlan: int = 10
    access_vlan_count: int = 4
    interface_count: int = 48


@dataclass
class BlueprintIntent:
    hostname: str
    site_name: str
    role: str  # access, leaf, spine
    model: str = "Generic"
    mgmt_ip: str = "10.0.0.10/24"
    mgmt_gw: str = "10.0.0.1"
    redundancy_mode: str = "standalone"  # standalone, vpc
    security_tier: str = "standard"  # standard, hardened
    uplink_ports: List[str] = field(default_factory=list)
    overrides: IntentOverrides = field(default_factory=IntentOverrides)


@dataclass
class BlueprintResolution:
    profile_name: str
    summary_lines: List[str]
    policy_flags: Dict[str, str]
