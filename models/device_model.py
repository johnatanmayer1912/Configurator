from dataclasses import dataclass, field
from typing import List, Optional
from models.vlan_model import VLAN
from models.interface_model import Interface
from models.l3_models import SVI, StaticRoute
from models.port_channel_model import PortChannel

@dataclass
class VPCConfig:
    domain_id: int
    role: str # primary, secondary
    keepalive_vrf: str
    local_keepalive_ip: str
    remote_keepalive_ip: str
    peer_link_id: int
    peer_link_interfaces: List[str] = field(default_factory=list)
    keepalive_interfaces: List[str] = field(default_factory=list)
    keepalive_po_id: int = 2
    system_priority: int = 32667
    role_priority: int = 4096
    peer_switch: bool = False
    delay_restore: Optional[int] = None

@dataclass
class Device:
    hostname: str
    mgmt_ip: str
    mgmt_gw: str
    model: str
    vlans: List[VLAN] = field(default_factory=list)
    interfaces: List[Interface] = field(default_factory=list)
    svis: List[SVI] = field(default_factory=list)
    static_routes: List[StaticRoute] = field(default_factory=list)
    vpc: Optional[VPCConfig] = None
    motd: str = "Authorized Access Only"
    admin_user: str = "admin"
    admin_password: str = ""
    nxos_version: str = "9.3"
    enabled_features: List[str] = field(default_factory=list)
    security_tier: str = "standard"
    ntp_servers: List[str] = field(default_factory=list)
    logging_hosts: List[str] = field(default_factory=list)
    snmp_location: str = ""
    snmp_contact: str = ""
    network_name: str = ""
    site_location: str = ""
    snmp_trap_host_1: str = ""
    snmp_trap_host_2: str = ""
    snmp_v3_user: str = ""
    boot_image: str = ""
    tacacs_server_1: str = ""
    tacacs_key: str = ""
    spectrum_user: bool = False
    create_local_user: bool = False
    port_channels: List[PortChannel] = field(default_factory=list)
    spanning_tree_priority: int = 8192
    baseline_options: List[str] = field(default_factory=list)
    fabric_bgp_asn: int = 65001
    fabric_loopback: str = "10.255.0.1/32"
    fabric_vni: int = 10000
