"""
Port Mapping Validation Test

This test validates that port mapping works correctly for all hardware models
and deployment scenarios. It ensures that:
1. Hardware profiles have correct vPC port assignments
2. Port parsing logic works for all port name formats
3. Port mapping is consistent across different scenarios
4. All models have required vPC port fields

This is a mandatory pre-build test to ensure port mapping functionality.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, List, Any


class TestPortMappingValidation:
    """Comprehensive port mapping validation for all hardware models."""
    
    @pytest.fixture
    def hardware_profiles(self) -> List[Dict[str, Any]]:
        """Load hardware profiles from YAML file."""
        hw_path = Path(__file__).resolve().parents[1] / "hardware_profiles.yaml"
        with open(hw_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("profiles", [])
    
    @pytest.fixture
    def expected_vpc_ports(self) -> Dict[str, Dict[str, List[str]]]:
        """Expected vPC port assignments for each model."""
        return {
            "Nexus 93180YC-EX": {
                "peer_link": ["Ethernet1/51", "Ethernet1/52"],
                "keepalive": ["Ethernet1/49", "Ethernet1/50"]
            },
            "Nexus 9336C-FX2": {
                "peer_link": ["Ethernet1/35", "Ethernet1/36"],
                "keepalive": ["Ethernet1/33", "Ethernet1/34"]
            },
            "Nexus 9348GC-FXP": {
                "peer_link": ["Ethernet1/51", "Ethernet1/52"],
                "keepalive": ["Ethernet1/47", "Ethernet1/48"]
            }
        }
    
    def test_all_profiles_have_display_name(self, hardware_profiles):
        """Ensure all hardware profiles have display_name field."""
        for profile in hardware_profiles:
            assert "display_name" in profile, f"Profile missing display_name: {profile.get('name')}"
            assert profile["display_name"], f"Empty display_name for: {profile.get('name')}"
    
    def test_all_profiles_have_vpc_fields(self, hardware_profiles):
        """Ensure all hardware profiles have vPC port fields (except Generic)."""
        for profile in hardware_profiles:
            display_name = profile.get("display_name")
            # Skip Generic profile as it's a fallback
            if display_name == "Generic":
                continue
            
            assert "vpc_peer_link" in profile, f"{display_name} missing vpc_peer_link"
            assert "vpc_keepalive" in profile, f"{display_name} missing vpc_keepalive"
            assert isinstance(profile["vpc_peer_link"], list), f"{display_name} vpc_peer_link not a list"
            assert isinstance(profile["vpc_keepalive"], list), f"{display_name} vpc_keepalive not a list"
            assert len(profile["vpc_peer_link"]) >= 2, f"{display_name} needs at least 2 peer-link ports"
            assert len(profile["vpc_keepalive"]) >= 2, f"{display_name} needs at least 2 keepalive ports"
    
    def test_vpc_ports_match_expected(self, hardware_profiles, expected_vpc_ports):
        """Validate vPC port assignments match expected values."""
        for profile in hardware_profiles:
            display_name = profile.get("display_name")
            if display_name in expected_vpc_ports:
                expected = expected_vpc_ports[display_name]
                
                # Validate peer-link ports
                actual_peer_link = profile["vpc_peer_link"]
                assert actual_peer_link == expected["peer_link"], \
                    f"{display_name} peer-link mismatch: expected {expected['peer_link']}, got {actual_peer_link}"
                
                # Validate keepalive ports
                actual_keepalive = profile["vpc_keepalive"]
                assert actual_keepalive == expected["keepalive"], \
                    f"{display_name} keepalive mismatch: expected {expected['keepalive']}, got {actual_keepalive}"
    
    def test_port_name_format_consistency(self, hardware_profiles):
        """Ensure all port names follow consistent format (Ethernet1/N)."""
        for profile in hardware_profiles:
            display_name = profile.get("display_name")
            
            # Check peer-link ports
            for port in profile["vpc_peer_link"]:
                assert port.startswith("Ethernet1/"), \
                    f"{display_name} peer-link port {port} doesn't start with 'Ethernet1/'"
                port_num = port.split("/")[-1]
                assert port_num.isdigit(), \
                    f"{display_name} peer-link port {port} has invalid port number"
            
            # Check keepalive ports
            for port in profile["vpc_keepalive"]:
                assert port.startswith("Ethernet1/"), \
                    f"{display_name} keepalive port {port} doesn't start with 'Ethernet1/'"
                port_num = port.split("/")[-1]
                assert port_num.isdigit(), \
                    f"{display_name} keepalive port {port} has invalid port number"
    
    def test_port_uniqueness_within_profile(self, hardware_profiles):
        """Ensure peer-link and keepalive ports don't overlap within a profile."""
        for profile in hardware_profiles:
            display_name = profile.get("display_name")
            peer_link = set(profile["vpc_peer_link"])
            keepalive = set(profile["vpc_keepalive"])
            
            overlap = peer_link & keepalive
            assert not overlap, \
                f"{display_name} has overlapping peer-link and keepalive ports: {overlap}"
    
    def test_port_ranges_are_valid(self, hardware_profiles):
        """Ensure port numbers are within valid ranges for the model."""
        for profile in hardware_profiles:
            display_name = profile.get("display_name")
            total_ports = profile.get("total_ports", 54)
            
            # Check peer-link ports
            for port in profile["vpc_peer_link"]:
                port_num = int(port.split("/")[-1])
                assert 1 <= port_num <= total_ports, \
                    f"{display_name} peer-link port {port} (port {port_num}) exceeds total ports {total_ports}"
            
            # Check keepalive ports
            for port in profile["vpc_keepalive"]:
                port_num = int(port.split("/")[-1])
                assert 1 <= port_num <= total_ports, \
                    f"{display_name} keepalive port {port} (port {port_num}) exceeds total ports {total_ports}"
    
    def test_backend_interface_manager_consistency(self, hardware_profiles):
        """Ensure backend interface_manager.py returns consistent ports."""
        from modules.interface_manager import get_vpc_ports
        from models.nexus_models import NexusModel
        
        # Map display names to NexusModel enum values
        model_mapping = {
            "Nexus 93180YC-EX": NexusModel.N93180YC_EX,
            "Nexus 9336C-FX2": NexusModel.N9336C_FX2,
            "Nexus 9348GC-FXP": NexusModel.N9348GC_FXP
        }
        
        for profile in hardware_profiles:
            display_name = profile.get("display_name")
            if display_name in model_mapping:
                model = model_mapping[display_name]
                backend_ports = get_vpc_ports(model)
                
                assert backend_ports is not None, \
                    f"get_vpc_ports returned None for {display_name}"
                
                # Validate peer-link ports match
                backend_peer = backend_ports.get("peer_link", [])
                yaml_peer = profile["vpc_peer_link"]
                assert set(backend_peer) == set(yaml_peer), \
                    f"{display_name} backend peer-link mismatch: backend {backend_peer}, yaml {yaml_peer}"
                
                # Validate keepalive ports match
                backend_ka = backend_ports.get("keepalive", [])
                yaml_ka = profile["vpc_keepalive"]
                assert set(backend_ka) == set(yaml_ka), \
                    f"{display_name} backend keepalive mismatch: backend {backend_ka}, yaml {yaml_ka}"
    
    def test_port_parsing_logic(self):
        """Test port parsing logic for different formats."""
        from modules.interface_manager import get_vpc_ports
        from models.nexus_models import NexusModel
        
        # Test each model
        test_cases = [
            (NexusModel.N93180YC_EX, ["Ethernet1/51", "Ethernet1/52"], ["Ethernet1/49", "Ethernet1/50"]),
            (NexusModel.N9336C_FX2, ["Ethernet1/35", "Ethernet1/36"], ["Ethernet1/33", "Ethernet1/34"]),
            (NexusModel.N9348GC_FXP, ["Ethernet1/51", "Ethernet1/52"], ["Ethernet1/47", "Ethernet1/48"])
        ]
        
        for model, expected_peer, expected_ka in test_cases:
            ports = get_vpc_ports(model)
            assert ports is not None, f"get_vpc_ports returned None for {model}"
            assert ports["peer_link"] == expected_peer, \
                f"Peer-link mismatch for {model}: expected {expected_peer}, got {ports['peer_link']}"
            assert ports["keepalive"] == expected_ka, \
                f"Keepalive mismatch for {model}: expected {expected_ka}, got {ports['keepalive']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
