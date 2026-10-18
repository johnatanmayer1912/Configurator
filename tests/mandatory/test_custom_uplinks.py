"""
Test custom uplink configuration and port map integration.

This test validates BUG #10 (backend uses deployment.uplinks) and BUG #6 (port map reflects custom uplinks).
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestCustomUplinks:
    """Test custom uplink configuration in multi-switch deployments."""
    
    def test_custom_uplink_configuration(self):
        """
        Test that custom uplinks from deployment are applied to switch configuration.
        
        Network Engineer Scenario:
        - User defines custom uplink between LEAF1 and CORE1
        - Backend should configure LEAF1 with uplink on specified ports
        - Port map should include the custom uplink
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
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                },
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
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
                    "role": "core"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "LEAF1",
                    "to": "CORE1",
                    "ports": "E1/5-6",
                    "po_id": "50"
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Custom uplink configuration failed: {response.text}"
        
        result = response.json()
        assert "results" in result, "No results in response"
        
        # Find LEAF1 result
        leaf1_result = next((r for r in result["results"] if r["hostname"] == "LEAF1"), None)
        assert leaf1_result is not None, "LEAF1 result not found"
        
        # Verify device_config exists
        assert "device_config" in leaf1_result, "device_config missing for LEAF1"
        
        # Verify uplink_config includes custom uplink
        uplink_config = leaf1_result["device_config"].get("uplink_config", [])
        assert len(uplink_config) > 0, "uplink_config is empty"
        
        # Verify E1/5 and E1/6 are configured
        uplink_interfaces = [u["interface"] for u in uplink_config]
        assert "E1/5" in uplink_interfaces, "E1/5 not in uplink_config"
        assert "E1/6" in uplink_interfaces, "E1/6 not in uplink_config"
        
        # Verify descriptions point to CORE1
        for uplink in uplink_config:
            if uplink["interface"] in ["E1/5", "E1/6"]:
                assert "CORE1" in uplink["description"], f"Uplink description doesn't mention CORE1: {uplink['description']}"
        
        print("✓ Custom uplink configuration test passed")
    
    def test_custom_uplink_port_map_integration(self):
        """
        Test that custom uplinks appear in port map.
        
        Network Engineer Scenario:
        - User defines custom uplink
        - Port map should show the uplink ports with correct type
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
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                },
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
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
                    "role": "core"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "LEAF1",
                    "to": "CORE1",
                    "ports": "E1/10",
                    "po_id": "100"
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Custom uplink port map test failed: {response.text}"
        
        result = response.json()
        leaf1_result = next((r for r in result["results"] if r["hostname"] == "LEAF1"), None)
        
        # Verify port_map exists
        assert "port_map" in leaf1_result["device_config"], "port_map missing"
        port_map = leaf1_result["device_config"]["port_map"]
        
        # Verify ports list includes uplink
        assert "ports" in port_map, "ports missing from port_map"
        ports = port_map["ports"]
        
        # Find E1/10 in port map
        e1_10_port = next((p for p in ports if "10" in p.get("port_name", "")), None)
        assert e1_10_port is not None, "E1/10 not found in port_map"
        
        # Verify port type is uplink
        assert e1_10_port.get("type") == "uplink", f"Expected uplink type, got {e1_10_port.get('type')}"
        
        # Verify description mentions CORE1
        assert "CORE1" in e1_10_port.get("description", ""), f"Port description doesn't mention CORE1: {e1_10_port.get('description')}"
        
        print("✓ Custom uplink port map integration test passed")
    
    def test_multiple_custom_uplinks(self):
        """
        Test multiple custom uplinks from one switch.
        
        Network Engineer Scenario:
        - Switch has multiple uplinks to different switches
        - All uplinks should be configured
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
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                },
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
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
                    "role": "core"
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.10.10.2/24",
                    "mgmt_gw": "10.0.0.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.10.10.2",
                    "remote_ka": "10.10.10.1",
                    "vpc_pl_ints": "",
                    "base_access_vlan": 10,
                    "access_vlan_count": 4,
                    "interface_count": 48,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "core"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "LEAF1",
                    "to": "CORE1",
                    "ports": "E1/5-6",
                    "po_id": "50"
                },
                {
                    "from": "LEAF1",
                    "to": "CORE2",
                    "ports": "E1/7-8",
                    "po_id": "51"
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Multiple uplinks test failed: {response.text}"
        
        result = response.json()
        leaf1_result = next((r for r in result["results"] if r["hostname"] == "LEAF1"), None)
        
        uplink_config = leaf1_result["device_config"].get("uplink_config", [])
        uplink_interfaces = [u["interface"] for u in uplink_config]
        
        # Verify all uplink ports are configured
        assert "E1/5" in uplink_interfaces, "E1/5 not configured"
        assert "E1/6" in uplink_interfaces, "E1/6 not configured"
        assert "E1/7" in uplink_interfaces, "E1/7 not configured"
        assert "E1/8" in uplink_interfaces, "E1/8 not configured"
        
        # Verify port-channel IDs
        e1_5_po = next((u for u in uplink_config if u["interface"] == "E1/5"), None)
        e1_7_po = next((u for u in uplink_config if u["interface"] == "E1/7"), None)
        assert str(e1_5_po["port_channel"]) == "50", f"E1/5 should have po_id 50, got {e1_5_po['port_channel']}"
        assert str(e1_7_po["port_channel"]) == "51", f"E1/7 should have po_id 51, got {e1_7_po['port_channel']}"
        
        print("✓ Multiple custom uplinks test passed")
