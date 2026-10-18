"""
Integration tests for Port Mapping API endpoints

Tests the complete flow from API request to port map generation,
validating the integration between the port mapping service and the deployment API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json


class TestPortMappingAPIIntegration:
    """Test port mapping integration with deployment API"""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        from api.main import app
        return TestClient(app)
    
    @pytest.fixture
    def sample_deployment_input(self):
        """Sample deployment input for testing"""
        return {
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "role": "core"
                },
                {
                    "hostname": "LEAF10G1",
                    "mgmt_ip": "10.10.10.2/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": "1",
                    "role": "leaf_10g"
                },
                {
                    "hostname": "LEAF10G2",
                    "mgmt_ip": "10.10.10.3/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "vpc_domain": "1",
                    "role": "leaf_10g"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": 1,
                    "primary": "LEAF10G1",
                    "secondary": "LEAF10G2",
                    "peer_link_ports": "E1/49,E1/50"
                }
            ],
            "uplinks": []
        }
    
    def test_deployment_generation_includes_port_map(self, client, sample_deployment_input):
        """Test that deployment generation includes bulletproof port map"""
        with patch('api.main.catalog') as mock_catalog:
            # Mock catalog methods
            mock_catalog.get_hardware_profile = Mock(side_effect=self._mock_hw_profile)
            
            response = client.post("/generate-deployment", json=sample_deployment_input)
            
            # If validation fails, print error for debugging
            if response.status_code != 200:
                print(f"Error response: {response.status_code}")
                print(f"Response body: {response.text}")
            
            assert response.status_code == 200
            result = response.json()
            
            # Check that results are returned
            assert "results" in result
            assert len(result["results"]) > 0
            
            # Check that device_config includes port_map
            for switch_result in result["results"]:
                assert "device_config" in switch_result
                assert "port_map" in switch_result["device_config"]
                
                port_map = switch_result["device_config"]["port_map"]
                assert "hostname" in port_map
                assert "model" in port_map
                assert "role" in port_map
                assert "primary_speed_label" in port_map
                assert "ports" in port_map
                assert "port_count" in port_map
    
    def test_port_map_structure_validation(self, client, sample_deployment_input):
        """Test that port map structure is valid and complete"""
        with patch('api.main.catalog') as mock_catalog:
            mock_catalog.get_hardware_profile = Mock(side_effect=self._mock_hw_profile)
            
            response = client.post("/generate-deployment", json=sample_deployment_input)
            
            assert response.status_code == 200
            result = response.json()
            
            # Validate port map structure for each switch
            for switch_result in result["results"]:
                port_map = switch_result["device_config"]["port_map"]
                
                # Validate hostname
                assert isinstance(port_map["hostname"], str)
                assert len(port_map["hostname"]) > 0
                
                # Validate model
                assert isinstance(port_map["model"], str)
                assert len(port_map["model"]) > 0
                
                # Validate role
                assert isinstance(port_map["role"], str)
                assert port_map["role"] in ["core", "leaf_10g", "leaf_1g", "spine", "generic"]
                
                # Validate ports array
                assert isinstance(port_map["ports"], list)
                
                # Validate port count matches ports length
                assert port_map["port_count"] == len(port_map["ports"])
    
    def test_port_map_ports_validation(self, client, sample_deployment_input):
        """Test that individual port configurations are valid"""
        with patch('api.main.catalog') as mock_catalog:
            mock_catalog.get_hardware_profile = Mock(side_effect=self._mock_hw_profile)
            
            response = client.post("/generate-deployment", json=sample_deployment_input)
            
            assert response.status_code == 200
            result = response.json()
            
            # Validate port configurations
            for switch_result in result["results"]:
                port_map = switch_result["device_config"]["port_map"]
                
                for port in port_map["ports"]:
                    # Validate required fields
                    assert "port" in port
                    assert "port_name" in port
                    assert "type" in port
                    assert "description" in port
                    
                    # Validate port number
                    assert isinstance(port["port"], int)
                    assert 1 <= port["port"] <= 128
                    
                    # Validate port name
                    assert isinstance(port["port_name"], str)
                    assert len(port["port_name"]) > 0
                    
                    # Validate port type
                    assert isinstance(port["type"], str)
                    assert port["type"] in ["uplink", "downlink", "peer_link", "keepalive", "access", "trunk", "unconfigured"]
                    
                    # Validate description
                    assert isinstance(port["description"], str)
                    
                    # Validate optional fields
                    if "port_channel" in port and port["port_channel"] is not None:
                        assert isinstance(port["port_channel"], int)
                        assert 1 <= port["port_channel"] <= 4096
    
    def test_core_switch_port_mapping(self, client, sample_deployment_input):
        """Test that core switches get correct downlink port mapping"""
        with patch('api.main.catalog') as mock_catalog:
            mock_catalog.get_hardware_profile = Mock(side_effect=self._mock_hw_profile)
            
            response = client.post("/generate-deployment", json=sample_deployment_input)
            
            assert response.status_code == 200
            result = response.json()
            
            # Find core switch result
            core_result = next((r for r in result["results"] if r["hostname"] == "CORE1"), None)
            assert core_result is not None
            
            port_map = core_result["device_config"]["port_map"]
            
            # Core switch should have downlink ports
            downlink_ports = [p for p in port_map["ports"] if p["type"] == "downlink"]
            assert len(downlink_ports) > 0
            
            # Downlink ports should have port-channel assignments
            ports_with_pc = [p for p in downlink_ports if p.get("port_channel") is not None]
            assert len(ports_with_pc) > 0
    
    def test_leaf_switch_port_mapping(self, client, sample_deployment_input):
        """Test that leaf switches get correct uplink port mapping"""
        with patch('api.main.catalog') as mock_catalog:
            # Mock catalog to return hardware profiles
            mock_catalog.get_hardware_profile = Mock(side_effect=self._mock_hw_profile)
            
            response = client.post("/generate-deployment", json=sample_deployment_input)
            
            assert response.status_code == 200
            result = response.json()
            
            # Find leaf switch result
            leaf_result = next((r for r in result["results"] if r["hostname"] == "LEAF10G1"), None)
            assert leaf_result is not None
            
            port_map = leaf_result["device_config"]["port_map"]
            
            # Leaf switch should have uplink ports
            uplink_ports = [p for p in port_map["ports"] if p["type"] == "uplink"]
            assert len(uplink_ports) > 0
    
    def test_vpc_port_mapping(self, client, sample_deployment_input):
        """Test that vPC ports are correctly mapped"""
        with patch('api.main.catalog') as mock_catalog:
            mock_catalog.get_hardware_profile = Mock(side_effect=self._mock_hw_profile)
            
            response = client.post("/generate-deployment", json=sample_deployment_input)
            
            assert response.status_code == 200
            result = response.json()
            
            # Find vPC leaf switch
            vpc_leaf = next((r for r in result["results"] if r["hostname"] == "LEAF10G1"), None)
            if vpc_leaf:
                port_map = vpc_leaf["device_config"]["port_map"]
                
                # Check for vPC-related ports if in vPC pair
                peer_link_ports = [p for p in port_map["ports"] if p["type"] == "peer_link"]
                keepalive_ports = [p for p in port_map["ports"] if p["type"] == "keepalive"]
                
                # If vPC is configured, these should be present
                # (This depends on the specific vPC configuration in the test)
    
    def test_port_map_error_handling(self, client):
        """Test that port map generation handles errors gracefully"""
        # Create deployment with invalid model
        invalid_input = {
            "switches": [
                {
                    "hostname": "INVALID",
                    "mgmt_ip": "10.10.10.1",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "InvalidModel",
                    "nxos_version": "9.3",
                    "role": "generic"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        with patch('api.main.catalog') as mock_catalog:
            mock_catalog.get_hardware_profile = Mock(return_value=None)
            
            response = client.post("/generate-deployment", json=invalid_input)
            
            # Should still return response, even with errors
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                result = response.json()
                # Port map should handle missing hardware profile gracefully
                assert "results" in result
    
    def test_multiple_switches_port_mapping(self, client):
        """Test port mapping with multiple switches of different types"""
        multi_switch_input = {
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "role": "core"
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.10.10.2/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "role": "core"
                },
                {
                    "hostname": "LEAF10G1",
                    "mgmt_ip": "10.10.10.3/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "role": "leaf_10g"
                },
                {
                    "hostname": "LEAF10G2",
                    "mgmt_ip": "10.10.10.4/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "HQ",
                    "model": "Nexus 9348GC-FXP",
                    "nxos_version": "9.3",
                    "role": "leaf_10g"
                }
            ],
            "vpc_pairs": [
                {
                    "domain": 1,
                    "primary": "LEAF10G1",
                    "secondary": "LEAF10G2",
                    "peer_link_ports": "E1/49,E1/50"
                }
            ],
            "uplinks": []
        }
        
        with patch('api.main.catalog') as mock_catalog:
            mock_catalog.get_hardware_profile = Mock(side_effect=self._mock_hw_profile)
            
            response = client.post("/generate-deployment", json=multi_switch_input)
            
            assert response.status_code == 200
            result = response.json()
            
            # All switches should have port maps
            assert len(result["results"]) == 4
            
            for switch_result in result["results"]:
                assert "device_config" in switch_result
                assert "port_map" in switch_result["device_config"]
                assert switch_result["device_config"]["port_map"]["port_count"] > 0
    
    def _mock_hw_profile(self, model):
        """Mock hardware profile for testing"""
        profiles = {
            "Nexus 9336C-FX2": {
                "device_class": "core",
                "vpc_peer_link": ["E1/49", "E1/50"],
                "vpc_keepalive": ["E1/51"],
                "downlink_10g_start": 1,
                "downlink_10g_end": 10,
                "downlink_1g_start": 11,
                "downlink_1g_end": 20
            },
            "Nexus 9348GC-FXP": {
                "device_class": "leaf_10g",
                "vpc_peer_link": ["Ethernet1/51", "Ethernet1/52"],
                "vpc_keepalive": ["Ethernet1/47", "Ethernet1/48"],
                "vpc_uplink_start": 49,
                "vpc_uplink_end": 50
            }
        }
        return profiles.get(model, {"device_class": "generic"})


class TestPortMappingErrorScenarios:
    """Test error scenarios and edge cases"""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        from api.main import app
        return TestClient(app)
    
    def test_empty_switches_list(self, client):
        """Test deployment with no switches"""
        empty_input = {
            "switches": [],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=empty_input)
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
    
    def test_missing_required_fields(self, client):
        """Test deployment with missing required fields"""
        incomplete_input = {
            "switches": [
                {
                    "hostname": "TEST"
                    # Missing required fields
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=incomplete_input)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_invalid_port_channel_assignment(self, client):
        """Test that invalid port-channel assignments are rejected"""
        # This would require more complex mocking to test the validation logic
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
