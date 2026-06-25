import ipaddress
from typing import List, Dict, Optional
from models.device_model import Device

class ValidationError(Exception):
    def __init__(self, report):
        self.report = report
        super().__init__(f"Validation failed: {report['errors']}")

class DeviceValidator:
    def __init__(self):
        self.errors = []

    def validate(self, device: Device) -> Dict:
        """
        Executes all validation rules against the Device model.
        Returns a structured report: {"status": "pass|fail", "errors": []}
        """
        self.errors = []
        
        # 1. IP Validation
        self._validate_ip(device.mgmt_ip, "Management IP")
        if device.vpc:
            self._validate_ip(device.vpc.local_keepalive_ip, "vPC Local Keepalive IP")
            self._validate_ip(device.vpc.remote_keepalive_ip, "vPC Remote Keepalive IP")
            
        # 2. VLAN Uniqueness
        vlan_ids = [v.id for v in device.vlans]
        if len(vlan_ids) != len(set(vlan_ids)):
            duplicates = set([x for x in vlan_ids if vlan_ids.count(x) > 1])
            self.errors.append(f"Duplicate VLAN IDs detected: {duplicates}")
            
        # 3. Interface Uniqueness
        intf_names = [i.name for i in device.interfaces]
        if len(intf_names) != len(set(intf_names)):
            duplicates = set([x for x in intf_names if intf_names.count(x) > 1])
            self.errors.append(f"Duplicate Interface names detected: {duplicates}")
            
        # 4. Interface Modes
        valid_modes = ["access", "trunk", "routed", "bare"]
        for intf in device.interfaces:
            if intf.mode not in valid_modes:
                self.errors.append(f"Interface {intf.name} has invalid mode: {intf.mode}. Expected: {valid_modes}")
                
        # 5. L3 Validation
        for svi in device.svis:
            self._validate_ip(svi.ip_address, f"SVI Vlan{svi.vlan_id} IP")
            if svi.hsrp:
                self._validate_ip(svi.hsrp.vip, f"SVI Vlan{svi.vlan_id} HSRP VIP")

        status = "pass" if not self.errors else "fail"
        return {
            "status": status,
            "errors": self.errors
        }

    def validate_vpc_pair(self, primary: Device, secondary: Device) -> Dict:
        """
        Phase 10: Ensures consistency between vPC peers.
        """
        self.errors = []
        
        # Validate Domain and Peer-Link matches
        if primary.vpc and secondary.vpc:
            if primary.vpc.domain_id != secondary.vpc.domain_id:
                self.errors.append(f"vPC Domain ID mismatch: {primary.vpc.domain_id} vs {secondary.vpc.domain_id}")
            if primary.vpc.peer_link_id != secondary.vpc.peer_link_id:
                self.errors.append(f"vPC Peer-Link PO ID mismatch: {primary.vpc.peer_link_id} vs {secondary.vpc.peer_link_id}")
            
            # Cross-check keepalives
            if primary.vpc.local_keepalive_ip.split('/')[0] != secondary.vpc.remote_keepalive_ip.split('/')[0]:
                self.errors.append("vPC Keepalive Cross-Check Failed: Primary Local does not match Secondary Remote")
            if primary.vpc.remote_keepalive_ip.split('/')[0] != secondary.vpc.local_keepalive_ip.split('/')[0]:
                self.errors.append("vPC Keepalive Cross-Check Failed: Primary Remote does not match Secondary Local")

        # VLAN Consistency
        p_vlans = {v.id for v in primary.vlans}
        s_vlans = {v.id for v in secondary.vlans}
        if p_vlans != s_vlans:
            diff = p_vlans.symmetric_difference(s_vlans)
            self.errors.append(f"vPC VLAN Mismatch detected in IDs: {diff}")

        status = "pass" if not self.errors else "fail"
        return {
            "status": status,
            "errors": self.errors
        }

    def _validate_ip(self, ip_str: str, label: str):
        if not ip_str:
            self.errors.append(f"{label} is missing")
            return
        clean_ip = ip_str.split('/')[0]
        try:
            ipaddress.ip_address(clean_ip)
        except ValueError:
            self.errors.append(f"Invalid {label} format: {ip_str}")
