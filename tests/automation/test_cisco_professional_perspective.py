"""Automation tests from Cisco Professional perspective - NX-OS compliance.

Cisco Professional Expectations:
- Validation based on official Cisco NX-OS documentation
- Detection of deprecated or unsupported commands
- Compliance with Cisco best practices and design guides
- Validation against Cisco NX-OS configuration guides
- Detection of configuration anti-patterns
- Support for latest NX-OS features and syntax
- Alignment with Cisco Validated Designs (CVD)
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestCiscoProfessionalPerspective:
    """Cisco Professional perspective automation tests for NX-OS compliance."""
    
    def test_nxos_command_syntax_compliance(self):
        """
        Cisco Professional Scenario: NX-OS command syntax must match official documentation.
        
        Expected Behavior:
        - System validates NX-OS command syntax
        - Detects deprecated command formats
        - Supports current NX-OS syntax standards
        """
        # Standard NX-OS config
        standard_config = """
hostname N9K-SWITCH-01
feature lacp
feature lldp
interface Ethernet1/1
  description Uplink to Core
  switchport mode trunk
  switchport trunk allowed vlan 100,200
  spanning-tree portfast edge trunk
"""
        
        response = client.post("/config/upload", json={
            "config_text": standard_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects syntax validation
        assert "validation_id" in result
        # Standard config should be valid or have minor warnings
        assert result["is_valid"] == True or len(result.get("warnings", [])) <= 2
    
    def test_vpc_configuration_per_cisco_guide(self):
        """
        Cisco Professional Scenario: vPC configuration must follow Cisco vPC design guide.
        
        Expected Behavior:
        - System validates vPC per Cisco design guide
        - Detects missing vPC keepalive configuration
        - Validates vPC peer-link configuration
        - Checks vPC domain ID uniqueness
        """
        # vPC configuration following Cisco best practices
        vpc_best_practices = """
hostname N9K-LEAF-01
feature vpc
vpc domain 100
  role priority 100
  peer-keepalive destination 10.1.1.2 source 10.1.1.1 vrf management
  delay restore 180
  auto-recovery
interface port-channel1
  vpc peer-link
  spanning-tree port type network
interface Ethernet1/51-52
  channel-group 1 mode active
"""
        
        response = client.post("/config/upload", json={
            "config_text": vpc_best_practices,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects vPC validation
        assert "validation_id" in result
        assert result.get("vpc_domain_id") == 100, "Should detect vPC domain ID"
    
    def test_vlan_configuration_per_cisco_standards(self):
        """
        Cisco Professional Scenario: VLAN configuration must follow Cisco standards.
        
        Expected Behavior:
        - System validates VLAN naming conventions
        - Detects VLAN 1 usage (reserved)
        - Validates SVI configuration
        - Checks for VLAN conflicts
        """
        # VLAN configuration following Cisco standards
        vlan_standard_config = """
hostname N9K-SWITCH
vlan 100
  name DATA_VLAN
  state active
vlan 200
  name VOICE_VLAN
  state active
interface vlan100
  description Data SVI
  ip address 10.1.100.1/24
  no shutdown
"""
        
        response = client.post("/config/upload", json={
            "config_text": vlan_standard_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects VLAN validation
        assert "validation_id" in result
        assert len(result.get("vlans", [])) >= 2, "Should detect VLANs"
    
    def test_interface_configuration_per_cisco_guide(self):
        """
        Cisco Professional Scenario: Interface configuration must follow Cisco NX-OS guide.
        
        Expected Behavior:
        - System validates interface naming
        - Detects invalid interface types
        - Validates port-channel configuration
        - Checks for interface conflicts
        """
        # Interface configuration following Cisco standards
        interface_standard_config = """
hostname N9K-SWITCH
interface Ethernet1/1
  description Server Port
  switchport access vlan 100
  spanning-tree portfast edge
  no shutdown
interface port-channel10
  description Uplink Port-Channel
  switchport mode trunk
  switchport trunk allowed vlan 100,200
"""
        
        response = client.post("/config/upload", json={
            "config_text": interface_standard_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects interface validation
        assert "validation_id" in result
    
    def test_spanning_tree_configuration_per_cisco_best_practices(self):
        """
        Cisco Professional Scenario: STP configuration must follow Cisco best practices.
        
        Expected Behavior:
        - System validates STP mode configuration
        - Detects STP misconfigurations
        - Validates Rapid PVST+ configuration
        - Checks for STP root bridge issues
        """
        # STP configuration following Cisco best practices
        stp_config = """
hostname N9K-SWITCH
spanning-tree mode rapid-pvst
spanning-tree vlan 100 priority 24576
spanning-tree vlan 200 priority 24576
interface Ethernet1/1
  spanning-tree portfast edge
"""
        
        response = client.post("/config/upload", json={
            "config_text": stp_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects STP validation
        assert "validation_id" in result
    
    def test_nxos_version_specific_features(self):
        """
        Cisco Professional Scenario: Features vary by NX-OS version.
        
        Expected Behavior:
        - System validates NX-OS version compatibility
        - Detects unsupported features for version
        - Provides version-specific guidance
        - Warns about deprecated features
        """
        # NX-OS 9.3 specific features
        nxos_93_config = """
hostname N9K-SWITCH
feature bfd
feature lacp
feature lldp
"""
        
        response = client.post("/config/upload", json={
            "config_text": nxos_93_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects version validation
        assert "validation_id" in result
    
    def test_hardware_specific_configuration(self):
        """
        Cisco Professional Scenario: Configuration must match hardware capabilities.
        
        Expected Behavior:
        - System validates hardware-specific features
        - Detects unsupported features for hardware
        - Validates port speed capabilities
        - Checks for hardware limitations
        """
        # 93180YC-EX specific configuration
        hardware_config = """
hostname N9K-SWITCH
feature lacp
interface Ethernet1/1
  description 10G Port
  speed 10000
"""
        
        response = client.post("/config/upload", json={
            "config_text": hardware_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects hardware validation
        assert "validation_id" in result
    
    def test_cisco_validated_design_compliance(self):
        """
        Cisco Professional Scenario: Configuration should align with Cisco Validated Designs.
        
        Expected Behavior:
        - System validates against CVD patterns
        - Detects deviations from CVD
        - Provides CVD-specific recommendations
        """
        # CVD-compliant spine-leaf configuration
        cvd_config = """
hostname N9K-SPINE-01
feature bgp
feature interface-vlan
router bgp 65001
  router-id 10.1.1.1
  address-family ipv4 unicast
"""
        
        response = client.post("/config/upload", json={
            "config_text": cvd_config,
            "hardware_model": "Nexus 9336C-FX2",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects CVD validation
        assert "validation_id" in result
    
    def test_nxos_security_hardening_per_cisco_guide(self):
        """
        Cisco Professional Scenario: Security hardening per Cisco NX-OS Security Configuration Guide.
        
        Expected Behavior:
        - System validates security hardening
        - Detects security vulnerabilities
        - Provides security recommendations
        - Checks for default credentials
        """
        # Security-hardened configuration
        security_config = """
hostname PROD-N9K-SECURE
feature ssh
feature tacacs+
username admin password5 $5$encrypted$encryptedpassword role network-admin
ip ssh version 2
"""
        
        response = client.post("/config/upload", json={
            "config_text": security_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Cisco professional expects security validation
        assert "validation_id" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
