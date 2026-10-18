"""Test the deployment generation API endpoint for multi-switch deployments."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


def test_generate_deployment_endpoint_exists():
    """Test that the /generate-deployment endpoint exists and is accessible."""
    from api.main import app
    client = TestClient(app)
    
    response = client.post("/generate-deployment", json={
        "switches": [],
        "vpc_pairs": [],
        "uplinks": []
    })
    # Should return 200 or 422 (validation error for empty switches is acceptable)
    assert response.status_code in [200, 422]


def test_generate_deployment_with_single_switch():
    """Test generating configuration for a single switch deployment."""
    from api.main import app
    client = TestClient(app)
    
    deployment_input = {
        "switches": [
            {
                "hostname": "core-sw1",
                "mgmt_ip": "10.10.10.1/24",
                "mgmt_gw": "10.10.10.1",
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
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "core"
            }
        ],
        "vpc_pairs": [],
        "uplinks": []
    }
    
    response = client.post("/generate-deployment", json=deployment_input)
    
    assert response.status_code == 200
    result = response.json()
    
    assert "status" in result
    assert "total_switches" in result
    assert "successful" in result
    assert "failed" in result
    assert result["total_switches"] == 1
    assert result["successful"] == 1
    assert result["failed"] == 0
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["hostname"] == "core-sw1"
    assert "export" in result["results"][0]


def test_generate_deployment_with_vpc_pair():
    """Test generating configuration for a vPC pair deployment."""
    from api.main import app
    client = TestClient(app)
    
    deployment_input = {
        "switches": [
            {
                "hostname": "core-sw1",
                "mgmt_ip": "10.10.10.1/24",
                "mgmt_gw": "10.10.10.1",
                "site_name": "HQ",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
                "vpc_domain": "100",
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.10.10.1",
                "remote_ka": "10.10.10.2",
                "vpc_pl_ints": "Ethernet1/51-52",
                "base_access_vlan": 10,
                "access_vlan_count": 4,
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "core"
            },
            {
                "hostname": "core-sw2",
                "mgmt_ip": "10.10.10.2/24",
                "mgmt_gw": "10.10.10.1",
                "site_name": "HQ",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
                "vpc_domain": "100",
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.10.10.2",
                "remote_ka": "10.10.10.1",
                "vpc_pl_ints": "Ethernet1/51-52",
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
                "primary": "core-sw1",
                "secondary": "core-sw2",
                "domain": "100",
                "peer_link_ports": "Ethernet1/51-52"
            }
        ],
        "uplinks": []
    }
    
    response = client.post("/generate-deployment", json=deployment_input)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["total_switches"] == 2
    assert result["successful"] == 2
    assert result["failed"] == 0
    assert len(result["results"]) == 2


def test_generate_deployment_with_leaf_switches():
    """Test generating configuration for core + leaf deployment."""
    from api.main import app
    client = TestClient(app)
    
    deployment_input = {
        "switches": [
            {
                "hostname": "core-sw1",
                "mgmt_ip": "10.10.10.1/24",
                "mgmt_gw": "10.10.10.1",
                "site_name": "HQ",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
                "vpc_domain": "100",
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.10.10.1",
                "remote_ka": "10.10.10.2",
                "vpc_pl_ints": "Ethernet1/51-52",
                "base_access_vlan": 10,
                "access_vlan_count": 4,
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "core"
            },
            {
                "hostname": "core-sw2",
                "mgmt_ip": "10.10.10.2/24",
                "mgmt_gw": "10.10.10.1",
                "site_name": "HQ",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
                "vpc_domain": "100",
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.10.10.2",
                "remote_ka": "10.10.10.1",
                "vpc_pl_ints": "Ethernet1/51-52",
                "base_access_vlan": 10,
                "access_vlan_count": 4,
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "core"
            },
            {
                "hostname": "leaf-sw1",
                "mgmt_ip": "10.10.10.11/24",
                "mgmt_gw": "10.10.10.1",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
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
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf"
            }
        ],
        "vpc_pairs": [
            {
                "primary": "core-sw1",
                "secondary": "core-sw2",
                "domain": "100",
                "peer_link_ports": "Ethernet1/51-52"
            }
        ],
        "uplinks": [
            {
                "from": "leaf-sw1",
                "to": "core-sw1",
                "ports": "Ethernet1/53-54",
                "po_id": 10
            },
            {
                "from": "leaf-sw1",
                "to": "core-sw2",
                "ports": "Ethernet1/53-54",
                "po_id": 10
            }
        ]
    }
    
    response = client.post("/generate-deployment", json=deployment_input)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["total_switches"] == 3
    assert result["successful"] == 3
    assert result["failed"] == 0
    assert len(result["results"]) == 3
    
    # Verify all switches have configs
    hostnames = [r["hostname"] for r in result["results"]]
    assert "core-sw1" in hostnames
    assert "core-sw2" in hostnames
    assert "leaf-sw1" in hostnames


def test_spine_leaf_vpc_deployment_respects_vlan_parameters():
    """Test that spine switches don't get vPC config when only leaves are in vPC pairs.
    
    This test validates the fix for the bug where spine switches were incorrectly
    getting vPC domain configuration and VLANs from vpc_core_pair scenario just
    because leaf switches had vPC pairs.
    """
    from api.main import app
    client = TestClient(app)
    
    deployment_input = {
        "switches": [
            {
                "hostname": "SPINE1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.0.0.1",
                "remote_ka": "10.0.0.2",
                "vpc_pl_ints": "",
                "base_access_vlan": 10,
                "access_vlan_count": 4,
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "spine"
            },
            {
                "hostname": "SPINE2",
                "mgmt_ip": "10.0.0.2/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.0.0.2",
                "remote_ka": "10.0.0.1",
                "vpc_pl_ints": "",
                "base_access_vlan": 10,
                "access_vlan_count": 4,
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "spine"
            },
            {
                "hostname": "LEAF1",
                "mgmt_ip": "10.0.0.11/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": "100",
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.0.0.11",
                "remote_ka": "10.0.0.12",
                "vpc_pl_ints": "Ethernet1/35-36",
                "base_access_vlan": 100,
                "access_vlan_count": 4,
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
                "vpc_peer_link_id": 1,
                "keepalive_po_id": 2,
                "vpc_system_priority": 32667,
                "local_ka": "10.0.0.12",
                "remote_ka": "10.0.0.11",
                "vpc_pl_ints": "Ethernet1/35-36",
                "base_access_vlan": 100,
                "access_vlan_count": 4,
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
                "peer_link_ports": "Ethernet1/35-36"
            }
        ],
        "uplinks": [
            {
                "from": "LEAF1",
                "to": "SPINE1",
                "ports": "Ethernet1/1-2",
                "po_id": 10
            },
            {
                "from": "LEAF1",
                "to": "SPINE2",
                "ports": "Ethernet1/3-4",
                "po_id": 10
            },
            {
                "from": "LEAF2",
                "to": "SPINE1",
                "ports": "Ethernet1/1-2",
                "po_id": 10
            },
            {
                "from": "LEAF2",
                "to": "SPINE2",
                "ports": "Ethernet1/3-4",
                "po_id": 10
            }
        ]
    }
    
    response = client.post("/generate-deployment", json=deployment_input)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["total_switches"] == 4
    assert result["successful"] == 4
    assert result["failed"] == 0
    
    # Get configs for each switch
    configs = {r["hostname"]: r["export"] for r in result["results"]}
    
    # Extract config strings (export might be a dict with 'config' key)
    def get_config_str(export):
        if isinstance(export, dict):
            return export.get("config", str(export))
        return str(export)
    
    spine1_config = get_config_str(configs["SPINE1"])
    spine2_config = get_config_str(configs["SPINE2"])
    
    # Spines should NOT have vPC domain configuration since they're not in a vPC pair
    assert "vpc domain" not in spine1_config.lower() or spine1_config.lower().count("vpc domain") == 0
    assert "vpc domain" not in spine2_config.lower() or spine2_config.lower().count("vpc domain") == 0
    
    # Spines should have VLANs based on their base_access_vlan (10), not leaf VLANs (100)
    assert "TRANSIT_10" in spine1_config or "vlan 10" in spine1_config
    assert "TRANSIT_10" in spine2_config or "vlan 10" in spine2_config
    
    # Leaf switches should have vPC domain 100
    leaf1_config = get_config_str(configs["LEAF1"])
    leaf2_config = get_config_str(configs["LEAF2"])
    
    assert "vpc domain 100" in leaf1_config
    assert "vpc domain 100" in leaf2_config
    
    # Leaves should have VLANs based on their base_access_vlan (100)
    assert "FABRIC_100" in leaf1_config or "vlan 100" in leaf1_config
    assert "FABRIC_100" in leaf2_config or "vlan 100" in leaf2_config
    
    # Verify keepalive IPs use actual management IPs, not hardcoded 1.1.1.1/1.1.1.2
    assert "10.0.0.11" in leaf1_config  # Local keepalive should use mgmt IP
    assert "10.0.0.12" in leaf1_config  # Remote keepalive should use peer mgmt IP
    assert "10.0.0.12" in leaf2_config  # Local keepalive should use mgmt IP
    assert "10.0.0.11" in leaf2_config  # Remote keepalive should use peer mgmt IP
    
    # Should NOT have hardcoded 1.1.1.1 or 1.1.1.2
    assert "1.1.1.1" not in leaf1_config
    assert "1.1.1.2" not in leaf1_config
    assert "1.1.1.1" not in leaf2_config
    assert "1.1.1.2" not in leaf2_config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
