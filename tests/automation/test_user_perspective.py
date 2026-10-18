"""Automation tests from User perspective - Config upload workflow.

User Expectations:
- Easy-to-use configuration upload interface
- Clear validation feedback with actionable suggestions
- Quick turnaround time for validation results
- Intuitive error messages that explain what's wrong and how to fix it
- Support for common NX-OS configuration patterns
- Ability to validate before deployment to avoid costly mistakes
"""

import pytest
import time
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestUserPerspective:
    """User perspective automation tests for config upload workflow."""
    
    def test_user_can_upload_config_simple_workflow(self):
        """
        User Story: As a network administrator, I want to upload my running config
        to validate it before deploying changes.
        
        Expected Behavior:
        - User uploads config text
        - System returns validation results within 2 seconds
        - Results clearly indicate if config is valid or has issues
        - Error messages are understandable to non-experts
        """
        user_config = """
hostname PROD-SWITCH-01
feature lacp
feature lldp
interface Ethernet1/1
  description Server Port
  switchport access vlan 100
  no shutdown
"""
        
        start_time = time.time()
        response = client.post("/config/upload", json={
            "config_text": user_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        elapsed_time = time.time() - start_time
        
        # User expects quick response
        assert elapsed_time < 2.0, f"Validation took {elapsed_time:.2f}s, user expects < 2s"
        assert response.status_code == 200
        
        result = response.json()
        
        # User expects clear validation status
        assert "is_valid" in result, "User needs to know if config is valid"
        assert "validation_id" in result, "User needs reference ID for tracking"
        
        # User expects understandable error messages
        if not result["is_valid"]:
            for error in result.get("errors", []):
                assert error["message"], "Error messages must be descriptive"
                assert error["suggestion"], "User needs actionable suggestions"
    
    def test_user_gets_helpful_suggestions_for_common_errors(self):
        """
        User Story: As a network administrator, I want helpful suggestions
        when I make common configuration mistakes.
        
        Expected Behavior:
        - System detects common mistakes (trailing whitespace, default hostname)
        - Provides clear, actionable suggestions
        - Suggestions include example fix commands when possible
        """
        # Common user mistake: trailing whitespace
        config_with_mistakes = """
hostname switch  
feature lacp
interface Ethernet1/1  
  description Test  
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_with_mistakes,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # User expects warnings for common mistakes
        warnings = result.get("warnings", [])
        assert len(warnings) > 0, "User expects warnings for common mistakes"
        
        # User expects helpful suggestions
        for warning in warnings:
            if warning["warning_code"] == "DEFAULT_HOSTNAME":
                assert "change" in warning["message"].lower() or "unique" in warning["message"].lower()
    
    def test_user_can_validate_before_deployment(self):
        """
        User Story: As a network administrator, I want to validate my config
        before deploying to production to avoid outages.
        
        Expected Behavior:
        - User uploads config for validation
        - System checks for critical errors that would cause deployment failure
        - User gets clear indication if config is deployment-ready
        """
        production_config = """
hostname PROD-CORE-01
feature vpc
vpc domain 100
  peer-keepalive destination 10.10.10.2 source 10.10.10.1
interface port-channel1
  vpc peer-link
interface Ethernet1/51-52
  channel-group 1 mode active
"""
        
        response = client.post("/config/upload", json={
            "config_text": production_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # User expects deployment readiness indicator
        if result["is_valid"]:
            # Config is ready for deployment
            assert result["severity"] in ["info", "low"], "Valid config should have low severity"
        else:
            # Config has issues that need fixing
            critical_errors = [e for e in result.get("errors", []) if e["severity"] == "critical"]
            assert len(critical_errors) > 0, "Invalid config should have critical errors"
    
    def test_user_can_understand_validation_severity_levels(self):
        """
        User Story: As a network administrator, I want to understand the severity
        of validation issues to prioritize fixes.
        
        Expected Behavior:
        - System categorizes issues by severity (critical, high, medium, low, info)
        - Overall severity level is clearly indicated
        - User can prioritize critical issues first
        """
        config_with_issues = """
hostname switch
feature nxapi
feature bash-shell
"""
        
        response = client.post("/config/upload", json={
            "config_text": config_with_issues,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # User expects severity categorization
        assert "severity" in result, "User needs overall severity level"
        
        # User expects individual issue severities
        for error in result.get("errors", []):
            assert "severity" in error, "Each error must have severity level"
            assert error["severity"] in ["critical", "high", "medium", "low", "info"]
        
        for warning in result.get("warnings", []):
            assert "severity" in warning, "Each warning must have severity level"
            assert warning["severity"] in ["critical", "high", "medium", "low", "info"]
    
    def test_user_can_reuse_validation_results(self):
        """
        User Story: As a network administrator, I want to save validation results
        for documentation and audit purposes.
        
        Expected Behavior:
        - Validation results include unique ID for reference
        - Results include timestamp for tracking
        - Results can be exported or saved
        """
        config = """
hostname TEST-SWITCH
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
        
        # User expects reference ID
        assert "validation_id" in result, "User needs ID for documentation"
        assert len(result["validation_id"]) > 0, "Validation ID must not be empty"
        
        # User expects timestamp
        assert "timestamp" in result, "User needs timestamp for audit trail"
        assert len(result["timestamp"]) > 0, "Timestamp must not be empty"
    
    def test_user_can_validate_different_hardware_models(self):
        """
        User Story: As a network administrator managing different switch models,
        I want to validate configs for each specific hardware type.
        
        Expected Behavior:
        - User can specify hardware model
        - Validation uses hardware-specific constraints
        - Results are accurate for the specified model
        """
        config = """
hostname SWITCH
feature lacp
vlan 100
  name Test_VLAN
"""
        
        # Test with different hardware models
        for model in ["Nexus 93180YC-EX", "Nexus 9336C-FX2", "Nexus 9348GC-FXP"]:
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": model,
                "nxos_version": "9.3",
                "validation_level": "standard"
            })
            
            assert response.status_code == 200
            result = response.json()
            assert "validation_id" in result, f"Validation should work for {model}"
    
    def test_user_can_choose_validation_level(self):
        """
        User Story: As a network administrator, I want to choose validation
        depth based on my needs (quick check vs comprehensive audit).
        
        Expected Behavior:
        - User can select validation level (basic, standard, comprehensive)
        - Basic level is faster for quick checks
        - Comprehensive level catches more issues
        """
        config = """
hostname SWITCH
feature lacp
interface Ethernet1/1
  description Test
"""
        
        # Test basic validation (should be faster)
        start_time = time.time()
        response_basic = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "basic"
        })
        basic_time = time.time() - start_time
        
        assert response_basic.status_code == 200
        
        # Test comprehensive validation (may be slower but more thorough)
        start_time = time.time()
        response_comprehensive = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        comprehensive_time = time.time() - start_time
        
        assert response_comprehensive.status_code == 200
        
        # User expects basic to be faster
        assert basic_time <= comprehensive_time, "Basic validation should be faster or equal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
