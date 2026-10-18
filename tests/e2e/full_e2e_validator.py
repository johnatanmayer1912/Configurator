"""
Full E2E Validation Framework
==============================

This module provides comprehensive validation for E2E tests including:
- VLAN assignment validation (TRANSIT vs FABRIC)
- Feature enablement verification
- Interface configuration validation
- vPC configuration validation
- Output comparison against expected results
"""

import re
from typing import Dict, List, Tuple, Optional
from tests.e2e.test_data.expected_outputs import (
    VLAN_ASSIGNMENT_RULES,
    VLAN_TEMPLATE_RANGES,
    FEATURE_EXPECTATIONS,
    VPC_EXPECTATIONS,
    INTERFACE_EXPECTATIONS,
    DEPLOYMENT_TEST_CASES
)


class ConfigValidator:
    """Validates NX-OS configurations against expected outputs."""
    
    def __init__(self, config_text: str):
        self.config_text = config_text
        self.lines = config_text.split('\n')
        self.vlans = self._extract_vlans()
        self.features = self._extract_features()
        self.interfaces = self._extract_interfaces()
        self.vpc_config = self._extract_vpc_config()
    
    def _extract_vlans(self) -> Dict[str, str]:
        """Extract VLAN configurations from config (handles multi-line NX-OS format)."""
        vlans = {}
        current_vlan_id = None
        
        # Pattern 1: inline  "vlan 10  name FOO"
        inline_pattern = re.compile(r'^vlan\s+(\d+)\s+name\s+(\S+)', re.IGNORECASE)
        # Pattern 2: vlan block header  "vlan 10"
        header_pattern = re.compile(r'^vlan\s+(\d+)\s*$')
        # Pattern 3: name line inside block  "  name FOO"
        name_pattern = re.compile(r'^\s+name\s+(\S+)', re.IGNORECASE)
        
        for line in self.lines:
            stripped = line.strip()
            
            # Try inline first
            m = inline_pattern.match(stripped)
            if m:
                vlans[m.group(1)] = m.group(2)
                current_vlan_id = None
                continue
            
            # Check for block header
            m = header_pattern.match(stripped)
            if m:
                current_vlan_id = m.group(1)
                continue
            
            # Check for name inside block
            if current_vlan_id:
                m = name_pattern.match(line)
                if m:
                    vlans[current_vlan_id] = m.group(1)
                    current_vlan_id = None
                    continue
                # Any non-indented line resets context
                if stripped and not line.startswith(' ') and not line.startswith('\t'):
                    current_vlan_id = None
        
        return vlans
    
    def _extract_features(self) -> List[str]:
        """Extract enabled features from config."""
        features = []
        feature_pattern = re.compile(r'feature (\S+)')
        for line in self.lines:
            match = feature_pattern.match(line.strip())
            if match:
                features.append(match.group(1))
        return features
    
    def _extract_interfaces(self) -> Dict[str, List[str]]:
        """Extract interface configurations from config."""
        interfaces = {}
        current_interface = None
        interface_pattern = re.compile(r'interface (\S+)')
        
        for line in self.lines:
            match = interface_pattern.match(line.strip())
            if match:
                current_interface = match.group(1)
                interfaces[current_interface] = []
            elif current_interface and line.strip():
                interfaces[current_interface].append(line.strip())
        
        return interfaces
    
    def _extract_vpc_config(self) -> Dict[str, str]:
        """Extract vPC configuration from config."""
        vpc_config = {}
        in_vpc_block = False
        
        for line in self.lines:
            stripped = line.strip()
            
            # vpc domain block header
            if re.match(r'vpc domain\s+\d+', stripped):
                match = re.search(r'vpc domain (\d+)', stripped)
                if match:
                    vpc_config['domain'] = match.group(1)
                in_vpc_block = True
                continue
            
            if in_vpc_block:
                if stripped and not line.startswith(' ') and not line.startswith('\t'):
                    in_vpc_block = False
                else:
                    # peer-keepalive
                    if 'peer-keepalive' in stripped:
                        vpc_config['peer-keepalive'] = stripped
                    elif 'peer-gateway' in stripped:
                        vpc_config['peer-gateway'] = stripped
                    elif 'auto-recovery' in stripped:
                        vpc_config['auto-recovery'] = stripped
                    elif 'system-priority' in stripped:
                        vpc_config['system-priority'] = stripped
                    elif 'role priority' in stripped:
                        vpc_config['role-priority'] = stripped
        
        # Also detect vpc peer-link port-channels (outside vpc domain block)
        for line in self.lines:
            stripped = line.strip()
            if 'vpc peer-link' in stripped:
                vpc_config['peer-link'] = stripped
        
        return vpc_config
    
    def validate_vlan_assignment(self, expected_vlan_type: str) -> Tuple[bool, List[str]]:
        """
        Validate that VLANs match expected type (TRANSIT or FABRIC).
        
        Returns (is_valid, error_messages)
        """
        errors = []
        
        for vlan_id, vlan_name in self.vlans.items():
            expected_prefix = expected_vlan_type.split('_')[0]
            if not vlan_name.startswith(expected_prefix):
                errors.append(
                    f"VLAN {vlan_id} named '{vlan_name}' does not match expected type '{expected_vlan_type}'"
                )
        
        return (len(errors) == 0, errors)
    
    def validate_features(self, expected_features: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that all expected features are enabled.
        
        Returns (is_valid, error_messages)
        """
        errors = []
        
        for feature in expected_features:
            if feature not in self.features:
                errors.append(f"Expected feature '{feature}' not found in config")
        
        return (len(errors) == 0, errors)
    
    def validate_vpc_configuration(self, expected_vpc_elements: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate vPC configuration elements.
        
        Returns (is_valid, error_messages)
        """
        errors = []
        
        for element in expected_vpc_elements:
            if element not in self.vpc_config:
                errors.append(f"Expected vPC element '{element}' not found in config")
        
        return (len(errors) == 0, errors)
    
    def validate_interface_count(self, expected_interfaces: Dict[str, int]) -> Tuple[bool, List[str]]:
        """
        Validate interface counts by type.
        
        Returns (is_valid, error_messages)
        """
        errors = []
        interface_counts = {}
        
        for interface in self.interfaces.keys():
            if interface.startswith('Ethernet'):
                interface_counts['ethernet'] = interface_counts.get('ethernet', 0) + 1
            elif interface.startswith('port-channel'):
                interface_counts['port_channel'] = interface_counts.get('port_channel', 0) + 1
            elif interface.startswith('Vlan'):
                interface_counts['svi'] = interface_counts.get('svi', 0) + 1
        
        for interface_type, expected_count in expected_interfaces.items():
            actual_count = interface_counts.get(interface_type, 0)
            if actual_count < expected_count:
                errors.append(
                    f"Expected at least {expected_count} {interface_type} interfaces, found {actual_count}"
                )
        
        return (len(errors) == 0, errors)
    
    def get_validation_summary(self) -> Dict:
        """Get summary of configuration for validation."""
        return {
            'vlan_count': len(self.vlans),
            'feature_count': len(self.features),
            'interface_count': len(self.interfaces),
            'has_vpc': len(self.vpc_config) > 0,
            'vlans': self.vlans,
            'features': self.features,
            'vpc_domain': self.vpc_config.get('domain', None)
        }


class MultiSwitchValidator:
    """Validates multi-switch deployments."""
    
    def __init__(self, deployment_configs: Dict[str, str]):
        """
        Initialize with switch configurations.
        
        Args:
            deployment_configs: Dict mapping hostname to config text
        """
        self.validators = {
            hostname: ConfigValidator(config)
            for hostname, config in deployment_configs.items()
        }
    
    def validate_deployment(self, test_case: Dict) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate entire deployment against test case expectations.
        
        Returns (is_valid, errors_by_switch)
        """
        all_errors = {}
        all_valid = True
        
        for hostname, expected_vlans in test_case['expected_vlans'].items():
            if hostname not in self.validators:
                all_errors[hostname] = [f"Switch {hostname} not found in deployment"]
                all_valid = False
                continue
            
            validator = self.validators[hostname]
            switch_errors = []
            
            # Validate VLAN type
            for vlan_type in expected_vlans:
                is_valid, errors = validator.validate_vlan_assignment(vlan_type)
                if not is_valid:
                    switch_errors.extend(errors)
            
            # Validate features
            expected_features = test_case['expected_features'].get(hostname, [])
            is_valid, errors = validator.validate_features(expected_features)
            if not is_valid:
                switch_errors.extend(errors)
            
            if switch_errors:
                all_errors[hostname] = switch_errors
                all_valid = False
        
        return (all_valid, all_errors)
    
    def get_deployment_summary(self) -> Dict:
        """Get summary of entire deployment."""
        return {
            hostname: validator.get_validation_summary()
            for hostname, validator in self.validators.items()
        }
