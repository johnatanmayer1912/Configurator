"""Integration tests for validation system with existing functionality.

This test file validates that the new validation and config upload features
integrate seamlessly with existing deployment generation, scenario application,
and hardware profile loading.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestValidationIntegration:
    """Integration tests for validation with existing functionality."""
    
    def test_config_upload_then_deployment_generation(self):
        """
        Test workflow: Upload config, validate, then generate deployment.
        
        Integration Scenario:
        - User uploads existing configuration for validation
        - System validates and provides feedback
        - User adjusts parameters and generates new deployment
        - Both workflows should work seamlessly
        """
        # Step 1: Upload and validate existing config
        existing_config = """
hostname OLD-LEAF1
feature lacp
feature lldp
feature vpc
vpc domain 100
interface Ethernet1/1
  description Server Port
  switchport access vlan 100
"""
        
        validation_response = client.post("/config/upload", json={
            "config_text": existing_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert validation_response.status_code == 200
        validation_result = validation_response.json()
        assert "validation_id" in validation_result
        assert "detected_role" in validation_result
        
        # Step 2: Generate new deployment based on validated config insights
        deployment_input = {
            "switches": [
                {
                    "hostname": "NEW-LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        deployment_response = client.post("/generate-deployment", json=deployment_input)
        
        assert deployment_response.status_code == 200
        deployment_result = deployment_response.json()
        assert deployment_result["total_switches"] == 1
        assert deployment_result["successful"] == 1
    
    def test_validation_service_with_deployment_state(self):
        """
        Test validation service integration with deployment state management.
        
        Integration Scenario:
        - Generate deployment
        - Validate deployment state
        - Both systems should work together
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                },
                {
                    "hostname": "LEAF2",
                    "mgmt_ip": "10.0.0.12/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [
                {
                    "primary": "LEAF1",
                    "secondary": "LEAF2",
                    "domain": "100",
                    "peer_link_ports": "Ethernet1/51-52"
                }
            ],
            "uplinks": []
        }
        
        # Generate deployment
        deployment_response = client.post("/generate-deployment", json=deployment_input)
        assert deployment_response.status_code == 200
        
        # Validate deployment state
        state_response = client.get("/deployment/state/validate")
        assert state_response.status_code == 200
        state_result = state_response.json()
        assert "valid" in state_result or "is_valid" in state_result
    
    def test_validation_with_hardware_profile_loading(self):
        """
        Test validation integration with hardware profile loading.
        
        Integration Scenario:
        - Validate config with specific hardware model
        - System should load correct hardware profile
        - Validation should use hardware constraints
        """
        config_text = """
hostname TEST-SWITCH
feature lacp
vlan 100
  name Test_VLAN
"""
        
        # Test with different hardware models
        for hardware_model in ["Nexus 93180YC-EX", "Nexus 9336C-FX2", "Nexus 9348GC-FXP"]:
            response = client.post("/config/upload", json={
                "config_text": config_text,
                "hardware_model": hardware_model,
                "nxos_version": "9.3",
                "validation_level": "comprehensive"
            })
            
            assert response.status_code == 200
            result = response.json()
            assert "validation_id" in result
            assert "detected_role" in result
    
    def test_validation_with_scenario_application(self):
        """
        Test validation integration with scenario application.
        
        Integration Scenario:
        - Validate config to detect role
        - Apply appropriate scenario based on detected role
        - Both systems should align
        """
        # Config that should be detected as leaf
        leaf_config = """
hostname TEST-LEAF
feature lacp
feature lldp
interface Ethernet1/1
  description Access Port
  switchport access vlan 100
"""
        
        validation_response = client.post("/config/upload", json={
            "config_text": leaf_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert validation_response.status_code == 200
        validation_result = validation_response.json()
        detected_role = validation_result.get("detected_role", "")
        
        # Generate deployment with matching role
        deployment_input = {
            "switches": [
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": detected_role if detected_role else "leaf"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        deployment_response = client.post("/generate-deployment", json=deployment_input)
        assert deployment_response.status_code == 200
    
    def test_baseline_validation_with_deployment(self):
        """
        Test baseline validation integration with deployment generation.
        
        Integration Scenario:
        - Validate config with baseline options
        - Generate deployment with same baseline options
        - Both should handle baselines consistently
        """
        config_text = """
hostname TEST-SWITCH
feature lacp
feature snmp
"""
        
        # Validate with baseline options
        validation_response = client.post("/config/upload", json={
            "config_text": config_text,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive",
            "baseline_options": ["baseline_cfs", "baseline_snmp_traps"]
        })
        
        assert validation_response.status_code == 200
        validation_result = validation_response.json()
        
        # Generate deployment with same baseline options
        deployment_input = {
            "switches": [
                {
                    "hostname": "SWITCH1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf",
                    "baseline_options": ["baseline_cfs", "baseline_snmp_traps"]
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        deployment_response = client.post("/generate-deployment", json=deployment_input)
        assert deployment_response.status_code == 200
    
    def test_vpc_validation_with_vpc_deployment(self):
        """
        Test vPC validation integration with vPC deployment generation.
        
        Integration Scenario:
        - Validate config with vPC configuration
        - Generate vPC deployment
        - Both should handle vPC consistently
        """
        vpc_config = """
hostname TEST-LEAF1
feature vpc
vpc domain 100
  peer-keepalive destination 10.10.10.2 source 10.10.10.1
interface port-channel1
  vpc peer-link
interface Ethernet1/51-52
  channel-group 1 mode active
"""
        
        validation_response = client.post("/config/upload", json={
            "config_text": vpc_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert validation_response.status_code == 200
        validation_result = validation_response.json()
        assert validation_result.get("vpc_domain_id") == 100
        
        # Generate vPC deployment
        deployment_input = {
            "switches": [
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                },
                {
                    "hostname": "LEAF2",
                    "mgmt_ip": "10.0.0.12/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [
                {
                    "primary": "LEAF1",
                    "secondary": "LEAF2",
                    "domain": "100",
                    "peer_link_ports": "Ethernet1/51-52"
                }
            ],
            "uplinks": []
        }
        
        deployment_response = client.post("/generate-deployment", json=deployment_input)
        assert deployment_response.status_code == 200
        deployment_result = deployment_response.json()
        assert deployment_result["total_switches"] == 2
        assert deployment_result["successful"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
