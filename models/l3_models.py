from dataclasses import dataclass
from typing import Optional

@dataclass
class HSRPConfig:
    group: int
    vip: str
    priority: int = 100
    preempt: bool = True

@dataclass
class SVI:
    vlan_id: int
    ip_address: str # CIDR format: 192.168.1.1/24
    description: Optional[str] = None
    hsrp: Optional[HSRPConfig] = None
    vrf: Optional[str] = None

@dataclass
class StaticRoute:
    prefix: str
    next_hop: str
    vrf: Optional[str] = None
    description: Optional[str] = None
