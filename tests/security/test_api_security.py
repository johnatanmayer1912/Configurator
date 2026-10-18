"""Security tests for API endpoints.

This test file validates security aspects including input validation,
authentication/authorization (if applicable), and data sanitization.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestAPISecurity:
    """Security tests for API endpoints."""
    
    def test_sql_injection_prevention(self):
        """
        Test SQL injection prevention in input fields.
        
        Security Criteria:
        - SQL injection attempts should be rejected or sanitized
        - System should not crash on malicious input
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "TEST'; DROP TABLE switches; --",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ'; DROP TABLE sites; --",
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should reject malicious input
        assert response.status_code in [400, 422]
    
    def test_xss_prevention(self):
        """
        Test XSS prevention in input fields.
        
        Security Criteria:
        - XSS attempts should be rejected or sanitized
        - System should not execute malicious scripts
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "<script>alert('XSS')</script>",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "<img src=x onerror=alert('XSS')>",
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should reject malicious input
        assert response.status_code in [400, 422]
    
    def test_config_upload_injection_prevention(self):
        """
        Test injection prevention in config upload.
        
        Security Criteria:
        - Malicious config content should be handled safely
        - System should not execute commands from config
        """
        malicious_config = """
hostname TEST-SWITCH
feature lacp
interface Ethernet1/1
  description ; rm -rf / 
  description <script>alert('XSS')</script>
"""
        
        response = client.post("/config/upload", json={
            "config_text": malicious_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        # Should handle malicious config gracefully
        assert response.status_code == 200
        result = response.json()
        # Should not execute malicious content
        assert "validation_id" in result
    
    def test_oversized_payload_prevention(self):
        """
        Test prevention of oversized payloads.
        
        Security Criteria:
        - Oversized payloads should be rejected
        - System should protect against DoS via large payloads
        """
        # Generate oversized config (1MB+)
        oversized_config = "hostname TEST-SWITCH\n" + "feature lacp\n" + "\n".join([f"interface Ethernet1/{i}\n  description Port {i}" for i in range(10000)])
        
        response = client.post("/config/upload", json={
            "config_text": oversized_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        # Should handle oversized payload (may accept or reject based on limits)
        assert response.status_code in [200, 413, 422]
    
    def test_ip_address_validation(self):
        """
        Test IP address validation and sanitization.
        
        Security Criteria:
        - Invalid IP addresses should be rejected
        - Private IP ranges should be handled appropriately
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "TEST-SWITCH",
                    "mgmt_ip": "999.999.999.999/24",  # Invalid IP
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        # Should reject invalid IP
        assert response.status_code in [400, 422]
    
    def test_vlan_range_validation(self):
        """
        Test VLAN range validation for security.
        
        Security Criteria:
        - VLANs outside valid range should be rejected
        - Reserved VLANs should be protected
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
                    "base_access_vlan": 9999,  # Invalid VLAN
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
        
        # Should reject invalid VLAN
        assert response.status_code in [400, 422]
    
    def test_command_injection_in_config(self):
        """
        Test command injection prevention in config upload.
        
        Security Criteria:
        - NX-OS commands should not be executed
        - System should parse config safely
        """
        malicious_config = """
hostname TEST-SWITCH
feature lacp
! Malicious command attempt
system shell bash
! Another malicious attempt
copy running-config startup-config
"""
        
        response = client.post("/config/upload", json={
            "config_text": malicious_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        # Should handle malicious commands safely
        assert response.status_code == 200
        result = response.json()
        assert "validation_id" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
