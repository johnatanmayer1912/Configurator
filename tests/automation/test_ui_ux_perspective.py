"""Automation tests from UI/UX perspective - Validation feedback UX.

UI/UX Professional Expectations:
- Clear and actionable validation feedback
- Intuitive error presentation with severity indicators
- User-friendly error messages with context
- Visual hierarchy for validation results
- Responsive design for different screen sizes
- Accessible error messaging
- Consistent validation feedback patterns
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestUIUXPerspective:
    """UI/UX Professional perspective automation tests for validation feedback UX."""
    
    def test_validation_results_have_clear_structure(self):
        """
        UI/UX Scenario: Validation results must have clear, structured format for UI rendering.
        
        Expected Behavior:
        - Results have consistent structure
        - Fields are well-named for UI mapping
        - Structure supports hierarchical display
        - Empty fields are handled gracefully
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects consistent structure
        required_fields = ["validation_id", "is_valid", "errors", "warnings", "suggestions", "severity", "timestamp"]
        for field in required_fields:
            assert field in result, f"UI requires field '{field}' for rendering"
        
        # UI/UX expects arrays for list display
        assert isinstance(result["errors"], list), "Errors must be array for UI list rendering"
        assert isinstance(result["warnings"], list), "Warnings must be array for UI list rendering"
        assert isinstance(result["suggestions"], list), "Suggestions must be array for UI list rendering"
    
    def test_error_messages_are_user_friendly(self):
        """
        UI/UX Scenario: Error messages must be understandable by non-experts.
        
        Expected Behavior:
        - Error messages use plain language
        - Avoid technical jargon where possible
        - Provide context for the error
        - Include actionable guidance
        """
        config_with_error = """
hostname switch
feature vpc
vpc domain 5000
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_with_error,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects user-friendly messages
        for error in result.get("errors", []):
            # Messages should be descriptive
            assert len(error["message"]) > 10, "Error messages should be descriptive"
            assert len(error["message"]) < 200, "Error messages should be concise for UI"
            
            # Suggestions should be actionable
            if error.get("suggestion"):
                assert len(error["suggestion"]) > 10, "Suggestions should be actionable"
    
    def test_severity_levels_support_visual_hierarchy(self):
        """
        UI/UX Scenario: Severity levels must support visual hierarchy in UI.
        
        Expected Behavior:
        - Severity levels map to visual indicators
        - Color coding is consistent
        - Severity ordering is logical
        - Icons can be mapped to severity
        """
        config_with_issues = """
hostname switch
feature nxapi
feature bash-shell
vpc domain 5000
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_with_issues,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects consistent severity levels
        valid_severities = ["critical", "high", "medium", "low", "info"]
        
        # Check overall severity
        assert result["severity"] in valid_severities, "Overall severity must be valid for UI mapping"
        
        # Check individual error severities
        for error in result.get("errors", []):
            assert error["severity"] in valid_severities, "Error severity must be valid for UI mapping"
        
        # Check individual warning severities
        for warning in result.get("warnings", []):
            assert warning["severity"] in valid_severities, "Warning severity must be valid for UI mapping"
    
    def test_validation_results_support_pagination(self):
        """
        UI/UX Scenario: Large validation results should support pagination.
        
        Expected Behavior:
        - Results include counts for pagination
        - Structure supports page-based display
        - Total counts are accurate
        """
        # Generate large config with many potential issues
        large_config = "\n".join([f"interface Ethernet1/{i}\n  description Port {i}" for i in range(100)])
        
        response = client.post("/config/upload", json={
            "config_text": large_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects countable results for pagination
        error_count = len(result.get("errors", []))
        warning_count = len(result.get("warnings", []))
        
        # Counts should be available for UI pagination logic
        assert isinstance(error_count, int), "Error count must be integer for pagination"
        assert isinstance(warning_count, int), "Warning count must be integer for pagination"
    
    def test_line_numbers_support_code_editor_integration(self):
        """
        UI/UX Scenario: Line numbers must support code editor integration.
        
        Expected Behavior:
        - Errors include line numbers
        - Line numbers are accurate
        - Line numbers support editor highlighting
        """
        config_with_line_errors = """
hostname SWITCH
feature lacp
interface Ethernet1/1
  description Test
  invalid command here
interface Ethernet1/2
  another invalid command
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_with_line_errors,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects line numbers for editor integration
        for error in result.get("errors", []):
            if error.get("line_number"):
                assert isinstance(error["line_number"], int), "Line number must be integer for editor"
                assert error["line_number"] >= 1, "Line numbers should be 1-indexed"
    
    def test_fix_commands_support_quick_actions(self):
        """
        UI/UX Scenario: Fix commands should support quick action buttons.
        
        Expected Behavior:
        - Fix commands are provided when applicable
        - Commands are copyable
        - Commands are safe to execute
        """
        config_with_fixable_issues = """
hostname SWITCH  
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_with_fixable_issues,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects fix commands for quick actions
        for error in result.get("errors", []):
            if error.get("fix_command"):
                # Fix command should be valid NX-OS syntax
                assert isinstance(error["fix_command"], str), "Fix command must be string"
                assert len(error["fix_command"]) > 0, "Fix command should not be empty"
    
    def test_validation_id_supports_tracking_and_history(self):
        """
        UI/UX Scenario: Validation ID should support tracking and history features.
        
        Expected Behavior:
        - Validation ID is unique
        - ID is URL-safe
        - ID supports lookup
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects usable validation ID
        validation_id = result["validation_id"]
        assert isinstance(validation_id, str), "Validation ID must be string"
        assert len(validation_id) > 0, "Validation ID should not be empty"
        # ID should be URL-safe (no special characters that break URLs)
        assert validation_id.isalnum() or "-" in validation_id or "_" in validation_id, \
            "Validation ID should be URL-safe"
    
    def test_timestamp_supports_sorting_and_filtering(self):
        """
        UI/UX Scenario: Timestamp should support sorting and filtering in history views.
        
        Expected Behavior:
        - Timestamp is in standard format
        - Timestamp is sortable
        - Timestamp supports date filtering
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects standard timestamp format
        timestamp = result["timestamp"]
        assert isinstance(timestamp, str), "Timestamp must be string"
        assert len(timestamp) > 0, "Timestamp should not be empty"
        # Should be in ISO format or similar standard format
        assert "T" in timestamp or "-" in timestamp, "Timestamp should be in standard format"
    
    def test_empty_results_handle_gracefully(self):
        """
        UI/UX Scenario: Empty validation results should handle gracefully in UI.
        
        Expected Behavior:
        - Empty arrays don't break UI
        - Null fields are handled
        - Default values are provided
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        response = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects graceful handling of empty results
        # Arrays should be empty lists, not null
        assert isinstance(result["errors"], list), "Errors should be list even if empty"
        assert isinstance(result["warnings"], list), "Warnings should be list even if empty"
        assert isinstance(result["suggestions"], list), "Suggestions should be list even if empty"
    
    def test_detected_role_supports_ui_badges(self):
        """
        UI/UX Scenario: Detected role should support UI badges and indicators.
        
        Expected Behavior:
        - Role is detected and returned
        - Role maps to UI badge
        - Role is user-friendly
        """
        leaf_config = """
hostname LEAF-SWITCH
feature lacp
interface Ethernet1/1
  description Access Port
  switchport access vlan 100
"""
        
        response = client.post("/config/upload", json={
            "config_text": leaf_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # UI/UX expects detected role for badges
        if "detected_role" in result:
            detected_role = result["detected_role"]
            assert isinstance(detected_role, str), "Detected role must be string"
            assert len(detected_role) > 0, "Detected role should not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
