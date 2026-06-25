from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Interface:
    name: str
    mode: str = "access"  # access, trunk, routed, bare (admin-up only)
    vlan: Optional[int] = None
    description: Optional[str] = None
    shutdown: bool = True
    vpc_id: Optional[int] = None
    trunk_vlans: Optional[str] = None  # comma-separated or range notation, e.g. "10,20,30-50"
    channel_group: Optional[int] = None
    channel_mode: str = "active"
    mtu: Optional[int] = None
    custom_lines: List[str] = field(default_factory=list)
