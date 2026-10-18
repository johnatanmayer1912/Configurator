"""
CLI Switching Test

This test validates that the CLI configuration generation endpoint
correctly handles requests for different switch nodes and returns
appropriate configurations for each device.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


@pytest.mark.mandatory
def test_generate_config_endpoint_accepts_different_hostnames():
    """Test that the generate-config endpoint accepts requests for different hostnames."""
    base_payload = {
        "mgmt_ip": "10.0.0.1/24",
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
        "security_tier": "standard"
    }
    
    # Test with different hostnames
    for hostname in ["SWITCH1", "SWITCH2", "CORE1", "LEAF1"]:
        payload = {**base_payload, "hostname": hostname}
        response = client.post("/generate-config", json=payload)
        assert response.status_code == 200, f"Failed for hostname {hostname}: {response.text}"
        data = response.json()
        assert "export" in data or "config" in data, f"Response should contain config data for {hostname}"


@pytest.mark.mandatory
def test_generate_config_accepts_vpc_parameters():
    """Test that the generate-config endpoint accepts vPC parameters."""
    payload = {
        "hostname": "TEST-SWITCH",
        "mgmt_ip": "10.0.0.1/24",
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
        "vpc_pl_ints": "Ethernet1/35,Ethernet1/36",
        "base_access_vlan": 10,
        "access_vlan_count": 4,
        "interface_count": 48,
        "bring_up_spare_ports": False,
        "security_tier": "standard"
    }
    
    response = client.post("/generate-config", json=payload)
    assert response.status_code == 200, f"Failed with vPC parameters: {response.text}"
    data = response.json()
    assert "export" in data or "config" in data, "Response should contain config data"


@pytest.mark.mandatory
def test_generate_config_accepts_different_models():
    """Test that the generate-config endpoint accepts different switch models."""
    base_payload = {
        "hostname": "TEST-SWITCH",
        "mgmt_ip": "10.0.0.1/24",
        "mgmt_gw": "10.0.0.1",
        "site_name": "HQ",
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
        "security_tier": "standard"
    }
    
    models_to_test = ["Nexus 9336C-FX2", "Nexus 93180YC-EX", "Nexus 9348GC-FXP"]
    
    for model in models_to_test:
        payload = {**base_payload, "model": model}
        response = client.post("/generate-config", json=payload)
        assert response.status_code == 200, f"Failed for model {model}: {response.text}"
        data = response.json()
        assert "export" in data or "config" in data, f"Response should contain config data for {model}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
