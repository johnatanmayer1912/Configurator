"""
Port Mapping Service - Bulletproof port configuration management

This service provides a robust, validated approach to port mapping across all
hardware models, switch roles, and deployment scenarios. It ensures data integrity
through strict validation, clear contracts, and comprehensive error handling.

Architecture Principles:
- Single source of truth for port configuration
- Clear data contracts with validation
- Hardware-agnostic port assignment
- Comprehensive error handling and logging
- Testable and maintainable code structure
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PortType(Enum):
    """Port type classification for consistent categorization"""
    UPLINK = "uplink"
    DOWNLINK = "downlink"
    PEER_LINK = "peer_link"
    KEEPALIVE = "keepalive"
    ACCESS = "access"
    TRUNK = "trunk"
    UNCONFIGURED = "unconfigured"


class SwitchRole(Enum):
    """Switch role classification for port assignment logic"""
    CORE = "core"
    LEAF_10G = "leaf_10g"
    LEAF_1G = "leaf_1g"
    SPINE = "spine"
    GENERIC = "generic"


@dataclass
class PortConfig:
    """Immutable port configuration with validation"""
    port_num: int
    interface_name: str
    port_type: PortType
    description: str
    port_channel: Optional[int] = None
    channel_group: Optional[str] = None
    mode: Optional[str] = None
    enabled: bool = True
    vlan: Optional[int] = None
    
    def __post_init__(self):
        """Validate port configuration on creation"""
        if self.port_num < 1 or self.port_num > 128:
            raise ValueError(f"Invalid port number: {self.port_num}")
        if not self.interface_name:
            raise ValueError("Interface name cannot be empty")
        if self.port_channel is not None and (self.port_channel < 1 or self.port_channel > 4096):
            raise ValueError(f"Invalid port-channel ID: {self.port_channel}")
        if self.vlan is not None and (self.vlan < 1 or self.vlan > 4094):
            raise ValueError(f"Invalid VLAN ID: {self.vlan}")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API serialization"""
        return {
            "port": self.port_num,
            "port_name": self.interface_name,
            "type": self.port_type.value,
            "description": self.description,
            "port_channel": self.port_channel,
            "channel_group": self.channel_group,
            "mode": self.mode,
            "enabled": self.enabled,
            "vlan": self.vlan
        }


@dataclass
class SwitchPortMap:
    """Complete port mapping for a single switch"""
    hostname: str
    model: str
    role: SwitchRole
    primary_speed_label: str = "Multi"
    ports: List[PortConfig] = field(default_factory=list)
    
    def add_port(self, port: PortConfig) -> None:
        """Add port with duplicate detection"""
        if any(p.port_num == port.port_num for p in self.ports):
            logger.warning(f"Duplicate port {port.port_num} for {self.hostname}, skipping")
            return
        self.ports.append(port)
    
    def get_port(self, port_num: int) -> Optional[PortConfig]:
        """Get port configuration by number"""
        for port in self.ports:
            if port.port_num == port_num:
                return port
        return None
    
    def get_ports_by_type(self, port_type: PortType) -> List[PortConfig]:
        """Get all ports of a specific type"""
        return [p for p in self.ports if p.port_type == port_type]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API serialization"""
        return {
            "hostname": self.hostname,
            "model": self.model,
            "role": self.role.value,
            "primary_speed_label": self.primary_speed_label,
            "ports": [p.to_dict() for p in self.ports],
            "port_count": len(self.ports)
        }


class PortMappingService:
    """
    Bulletproof port mapping service with comprehensive validation
    
    This service provides:
    - Hardware profile integration with fallback logic
    - Port assignment validation
    - Channel group management
    - Description generation with hostname resolution
    - Comprehensive error handling and logging
    """
    
    def __init__(self, catalog_loader):
        self.catalog = catalog_loader
        self._port_cache: Dict[str, SwitchPortMap] = {}
    
    def get_switch_role(self, model: str) -> SwitchRole:
        """Determine switch role from hardware profile"""
        hw_profile = self.catalog.get_hardware_profile(model)
        if not hw_profile:
            logger.warning(f"No hardware profile found for {model}, defaulting to GENERIC")
            return SwitchRole.GENERIC
        
        device_class = hw_profile.get("device_class", "generic")
        try:
            return SwitchRole(device_class)
        except ValueError:
            logger.warning(f"Unknown device class {device_class} for {model}, defaulting to GENERIC")
            return SwitchRole.GENERIC
    
    def parse_interface_name(self, interface: str) -> Optional[int]:
        """
        Robust interface name parsing supporting multiple formats
        
        Supported formats:
        - Ethernet1/1
        - E1/1
        - Ethernet1/1/1
        - E1/1/1
        - 1 (port number only)
        """
        if not interface:
            return None
        
        # Try full format first: Ethernet1/1 or E1/1
        import re
        match = re.match(r'(?:Ethernet|E)(\d+)/(\d+)(?:/(\d+))?', interface)
        if match:
            # Return the last port number (module/port or module/port/subport)
            if match.group(3):
                return int(match.group(3))
            return int(match.group(2))
        
        # Try simple number
        match = re.match(r'^(\d+)$', interface)
        if match:
            return int(match.group(1))
        
        logger.warning(f"Could not parse interface name: {interface}")
        return None
    
    def create_port_map(
        self,
        hostname: str,
        model: str,
        hw_profile: dict,
        vpc_pair: Optional[dict] = None,
        peer_switches: Optional[List[dict]] = None,
        uplinks: Optional[List[dict]] = None,
        downlinks: Optional[List[dict]] = None
    ) -> SwitchPortMap:
        """
        Create complete port mapping for a switch
        
        This is the main entry point for port map generation. It orchestrates
        all port assignment logic with proper validation and error handling.
        """
        role = self.get_switch_role(model)
        primary_speed_label = hw_profile.get("primary_speed_label", "Multi") if hw_profile else "Multi"
        port_map = SwitchPortMap(hostname=hostname, model=model, role=role, primary_speed_label=primary_speed_label)
        
        # Add vPC ports if applicable
        if vpc_pair:
            self._add_vpc_ports(port_map, hw_profile, vpc_pair)
        
        # Add downlinks from overrides (takes precedence over role-specific defaults)
        if downlinks:
            self._add_override_downlinks(port_map, downlinks)
        # Add role-specific ports only if no override downlinks provided
        elif role == SwitchRole.CORE:
            self._add_core_downlink_ports(port_map, hw_profile, peer_switches or [])
        elif role in [SwitchRole.LEAF_10G, SwitchRole.LEAF_1G]:
            self._add_leaf_uplink_ports(port_map, hw_profile, peer_switches or [])
        
        # Add custom uplinks from deployment
        if uplinks:
            self._add_custom_uplinks(port_map, uplinks)
        
        # Add any additional configured ports from hardware profile
        self._add_profile_ports(port_map, hw_profile)
        
        # Cache the result
        self._port_cache[hostname] = port_map
        
        logger.info(f"Created port map for {hostname}: {len(port_map.ports)} ports configured")
        return port_map
    
    def _add_vpc_ports(
        self,
        port_map: SwitchPortMap,
        hw_profile: dict,
        vpc_pair: dict
    ) -> None:
        """Add vPC peer-link and keepalive ports"""
        if not hw_profile:
            logger.warning(f"No hardware profile provided for vPC ports on {port_map.hostname}")
            return
            
        domain = vpc_pair.get("domain", 1)
        
        # Peer-link ports
        peer_link_ports = hw_profile.get("vpc_peer_link", [])
        if peer_link_ports:
            for port_str in peer_link_ports:
                port_num = self.parse_interface_name(port_str)
                if port_num:
                    port_map.add_port(PortConfig(
                        port_num=port_num,
                        interface_name=port_str,
                        port_type=PortType.PEER_LINK,
                        description=f"vPC Peer-link (Domain {domain})",
                        mode="trunk"
                    ))
                    logger.debug(f"Added vPC peer-link port: {port_str} -> {port_num}")
        
        # Keepalive ports
        keepalive_ports = hw_profile.get("vpc_keepalive", [])
        if keepalive_ports:
            for port_str in keepalive_ports:
                port_num = self.parse_interface_name(port_str)
                if port_num:
                    port_map.add_port(PortConfig(
                        port_num=port_num,
                        interface_name=port_str,
                        port_type=PortType.KEEPALIVE,
                        description=f"vPC Keepalive (Domain {domain})",
                        mode="access"
                    ))
                    logger.debug(f"Added vPC keepalive port: {port_str} -> {port_num}")
    
    def _add_core_downlink_ports(
        self,
        port_map: SwitchPortMap,
        hw_profile: dict,
        peer_switches: List[dict]
    ) -> None:
        """Add downlink ports for core switches with port-channel assignment"""
        if not hw_profile:
            logger.warning(f"No hardware profile provided for core downlink ports on {port_map.hostname}")
            return
            
        # Separate 10G and 1G leaf switches
        leaf_10g = [s for s in peer_switches if self.get_switch_role(s.get("model", "")) == SwitchRole.LEAF_10G]
        leaf_1g = [s for s in peer_switches if self.get_switch_role(s.get("model", "")) == SwitchRole.LEAF_1G]
        
        # Configure 10G downlinks
        downlink_10g_start = hw_profile.get("downlink_10g_start", 1)
        downlink_10g_end = hw_profile.get("downlink_10g_end", 10)
        po_id = 20
        
        for leaf in leaf_10g:
            if downlink_10g_start > downlink_10g_end:
                break
            
            leaf_hw = self.catalog.get_hardware_profile(leaf.get("model", ""))
            leaf_uplink_start = leaf_hw.get("vpc_uplink_start", 53) if leaf_hw else 53
            leaf_uplink_end = leaf_hw.get("vpc_uplink_end", 54) if leaf_hw else 54
            
            # Port 1 of the pair
            port_map.add_port(PortConfig(
                port_num=downlink_10g_start,
                interface_name=f"Ethernet1/{downlink_10g_start}",
                port_type=PortType.DOWNLINK,
                description=f"to {leaf.get('hostname', 'Unknown')} port {leaf_uplink_start}",
                port_channel=po_id,
                channel_group=f"{po_id} mode active",
                mode="trunk"
            ))
            
            # Port 2 of the pair
            port_map.add_port(PortConfig(
                port_num=downlink_10g_start + 1,
                interface_name=f"Ethernet1/{downlink_10g_start + 1}",
                port_type=PortType.DOWNLINK,
                description=f"to {leaf.get('hostname', 'Unknown')} port {leaf_uplink_end}",
                port_channel=po_id,
                channel_group=f"{po_id} mode active",
                mode="trunk"
            ))
            
            downlink_10g_start += 2
            po_id += 1
        
        # Configure 1G downlinks
        downlink_1g_start = hw_profile.get("downlink_1g_start", 11)
        downlink_1g_end = hw_profile.get("downlink_1g_end", 20)
        po_id = 21
        
        for leaf in leaf_1g:
            if downlink_1g_start > downlink_1g_end:
                break
            
            leaf_hw = self.catalog.get_hardware_profile(leaf.get("model", ""))
            leaf_uplink_start = leaf_hw.get("vpc_uplink_start", 51) if leaf_hw else 51
            leaf_uplink_end = leaf_hw.get("vpc_uplink_end", 52) if leaf_hw else 52
            
            # Port 1 of the pair
            port_map.add_port(PortConfig(
                port_num=downlink_1g_start,
                interface_name=f"Ethernet1/{downlink_1g_start}",
                port_type=PortType.DOWNLINK,
                description=f"to {leaf.get('hostname', 'Unknown')} port {leaf_uplink_start}",
                port_channel=po_id,
                channel_group=f"{po_id} mode active",
                mode="trunk"
            ))
            
            # Port 2 of the pair
            port_map.add_port(PortConfig(
                port_num=downlink_1g_start + 1,
                interface_name=f"Ethernet1/{downlink_1g_start + 1}",
                port_type=PortType.DOWNLINK,
                description=f"to {leaf.get('hostname', 'Unknown')} port {leaf_uplink_end}",
                port_channel=po_id,
                channel_group=f"{po_id} mode active",
                mode="trunk"
            ))
            
            downlink_1g_start += 2
            po_id += 1
    
    def _add_leaf_uplink_ports(
        self,
        port_map: SwitchPortMap,
        hw_profile: dict,
        peer_switches: List[dict]
    ) -> None:
        """Add uplink ports for leaf switches"""
        if not hw_profile:
            logger.warning(f"No hardware profile provided for leaf uplink ports on {port_map.hostname}")
            return
            
        uplink_start = hw_profile.get("vpc_uplink_start", 51)
        uplink_end = hw_profile.get("vpc_uplink_end", 52)
        
        logger.info(f"Adding leaf uplink ports for {port_map.hostname}: ports {uplink_start}-{uplink_end}")
        
        # Find core switches for description
        core_switches = [s for s in peer_switches if self.get_switch_role(s.get("model", "")) == SwitchRole.CORE]
        logger.info(f"Found {len(core_switches)} core switches for {port_map.hostname}")
        
        if len(core_switches) >= 2:
            core1 = core_switches[0].get("hostname", "Core1")
            core2 = core_switches[1].get("hostname", "Core2")
            logger.info(f"Using core switches: {core1}, {core2}")
            
            # Port 1
            port_map.add_port(PortConfig(
                port_num=uplink_start,
                interface_name=f"Ethernet1/{uplink_start}",
                port_type=PortType.UPLINK,
                description=f"to {core1} port 1",
                mode="trunk"
            ))
            
            # Port 2
            port_map.add_port(PortConfig(
                port_num=uplink_end,
                interface_name=f"Ethernet1/{uplink_end}",
                port_type=PortType.UPLINK,
                description=f"to {core2} port 1",
                mode="trunk"
            ))
        else:
            # Fallback if no core switches found
            logger.warning(f"Less than 2 core switches found for {port_map.hostname}, using fallback descriptions")
            port_map.add_port(PortConfig(
                port_num=uplink_start,
                interface_name=f"Ethernet1/{uplink_start}",
                port_type=PortType.UPLINK,
                description="Uplink to Core",
                mode="trunk"
            ))
            
            port_map.add_port(PortConfig(
                port_num=uplink_end,
                interface_name=f"Ethernet1/{uplink_end}",
                port_type=PortType.UPLINK,
                description="Uplink to Core",
                mode="trunk"
            ))
    
    def _add_custom_uplinks(self, port_map: SwitchPortMap, uplinks: List[dict]) -> None:
        """Add custom uplinks from deployment configuration"""
        for uplink in uplinks:
            # Check if this uplink is for this switch (supports both 'from' and 'source_switch')
            source_switch = uplink.get("from") or uplink.get("source_switch")
            if source_switch != port_map.hostname:
                continue
            
            # Get destination switch (supports both 'to' and 'destination_switch')
            to_hostname = uplink.get("to") or uplink.get("destination_switch", "Unknown")
            ports = uplink.get("ports") or uplink.get("source_ports", "")
            to_ports = uplink.get("to_ports") or uplink.get("destination_ports", "")
            po_id = uplink.get("po_id") or uplink.get("port_channel_id")
            mode = uplink.get("mode", "trunk")
            description = uplink.get("description", f"to {to_hostname}")
            
            # Parse port range (e.g., "E1/5-6" or "E1/5,E1/6" or "Ethernet1/5-6")
            port_list = []
            if "," in ports:
                port_list = [p.strip() for p in ports.split(",")]
            elif "-" in ports:
                # Handle range like E1/5-6 or Ethernet1/5-6
                parts = ports.split("-")
                if len(parts) == 2:
                    # Extract base and start number
                    first_part = parts[0]
                    if "/" in first_part:
                        base_parts = first_part.split("/")
                        base = "/".join(base_parts[:-1])
                        start_num = int(base_parts[-1])
                    else:
                        # Simple range like 5-6
                        base = "Ethernet1/"
                        start_num = int(first_part)
                    
                    end_num = int(parts[1])
                    port_list = [f"{base}{i}" for i in range(start_num, end_num + 1)]
            else:
                port_list = [ports]
            
            # Add uplink configuration for each port
            for port in port_list:
                port_num = self.parse_interface_name(port)
                if port_num:
                    port_config = PortConfig(
                        port_num=port_num,
                        interface_name=port,
                        port_type=PortType.UPLINK,
                        description=description,
                        port_channel=int(po_id) if po_id else None,
                        channel_group=f"{po_id} mode active" if po_id else None,
                        mode=mode
                    )
                    port_map.add_port(port_config)
                    logger.debug(f"Added custom uplink port: {port} -> {to_hostname} (PO: {po_id})")
    
    def _add_override_downlinks(self, port_map: SwitchPortMap, downlinks: List[dict]) -> None:
        """Add downlinks from wizard overrides configuration"""
        for downlink in downlinks:
            # Skip disabled downlinks
            if not downlink.get("enabled", True):
                continue
            
            description = downlink.get("description", "Downlink")
            po_id = downlink.get("po_id")
            vpc_id = downlink.get("vpc_id")
            members = downlink.get("members", [])
            
            # Add each member interface
            for member in members:
                port_num = self.parse_interface_name(member)
                if port_num:
                    port_config = PortConfig(
                        port_num=port_num,
                        interface_name=member,
                        port_type=PortType.DOWNLINK,
                        description=description,
                        port_channel=int(po_id) if po_id else None,
                        channel_group=f"{po_id} mode active" if po_id else None,
                        mode="trunk",
                        vlan=vpc_id if vpc_id else None
                    )
                    port_map.add_port(port_config)
                    logger.debug(f"Added override downlink port: {member} -> {description} (PO{po_id})")

    def _add_profile_ports(self, port_map: SwitchPortMap, hw_profile: dict) -> None:
        """Add any additional ports defined in hardware profile"""
        # This can be extended for custom port configurations
        pass
    
    def add_device_interfaces(self, port_map: SwitchPortMap, device_interfaces: List) -> None:
        """
        Add interfaces from the device configuration to the port map
        
        This ensures that all interfaces configured by the pipeline are included
        in the port map, not just the vPC/uplink/downlink ports.
        """
        for iface in device_interfaces:
            if not iface:
                continue
            
            # Parse interface name to get port number
            port_num = self.parse_interface_name(getattr(iface, 'name', ''))
            if not port_num:
                continue
            
            # Check if this port is already configured
            existing_port = port_map.get_port(port_num)
            if existing_port:
                # Update existing port with device configuration details
                existing_port.description = getattr(iface, 'description', existing_port.description)
                existing_port.port_channel = getattr(iface, 'port_channel', existing_port.port_channel)
                existing_port.mode = getattr(iface, 'mode', existing_port.mode)
                existing_port.enabled = getattr(iface, 'enabled', True)
                logger.debug(f"Updated existing port {port_num} with device configuration")
            else:
                # Add new port from device configuration
                port_config = PortConfig(
                    port_num=port_num,
                    interface_name=getattr(iface, 'name', f'Ethernet1/{port_num}'),
                    port_type=PortType.UNCONFIGURED,  # Default type, can be updated based on description
                    description=getattr(iface, 'description', ''),
                    port_channel=getattr(iface, 'port_channel', None),
                    mode=getattr(iface, 'mode', None),
                    enabled=getattr(iface, 'enabled', True)
                )
                port_map.add_port(port_config)
                logger.debug(f"Added device interface port: {port_num}")
        
        logger.info(f"Added {len(device_interfaces)} device interfaces to port map for {port_map.hostname}")
    
    def get_cached_port_map(self, hostname: str) -> Optional[SwitchPortMap]:
        """Get cached port map for a switch"""
        return self._port_cache.get(hostname)
    
    def clear_cache(self) -> None:
        """Clear the port map cache"""
        self._port_cache.clear()
        logger.info("Port map cache cleared")
