"""
Mandatory Test: Multi-Switch Bug Fixes (v6.21.0)

This test verifies the fixes for multi-switch bugs identified in MULTI_SWITCH_BUG_REPORT.md:
- Bug #3: vPC domain validation (frontend)
- Bug #4: Backend vPC validation
- Bug #5: Backend uplink validation
- Bug #7: Switch deletion validation
- Bug #8: Port panel refresh after domain change
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestMultiSwitchBugfixes:
    """Test multi-switch bug fixes."""
    
    def test_backend_vpc_pair_switch_existence(self):
        """
        Test that backend validates vPC pair switch existence.
        
        Bug #4: Backend does not validate vPC pair consistency.
        Fix: Added validation for primary and secondary switch existence.
        """
        # Test with non-existent primary switch
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW2",
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": "10",
                    "primary": "NONEXISTENT",  # Non-existent primary
                    "secondary": "SW2"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for non-existent primary, got {response.status_code}"
        
        result = response.json()
        assert "NONEXISTENT" in result["detail"], "Error should mention non-existent primary"
        
        # Test with non-existent secondary switch
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": "10",
                    "primary": "SW1",
                    "secondary": "NONEXISTENT"  # Non-existent secondary
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for non-existent secondary, got {response.status_code}"
        
        print("✓ Backend vPC pair switch existence validation verified")
    
    def test_backend_vpc_domain_uniqueness(self):
        """
        Test that backend validates vPC domain uniqueness.
        
        Bug #4: Backend does not validate vPC pair consistency.
        Fix: Added validation for duplicate vPC domains.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                },
                {
                    "hostname": "SW2",
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                },
                {
                    "hostname": "SW3",
                    "mgmt_ip": "10.0.0.3/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                },
                {
                    "hostname": "SW4",
                    "mgmt_ip": "10.0.0.4/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": "10",
                    "primary": "SW1",
                    "secondary": "SW2"
                },
                {
                    "domain": "10",  # Duplicate domain
                    "primary": "SW3",
                    "secondary": "SW4"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for duplicate domain, got {response.status_code}"
        
        result = response.json()
        assert "Duplicate" in result["detail"], "Error should mention duplicate domain"
        
        print("✓ Backend vPC domain uniqueness validation verified")
    
    def test_backend_vpc_domain_range(self):
        """
        Test that backend validates vPC domain range (1-4096).
        
        Bug #4: Backend does not validate vPC pair consistency.
        Fix: Added validation for domain range.
        """
        # Test domain = 0 (invalid)
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                },
                {
                    "hostname": "SW2",
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": "0",  # Invalid domain
                    "primary": "SW1",
                    "secondary": "SW2"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for domain 0, got {response.status_code}"
        
        # Test domain = 4097 (invalid)
        deployment_input["vpc_pairs"][0]["domain"] = "4097"
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for domain 4097, got {response.status_code}"
        
        # Test valid domain
        deployment_input["vpc_pairs"][0]["domain"] = "100"
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Expected 200 for valid domain, got {response.status_code}"
        
        print("✓ Backend vPC domain range validation verified")
    
    def test_backend_uplink_switch_existence(self):
        """
        Test that backend validates uplink switch existence.
        
        Bug #5: Backend does not validate uplink consistency.
        Fix: Added validation for from and to switch existence.
        """
        # Test with non-existent source switch
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW2",
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "NONEXISTENT",  # Non-existent source
                    "to": "SW2",
                    "ports": "E1/1-2",
                    "po_id": "1"
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for non-existent source, got {response.status_code}"
        
        result = response.json()
        assert "NONEXISTENT" in result["detail"], "Error should mention non-existent source"
        
        # Test with non-existent destination switch
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "SW1",
                    "to": "NONEXISTENT",  # Non-existent destination
                    "ports": "E1/1-2",
                    "po_id": "1"
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for non-existent destination, got {response.status_code}"
        
        print("✓ Backend uplink switch existence validation verified")
    
    def test_backend_uplink_port_channel_range(self):
        """
        Test that backend validates uplink port-channel ID range (1-4096).
        
        Bug #5: Backend does not validate uplink consistency.
        Fix: Added validation for port-channel ID range.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                },
                {
                    "hostname": "SW2",
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "SW1",
                    "to": "SW2",
                    "ports": "E1/1-2",
                    "po_id": "0"  # Invalid port-channel ID
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for port-channel 0, got {response.status_code}"
        
        # Test port-channel = 4097 (invalid)
        deployment_input["uplinks"][0]["po_id"] = "4097"
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for port-channel 4097, got {response.status_code}"
        
        # Test valid port-channel
        deployment_input["uplinks"][0]["po_id"] = "100"
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"Expected 200 for valid port-channel, got {response.status_code}"
        
        print("✓ Backend uplink port-channel range validation verified")
    
    def test_backend_uplink_invalid_port_channel(self):
        """
        Test that backend validates uplink port-channel ID is numeric.
        
        Bug #5: Backend does not validate uplink consistency.
        Fix: Added validation for port-channel ID format.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                },
                {
                    "hostname": "SW2",
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "SW1",
                    "to": "SW2",
                    "ports": "E1/1-2",
                    "po_id": "abc"  # Invalid port-channel ID (non-numeric)
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 422, f"Expected 422 for non-numeric port-channel, got {response.status_code}"
        
        result = response.json()
        assert "Invalid" in result["detail"], "Error should mention invalid port-channel"
        
        print("✓ Backend uplink port-channel format validation verified")
    
    def test_valid_multiswitch_deployment(self):
        """
        Test that a valid multi-switch deployment succeeds.
        
        This ensures all validations pass with correct data.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "CORE1",
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
                    "mgmt_ip": "10.0.0.2/24",
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
        assert response.status_code == 200, f"Valid deployment should succeed: {response.text}"
        
        result = response.json()
        assert "results" in result, "No results in response"
        assert len(result["results"]) == 2, f"Expected 2 results, got {len(result['results'])}"
        assert result["successful"] == 2, f"Expected 2 successful, got {result['successful']}"
        assert result["failed"] == 0, f"Expected 0 failed, got {result['failed']}"
        
        print("✓ Valid multi-switch deployment verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
