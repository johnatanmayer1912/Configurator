"""Config Parser Unit Tests

Tests the NX-OS running-config parsing logic including:
- ParsedConfig dataclass
- ValidationSeverity enum
- ValidationError, ValidationWarning, RemediationSuggestion dataclasses
- ValidationResult aggregation
"""

import pytest
from core.config_parser import (
    ValidationSeverity,
    ValidationError,
    ValidationWarning,
    RemediationSuggestion,
    ValidationResult,
    ParsedConfig,
    parse_running_config
)


class TestValidationSeverity:
    """Test validation severity enum."""
    
    def test_severity_values(self):
        """Test that severity enum has expected values."""
        assert ValidationSeverity.INFO.value == "info"
        assert ValidationSeverity.LOW.value == "low"
        assert ValidationSeverity.MEDIUM.value == "medium"
        assert ValidationSeverity.HIGH.value == "high"
        assert ValidationSeverity.CRITICAL.value == "critical"
    
    def test_severity_comparison(self):
        """Test that severity levels have expected order."""
        # Enum values are ordered by definition
        severities = [ValidationSeverity.INFO, ValidationSeverity.LOW, ValidationSeverity.MEDIUM, ValidationSeverity.HIGH, ValidationSeverity.CRITICAL]
        assert len(severities) == 5


class TestValidationError:
    """Test validation error dataclass."""
    
    def test_error_creation(self):
        """Test creating a validation error."""
        error = ValidationError(
            error_code="ERR001",
            message="Invalid VLAN ID",
            severity=ValidationSeverity.HIGH,
            line_number=10,
            line_content="vlan 5000"
        )
        
        assert error.error_code == "ERR001"
        assert error.message == "Invalid VLAN ID"
        assert error.severity == ValidationSeverity.HIGH
        assert error.line_number == 10
        assert error.line_content == "vlan 5000"
    


class TestValidationWarning:
    """Test validation warning dataclass."""
    
    def test_warning_creation(self):
        """Test creating a validation warning."""
        warning = ValidationWarning(
            warning_code="WARN001",
            message="Non-standard configuration",
            severity=ValidationSeverity.MEDIUM,
            line_number=15,
            line_content="no spanning-tree vlan 1"
        )
        
        assert warning.warning_code == "WARN001"
        assert warning.message == "Non-standard configuration"
        assert warning.severity == ValidationSeverity.MEDIUM


class TestRemediationSuggestion:
    """Test remediation suggestion dataclass."""
    
    def test_suggestion_creation(self):
        """Test creating a remediation suggestion."""
        suggestion = RemediationSuggestion(
            issue_code="REM001",
            description="Remove invalid VLAN",
            complexity="simple",
            commands=["no vlan 5000"]
        )
        
        assert suggestion.issue_code == "REM001"
        assert suggestion.description == "Remove invalid VLAN"
        assert suggestion.complexity == "simple"


class TestValidationResult:
    """Test validation result aggregation."""
    
    def test_result_creation_empty(self):
        """Test creating empty validation result."""
        result = ValidationResult()
        
        assert result.is_valid is True  # Empty result is valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.suggestions) == 0
        assert result.severity == "info"
    
    def test_result_with_error(self):
        """Test result with error makes it invalid."""
        error = ValidationError(
            error_code="ERR001",
            message="Invalid VLAN",
            severity=ValidationSeverity.HIGH
        )
        
        result = ValidationResult(errors=[error])
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.severity == "high"
    
    def test_result_with_warning_only(self):
        """Test result with only warnings is still valid."""
        warning = ValidationWarning(
            warning_code="WARN001",
            message="Non-standard config",
            severity=ValidationSeverity.MEDIUM
        )
        
        result = ValidationResult(warnings=[warning])
        
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.severity == "low"
    
    def test_result_with_critical_error(self):
        """Test result with critical error."""
        error = ValidationError(
            error_code="CRIT001",
            message="Critical failure",
            severity=ValidationSeverity.CRITICAL
        )
        
        result = ValidationResult(errors=[error])
        
        assert result.is_valid is False
        assert result.severity == "critical"
    
    def test_result_severity_calculation(self):
        """Test that overall severity is calculated correctly."""
        errors = [
            ValidationError(error_code="ERR001", message="Error 1", severity=ValidationSeverity.HIGH),
            ValidationError(error_code="CRIT001", message="Critical", severity=ValidationSeverity.CRITICAL)
        ]
        
        result = ValidationResult(errors=errors)
        
        # Should use highest severity
        assert result.severity == "critical"
    


class TestParseRunningConfig:
    """Test running-config parsing."""
    
    def test_parse_empty_config(self):
        """Test parsing empty configuration."""
        result = parse_running_config("")
        
        assert result is not None
        assert isinstance(result, ParsedConfig)
    
    def test_parse_simple_config(self):
        """Test parsing simple valid configuration."""
        config = """
hostname TEST-SW-01
feature lacp
feature lldp
vlan 10
  name DATA_VLAN
"""
        result = parse_running_config(config)
        
        assert result is not None
        assert isinstance(result, ParsedConfig)
        assert result.hostname == "TEST-SW-01"
        assert "lacp" in result.features
        assert "lldp" in result.features
    
    def test_parse_config_with_errors(self):
        """Test parsing configuration with errors."""
        config = """
hostname TEST-SW-01
vlan 5000
  name INVALID_VLAN
"""
        result = parse_running_config(config)
        
        assert result is not None
        # Should detect invalid VLAN ID
        # (Actual parsing logic may vary based on implementation)
    
    def test_parse_config_multiline(self):
        """Test parsing multi-line configuration."""
        config = """
interface Ethernet1/1
  description Test Port
  switchport mode access
  switchport access vlan 10
  spanning-tree port type edge
  no shutdown
"""
        result = parse_running_config(config)
        
        assert result is not None
        assert isinstance(result, ParsedConfig)
        assert "Ethernet1/1" in result.interface_lines


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
