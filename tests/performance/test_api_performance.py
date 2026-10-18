"""Performance tests for API endpoints.

This test file validates API performance under various load conditions including
response times, throughput, and resource utilization.
"""

import pytest
import time
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestAPIPerformance:
    """Performance tests for API endpoints."""
    
    def test_single_switch_generation_performance(self):
        """
        Test single switch configuration generation performance.
        
        Performance Criteria:
        - Single switch generation should complete within 2 seconds
        - Response should include all required fields
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
        
        start_time = time.time()
        response = client.post("/generate-deployment", json=deployment_input)
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 2.0, f"Single switch generation took {elapsed_time:.2f}s, expected < 2.0s"
        
        result = response.json()
        assert result["total_switches"] == 1
        assert result["successful"] == 1
    
    def test_vpc_pair_generation_performance(self):
        """
        Test vPC pair configuration generation performance.
        
        Performance Criteria:
        - vPC pair generation should complete within 3 seconds
        - Both switches should be generated successfully
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
        
        start_time = time.time()
        response = client.post("/generate-deployment", json=deployment_input)
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 3.0, f"vPC pair generation took {elapsed_time:.2f}s, expected < 3.0s"
        
        result = response.json()
        assert result["total_switches"] == 2
        assert result["successful"] == 2
    
    def test_config_upload_validation_performance(self):
        """
        Test configuration upload and validation performance.
        
        Performance Criteria:
        - Config validation should complete within 1 second
        - Should return comprehensive validation results
        """
        config_text = """
hostname TEST-SWITCH
feature lacp
feature lldp
interface Ethernet1/1
  description Test Interface
  no shutdown
"""
        
        start_time = time.time()
        response = client.post("/config/upload", json={
            "config_text": config_text,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 1.0, f"Config validation took {elapsed_time:.2f}s, expected < 1.0s"
        
        result = response.json()
        assert "validation_id" in result
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
    
    def test_large_config_validation_performance(self):
        """
        Test large configuration validation performance.
        
        Performance Criteria:
        - Large config (1000+ lines) validation should complete within 5 seconds
        """
        # Generate a large configuration
        config_lines = ["hostname TEST-SWITCH", "feature lacp", "feature lldp"]
        for i in range(500):
            config_lines.append(f"interface Ethernet1/{i}")
            config_lines.append(f"  description Port {i}")
            config_lines.append("  no shutdown")
        
        config_text = "\n".join(config_lines)
        
        start_time = time.time()
        response = client.post("/config/upload", json={
            "config_text": config_text,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 5.0, f"Large config validation took {elapsed_time:.2f}s, expected < 5.0s"
    
    def test_deployment_state_operations_performance(self):
        """
        Test deployment state CRUD operations performance.
        
        Performance Criteria:
        - State operations should complete within 500ms
        """
        # Test state retrieval
        start_time = time.time()
        response = client.get("/deployment/state")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 0.5, f"State retrieval took {elapsed_time:.3f}s, expected < 0.5s"
        
        # Test state validation
        start_time = time.time()
        response = client.get("/deployment/state/validate")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 0.5, f"State validation took {elapsed_time:.3f}s, expected < 0.5s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
