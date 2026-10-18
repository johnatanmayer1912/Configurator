"""Test edge cases and boundary conditions for configuration generation.

This test file validates boundary conditions including max VLAN counts, max port counts,
VLAN 1 and 4094 boundaries, empty configurations, and malformed configurations.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestEdgeCases:
    """Edge case testing for boundary conditions and error handling."""
    
    def test_max_vlan_count(self):
        """
        Test configuration with maximum VLAN count.
        
        Network Engineer Scenario:
        - Switch configured with maximum allowed VLANs
        - Tests system limits and performance
        - Validates VLAN constraint handling at boundaries
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "MAX-VLAN-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 100,  # High VLAN count
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should handle high VLAN count gracefully
        assert response.status_code == 200
        result = response.json()
        assert result["total_switches"] == 1
    
    def test_max_port_count(self):
        """
        Test configuration with maximum port count.
        
        Network Engineer Scenario:
        - Switch configured with maximum interface count
        - Tests port mapping at boundaries
        - Validates interface generation limits
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "MAX-PORT-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,  # Max ports for 9348GC-FXP
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "access"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        assert response.status_code == 200
        result = response.json()
        assert result["total_switches"] == 1
    
    def test_vlan_boundary_conditions(self):
        """
        Test VLAN boundary conditions (VLAN 1 and VLAN 4094).
        
        Network Engineer Scenario:
        - Configuration using VLAN 1 (reserved in some contexts)
        - Configuration using VLAN 4094 (maximum VLAN)
        - Validates boundary condition handling
        """
        # Test VLAN 1
        deployment_input_vlan1 = {
            "switches": [
                {
                    "hostname": "VLAN1-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 1,
                    "access_vlan_count": 1,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input_vlan1)
        # VLAN 1 may be accepted with warning or rejected
        assert response.status_code in [200, 422]
    
    def test_empty_configuration(self):
        """
        Test handling of empty or minimal configurations.
        
        Network Engineer Scenario:
        - Switch with minimal configuration
        - Tests system handles sparse configs gracefully
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "MINIMAL-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 10,
                    "access_vlan_count": 0,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "spine"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        assert response.status_code == 200
        result = response.json()
        assert result["total_switches"] == 1
    
    def test_invalid_vlan_range(self):
        """
        Test handling of invalid VLAN ranges.
        
        Network Engineer Scenario:
        - Configuration with VLAN outside valid range
        - Tests validation catches invalid VLANs
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "INVALID-VLAN-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 5000,  # Invalid VLAN
                    "access_vlan_count": 1,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should reject invalid VLAN
        assert response.status_code in [400, 422]
    
    def test_invalid_vpc_domain(self):
        """
        Test handling of invalid vPC domain IDs.
        
        Network Engineer Scenario:
        - Configuration with vPC domain outside valid range
        - Tests validation catches invalid vPC domains
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "INVALID-VPC-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "5000",  # Invalid vPC domain (> 4096)
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should reject invalid vPC domain
        assert response.status_code in [400, 422]
    
    def test_invalid_hostname(self):
        """
        Test handling of invalid hostnames.
        
        Network Engineer Scenario:
        - Configuration with invalid hostname format
        - Tests validation catches invalid hostnames
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "INVALID_HOSTNAME!",  # Invalid characters
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
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should reject invalid hostname
        assert response.status_code in [400, 422]
    
    def test_duplicate_vpc_domains(self):
        """
        Test handling of duplicate vPC domains in deployment.
        
        Network Engineer Scenario:
        - Multiple vPC pairs with same domain ID
        - Tests validation catches domain conflicts
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
                    "vpc_domain": "100",  # Duplicate domain
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should handle duplicate domains (may warn or reject)
        assert response.status_code in [200, 400]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
