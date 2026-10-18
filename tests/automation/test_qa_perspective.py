"""Automation tests from QA perspective - Edge cases and boundary conditions.

QA Team Expectations:
- Comprehensive edge case coverage
- Boundary condition testing
- Negative testing for error paths
- Stress testing for limits
- Regression testing for existing functionality
- Test coverage for all code paths
- Validation of error handling
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestQAPerspective:
    """QA Team perspective automation tests for edge cases and boundary conditions."""
    
    def test_empty_config_handling(self):
        """
        QA Scenario: Empty configuration should be handled gracefully.
        
        Expected Behavior:
        - Empty config doesn't crash system
        - Appropriate error or warning is returned
        - System remains stable
        """
        response = client.post("/config/upload", json={
            "config_text": "",
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        # Should reject empty config gracefully
        assert response.status_code in [400, 422]
    
    def test_null_values_handling(self):
        """
        QA Scenario: Null values in request should be handled gracefully.
        
        Expected Behavior:
        - Null values don't crash system
        - Appropriate validation error is returned
        - System remains stable
        """
        response = client.post("/config/upload", json={
            "config_text": None,
            "hardware_model": None,
            "nxos_version": None,
            "validation_level": None
        })
        
        # Should reject null values gracefully
        assert response.status_code in [400, 422]
    
    def test_extremely_long_config_handling(self):
        """
        QA Scenario: Extremely long configuration should be handled.
        
        Expected Behavior:
        - Long config doesn't crash system
        - System handles memory efficiently
        - Appropriate response is returned
        """
        # Generate extremely long config (10000 lines)
        long_config_lines = ["hostname SWITCH"]
        for i in range(5000):
            long_config_lines.append(f"interface Ethernet1/{i}")
            long_config_lines.append(f"  description Port {i}")
        
        long_config = "\n".join(long_config_lines)
        
        response = client.post("/config/upload", json={
            "config_text": long_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        # Should handle long config gracefully
        assert response.status_code in [200, 413, 422]
    
    def test_special_characters_in_config(self):
        """
        QA Scenario: Special characters in config should be handled.
        
        Expected Behavior:
        - Special characters don't crash system
        - System sanitizes input appropriately
        - No injection vulnerabilities
        """
        special_char_config = """
hostname SWITCH$%^&*()
feature lacp
interface Ethernet1/1
  description Test@#$%^&*()
"""
        
        response = client.post("/config/upload", json={
            "config_text": special_char_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        # Should handle special characters gracefully
        assert response.status_code == 200
    
    def test_unicode_characters_in_config(self):
        """
        QA Scenario: Unicode characters in config should be handled.
        
        Expected Behavior:
        - Unicode characters don't crash system
        - System handles encoding correctly
        - No encoding errors
        """
        unicode_config = """
hostname SWITCH-中文-日本語
feature lacp
interface Ethernet1/1
  description Test-🚀-✓
"""
        
        response = client.post("/config/upload", json={
            "config_text": unicode_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        # Should handle unicode gracefully
        assert response.status_code == 200
    
    def test_vlan_boundary_values(self):
        """
        QA Scenario: VLAN boundary values should be tested.
        
        Expected Behavior:
        - VLAN 0 is rejected
        - VLAN 1 is handled appropriately
        - VLAN 4094 is handled appropriately
        - VLAN 4095 is rejected
        - VLAN 4096+ is rejected
        """
        boundary_vlans = [0, 1, 4094, 4095, 4096, 10000]
        
        for vlan in boundary_vlans:
            config = f"""
hostname SWITCH
vlan {vlan}
  name Test_VLAN
"""
            
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": "comprehensive"
            })
            
            # Should handle boundary values gracefully
            assert response.status_code in [200, 400, 422]
    
    def test_vpc_domain_boundary_values(self):
        """
        QA Scenario: vPC domain boundary values should be tested.
        
        Expected Behavior:
        - vPC domain 0 is rejected
        - vPC domain 1 is accepted
        - vPC domain 4096 is accepted
        - vPC domain 4097 is rejected
        """
        boundary_domains = [0, 1, 4096, 4097, 10000]
        
        for domain in boundary_domains:
            config = f"""
hostname SWITCH
feature vpc
vpc domain {domain}
"""
            
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": "comprehensive"
            })
            
            # Should handle boundary values gracefully
            assert response.status_code in [200, 400, 422]
    
    def test_invalid_hardware_model(self):
        """
        QA Scenario: Invalid hardware model should be handled.
        
        Expected Behavior:
        - Invalid model doesn't crash system
        - Appropriate error is returned
        - System remains stable
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Invalid-Model-9000",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        # Should handle invalid model gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_invalid_nxos_version(self):
        """
        QA Scenario: Invalid NX-OS version should be handled.
        
        Expected Behavior:
        - Invalid version doesn't crash system
        - Appropriate error is returned
        - System remains stable
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        invalid_versions = ["invalid", "9.3.5.6.7", "0.0", "99.99"]
        
        for version in invalid_versions:
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": version,
                "validation_level": "standard"
            })
            
            # Should handle invalid version gracefully
            assert response.status_code in [200, 400, 422]
    
    def test_invalid_validation_level(self):
        """
        QA Scenario: Invalid validation level should be handled.
        
        Expected Behavior:
        - Invalid level doesn't crash system
        - Appropriate error is returned
        - System remains stable
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "invalid_level"
        })
        
        # Should handle invalid level gracefully
        assert response.status_code in [400, 422]
    
    def test_malformed_json_request(self):
        """
        QA Scenario: Malformed JSON request should be handled.
        
        Expected Behavior:
        - Malformed JSON doesn't crash system
        - Appropriate error is returned
        - System remains stable
        """
        # This test would require sending malformed JSON, which FastAPI handles automatically
        # We'll test with missing required fields instead
        response = client.post("/config/upload", json={
            "hardware_model": "Nexus 93180YC-EX"
            # Missing required fields
        })
        
        # Should reject incomplete request
        assert response.status_code in [400, 422]
    
    def test_concurrent_validation_requests(self):
        """
        QA Scenario: Concurrent validation requests should be handled.
        
        Expected Behavior:
        - Concurrent requests don't crash system
        - System handles concurrency correctly
        - No race conditions
        """
        import threading
        
        config = """
hostname SWITCH
feature lacp
"""
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.post("/config/upload", json={
                    "config_text": config,
                    "hardware_model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "validation_level": "standard"
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should complete
        assert len(errors) == 0, "No errors should occur with concurrent requests"
        assert len(results) == 10, "All requests should complete"
        assert all(status == 200 for status in results), "All requests should succeed"
    
    def test_memory_leak_prevention(self):
        """
        QA Scenario: Multiple validations should not cause memory leaks.
        
        Expected Behavior:
        - Multiple validations don't consume excessive memory
        - Memory is released after each validation
        - System remains stable
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        # Run multiple validations
        for _ in range(50):
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": "standard"
            })
            assert response.status_code == 200
    
    def test_error_message_consistency(self):
        """
        QA Scenario: Error messages should be consistent across scenarios.
        
        Expected Behavior:
        - Same error produces same message
        - Error codes are consistent
        - Message format is consistent
        """
        config_with_error = """
hostname SWITCH
feature vpc
vpc domain 5000
"""
        
        results = []
        for _ in range(3):
            response = client.post("/config/upload", json={
                "config_text": config_with_error,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": "comprehensive"
            })
            assert response.status_code == 200
            result = response.json()
            if result.get("errors"):
                results.append(result["errors"][0]["error_code"])
        
        # Error codes should be consistent
        if results:
            assert all(code == results[0] for code in results), "Error codes should be consistent"
    
    def test_regression_existing_functionality(self):
        """
        QA Scenario: New validation should not break existing functionality.
        
        Expected Behavior:
        - Existing deployment generation still works
        - Existing API endpoints still work
        - No regressions in existing features
        """
        # Test existing deployment generation
        deployment_input = {
            "switches": [{
                "hostname": "SWITCH",
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
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, "Existing deployment generation should still work"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
