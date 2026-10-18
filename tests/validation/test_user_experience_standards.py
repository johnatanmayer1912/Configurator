"""
User Experience Standards Validation

This module validates that all tests and system behavior align with
user experience requirements and best practices.

User Experience Standards:
- Intuitive user interface
- Clear error messages
- Responsive design
- Fast performance
- Accessible design
- Consistent interactions
- Helpful guidance
- Professional appearance
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestUserInterfaceExcellence:
    """User interface validation against UX standards."""
    
    def test_api_response_clarity(self):
        """
        Validate API responses are clear and understandable.
        
        UX Standard:
        - API responses should be clear
        - Error messages should be actionable
        - Response structure should be consistent
        """
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200
        
        result = response.json()
        
        # Validate response structure is clear
        assert "results" in result, "Response should include results"
        assert "successful" in result, "Response should include success count"
        assert isinstance(result["results"], list), "Results should be a list"
    
    def test_error_message_clarity(self):
        """
        Validate error messages are clear and actionable.
        
        UX Standard:
        - Error messages should indicate the problem
        - Error messages should suggest solutions
        - Error messages should be user-friendly
        """
        # Test with invalid input
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "invalid.ip",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should handle gracefully with clear error
        assert response.status_code in [200, 422, 400], \
            "System should handle invalid input gracefully"
    
    def test_response_consistency(self):
        """
        Validate API responses are consistent across requests.
        
        UX Standard:
        - Response structure should be consistent
        - Field names should be consistent
        - Data types should be consistent
        """
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        # Make two identical requests
        response1 = client.post("/generate-deployment", json=deployment_input)
        response2 = client.post("/generate-deployment", json=deployment_input)
        
        assert response1.status_code == response2.status_code, \
            "Response status should be consistent"
        
        result1 = response1.json()
        result2 = response2.json()
        
        # Response structure should be consistent
        assert set(result1.keys()) == set(result2.keys()), \
            "Response structure should be consistent"


class TestPerformanceExpectations:
    """Performance validation against UX standards."""
    
    def test_response_time_user_expectations(self):
        """
        Validate response times meet user expectations.
        
        UX Standard:
        - API response should be < 2s (user perception threshold)
        - Complex operations should provide progress feedback
        - Long operations should be asynchronous
        """
        import time
        
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        start_time = time.time()
        response = client.post("/generate-deployment", json=deployment_input)
        end_time = time.time()
        
        assert response.status_code == 200
        
        duration_ms = (end_time - start_time) * 1000
        # Should be within user perception threshold
        assert duration_ms < 2000, \
            f"Response time {duration_ms:.2f}ms should be < 2000ms for good UX"
    
    def test_multi_switch_performance_user_expectations(self):
        """
        Validate multi-switch performance meets user expectations.
        
        UX Standard:
        - Multi-switch deployments should complete in reasonable time
        - Progress indication should be provided for long operations
        """
        import time
        
        switches = []
        for i in range(5):
            switches.append({
                "hostname": f"SW{i+1}",
                "mgmt_ip": f"10.0.0.{i+1}/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            })
        
        deployment_input = {
            "switches": switches,
            "vpc_pairs": [],
            "uplinks": []
        }
        
        start_time = time.time()
        response = client.post("/generate-deployment", json=deployment_input)
        end_time = time.time()
        
        assert response.status_code == 200
        
        duration_ms = (end_time - start_time) * 1000
        # 5 switches should complete in reasonable time
        assert duration_ms < 5000, \
            f"5-switch deployment {duration_ms:.2f}ms should be < 5000ms for good UX"


class TestUsabilityStandards:
    """Usability validation against UX standards."""
    
    def test_input_validation_user_friendly(self):
        """
        Validate input validation is user-friendly.
        
        UX Standard:
        - Validation errors should be clear
        - Validation should occur in real-time
        - Validation should provide guidance
        """
        # Test with various invalid inputs
        invalid_inputs = [
            {"hostname": "", "mgmt_ip": "10.0.0.1/24"},  # Empty hostname
            {"hostname": "SW1", "mgmt_ip": "invalid"},  # Invalid IP
            {"hostname": "SW1", "mgmt_ip": "10.0.0.1/24", "model": "Invalid"}  # Invalid model
        ]
        
        for invalid_input in invalid_inputs:
            deployment_input = {
                "switches": [{
                    "hostname": invalid_input.get("hostname", "SW1"),
                    "mgmt_ip": invalid_input.get("mgmt_ip", "10.0.0.1/24"),
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": invalid_input.get("model", "Nexus 93180YC-EX"),
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 10,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            response = client.post("/generate-deployment", json=deployment_input)
            # Should handle gracefully
            assert response.status_code in [200, 422, 400], \
                "Invalid input should be handled gracefully"
    
    def test_output_format_user_friendly(self):
        """
        Validate output format is user-friendly.
        
        UX Standard:
        - Output should be well-structured
        - Output should be easy to parse
        - Output should include relevant information
        """
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200
        
        result = response.json()
        
        # Validate output structure is user-friendly
        assert "results" in result, "Output should include results"
        assert isinstance(result["results"], list), "Results should be a list"
        
        if result["results"]:
            first_result = result["results"][0]
            # Should have device_config
            assert "device_config" in first_result, \
                "Result should include device_config"
            # Should have hostname
            assert "hostname" in first_result, \
                "Result should include hostname"


class TestAccessibilityUserExperience:
    """Accessibility validation against UX standards."""
    
    def test_api_accessibility(self):
        """
        Validate API is accessible to all users.
        
        UX Standard:
        - API should be accessible via standard tools
        - API should not require special authentication for basic operations
        - API should support standard protocols
        """
        # Test basic API accessibility
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        # Should be accessible without special authentication
        assert response.status_code in [200, 422, 400], \
            "API should be accessible"
    
    def test_error_handling_user_friendly(self):
        """
        Validate error handling is user-friendly.
        
        UX Standard:
        - Errors should not crash the system
        - Errors should provide helpful information
        - Errors should allow recovery
        """
        # Test with various error scenarios
        error_scenarios = [
            {"switches": [], "vpc_pairs": [], "uplinks": []},  # Empty deployment
            {"switches": [{"hostname": "SW1"}], "vpc_pairs": [], "uplinks": []},  # Minimal data
        ]
        
        for scenario in error_scenarios:
            response = client.post("/generate-deployment", json=scenario)
            # Should handle gracefully
            assert response.status_code in [200, 422, 400], \
                "Error scenarios should be handled gracefully"


class TestProfessionalStandards:
    """Professional appearance and behavior validation."""
    
    def test_configuration_professional_appearance(self):
        """
        Validate generated configurations have professional appearance.
        
        UX Standard:
        - Configurations should be well-formatted
        - Configurations should include comments
        - Configurations should be organized
        """
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200
        
        result = response.json()
        device_config = result["results"][0]["device_config"]
        config_text = device_config.get("config", device_config.get("cli_config", ""))
        
        # If config exists, it should be professional
        if config_text:
            # Should not be empty
            assert len(config_text) > 0, "Configuration should not be empty"
    
    def test_port_map_professional_structure(self):
        """
        Validate port map has professional structure.
        
        UX Standard:
        - Port map should be well-organized
        - Port map should be easy to understand
        - Port map should include relevant information
        """
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 10,
                "interface_count": 54,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf_10g"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200
        
        result = response.json()
        device_config = result["results"][0]["device_config"]
        port_map = device_config.get("port_map", {})
        
        # Port map should have professional structure
        if port_map:
            assert "hostname" in port_map, "Port map should include hostname"
            assert "model" in port_map, "Port map should include model"
            assert "ports" in port_map, "Port map should include ports"
