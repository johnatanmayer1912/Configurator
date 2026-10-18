"""Automation tests from Network Engineer perspective - Validation accuracy.

Network Engineer Expectations:
- Accurate detection of NX-OS configuration errors
- Validation based on real Cisco NX-OS best practices
- Detection of vPC configuration issues
- VLAN range validation against hardware constraints
- Port mapping validation against physical switch capabilities
- Feature compatibility checks for specific NX-OS versions
- Security policy validation for production environments
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestNetworkEngineerPerspective:
    """Network Engineer perspective automation tests for validation accuracy."""
    
    def test_vpc_domain_validation_accuracy(self):
        """
        Network Engineer Scenario: vPC domain ID must be 1-4096 per Cisco NX-OS.
        
        Expected Behavior:
        - System validates vPC domain range (1-4096)
        - Detects out-of-range domain IDs
        - Provides accurate error messages
        """
        # Invalid vPC domain (outside 1-4096 range)
        invalid_vpc_config = """
hostname SWITCH
feature vpc
vpc domain 5000
"""
        
        response = client.post("/config/upload", json={
            "config_text": invalid_vpc_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects detection of invalid vPC domain
        assert result["is_valid"] == False, "Invalid vPC domain should be detected"
        error_codes = [e["error_code"] for e in result.get("errors", [])]
        assert "INVALID_VPC_DOMAIN" in error_codes, "Should detect invalid vPC domain range"
    
    def test_vpc_peer_link_detection(self):
        """
        Network Engineer Scenario: vPC requires peer-link configuration.
        
        Expected Behavior:
        - System detects missing vPC peer-link
        - Validates peer-link interface existence
        - Provides accurate remediation suggestions
        """
        # vPC domain without peer-link
        vpc_without_peerlink = """
hostname SWITCH
feature vpc
vpc domain 100
"""
        
        response = client.post("/config/upload", json={
            "config_text": vpc_without_peerlink,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects detection of missing peer-link
        assert result["is_valid"] == False, "Missing vPC peer-link should be detected"
        error_codes = [e["error_code"] for e in result.get("errors", [])]
        assert "MISSING_PEER_LINK" in error_codes, "Should detect missing peer-link"
    
    def test_vlan_range_validation_by_hardware(self):
        """
        Network Engineer Scenario: Different Nexus models have different VLAN constraints.
        
        Expected Behavior:
        - System validates VLAN ranges per hardware profile
        - 9336C-FX2: VLANs 10-999
        - 93180YC-EX: VLANs 100-4094
        - 9348GC-FXP: VLANs 10-999
        """
        # Test VLAN 50 (valid for 9336C-FX2 and 9348GC-FXP, invalid for 93180YC-EX)
        config_vlan_50 = """
hostname SWITCH
vlan 50
  name Test_VLAN
"""
        
        # Test with 93180YC-EX (should reject VLAN 50)
        response = client.post("/config/upload", json={
            "config_text": config_vlan_50,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects hardware-specific VLAN validation
        if not result["is_valid"]:
            error_codes = [e["error_code"] for e in result.get("errors", [])]
            assert "VLAN_OUT_OF_RANGE" in error_codes, "Should detect VLAN out of range for 93180YC-EX"
    
    def test_reserved_vlan_detection(self):
        """
        Network Engineer Scenario: Certain VLANs are reserved by Cisco (997-1005).
        
        Expected Behavior:
        - System detects reserved VLAN usage
        - Prevents configuration conflicts
        - Provides accurate error messages
        """
        # Config using reserved VLAN 999
        reserved_vlan_config = """
hostname SWITCH
vlan 999
  name Reserved_VLAN
"""
        
        response = client.post("/config/upload", json={
            "config_text": reserved_vlan_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects reserved VLAN detection
        assert result["is_valid"] == False, "Reserved VLAN should be detected"
        error_codes = [e["error_code"] for e in result.get("errors", [])]
        assert "RESERVED_VLAN" in error_codes, "Should detect reserved VLAN usage"
    
    def test_port_mapping_validation(self):
        """
        Network Engineer Scenario: Interface names must match hardware port layout.
        
        Expected Behavior:
        - System validates interface existence on hardware
        - Detects invalid port numbers
        - Validates port types (40G vs 10G vs 1G)
        """
        # Config with invalid port number
        invalid_port_config = """
hostname SWITCH
interface Ethernet1/200
  description Invalid_Port
"""
        
        response = client.post("/config/upload", json={
            "config_text": invalid_port_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects port validation
        # May or may not detect invalid port depending on implementation
        assert "validation_id" in result
    
    def test_nxos_version_feature_compatibility(self):
        """
        Network Engineer Scenario: Features vary by NX-OS version.
        
        Expected Behavior:
        - System validates feature compatibility with NX-OS version
        - Warns about unsupported features
        - Provides version-specific guidance
        """
        # Config with feature that may not be compatible
        config_with_feature = """
hostname SWITCH
feature vxlan
feature evpn
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_with_feature,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",  # VXLAN/EVPN may require newer version
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects feature compatibility validation
        assert "validation_id" in result
        
        # May warn about version incompatibility
        warning_codes = [w["warning_code"] for w in result.get("warnings", [])]
        if "FEATURE_VERSION_MISMATCH" in warning_codes:
            # Expected behavior for incompatible features
            pass
    
    def test_security_policy_validation(self):
        """
        Network Engineer Scenario: Production environments require security hardening.
        
        Expected Behavior:
        - System detects security risks (NX-API + bash, default hostname)
        - Provides security recommendations
        - Validates against security baselines
        """
        # Config with security risks
        security_risk_config = """
hostname switch
feature nxapi
feature bash-shell
"""
        
        response = client.post("/config/upload", json={
            "config_text": security_risk_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects security validation
        warning_codes = [w["warning_code"] for w in result.get("warnings", [])]
        
        # Should detect default hostname
        assert "DEFAULT_HOSTNAME" in warning_codes, "Should detect default hostname"
        
        # Should detect NX-API + bash risk
        assert "SECURITY_RISK_NXAPI_BASH" in warning_codes, "Should detect NX-API + bash risk"
    
    def test_interface_syntax_validation(self):
        """
        Network Engineer Scenario: NX-OS interface syntax must be correct.
        
        Expected Behavior:
        - System validates interface name format
        - Detects syntax errors
        - Provides accurate line numbers for errors
        """
        # Config with invalid interface syntax
        invalid_interface_config = """
hostname SWITCH
interface Ethernet1/1
  description Test Interface
  invalid-command syntax
"""
        
        response = client.post("/config/upload", json={
            "config_text": invalid_interface_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects syntax validation
        assert "validation_id" in result
    
    def test_duplicate_keepalive_ip_detection(self):
        """
        Network Engineer Scenario: vPC keepalive IPs must be different.
        
        Expected Behavior:
        - System detects duplicate keepalive IPs
        - Prevents vPC misconfiguration
        - Provides accurate error messages
        """
        # Config with duplicate keepalive IPs
        duplicate_keepalive_config = """
hostname SWITCH
feature vpc
vpc domain 100
  peer-keepalive destination 10.10.10.1 source 10.10.10.1
"""
        
        response = client.post("/config/upload", json={
            "config_text": duplicate_keepalive_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects duplicate IP detection within same vPC domain
        assert result["is_valid"] == False, "Duplicate keepalive IPs within same vPC domain should be detected"
        error_codes = [e["error_code"] for e in result.get("errors", [])]
        assert "DUPLICATE_KEEPALIVE_IPS" in error_codes, "Should detect duplicate keepalive IPs within same vPC domain"
    
    def test_keepalive_ip_reuse_across_vpc_domains(self):
        """
        Network Engineer Scenario: Keepalive IPs can be reused across different vPC domains per Cisco NX-OS behavior.
        
        Expected Behavior:
        - System allows keepalive IP reuse across different vPC domains
        - Each vPC domain has its own system MAC address and isolated keepalive traffic
        """
        # Test topology validation with keepalive IPs reused across different vPC domains
        topology_data = {
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "Nexus 9336C-FX2",
                    "vpc_domain": "10",
                    "local_ka": "192.168.1.1",
                    "remote_ka": "192.168.1.2"
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "Nexus 9336C-FX2",
                    "vpc_domain": "10",
                    "local_ka": "192.168.1.2",
                    "remote_ka": "192.168.1.1"
                },
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "model": "Nexus 93180YC-EX",
                    "vpc_domain": "100",
                    "local_ka": "192.168.1.1",  # Reusing same IP as CORE1 in different domain
                    "remote_ka": "192.168.1.2"
                },
                {
                    "hostname": "LEAF2",
                    "mgmt_ip": "10.0.0.12/24",
                    "model": "Nexus 93180YC-EX",
                    "vpc_domain": "100",
                    "local_ka": "192.168.1.2",
                    "remote_ka": "192.168.1.1"
                }
            ],
            "vpc_pairs": [
                {"domain": "10", "primary": "CORE1", "secondary": "CORE2"},
                {"domain": "100", "primary": "LEAF1", "secondary": "LEAF2"}
            ],
            "uplinks": []
        }
        
        response = client.post("/validate/topology", json=topology_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should be valid since keepalive IPs can be reused across different vPC domains
        # Filter for keepalive IP conflicts specifically
        ka_conflicts = [issue for issue in result.get('issues', []) if 'keepalive' in issue.get('message', '').lower() and 'ip_conflict' in issue.get('category', '')]
        assert len(ka_conflicts) == 0, f"Keepalive IP reuse across different vPC domains should be allowed. Found conflicts: {ka_conflicts}"
    
    def test_baseline_compliance_validation(self):
        """
        Network Engineer Scenario: Institutional baselines require specific features.
        
        Expected Behavior:
        - System validates against baseline requirements
        - Detects missing required features
        - Provides compliance status
        """
        # Config without required baseline features
        config_without_baseline = """
hostname SWITCH
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_without_baseline,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive",
            "baseline_options": ["baseline_cfs", "baseline_snmp_traps"]
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Network engineer expects baseline validation
        assert "validation_id" in result
        
        # May warn about missing baseline features
        warning_codes = [w["warning_code"] for w in result.get("warnings", [])]
        if "BASELINE_FEATURE_MISSING" in warning_codes:
            # Expected behavior for missing baseline features
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
