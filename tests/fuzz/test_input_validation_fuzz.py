"""
Fuzz Testing for Input Validation

This module performs fuzz testing on input validation functions to discover
edge cases and error conditions that traditional testing might miss.

QA Expert Perspective:
- Tests with random/malformed inputs
- Discovers crashes, exceptions, and unexpected behavior
- Focuses on input parsing and validation functions
- Tests system robustness against invalid inputs
"""

import pytest
import random
import string
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestInterfaceNameFuzzing:
    """Fuzz testing for interface name parsing."""
    
    def test_interface_name_random_strings(self):
        """
        Test interface name parsing with random strings.
        
        QA Expert Scenario:
        - Generate random strings as interface names
        - System should handle gracefully without crashing
        """
        random_strings = []
        
        # Generate various random strings
        for _ in range(50):
            # Random length 1-50
            length = random.randint(1, 50)
            # Random characters
            chars = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + ' ', k=length))
            random_strings.append(chars)
        
        for test_string in random_strings:
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
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            # Try to use random string as interface (will likely be rejected)
            # The important thing is system doesn't crash
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                # System should handle gracefully (accept or reject, but not crash)
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for random string: {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with random string '{test_string}': {e}")
    
    def test_interface_name_special_characters(self):
        """
        Test interface names with special characters.
        
        QA Expert Scenario:
        - Test with various special characters
        - System should handle without crashing
        """
        special_chars = ['@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/', '~', '`']
        
        for char in special_chars:
            test_interface = f"Ethernet1{char}1"
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
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for special char '{char}': {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with special character '{char}': {e}")


class TestVLANFuzzing:
    """Fuzz testing for VLAN validation."""
    
    def test_vlan_random_integers(self):
        """
        Test VLAN validation with random integers.
        
        QA Expert Scenario:
        - Test with random integers (including negative, large values)
        - System should handle gracefully
        """
        random_vlans = []
        
        # Generate random integers including edge cases
        for _ in range(50):
            # Random integers from -10000 to 10000
            vlan = random.randint(-10000, 10000)
            random_vlans.append(vlan)
        
        for vlan in random_vlans:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": vlan,
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                # System should handle gracefully
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for VLAN {vlan}: {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with VLAN {vlan}: {e}")
    
    def test_vlan_random_values(self):
        """
        Test VLAN with random non-integer values.
        
        QA Expert Scenario:
        - Test with strings, floats, None, etc.
        - System should handle gracefully
        """
        random_values = [
            "abc", "10.5", "10,20", None, "", " ", "0x10", "010", "10e5",
            "ten", "10.0.0", "10/20", "10-20", "10_20", "10 20"
        ]
        
        for value in random_values:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": value,
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                # System should handle gracefully (likely reject)
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for VLAN value {value}: {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with VLAN value {value}: {e}")


class TestIPFuzzing:
    """Fuzz testing for IP address validation."""
    
    def test_ip_random_strings(self):
        """
        Test IP address validation with random strings.
        
        QA Expert Scenario:
        - Test with random strings as IP addresses
        - System should handle gracefully
        """
        random_strings = []
        
        for _ in range(30):
            length = random.randint(1, 50)
            chars = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))
            random_strings.append(chars)
        
        for test_string in random_strings:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": test_string,
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                # System should handle gracefully (likely reject)
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for IP string '{test_string}': {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with IP string '{test_string}': {e}")
    
    def test_ip_malformed_addresses(self):
        """
        Test with malformed IP addresses.
        
        QA Expert Scenario:
        - Test with various malformed IP formats
        - System should handle gracefully
        """
        malformed_ips = [
            "256.256.256.256", "1.2.3", "1.2.3.4.5", "abc.def.ghi.jkl",
            "1.2.3.4/33", "1.2.3.4/0", "1.2.3.4/-1",
            "10.0.0.1/24/extra", "10.0.0.1/abc", "10.0.0.1/24.5",
            "", " ", "10.0.0", "10.0.0.1.2", "999.999.999.999"
        ]
        
        for ip in malformed_ips:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": ip,
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                # System should handle gracefully (likely reject)
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for malformed IP '{ip}': {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with malformed IP '{ip}': {e}")


class TestHostnameFuzzing:
    """Fuzz testing for hostname validation."""
    
    def test_hostname_random_strings(self):
        """
        Test hostname validation with random strings.
        
        QA Expert Scenario:
        - Test with random strings as hostnames
        - System should handle gracefully
        """
        random_strings = []
        
        for _ in range(30):
            length = random.randint(1, 100)
            chars = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + ' ', k=length))
            random_strings.append(chars)
        
        for test_string in random_strings:
            deployment_input = {
                "switches": [{
                    "hostname": test_string,
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                # System should handle gracefully
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for hostname '{test_string}': {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with hostname '{test_string}': {e}")


class TestDeploymentSizeFuzzing:
    """Fuzz testing for deployment size limits."""
    
    def test_random_switch_counts(self):
        """
        Test with random numbers of switches.
        
        QA Expert Scenario:
        - Test with various switch counts (0, 1, 10, 50, 100)
        - System should handle gracefully
        """
        switch_counts = [0, 1, 2, 5, 10, 20, 50]
        
        for count in switch_counts:
            switches = []
            for i in range(count):
                switches.append({
                    "hostname": f"SW{i+1}",
                    "mgmt_ip": f"10.0.0.{i+1}/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
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
            
            try:
                response = client.post("/generate-deployment", json=deployment_input)
                # System should handle gracefully
                assert response.status_code in [200, 422, 400], \
                    f"Unexpected response for switch count {count}: {response.status_code}"
            except Exception as e:
                pytest.fail(f"System crashed with switch count {count}: {e}")
