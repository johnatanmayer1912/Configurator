"""Deployment State Management Module

This module provides in-memory state management for multi-switch deployments,
including switches, vPC pairs, and uplinks. It supports CRUD operations with
validation and consistency checks.

Architecture Principles:
- Thread-safe state management with locking
- Automatic validation on state mutations
- Consistency checks for vPC pairs and uplinks
- Support for deployment snapshots and rollback
"""

import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeploymentStateError(Exception):
    """Exception raised for deployment state errors"""
    pass


@dataclass
class SwitchState:
    """Represents a switch in the deployment"""
    hostname: str
    mgmt_ip: str
    mgmt_gw: str = "10.10.10.1"
    site_name: str = "HQ"
    model: str = "Nexus 9336C-FX2"
    nxos_version: str = "9.3"
    vpc_domain: Optional[str] = None
    vpc_peer_link_id: int = 1
    keepalive_po_id: int = 2
    vpc_system_priority: int = 32667
    local_ka: str = "10.10.10.1"
    remote_ka: str = "10.10.10.2"
    vpc_pl_ints: str = ""
    base_access_vlan: int = 10
    access_vlan_count: int = 4
    interface_count: int = 0
    bring_up_spare_ports: bool = False
    security_tier: str = "standard"
    role: Optional[str] = None
    baseline_options: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return asdict(self)

    def update(self, updates: Dict[str, Any]) -> None:
        """Update switch state with validation"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()


@dataclass
class VPCPairState:
    """Represents a vPC pair configuration"""
    domain: int
    primary: str
    secondary: str
    peer_link_ports: str = ""
    keepalive_ports: str = ""
    keepalive_vrf: str = "management"
    local_keepalive_ip: str = "10.255.255.1"
    remote_keepalive_ip: str = "10.255.255.2"
    peer_link_id: int = 1
    system_priority: int = 32667
    role_priority_primary: int = 4096
    role_priority_secondary: int = 2000
    delay_restore: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return asdict(self)

    def update(self, updates: Dict[str, Any]) -> None:
        """Update vPC pair state with validation"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()


@dataclass
class UplinkState:
    """Represents an uplink configuration"""
    source_switch: str
    destination_switch: str
    source_ports: str
    destination_ports: str
    port_channel_id: int
    mode: str = "trunk"
    description: str = ""
    mtu: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return asdict(self)

    def update(self, updates: Dict[str, Any]) -> None:
        """Update uplink state with validation"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()


class DeploymentStateManager:
    """Thread-safe state manager for multi-switch deployments"""

    def __init__(self):
        self._lock = threading.RLock()
        self._switches: Dict[str, SwitchState] = {}
        self._vpc_pairs: Dict[int, VPCPairState] = {}
        self._uplinks: Dict[str, UplinkState] = {}
        self._snapshots: Dict[str, Dict] = {}
        self._snapshot_counter = 0

    # Switch CRUD Operations
    def add_switch(self, switch_data: Dict[str, Any]) -> SwitchState:
        """Add a new switch to the deployment"""
        with self._lock:
            hostname = switch_data.get("hostname")
            if not hostname:
                raise ValueError("Hostname is required")
            if hostname in self._switches:
                raise ValueError(f"Switch {hostname} already exists")

            switch = SwitchState(**switch_data)
            self._switches[hostname] = switch
            logger.info(f"Added switch: {hostname}")
            return switch

    def get_switch(self, hostname: str) -> Optional[SwitchState]:
        """Get a switch by hostname"""
        with self._lock:
            return self._switches.get(hostname)

    def list_switches(self) -> List[SwitchState]:
        """List all switches"""
        with self._lock:
            return list(self._switches.values())

    def update_switch(self, hostname: str, updates: Dict[str, Any]) -> SwitchState:
        """Update an existing switch"""
        with self._lock:
            switch = self._switches.get(hostname)
            if not switch:
                raise ValueError(f"Switch {hostname} not found")
            
            # Prevent hostname change
            if "hostname" in updates and updates["hostname"] != hostname:
                raise ValueError("Cannot change hostname")
            
            switch.update(updates)
            logger.info(f"Updated switch: {hostname}")
            return switch

    def delete_switch(self, hostname: str) -> bool:
        """Delete a switch from the deployment"""
        with self._lock:
            if hostname not in self._switches:
                raise ValueError(f"Switch {hostname} not found")
            
            # Check if switch is part of any vPC pair
            for pair in self._vpc_pairs.values():
                if pair.primary == hostname or pair.secondary == hostname:
                    raise ValueError(f"Cannot delete switch {hostname}: part of vPC pair domain {pair.domain}")
            
            # Check if switch is part of any uplink
            for uplink in self._uplinks.values():
                if uplink.source_switch == hostname or uplink.destination_switch == hostname:
                    raise ValueError(f"Cannot delete switch {hostname}: part of uplink configuration")
            
            del self._switches[hostname]
            logger.info(f"Deleted switch: {hostname}")
            return True

    # vPC Pair CRUD Operations
    def add_vpc_pair(self, pair_data: Dict[str, Any]) -> VPCPairState:
        """Add a new vPC pair"""
        with self._lock:
            domain = pair_data.get("domain")
            if domain is None:
                raise ValueError("vPC domain is required")
            if domain in self._vpc_pairs:
                raise ValueError(f"vPC domain {domain} already exists")
            
            primary = pair_data.get("primary")
            secondary = pair_data.get("secondary")
            
            # Validate switches exist
            if primary and primary not in self._switches:
                raise ValueError(f"Primary switch {primary} not found")
            if secondary and secondary not in self._switches:
                raise ValueError(f"Secondary switch {secondary} not found")
            
            # Check for domain conflicts
            for switch in self._switches.values():
                if switch.vpc_domain == str(domain):
                    raise ValueError(f"Switch {switch.hostname} already has vPC domain {domain}")
            
            pair = VPCPairState(**pair_data)
            self._vpc_pairs[domain] = pair
            
            # Update switches with vPC domain
            if primary:
                self._switches[primary].vpc_domain = str(domain)
            if secondary:
                self._switches[secondary].vpc_domain = str(domain)
            
            logger.info(f"Added vPC pair: domain {domain}")
            return pair

    def get_vpc_pair(self, domain: int) -> Optional[VPCPairState]:
        """Get a vPC pair by domain"""
        with self._lock:
            return self._vpc_pairs.get(domain)

    def list_vpc_pairs(self) -> List[VPCPairState]:
        """List all vPC pairs"""
        with self._lock:
            return list(self._vpc_pairs.values())

    def update_vpc_pair(self, domain: int, updates: Dict[str, Any]) -> VPCPairState:
        """Update an existing vPC pair"""
        with self._lock:
            pair = self._vpc_pairs.get(domain)
            if not pair:
                raise ValueError(f"vPC domain {domain} not found")
            
            # Prevent domain change
            if "domain" in updates and updates["domain"] != domain:
                raise ValueError("Cannot change vPC domain")
            
            # Validate switch changes
            if "primary" in updates and updates["primary"] not in self._switches:
                raise ValueError(f"Primary switch {updates['primary']} not found")
            if "secondary" in updates and updates["secondary"] not in self._switches:
                raise ValueError(f"Secondary switch {updates['secondary']} not found")
            
            pair.update(updates)
            logger.info(f"Updated vPC pair: domain {domain}")
            return pair

    def delete_vpc_pair(self, domain: int) -> bool:
        """Delete a vPC pair"""
        with self._lock:
            if domain not in self._vpc_pairs:
                raise ValueError(f"vPC domain {domain} not found")
            
            pair = self._vpc_pairs[domain]
            
            # Clear vPC domain from switches
            if pair.primary and pair.primary in self._switches:
                self._switches[pair.primary].vpc_domain = None
            if pair.secondary and pair.secondary in self._switches:
                self._switches[pair.secondary].vpc_domain = None
            
            del self._vpc_pairs[domain]
            logger.info(f"Deleted vPC pair: domain {domain}")
            return True

    # Uplink CRUD Operations
    def add_uplink(self, uplink_data: Dict[str, Any]) -> UplinkState:
        """Add a new uplink"""
        with self._lock:
            source_switch = uplink_data.get("source_switch")
            destination_switch = uplink_data.get("destination_switch")
            
            if not source_switch or not destination_switch:
                raise ValueError("Source and destination switches are required")
            
            if source_switch not in self._switches:
                raise ValueError(f"Source switch {source_switch} not found")
            if destination_switch not in self._switches:
                raise ValueError(f"Destination switch {destination_switch} not found")
            
            # Generate unique ID
            uplink_id = f"{source_switch}-{destination_switch}-{uplink_data.get('port_channel_id', 1)}"
            if uplink_id in self._uplinks:
                raise ValueError(f"Uplink {uplink_id} already exists")
            
            uplink = UplinkState(**uplink_data)
            self._uplinks[uplink_id] = uplink
            logger.info(f"Added uplink: {uplink_id}")
            return uplink

    def get_uplink(self, uplink_id: str) -> Optional[UplinkState]:
        """Get an uplink by ID"""
        with self._lock:
            return self._uplinks.get(uplink_id)

    def list_uplinks(self) -> List[UplinkState]:
        """List all uplinks"""
        with self._lock:
            return list(self._uplinks.values())

    def update_uplink(self, uplink_id: str, updates: Dict[str, Any]) -> UplinkState:
        """Update an existing uplink"""
        with self._lock:
            uplink = self._uplinks.get(uplink_id)
            if not uplink:
                raise ValueError(f"Uplink {uplink_id} not found")
            
            # Validate switch changes
            if "source_switch" in updates and updates["source_switch"] not in self._switches:
                raise ValueError(f"Source switch {updates['source_switch']} not found")
            if "destination_switch" in updates and updates["destination_switch"] not in self._switches:
                raise ValueError(f"Destination switch {updates['destination_switch']} not found")
            
            uplink.update(updates)
            logger.info(f"Updated uplink: {uplink_id}")
            return uplink

    def delete_uplink(self, uplink_id: str) -> bool:
        """Delete an uplink"""
        with self._lock:
            if uplink_id not in self._uplinks:
                raise ValueError(f"Uplink {uplink_id} not found")
            
            del self._uplinks[uplink_id]
            logger.info(f"Deleted uplink: {uplink_id}")
            return True

    # Snapshot and Rollback Operations
    def create_snapshot(self, name: Optional[str] = None) -> str:
        """Create a snapshot of the current deployment state"""
        with self._lock:
            self._snapshot_counter += 1
            snapshot_id = name or f"snapshot_{self._snapshot_counter}"
            
            snapshot = {
                "id": snapshot_id,
                "timestamp": datetime.now().isoformat(),
                "switches": {k: v.to_dict() for k, v in self._switches.items()},
                "vpc_pairs": {k: v.to_dict() for k, v in self._vpc_pairs.items()},
                "uplinks": {k: v.to_dict() for k, v in self._uplinks.items()},
            }
            
            self._snapshots[snapshot_id] = snapshot
            logger.info(f"Created snapshot: {snapshot_id}")
            return snapshot_id

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all snapshots"""
        with self._lock:
            return [
                {"id": k, "timestamp": v["timestamp"]}
                for k, v in self._snapshots.items()
            ]

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore deployment state from a snapshot"""
        with self._lock:
            if snapshot_id not in self._snapshots:
                raise ValueError(f"Snapshot {snapshot_id} not found")
            
            snapshot = self._snapshots[snapshot_id]
            
            # Restore switches
            self._switches.clear()
            for hostname, switch_data in snapshot["switches"].items():
                self._switches[hostname] = SwitchState(**switch_data)
            
            # Restore vPC pairs
            self._vpc_pairs.clear()
            for domain, pair_data in snapshot["vpc_pairs"].items():
                self._vpc_pairs[int(domain)] = VPCPairState(**pair_data)
            
            # Restore uplinks
            self._uplinks.clear()
            for uplink_id, uplink_data in snapshot["uplinks"].items():
                self._uplinks[uplink_id] = UplinkState(**uplink_data)
            
            logger.info(f"Restored snapshot: {snapshot_id}")
            return True

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""
        with self._lock:
            if snapshot_id not in self._snapshots:
                raise ValueError(f"Snapshot {snapshot_id} not found")
            
            del self._snapshots[snapshot_id]
            logger.info(f"Deleted snapshot: {snapshot_id}")
            return True

    # Utility Operations
    def clear_all(self) -> None:
        """Clear all deployment state"""
        with self._lock:
            self._switches.clear()
            self._vpc_pairs.clear()
            self._uplinks.clear()
            logger.info("Cleared all deployment state")

    def get_deployment_summary(self) -> Dict[str, Any]:
        """Get a summary of the current deployment"""
        with self._lock:
            return {
                "switch_count": len(self._switches),
                "vpc_pair_count": len(self._vpc_pairs),
                "uplink_count": len(self._uplinks),
                "snapshot_count": len(self._snapshots),
                "switches": [s.to_dict() for s in self._switches.values()],
                "vpc_pairs": [p.to_dict() for p in self._vpc_pairs.values()],
                "uplinks": [u.to_dict() for u in self._uplinks.values()],
            }

    def validate_consistency(self) -> List[str]:
        """Validate deployment consistency and return list of errors"""
        with self._lock:
            errors = []
            
            # Check vPC pair consistency
            for domain, pair in self._vpc_pairs.items():
                if pair.primary and pair.primary not in self._switches:
                    errors.append(f"vPC domain {domain}: Primary switch {pair.primary} not found")
                if pair.secondary and pair.secondary not in self._switches:
                    errors.append(f"vPC domain {domain}: Secondary switch {pair.secondary} not found")
                if pair.primary == pair.secondary:
                    errors.append(f"vPC domain {domain}: Primary and secondary cannot be the same switch")
            
            # Check uplink consistency
            for uplink_id, uplink in self._uplinks.items():
                if uplink.source_switch not in self._switches:
                    errors.append(f"Uplink {uplink_id}: Source switch {uplink.source_switch} not found")
                if uplink.destination_switch not in self._switches:
                    errors.append(f"Uplink {uplink_id}: Destination switch {uplink.destination_switch} not found")
                if uplink.source_switch == uplink.destination_switch:
                    errors.append(f"Uplink {uplink_id}: Source and destination cannot be the same switch")
            
            # Check for duplicate vPC domains on switches
            switch_domains = {}
            for hostname, switch in self._switches.items():
                if switch.vpc_domain:
                    if switch.vpc_domain in switch_domains:
                        errors.append(
                            f"Duplicate vPC domain {switch.vpc_domain} on switches "
                            f"{switch_domains[switch.vpc_domain]} and {hostname}"
                        )
                    else:
                        switch_domains[switch.vpc_domain] = hostname
            
            return errors


# Global state manager instance
_global_state_manager: Optional[DeploymentStateManager] = None
_state_lock = threading.Lock()


def get_state_manager() -> DeploymentStateManager:
    """Get the global state manager instance (singleton pattern)"""
    global _global_state_manager
    with _state_lock:
        if _global_state_manager is None:
            _global_state_manager = DeploymentStateManager()
    return _global_state_manager


def reset_state_manager() -> None:
    """Reset the global state manager (primarily for testing)"""
    global _global_state_manager
    with _state_lock:
        _global_state_manager = None
