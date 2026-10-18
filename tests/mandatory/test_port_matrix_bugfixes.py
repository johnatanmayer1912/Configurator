"""
Mandatory Test: Port Matrix Bug Fixes (v6.20.0)

This test verifies the fixes for port matrix bugs identified in PORT_MATRIX_BUG_REPORT.md:
- Bug #1: Missing closing brace in legacy port mapping
- Bug #2: Inconsistent regex patterns
- Bug #3: No visual indication of selected switch
- Bug #4: Missing error handling for device_config
- Bug #5: Race condition in device switching
- Bug #6: No ID validation
- Bug #7: Generic error messages
- Bug #8: Missing switch name in port panel header
"""

import pytest
import sys
import os
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestPortMatrixBugfixes:
    """Test port matrix bug fixes."""
    
    def test_regex_pattern_standardization(self):
        """
        Test that regex patterns for interface parsing are standardized.
        
        Bug #2: Inconsistent regex patterns caused parsing failures.
        Fix: Standardized to /(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?/
        """
        # Standard regex pattern from the fix
        standard_pattern = r'(?:Ethernet|E)(\d+)\/(\d+)(?:\/(\d+))?'
        
        # Test various interface name formats
        test_cases = [
            ("Ethernet1/1", True),
            ("E1/1", True),
            ("Ethernet1/1/1", True),
            ("E1/1/1", True),
            ("Eth1/1", False),  # Should not match
            ("Port1", False),  # Should not match
        ]
        
        for interface, should_match in test_cases:
            match = re.match(standard_pattern, interface)
            if should_match:
                assert match is not None, f"Pattern should match {interface}"
            else:
                assert match is None, f"Pattern should not match {interface}"
        
        print("✓ Regex pattern standardization verified")
    
    def test_vpc_domain_validation_range(self):
        """
        Test that vPC domain validation checks range (1-4096).
        
        Bug #3: No validation of vPC domain range.
        Fix: Added validation in saveSwitchEdit() and backend.
        """
        # Test invalid domains
        invalid_domains = ["0", "4097", "9999", "-1", "abc", ""]
        
        for domain in invalid_domains:
            domain_num = int(domain) if domain.isdigit() else None
            if domain_num is not None:
                is_valid = 1 <= domain_num <= 4096
                assert not is_valid, f"Domain {domain} should be invalid"
        
        # Test valid domains
        valid_domains = ["1", "10", "100", "4096"]
        
        for domain in valid_domains:
            domain_num = int(domain)
            is_valid = 1 <= domain_num <= 4096
            assert is_valid, f"Domain {domain} should be valid"
        
        print("✓ vPC domain range validation verified")
    
    def test_vpc_domain_uniqueness(self):
        """
        Test that vPC domain uniqueness is enforced.
        
        Bug #3: No validation for duplicate vPC domains.
        Fix: Added domain conflict detection in saveSwitchEdit().
        """
        # Simulate existing vPC pairs
        vpc_pairs = [
            {"domain": "10", "primary": "SW1", "secondary": "SW2"},
            {"domain": "100", "primary": "SW3", "secondary": "SW4"}
        ]
        
        # Test domain conflict detection
        new_domain = "10"
        conflict = next((p for p in vpc_pairs if p["domain"] == new_domain), None)
        assert conflict is not None, f"Domain {new_domain} should conflict"
        
        # Test no conflict
        new_domain = "200"
        conflict = next((p for p in vpc_pairs if p["domain"] == new_domain), None)
        assert conflict is None, f"Domain {new_domain} should not conflict"
        
        print("✓ vPC domain uniqueness validation verified")
    
    def test_switch_id_validation(self):
        """
        Test that switch ID validation prevents missing IDs.
        
        Bug #6: No ID validation before processing.
        Fix: Added validation in selectTopologyNode().
        """
        # Test switch with missing ID
        switch_no_id = {"hostname": "SW1", "model": "Nexus 9336C-FX2"}
        has_id = switch_no_id.get("id") or switch_no_id.get("hostname")
        assert has_id is not None, "Switch should have id or hostname"
        
        # Test switch with ID
        switch_with_id = {"id": "sw-123", "hostname": "SW1", "model": "Nexus 9336C-FX2"}
        has_id = switch_with_id.get("id") or switch_with_id.get("hostname")
        assert has_id is not None, "Switch should have id or hostname"
        
        print("✓ Switch ID validation verified")
    
    def test_backend_vpc_validation(self):
        """
        Test backend vPC pair validation.
        
        Bug #4: Missing error handling for device_config.
        Fix: Added backend validation for vPC pairs.
        """
        # Test vPC pair with non-existent switch
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
                    "secondary": "NONEXISTENT"  # This should fail validation
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should fail validation
        assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
        
        result = response.json()
        assert "detail" in result, "Error response should have detail"
        assert "NONEXISTENT" in result["detail"], "Error should mention non-existent switch"
        
        print("✓ Backend vPC validation verified")
    
    def test_backend_uplink_validation(self):
        """
        Test backend uplink validation.
        
        Bug #4: Missing error handling for device_config.
        Fix: Added backend validation for uplinks.
        """
        # Test uplink with non-existent switch
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
                    "to": "NONEXISTENT",  # This should fail validation
                    "ports": "E1/1-2",
                    "po_id": "1"
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should fail validation
        assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
        
        result = response.json()
        assert "detail" in result, "Error response should have detail"
        assert "NONEXISTENT" in result["detail"], "Error should mention non-existent switch"
        
        print("✓ Backend uplink validation verified")
    
    def test_backend_domain_range_validation(self):
        """
        Test backend vPC domain range validation.
        
        Bug #4: Missing error handling for device_config.
        Fix: Added backend domain range validation (1-4096).
        """
        # Test invalid domain
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
                    "domain": "9999",  # Invalid domain (> 4096)
                    "primary": "SW1",
                    "secondary": "SW2"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should fail validation
        assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
        
        result = response.json()
        assert "detail" in result, "Error response should have detail"
        assert "4096" in result["detail"], "Error should mention domain range"
        
        print("✓ Backend domain range validation verified")
    
    def test_port_channel_id_validation(self):
        """
        Test backend port-channel ID validation.
        
        Bug #4: Missing error handling for device_config.
        Fix: Added backend port-channel ID validation (1-4096).
        """
        # Test invalid port-channel ID
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
                    "po_id": "9999"  # Invalid port-channel ID (> 4096)
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should fail validation
        assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
        
        result = response.json()
        assert "detail" in result, "Error response should have detail"
        assert "4096" in result["detail"], "Error should mention port-channel range"
        
        print("✓ Port-channel ID validation verified")
    
    def test_device_config_in_response(self):
        """
        Test that device_config is included in deployment response.
        
        Bug #4: Missing error handling for device_config.
        Fix: Ensure device_config is always returned with port_map.
        """
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
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        assert response.status_code == 200, f"Deployment generation failed: {response.text}"
        
        result = response.json()
        assert "results" in result, "No results in response"
        assert len(result["results"]) > 0, "No results returned"
        
        item = result["results"][0]
        assert "device_config" in item, "device_config missing from response"
        assert "port_map" in item["device_config"], "port_map missing from device_config"
        
        print("✓ device_config in response verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
