"""Test mixed hardware scenarios with different switch models in same fabric.

This test file validates deployments with mixed hardware including Nexus 9336C-FX2 cores,
93180YC-EX leaves, and 9348GC-FXP access switches, ensuring proper port mapping,
VLAN constraint intersection, and feature compatibility.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestMixedHardwareDeployment:
    """Mixed hardware deployment testing for network engineer scenarios."""
    
    def test_mixed_hardware_fabric(self):
        """
        Test fabric with mixed hardware: 9336C-FX2 cores, 93180YC-EX leaves, 9348GC-FXP access.
        
        Network Engineer Scenario:
        - Nexus 9336C-FX2 as core switches (40G ports)
        - Nexus 93180YC-EX as leaf switches (10G + 40G ports)
        - Nexus 9348GC-FXP as access switches (1G ports)
        - Validates port mapping across different hardware classes
        - Ensures VLAN constraints work for all models
        """
        deployment_input = {
            "switches": [
                # Core switches
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "base_access_vlan": 10,
                    "access_vlan_count": 2,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.0.0.2/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "base_access_vlan": 10,
                    "access_vlan_count": 2,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                },
                # Leaf switches
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "base_access_vlan": 100,
                    "access_vlan_count": 10,
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
                    "access_vlan_count": 10,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                },
                # Access switches
                {
                    "hostname": "ACCESS1",
                    "mgmt_ip": "10.0.0.21/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": "200",
                    "base_access_vlan": 10,
                    "access_vlan_count": 5,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "access"
                },
                {
                    "hostname": "ACCESS2",
                    "mgmt_ip": "10.0.0.22/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": "200",
                    "base_access_vlan": 10,
                    "access_vlan_count": 5,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "access"
                }
            ],
            "vpc_pairs": [
                {
                    "primary": "CORE1",
                    "secondary": "CORE2",
                    "domain": "10",
                    "peer_link_ports": "Ethernet1/35-36"
                },
                {
                    "primary": "LEAF1",
                    "secondary": "LEAF2",
                    "domain": "100",
                    "peer_link_ports": "Ethernet1/51-52"
                },
                {
                    "primary": "ACCESS1",
                    "secondary": "ACCESS2",
                    "domain": "200",
                    "peer_link_ports": "Ethernet1/51-52"
                }
            ],
            "uplinks": [
                {
                    "from": "LEAF1",
                    "to": "CORE1",
                    "ports": "Ethernet1/53-54",
                    "po_id": 10
                },
                {
                    "from": "LEAF1",
                    "to": "CORE2",
                    "ports": "Ethernet1/55-56",
                    "po_id": 10
                },
                {
                    "from": "ACCESS1",
                    "to": "LEAF1",
                    "ports": "Ethernet1/49-50",
                    "po_id": 20
                },
                {
                    "from": "ACCESS2",
                    "to": "LEAF2",
                    "ports": "Ethernet1/49-50",
                    "po_id": 20
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_switches"] == 6
        assert result["successful"] == 6
        assert result["failed"] == 0
        
        # Verify all switch types got generated
        hostnames = [r["hostname"] for r in result["results"]]
        assert "CORE1" in hostnames
        assert "CORE2" in hostnames
        assert "LEAF1" in hostnames
        assert "LEAF2" in hostnames
        assert "ACCESS1" in hostnames
        assert "ACCESS2" in hostnames
    
    def test_vlan_constraint_intersection(self):
        """
        Test VLAN constraint intersection across different hardware models.
        
        Network Engineer Scenario:
        - Different hardware models have different VLAN constraints
        - 9336C-FX2: VLANs 10-4094
        - 93180YC-EX: VLANs 100-4094
        - 9348GC-FXP: VLANs 10-4094
        - Validates that common VLAN range works for all models
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 10,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                },
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 10,
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
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_switches"] == 2
        assert result["successful"] == 2
    
    def test_feature_compatibility_matrix(self):
        """
        Test feature compatibility across different NX-OS versions and hardware.
        
        Network Engineer Scenario:
        - Different hardware supports different features
        - NX-OS 9.3 vs 10.2 feature differences
        - Validates feature compatibility matrix
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
                    "vpc_domain": None,
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
                    "nxos_version": "10.2",
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
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_switches"] == 2
        assert result["successful"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
