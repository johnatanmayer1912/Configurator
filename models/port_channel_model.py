from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PortChannel:
  """LACP port-channel — peer-link, keepalive L3, or vPC member."""

  number: int
  description: str
  mode: str = "trunk"
  vpc_id: Optional[int] = None
  vpc_peer_link: bool = False
  vpc_keepalive: bool = False
  vrf: Optional[str] = None
  ip_address: Optional[str] = None
  mtu: Optional[int] = None
  spanning_tree_network: bool = False
  member_interfaces: List[str] = field(default_factory=list)
  access_vlan: Optional[int] = None
  trunk_vlans: Optional[str] = None
