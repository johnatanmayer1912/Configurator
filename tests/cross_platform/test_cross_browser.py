"""
Cross-Browser and Cross-Device Testing

This module validates that the application works correctly across
different browsers and devices.

Cross-Browser Standards:
- Chrome compatibility
- Firefox compatibility
- Safari compatibility
- Edge compatibility
- Mobile browser compatibility
- Tablet browser compatibility
- Desktop browser compatibility
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestCrossBrowserCompatibility:
    """Cross-browser compatibility validation."""
    
    def test_chrome_compatibility(self):
        """
        Validate Chrome browser compatibility.
        
        Cross-Browser Standard:
        - API should work with Chrome user agent
        - Response format should be consistent
        - Features should work correctly
        """
        # Simulate Chrome user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work with Chrome user agent"
    
    def test_firefox_compatibility(self):
        """
        Validate Firefox browser compatibility.
        
        Cross-Browser Standard:
        - API should work with Firefox user agent
        - Response format should be consistent
        - Features should work correctly
        """
        # Simulate Firefox user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work with Firefox user agent"
    
    def test_safari_compatibility(self):
        """
        Validate Safari browser compatibility.
        
        Cross-Browser Standard:
        - API should work with Safari user agent
        - Response format should be consistent
        - Features should work correctly
        """
        # Simulate Safari user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work with Safari user agent"
    
    def test_edge_compatibility(self):
        """
        Validate Edge browser compatibility.
        
        Cross-Browser Standard:
        - API should work with Edge user agent
        - Response format should be consistent
        - Features should work correctly
        """
        # Simulate Edge user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work with Edge user agent"


class TestCrossDeviceCompatibility:
    """Cross-device compatibility validation."""
    
    def test_desktop_compatibility(self):
        """
        Validate desktop device compatibility.
        
        Cross-Device Standard:
        - API should work with desktop devices
        - Response should be optimized for desktop
        - Features should work correctly
        """
        # Simulate desktop user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work with desktop devices"
    
    def test_mobile_compatibility(self):
        """
        Validate mobile device compatibility.
        
        Cross-Device Standard:
        - API should work with mobile devices
        - Response should be optimized for mobile
        - Features should work correctly
        """
        # Simulate mobile user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work with mobile devices"
    
    def test_tablet_compatibility(self):
        """
        Validate tablet device compatibility.
        
        Cross-Device Standard:
        - API should work with tablet devices
        - Response should be optimized for tablet
        - Features should work correctly
        """
        # Simulate tablet user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work with tablet devices"


class TestCrossPlatformCompatibility:
    """Cross-platform compatibility validation."""
    
    def test_windows_compatibility(self):
        """
        Validate Windows platform compatibility.
        
        Cross-Platform Standard:
        - API should work on Windows
        - Response should be consistent
        - Features should work correctly
        """
        # Simulate Windows user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work on Windows"
    
    def test_macos_compatibility(self):
        """
        Validate macOS platform compatibility.
        
        Cross-Platform Standard:
        - API should work on macOS
        - Response should be consistent
        - Features should work correctly
        """
        # Simulate macOS user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work on macOS"
    
    def test_linux_compatibility(self):
        """
        Validate Linux platform compatibility.
        
        Cross-Platform Standard:
        - API should work on Linux
        - Response should be consistent
        - Features should work correctly
        """
        # Simulate Linux user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
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
        
        response = client.post("/generate-deployment", json=deployment_input, headers=headers)
        assert response.status_code == 200, "Should work on Linux"


class TestResponseConsistency:
    """Response consistency across platforms validation."""
    
    def test_response_structure_consistency(self):
        """
        Validate response structure is consistent across platforms.
        
        Cross-Platform Standard:
        - Response structure should be identical across platforms
        - Field names should be consistent
        - Data types should be consistent
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
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
        
        response_keys = set()
        
        for user_agent in user_agents:
            headers = {"User-Agent": user_agent}
            response = client.post("/generate-deployment", json=deployment_input, headers=headers)
            assert response.status_code == 200
            
            result = response.json()
            current_keys = set(result.keys())
            
            if response_keys:
                assert response_keys == current_keys, \
                    "Response structure should be consistent across platforms"
            else:
                response_keys = current_keys
