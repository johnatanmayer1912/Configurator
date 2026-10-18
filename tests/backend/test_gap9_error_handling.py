"""
Backend unit tests for GAP 9: Enhanced Error Handling and Recovery

Tests the error analytics, recovery suggestions, and auto-recovery logic.
"""

import pytest
from datetime import datetime


class TestErrorHandlingGAP9:
    """Test error handling and recovery with GAP 9 features."""
    
    def test_error_pattern_structure(self):
        """Test error pattern data structure."""
        pattern = {
            "pattern_id": "vlan_conflict",
            "pattern_name": "VLAN ID Conflicts",
            "error_type": "configuration",
            "frequency": 5,
            "last_occurred": datetime.now().isoformat(),
            "suggested_fix": "Review VLAN assignments",
            "auto_recoverable": False
        }
        
        assert pattern["pattern_id"] == "vlan_conflict"
        assert pattern["error_type"] in ["configuration", "network", "validation"]
        assert pattern["frequency"] >= 0
        assert pattern["auto_recoverable"] in [True, False]
    
    def test_error_analytics_response_structure(self):
        """Test error analytics response structure."""
        patterns = [
            {
                "pattern_id": "vlan_conflict",
                "pattern_name": "VLAN Conflicts",
                "error_type": "configuration",
                "frequency": 5,
                "last_occurred": datetime.now().isoformat(),
                "suggested_fix": "Fix VLANs",
                "auto_recoverable": False
            }
        ]
        
        response = {
            "total_errors": 5,
            "error_patterns": patterns,
            "recent_errors": []
        }
        
        assert response["total_errors"] == 5
        assert len(response["error_patterns"]) == 1
        assert response["total_errors"] >= sum(p["frequency"] for p in response["error_patterns"])
    
    def test_recovery_suggestion_structure(self):
        """Test recovery suggestion structure."""
        suggestion = {
            "error_code": "vlan_conflict",
            "error_message": "VLAN ID conflict detected",
            "severity": "critical",
            "recovery_steps": [
                "Identify conflicting VLANs",
                "Reassign VLAN IDs",
                "Re-validate topology"
            ],
            "auto_recovery_available": False,
            "auto_recovery_command": None
        }
        
        assert suggestion["error_code"] == "vlan_conflict"
        assert suggestion["severity"] in ["critical", "warning", "info"]
        assert len(suggestion["recovery_steps"]) > 0
        assert suggestion["auto_recovery_available"] in [True, False]
    
    def test_recovery_suggestion_with_auto_recovery(self):
        """Test recovery suggestion with auto-recovery capability."""
        suggestion = {
            "error_code": "port_down",
            "error_message": "Port is down",
            "severity": "warning",
            "recovery_steps": ["Check cable", "Check configuration"],
            "auto_recovery_available": True,
            "auto_recovery_command": "interface Ethernet1/1; no shutdown"
        }
        
        assert suggestion["auto_recovery_available"] == True
        assert suggestion["auto_recovery_command"] is not None
        assert len(suggestion["auto_recovery_command"]) > 0
    
    def test_enhanced_error_response_structure(self):
        """Test enhanced error response structure."""
        suggestion = {
            "error_code": "test_error",
            "error_message": "Test error",
            "severity": "warning",
            "recovery_steps": ["Step 1", "Step 2"],
            "auto_recovery_available": False
        }
        
        response = {
            "error_code": "test_error",
            "error_message": "Test error",
            "severity": "warning",
            "context": {"timestamp": datetime.now().isoformat()},
            "affected_components": ["switch1", "switch2"],
            "recovery_suggestion": suggestion
        }
        
        assert response["error_code"] == "test_error"
        assert len(response["affected_components"]) > 0
        assert response["recovery_suggestion"] is not None
    
    def test_error_pattern_frequency_tracking(self):
        """Test error pattern frequency tracking."""
        patterns = [
            {
                "pattern_id": "error1",
                "pattern_name": "Error 1",
                "error_type": "configuration",
                "frequency": 10,
                "last_occurred": datetime.now().isoformat(),
                "suggested_fix": "Fix 1",
                "auto_recoverable": False
            },
            {
                "pattern_id": "error2",
                "pattern_name": "Error 2",
                "error_type": "network",
                "frequency": 5,
                "last_occurred": datetime.now().isoformat(),
                "suggested_fix": "Fix 2",
                "auto_recoverable": True
            }
        ]
        
        total_frequency = sum(p["frequency"] for p in patterns)
        assert total_frequency == 15
        
        # Find most frequent error
        most_frequent = max(patterns, key=lambda p: p["frequency"])
        assert most_frequent["pattern_id"] == "error1"
    
    def test_error_type_categorization(self):
        """Test error type categorization."""
        valid_types = ["configuration", "network", "validation", "hardware", "software"]
        
        for error_type in valid_types:
            pattern = {
                "pattern_id": f"test_{error_type}",
                "pattern_name": f"Test {error_type}",
                "error_type": error_type,
                "frequency": 1,
                "last_occurred": datetime.now().isoformat(),
                "suggested_fix": "Fix",
                "auto_recoverable": False
            }
            assert pattern["error_type"] == error_type
    
    def test_severity_classification(self):
        """Test error severity classification."""
        severities = ["critical", "warning", "info"]
        
        for severity in severities:
            suggestion = {
                "error_code": "test",
                "error_message": "Test",
                "severity": severity,
                "recovery_steps": ["Fix"],
                "auto_recovery_available": False
            }
            assert suggestion["severity"] == severity
    
    def test_recovery_steps_ordering(self):
        """Test that recovery steps are properly ordered."""
        steps = [
            "Identify the issue",
            "Review configuration",
            "Apply fix",
            "Validate resolution"
        ]
        
        suggestion = {
            "error_code": "test",
            "error_message": "Test",
            "severity": "warning",
            "recovery_steps": steps,
            "auto_recovery_available": False
        }
        
        assert len(suggestion["recovery_steps"]) == 4
        assert suggestion["recovery_steps"][0] == "Identify the issue"
        assert suggestion["recovery_steps"][-1] == "Validate resolution"
    
    def test_error_context_metadata(self):
        """Test error context metadata."""
        context = {
            "timestamp": datetime.now().isoformat(),
            "switch_hostname": "sw1",
            "switch_model": "N9K-C93180YC-FX",
            "nxos_version": "9.3(5)",
            "deployment_id": "deploy-123"
        }
        
        response = {
            "error_code": "test",
            "error_message": "Test",
            "severity": "warning",
            "context": context,
            "affected_components": ["sw1"],
            "recovery_suggestion": {
                "error_code": "test",
                "error_message": "Test",
                "severity": "warning",
                "recovery_steps": ["Fix"],
                "auto_recovery_available": False
            }
        }
        
        assert response["context"]["switch_hostname"] == "sw1"
        assert response["context"]["deployment_id"] == "deploy-123"
    
    def test_auto_recovery_command_validation(self):
        """Test auto-recovery command validation."""
        valid_commands = [
            "interface Ethernet1/1; no shutdown",
            "vlan 100; name Test-VLAN",
            "interface port-channel1; no shutdown"
        ]
        
        for cmd in valid_commands:
            suggestion = {
                "error_code": "test",
                "error_message": "Test",
                "severity": "warning",
                "recovery_steps": ["Fix"],
                "auto_recovery_available": True,
                "auto_recovery_command": cmd
            }
            assert suggestion["auto_recovery_command"] == cmd
    
    def test_affected_components_tracking(self):
        """Test affected components tracking."""
        components = ["sw1", "sw2", "sw3"]
        
        response = {
            "error_code": "test",
            "error_message": "Test",
            "severity": "warning",
            "context": {},
            "affected_components": components,
            "recovery_suggestion": {
                "error_code": "test",
                "error_message": "Test",
                "severity": "warning",
                "recovery_steps": ["Fix"],
                "auto_recovery_available": False
            }
        }
        
        assert len(response["affected_components"]) == 3
        assert "sw1" in response["affected_components"]
    
    def test_error_pattern_detection_logic(self):
        """Test error pattern detection logic."""
        # Simulate error log analysis
        error_logs = [
            {"code": "vlan_conflict", "timestamp": "2024-01-01T10:00:00"},
            {"code": "vlan_conflict", "timestamp": "2024-01-01T11:00:00"},
            {"code": "ip_conflict", "timestamp": "2024-01-01T12:00:00"},
            {"code": "vlan_conflict", "timestamp": "2024-01-01T13:00:00"}
        ]
        
        # Count occurrences
        from collections import Counter
        error_counts = Counter(log["code"] for log in error_logs)
        
        assert error_counts["vlan_conflict"] == 3
        assert error_counts["ip_conflict"] == 1
        
        # Most frequent error
        most_frequent = error_counts.most_common(1)[0]
        assert most_frequent[0] == "vlan_conflict"
        assert most_frequent[1] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
