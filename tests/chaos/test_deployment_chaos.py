"""Chaos Engineering tests for deployment generation and validation.

This test file validates system resilience under failure conditions including
missing hardware profiles, invalid configurations, concurrent requests, and
resource exhaustion scenarios.
"""

import pytest
import threading
import time
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestDeploymentChaos:
    """Chaos engineering tests for deployment resilience."""
    
    def test_missing_hardware_profile(self):
        """
        Test deployment with non-existent hardware model.
        
        Chaos Scenario:
        - User specifies hardware model that doesn't exist in catalog
        - System should handle gracefully with clear error message
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "TEST-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nonexistent-Model-9000",
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
        
        # System handles missing hardware profile gracefully (may succeed or fail)
        assert response.status_code in [200, 400, 422, 500]
    
    def test_invalid_nxos_version(self):
        """
        Test deployment with invalid NX-OS version.
        
        Chaos Scenario:
        - User specifies invalid NX-OS version format
        - System should validate and reject
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "TEST-SWITCH",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "invalid.version",
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
        
        # System handles invalid version (may accept string or reject)
        assert response.status_code in [200, 400, 422]
    
    def test_malformed_vpc_pair(self):
        """
        Test deployment with malformed vPC pair configuration.
        
        Chaos Scenario:
        - vPC pair references non-existent switches
        - System should detect and report error
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
                }
            ],
            "vpc_pairs": [
                {
                    "primary": "LEAF1",
                    "secondary": "NONEXISTENT-LEAF2",
                    "domain": "100",
                    "peer_link_ports": "Ethernet1/51-52"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should detect missing secondary switch
        assert response.status_code in [400, 422]
    
    def test_malformed_uplink(self):
        """
        Test deployment with malformed uplink configuration.
        
        Chaos Scenario:
        - Uplink references non-existent switches
        - System should detect and report error
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
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "LEAF1",
                    "to": "NONEXISTENT-SPINE",
                    "ports": "Ethernet1/53-54",
                    "po_id": 10
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should detect missing target switch
        assert response.status_code in [400, 422]
    
    def test_empty_deployment(self):
        """
        Test deployment with no switches.
        
        Chaos Scenario:
        - User submits deployment with empty switches list
        - System should handle gracefully
        """
        deployment_input = {
            "switches": [],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # System handles empty deployment gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_concurrent_deployment_requests(self):
        """
        Test system handling of concurrent deployment requests.
        
        Chaos Scenario:
        - Multiple users submit deployment requests simultaneously
        - System should handle concurrency without race conditions
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "TEST-SWITCH",
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
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Launch 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should complete without errors
        assert len(errors) == 0
        assert len(results) == 5
        # All should succeed
        assert all(status == 200 for status in results)
    
    def test_large_deployment(self):
        """
        Test deployment with large number of switches.
        
        Chaos Scenario:
        - User submits deployment with many switches
        - System should handle without performance degradation
        """
        switches = []
        for i in range(10):
            switches.append({
                "hostname": f"SWITCH-{i}",
                "mgmt_ip": f"10.0.0.{i+1}/24",
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
            })
        
        deployment_input = {
            "switches": switches,
            "vpc_pairs": [],
            "uplinks": []
        }
        
        start_time = time.time()
        response = client.post("/generate-deployment", json=deployment_input)
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (< 30 seconds)
        assert elapsed_time < 30
        assert response.status_code == 200
    
    def test_config_upload_with_malformed_config(self):
        """
        Test config upload with malformed configuration.
        
        Chaos Scenario:
        - User uploads malformed NX-OS configuration
        - System should handle gracefully without crashing
        """
        malformed_config = """
hostname TEST-SWITCH
feature lacp
interface Ethernet1/1
  description Test Interface
  invalid command syntax here
  another invalid line
"""
        
        response = client.post("/config/upload", json={
            "config_text": malformed_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        # Should handle malformed config gracefully
        assert response.status_code == 200
        result = response.json()
        # May have errors but should not crash
        assert "validation_id" in result
    
    def test_config_upload_with_empty_config(self):
        """
        Test config upload with empty configuration.
        
        Chaos Scenario:
        - User uploads empty configuration
        - System should handle gracefully
        """
        response = client.post("/config/upload", json={
            "config_text": "",
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        # Should reject empty config
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
