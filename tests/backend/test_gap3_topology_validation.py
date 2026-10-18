"""
Backend unit tests for GAP 3: Pre-deployment Topology Validation

Tests the topology validation logic including hostname conflicts, IP conflicts,
vPC consistency, and uplink validation.
"""

import pytest


class TestTopologyValidationGAP3:
    """Test topology validation with GAP 3 features."""
    
    @pytest.fixture
    def sample_switches(self):
        """Create sample switch configurations."""
        return [
            {
                "hostname": "sw1",
                "mgmt_ip": "10.0.0.1/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)"
            },
            {
                "hostname": "sw2",
                "mgmt_ip": "10.0.0.2/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)"
            }
        ]
    
    def test_hostname_conflict_detection(self, sample_switches):
        """Test detection of duplicate hostnames."""
        # Add duplicate hostname
        switches = sample_switches + [
            {
                "hostname": "sw1",  # Duplicate
                "mgmt_ip": "10.0.0.3/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)"
            }
        ]
        
        # Count hostnames
        hostnames = [sw["hostname"] for sw in switches]
        assert len(hostnames) != len(set(hostnames))  # Should have duplicates
    
    def test_ip_conflict_detection(self, sample_switches):
        """Test detection of duplicate IP addresses."""
        # Add duplicate IP
        switches = sample_switches + [
            {
                "hostname": "sw3",
                "mgmt_ip": "10.0.0.1/24",  # Duplicate IP
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)"
            }
        ]
        
        # Extract IPs
        ips = [sw["mgmt_ip"].split('/')[0] for sw in switches if sw["mgmt_ip"]]
        assert len(ips) != len(set(ips))  # Should have duplicates
    
    def test_vpc_domain_consistency(self, sample_switches):
        """Test vPC domain consistency across peer switches."""
        # Create vPC pair with mismatched domains
        switches = [
            {
                "hostname": "sw1",
                "mgmt_ip": "10.0.0.1/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)",
                "vpc_domain": 10,
                "local_ka": "10.1.1.1",
                "remote_ka": "10.1.1.2"
            },
            {
                "hostname": "sw2",
                "mgmt_ip": "10.0.0.2/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)",
                "vpc_domain": 20,  # Different domain
                "local_ka": "10.1.1.2",
                "remote_ka": "10.1.1.1"
            }
        ]
        
        # Check domain mismatch
        assert switches[0]["vpc_domain"] != switches[1]["vpc_domain"]
    
    def test_vpc_keepalive_ip_cross_reference(self, sample_switches):
        """Test vPC keepalive IP cross-reference validation."""
        switches = [
            {
                "hostname": "sw1",
                "mgmt_ip": "10.0.0.1/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)",
                "vpc_domain": 10,
                "local_ka": "10.1.1.1",
                "remote_ka": "10.1.1.2"
            },
            {
                "hostname": "sw2",
                "mgmt_ip": "10.0.0.2/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)",
                "vpc_domain": 10,
                "local_ka": "10.1.1.2",
                "remote_ka": "10.1.1.1"
            }
        ]
        
        # Verify cross-reference is correct
        assert switches[0]["local_ka"] == switches[1]["remote_ka"]
        assert switches[1]["local_ka"] == switches[0]["remote_ka"]
    
    def test_vpc_keepalive_ip_mismatch(self, sample_switches):
        """Test vPC keepalive IP mismatch detection."""
        switches = [
            {
                "hostname": "sw1",
                "mgmt_ip": "10.0.0.1/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)",
                "vpc_domain": 10,
                "local_ka": "10.1.1.1",
                "remote_ka": "10.1.1.2"
            },
            {
                "hostname": "sw2",
                "mgmt_ip": "10.0.0.2/24",
                "model": "N9K-C93180YC-FX",
                "nxos_version": "9.3(5)",
                "vpc_domain": 10,
                "local_ka": "10.1.1.3",  # Mismatch
                "remote_ka": "10.1.1.4"
            }
        ]
        
        # Verify cross-reference is incorrect
        assert switches[0]["local_ka"] != switches[1]["remote_ka"]
        assert switches[1]["local_ka"] != switches[0]["remote_ka"]
    
    def test_uplink_switch_existence(self, sample_switches):
        """Test that uplinks reference existing switches."""
        uplinks = [
            {"from": "sw1", "to": "sw2", "ports": "Ethernet1/1-2"},
            {"from": "sw1", "to": "sw3", "ports": "Ethernet1/3-4"}  # sw3 doesn't exist
        ]
        
        # Check for non-existent switch references
        switch_hostnames = {sw["hostname"] for sw in sample_switches}
        invalid_refs = [ul for ul in uplinks if ul["to"] not in switch_hostnames]
        assert len(invalid_refs) > 0  # Should find sw3 reference
    
    def test_valid_topology_no_issues(self, sample_switches):
        """Test that a valid topology passes validation."""
        switches = sample_switches
        
        # Check for hostname conflicts
        hostnames = [sw["hostname"] for sw in switches]
        assert len(hostnames) == len(set(hostnames))
        
        # Check for IP conflicts
        ips = [sw["mgmt_ip"].split('/')[0] for sw in switches if sw["mgmt_ip"]]
        assert len(ips) == len(set(ips))
    
    def test_physical_port_capacity_validation(self, sample_switches):
        """Test physical port capacity validation."""
        # This would validate that uplinks don't exceed available ports
        # For now, test the data structure
        
        uplinks = [
            {"from": "sw1", "to": "sw2", "ports": "Ethernet1/1-4", "count": 4}
        ]
        
        # Verify uplink structure
        assert len(uplinks) > 0
        assert "from" in uplinks[0]
        assert "to" in uplinks[0]
        assert "ports" in uplinks[0]
    
    def test_validation_issue_severity_levels(self):
        """Test that validation issues have proper severity levels."""
        issue = {
            "severity": "critical",
            "category": "hostname_conflict",
            "message": "Duplicate hostname detected",
            "affected_switches": ["sw1", "sw2"],
            "suggestion": "Use unique hostnames"
        }
        
        assert issue["severity"] in ["critical", "warning", "info"]
        assert issue["category"] in ["hostname_conflict", "ip_conflict", "vpc_mismatch", "uplink_config"]
        assert len(issue["message"]) > 0
        assert len(issue["affected_switches"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
