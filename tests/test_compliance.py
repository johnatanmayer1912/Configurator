"""Compliance Engine Unit Tests

Tests the compliance auditing logic for institutional standards including:
- VLAN naming conventions
- Reserved VLAN ranges
- Management IP format validation
- Hostname conventions
"""

import pytest
from models.device_model import Device, VPCConfig
from models.vlan_model import VLAN
from core.compliance import ComplianceEngine


class TestComplianceEngine:
    """Test compliance engine auditing functionality."""
    
    @pytest.fixture
    def compliance_engine(self):
        """Create compliance engine instance."""
        return ComplianceEngine()
    
    @pytest.fixture
    def sample_device(self):
        """Create a sample device for testing."""
        device = Device(
            hostname="TEST-SW-01",
            mgmt_ip="10.10.10.10/24",
            mgmt_gw="10.10.10.1",
            model="Nexus 93180YC-EX",
            nxos_version="9.3"
        )
        device.vlans = [
            VLAN(id=10, name="DATA_VLAN"),
            VLAN(id=20, name="VOICE_VLAN"),
        ]
        return device
    
    def test_vlan_naming_convention_valid(self, compliance_engine, sample_device):
        """Test that valid VLAN names pass compliance check."""
        findings = compliance_engine.audit(sample_device)
        
        # Should not have warnings about valid VLAN names
        vlan_warnings = [f for f in findings if "VLAN" in f.get("message", "") and "name" in f.get("message", "")]
        assert len(vlan_warnings) == 0, f"Valid VLAN names should not generate warnings: {vlan_warnings}"
    
    def test_vlan_naming_convention_invalid_spaces(self, compliance_engine, sample_device):
        """Test that VLAN names with spaces generate warnings."""
        sample_device.vlans.append(VLAN(id=30, name="Invalid VLAN Name"))
        
        findings = compliance_engine.audit(sample_device)
        
        # Should have warning about spaces
        space_warnings = [f for f in findings if "spaces" in f.get("message", "").lower()]
        assert len(space_warnings) > 0, "VLAN names with spaces should generate warnings"
    
    def test_vlan_naming_convention_invalid_lowercase(self, compliance_engine, sample_device):
        """Test that lowercase VLAN names generate warnings."""
        sample_device.vlans.append(VLAN(id=40, name="lowercase_vlan"))
        
        findings = compliance_engine.audit(sample_device)
        
        # Should have warning about uppercase
        case_warnings = [f for f in findings if "uppercase" in f.get("message", "").lower()]
        assert len(case_warnings) > 0, "Lowercase VLAN names should generate warnings"
    
    def test_reserved_vlan_ranges_error(self, compliance_engine, sample_device):
        """Test that reserved VLANs generate errors."""
        # Add VLAN in reserved range 3968-4047
        sample_device.vlans.append(VLAN(id=3970, name="RESERVED_VLAN"))
        
        findings = compliance_engine.audit(sample_device)
        
        # Should have error about reserved VLAN
        reserved_errors = [f for f in findings if f.get("level") == "error" and "reserved" in f.get("message", "").lower()]
        assert len(reserved_errors) > 0, "Reserved VLANs should generate errors"
    
    def test_reserved_vlan_4094_error(self, compliance_engine, sample_device):
        """Test that VLAN 4094 generates error."""
        sample_device.vlans.append(VLAN(id=4094, name="RESERVED_4094"))
        
        findings = compliance_engine.audit(sample_device)
        
        # Should have error about reserved VLAN
        reserved_errors = [f for f in findings if f.get("level") == "error" and "4094" in f.get("message", "")]
        assert len(reserved_errors) > 0, "VLAN 4094 should generate error"
    
    def test_management_ip_format_valid(self, compliance_engine, sample_device):
        """Test that valid management IP with CIDR passes."""
        findings = compliance_engine.audit(sample_device)
        
        # Should not have IP format errors
        ip_errors = [f for f in findings if "Management IP" in f.get("message", "") and f.get("level") == "error"]
        assert len(ip_errors) == 0, "Valid management IP should not generate errors"
    
    def test_management_ip_format_invalid_no_cidr(self, compliance_engine, sample_device):
        """Test that management IP without CIDR generates error."""
        sample_device.mgmt_ip = "10.10.10.10"  # Missing CIDR
        
        findings = compliance_engine.audit(sample_device)
        
        # Should have error about CIDR notation
        cidr_errors = [f for f in findings if "CIDR" in f.get("message", "")]
        assert len(cidr_errors) > 0, "Management IP without CIDR should generate error"
    
    def test_hostname_convention_valid(self, compliance_engine, sample_device):
        """Test that valid hostname passes compliance check."""
        findings = compliance_engine.audit(sample_device)
        
        # Should not have hostname errors
        hostname_errors = [f for f in findings if "Hostname" in f.get("message", "") and f.get("level") == "error"]
        assert len(hostname_errors) == 0, "Valid hostname should not generate errors"
    
    def test_hostname_convention_invalid_special_chars(self, compliance_engine, sample_device):
        """Test that hostname with special characters generates error."""
        sample_device.hostname = "TEST_SW_01$"  # Invalid character
        
        findings = compliance_engine.audit(sample_device)
        
        # Should have error about invalid characters
        hostname_errors = [f for f in findings if "Hostname" in f.get("message", "") and f.get("level") == "error"]
        assert len(hostname_errors) > 0, "Hostname with special characters should generate error"
    
    def test_hostname_convention_invalid_underscore(self, compliance_engine, sample_device):
        """Test that hostname with underscore generates error."""
        sample_device.hostname = "TEST_SW_01"  # Underscore not allowed
        
        findings = compliance_engine.audit(sample_device)
        
        # Should have error about invalid characters
        hostname_errors = [f for f in findings if "Hostname" in f.get("message", "") and f.get("level") == "error"]
        assert len(hostname_errors) > 0, "Hostname with underscore should generate error"
    
    def test_compliance_audit_returns_list(self, compliance_engine, sample_device):
        """Test that audit returns a list of findings."""
        findings = compliance_engine.audit(sample_device)
        
        assert isinstance(findings, list), "Audit should return a list"
        assert all(isinstance(f, dict) for f in findings), "All findings should be dictionaries"
    
    def test_compliance_finding_structure(self, compliance_engine, sample_device):
        """Test that findings have required structure."""
        sample_device.mgmt_ip = "10.10.10.10"  # Trigger error
        findings = compliance_engine.audit(sample_device)
        
        for finding in findings:
            assert "level" in finding, "Finding must have 'level' field"
            assert finding["level"] in ["warning", "error"], "Level must be 'warning' or 'error'"
            assert "message" in finding, "Finding must have 'message' field"
            assert isinstance(finding["message"], str), "Message must be a string"
    
    def test_compliance_with_vpc_device(self, compliance_engine):
        """Test compliance audit on vPC device."""
        device = Device(
            hostname="CORE1-VPC",
            mgmt_ip="10.10.10.10/24",
            mgmt_gw="10.10.10.1",
            model="Nexus 9336C-FX2",
            nxos_version="9.3"
        )
        device.vpc = VPCConfig(
            domain_id=100,
            role="primary",
            keepalive_vrf="management",
            peer_link_id=1,
            local_keepalive_ip="10.255.255.1",
            remote_keepalive_ip="10.255.255.2"
        )
        device.vlans = [VLAN(id=10, name="FABRIC_VLAN")]
        
        findings = compliance_engine.audit(device)
        
        # Should not crash with vPC device
        assert isinstance(findings, list)
    
    def test_compliance_empty_device(self, compliance_engine):
        """Test compliance audit on minimal device."""
        device = Device(
            hostname="TEST",
            mgmt_ip="10.10.10.10/24",
            mgmt_gw="10.10.10.1",
            model="Generic",
            nxos_version="9.3"
        )
        
        findings = compliance_engine.audit(device)
        
        # Should not crash with minimal device
        assert isinstance(findings, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
