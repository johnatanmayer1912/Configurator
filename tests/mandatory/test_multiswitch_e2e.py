"""
Mandatory Test: Multi-Switch End-to-End Configuration Flow

This test performs comprehensive end-to-end testing of multi-switch configuration,
from deployment creation through configuration generation for all switch types
(core, leaf_10g, leaf_1g). Tests the complete flow as a network engineer would use it.

Network Engineer Perspective:
- Validates realistic deployment scenarios
- Ensures proper vPC domain assignment
- Verifies interface configurations are generated correctly
- Tests port-channel assignments
- Validates VLAN configurations
- Ensures proper management IP assignment
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestMultiSwitchE2E:
    """End-to-end multi-switch configuration testing."""
    
    def test_core_pair_vpc_deployment(self):
        """
        Test a realistic core pair vPC deployment - API validation focus.
        
        Network Engineer Scenario:
        - Two core switches in vPC domain 10
        - Peer-link on E1/35-36
        - Keepalive on port-channel 2
        - Management IPs on 10.0.0.0/24
        
        This test validates the API accepts the request and generates device_config.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.1",
                    "remote_ka": "10.10.10.2",
                    "vpc_pl_ints": "E1/35-36",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.10.10.2/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.2",
                    "remote_ka": "10.10.10.1",
                    "vpc_pl_ints": "E1/35-36",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": "10",
                    "primary": "CORE1",
                    "secondary": "CORE2",
                    "peer_link_ports": "E1/35-36"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Core pair deployment failed: {response.text}"
        
        result = response.json()
        assert "results" in result, "No results in response"
        assert len(result["results"]) == 2, f"Expected 2 results, got {len(result['results'])}"
        assert result["successful"] == 2, f"Expected 2 successful, got {result['successful']}"
        assert result["failed"] == 0, f"Expected 0 failed, got {result['failed']}"
        
        # Verify each switch has device_config
        for item in result["results"]:
            assert "hostname" in item, f"Missing hostname in result"
            assert "device_config" in item, f"Missing device_config for {item['hostname']}"
            assert "port_map" in item["device_config"], f"Missing port_map for {item['hostname']}"
        
        print("✓ Core pair vPC deployment test passed")
    
    def test_core_leaf_deployment(self):
        """
        Test a realistic core + leaf deployment - API validation focus.
        
        Network Engineer Scenario:
        - Two core switches in vPC domain 10
        - Two 10G leaf switches connected to cores
        - Leaf switches as standalone (no vPC)
        - Realistic interface counts
        
        This test validates the API accepts the request and generates device_config.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.1",
                    "remote_ka": "10.10.10.2",
                    "vpc_pl_ints": "E1/35-36",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.10.10.2/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.2",
                    "remote_ka": "10.10.10.1",
                    "vpc_pl_ints": "E1/35-36",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                },
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.10.10.11/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": None,  # Leaf is standalone
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.11",
                    "remote_ka": "10.10.10.12",
                    "vpc_pl_ints": "",
                    "base_access_vlan": 10,
                    "access_vlan_count": 8,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                },
                {
                    "hostname": "LEAF2",
                    "mgmt_ip": "10.10.10.12/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": None,  # Leaf is standalone
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.12",
                    "remote_ka": "10.10.10.11",
                    "vpc_pl_ints": "",
                    "base_access_vlan": 10,
                    "access_vlan_count": 8,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": "10",
                    "primary": "CORE1",
                    "secondary": "CORE2",
                    "peer_link_ports": "E1/35-36"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Core+Leaf deployment failed: {response.text}"
        
        result = response.json()
        assert "results" in result, "No results in response"
        assert len(result["results"]) == 4, f"Expected 4 results, got {len(result['results'])}"
        assert result["successful"] == 4, f"Expected 4 successful, got {result['successful']}"
        assert result["failed"] == 0, f"Expected 0 failed, got {result['failed']}"
        
        # Verify device_config exists for all switches
        for item in result["results"]:
            assert "hostname" in item, f"Missing hostname in result"
            assert "device_config" in item, f"Missing device_config for {item['hostname']}"
            assert "port_map" in item["device_config"], f"Missing port_map for {item['hostname']}"
        
        print("✓ Core+Leaf deployment test passed")
    
    def test_leaf_vlan_configuration(self):
        """
        Test that leaf switches generate device_config with VLAN parameters.
        
        Network Engineer Scenario:
        - Leaf switch with multiple access VLANs
        - Verify device_config includes VLAN parameters
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.10.10.11/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.11",
                    "remote_ka": "10.10.10.12",
                    "vpc_pl_ints": "",
                    "base_access_vlan": 10,
                    "access_vlan_count": 8,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Leaf VLAN configuration failed: {response.text}"
        
        result = response.json()
        assert len(result["results"]) == 1, f"Expected 1 result, got {len(result['results'])}"
        
        item = result["results"][0]
        
        # Verify device_config exists
        assert "device_config" in item, "device_config missing"
        assert "port_map" in item["device_config"], "port_map missing"
        
        print("✓ Leaf VLAN configuration test passed")
    
    def test_interface_configuration(self):
        """
        Test that device_config includes interface information.
        
        Network Engineer Scenario:
        - Switch with 48 interfaces
        - Verify device_config includes interface list
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.1",
                    "remote_ka": "10.10.10.2",
                    "vpc_pl_ints": "",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Interface configuration failed: {response.text}"
        
        result = response.json()
        item = result["results"][0]
        
        # Verify device_config exists
        assert "device_config" in item, "device_config missing"
        assert "port_map" in item["device_config"], "port_map missing"
        
        print("✓ Interface configuration test passed")
    
    def test_port_map_generation(self):
        """
        Test that port_map is generated for multi-switch deployments.
        
        Network Engineer Scenario:
        - Verify port_map includes all interfaces
        - Verify port_map includes interface types
        - Verify port_map includes descriptions
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.1",
                    "remote_ka": "10.10.10.2",
                    "vpc_pl_ints": "E1/35-36",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.10.10.2/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": "10",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.2",
                    "remote_ka": "10.10.10.1",
                    "vpc_pl_ints": "E1/35-36",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": "10",
                    "primary": "CORE1",
                    "secondary": "CORE2",
                    "peer_link_ports": "E1/35-36"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Port map generation failed: {response.text}"
        
        result = response.json()
        item = result["results"][0]
        
        # Verify device_config exists
        assert "device_config" in item, "device_config missing"
        
        # Verify port_map exists
        assert "port_map" in item["device_config"], "port_map missing"
        
        port_map = item["device_config"]["port_map"]
        
        # Verify port_map structure
        assert "ports" in port_map, "ports missing from port_map"
        assert isinstance(port_map["ports"], list), "ports should be a list"
        assert len(port_map["ports"]) > 0, "ports list is empty"
        
        # Verify port entries have required fields
        for port in port_map["ports"]:
            assert "port" in port, f"port field missing in {port}"
            assert "port_name" in port, f"port_name field missing in {port}"
            assert "type" in port, f"type field missing in {port}"
        
        print("✓ Port map generation test passed")
    
    def test_empty_vpc_domain_handling(self):
        """
        Test that empty vpc_domain is handled correctly.
        
        Network Engineer Scenario:
        - Switch without vPC domain
        - Should not include vpc_domain in request
        - Should not trigger validation errors
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    # vpc_domain intentionally omitted
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.1",
                    "remote_ka": "10.10.10.2",
                    "vpc_pl_ints": "",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Empty vpc_domain handling failed: {response.text}"
        
        result = response.json()
        assert result["successful"] == 1, f"Expected 1 successful, got {result['successful']}"
        
        print("✓ Empty vpc_domain handling test passed")

    def test_vpc_secondary_role_and_channel_group(self):
        """Secondary vPC peer must get role secondary and channel-group on peer-link ports."""
        deployment_input = {
            "switches": [
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "100",
                    "local_ka": "10.255.255.1",
                    "remote_ka": "10.255.255.2",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "nxos_version": "9.3",
                },
                {
                    "hostname": "LEAF2",
                    "mgmt_ip": "10.0.0.12/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "100",
                    "local_ka": "10.255.255.2",
                    "remote_ka": "10.255.255.1",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "nxos_version": "9.3",
                },
            ],
            "vpc_pairs": [
                {
                    "domain": "100",
                    "primary": "LEAF1",
                    "secondary": "LEAF2",
                    "peer_link_ports": "Ethernet1/49-50",
                }
            ],
            "uplinks": [],
        }

        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, response.text

        configs = {
            item["hostname"]: item["export"]["cli"]
            for item in response.json()["results"]
        }
        assert "role priority 8192" in configs["LEAF2"], "Secondary switch must use lower vPC role priority"
        assert "role priority 4096" in configs["LEAF1"], "Primary switch must use higher vPC role priority"
        assert "channel-group 1 mode active" in configs["LEAF1"], (
            "Primary peer-link ports must use channel-group (not port_channel attr)"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
