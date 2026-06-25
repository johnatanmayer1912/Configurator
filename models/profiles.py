from dataclasses import dataclass
from typing import Optional

@dataclass
class InterfaceProfile:
    name: str
    mode: str
    description_suffix: str
    spanning_tree_port_type: Optional[str] = None # e.g., 'edge', 'network'
    mtu: Optional[int] = None

# Institutional Standard Profiles
PROFILES = {
    "ACCESS_SERVER": InterfaceProfile(
        name="ACCESS_SERVER",
        mode="access",
        description_suffix="- HOST_PORT",
        spanning_tree_port_type="edge"
    ),
    "TRUNK_UPLINK": InterfaceProfile(
        name="TRUNK_UPLINK",
        mode="trunk",
        description_suffix="- UPLINK_PORT",
        spanning_tree_port_type="network",
        mtu=9216
    )
}
