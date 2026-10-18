"""Validation Service Unit Tests

Tests the validation service orchestration pipeline including:
- Validation caching
- Validation statistics
- Validation report generation
"""

import pytest
from datetime import datetime
from core.validation_service import (
    ValidationService,
    ValidationCacheEntry,
    ValidationStatistics,
    ValidationReport
)
from core.config_parser import ValidationResult, ValidationSeverity


class TestValidationCacheEntry:
    """Test validation cache entry dataclass."""
    
    def test_cache_entry_creation(self):
        """Test creating a validation cache entry."""
        entry = ValidationCacheEntry(
            validation_id="test-123",
            config_hash="abc123",
            hardware_model="Nexus 93180YC-EX",
            nxos_version="9.3",
            validation_level="standard",
            result=ValidationResult(is_valid=True),
            timestamp=datetime.now()
        )
        
        assert entry.validation_id == "test-123"
        assert entry.config_hash == "abc123"
        assert entry.hardware_model == "Nexus 93180YC-EX"
        assert entry.nxos_version == "9.3"
        assert entry.validation_level == "standard"
        assert entry.hit_count == 0
    
    def test_cache_entry_hit_count_increment(self):
        """Test that hit count can be incremented."""
        entry = ValidationCacheEntry(
            validation_id="test-123",
            config_hash="abc123",
            hardware_model="Nexus 93180YC-EX",
            nxos_version="9.3",
            validation_level="standard",
            result=ValidationResult(is_valid=True),
            timestamp=datetime.now()
        )
        
        entry.hit_count += 1
        assert entry.hit_count == 1


class TestValidationStatistics:
    """Test validation statistics dataclass."""
    
    def test_statistics_initialization(self):
        """Test creating validation statistics."""
        stats = ValidationStatistics()
        
        assert stats.total_validations == 0
        assert stats.successful_validations == 0
        assert stats.failed_validations == 0
        assert stats.cache_hits == 0
        assert stats.cache_misses == 0
        assert stats.average_validation_time_ms == 0.0
        assert stats.last_validation_time is None
    
    def test_statistics_increment(self):
        """Test incrementing statistics."""
        stats = ValidationStatistics()
        
        stats.total_validations += 1
        stats.successful_validations += 1
        
        assert stats.total_validations == 1
        assert stats.successful_validations == 1


class TestValidationReport:
    """Test validation report dataclass."""
    
    def test_report_creation(self):
        """Test creating a validation report."""
        report = ValidationReport(
            validation_id="test-123",
            timestamp=datetime.now().isoformat(),
            hardware_model="Nexus 93180YC-EX",
            nxos_version="9.3",
            validation_level="standard",
            is_valid=True,
            severity="info",
            error_count=0,
            warning_count=0,
            suggestion_count=0,
            hostname="TEST-SW-01",
            mgmt_ip="10.10.10.10/24"
        )
        
        assert report.validation_id == "test-123"
        assert report.is_valid is True
        assert report.severity == "info"
        assert report.error_count == 0
        assert report.hostname == "TEST-SW-01"
    
    def test_report_with_errors(self):
        """Test report with errors."""
        report = ValidationReport(
            validation_id="test-456",
            timestamp=datetime.now().isoformat(),
            hardware_model="Nexus 93180YC-EX",
            nxos_version="9.3",
            validation_level="standard",
            is_valid=False,
            severity="critical",
            error_count=2,
            warning_count=1,
            suggestion_count=0,
            errors=[
                {"code": "ERR001", "message": "Invalid VLAN"},
                {"code": "ERR002", "message": "Invalid IP"}
            ],
            warnings=[
                {"code": "WARN001", "message": "Non-standard config"}
            ]
        )
        
        assert report.is_valid is False
        assert report.severity == "critical"
        assert report.error_count == 2
        assert report.warning_count == 1
        assert len(report.errors) == 2
        assert len(report.warnings) == 1


class TestValidationService:
    """Test validation service orchestration."""
    
    @pytest.fixture
    def validation_service(self):
        """Create validation service instance."""
        return ValidationService()
    
    def test_service_initialization(self, validation_service):
        """Test that validation service initializes correctly."""
        assert validation_service._cache == {}
        assert validation_service._statistics.total_validations == 0
        assert validation_service._catalog is not None
    
    def test_generate_config_hash(self, validation_service):
        """Test configuration hash generation."""
        config1 = "interface Ethernet1/1\n  description Test"
        config2 = "interface Ethernet1/1\n  description Test"
        config3 = "interface Ethernet1/1\n  description Different"
        
        hash1 = validation_service._generate_config_hash(config1)
        hash2 = validation_service._generate_config_hash(config2)
        hash3 = validation_service._generate_config_hash(config3)
        
        assert hash1 == hash2, "Same config should produce same hash"
        assert hash1 != hash3, "Different config should produce different hash"
    
    def test_generate_cache_key(self, validation_service):
        """Test cache key generation."""
        key = validation_service._generate_cache_key(
            "abc123",
            "Nexus 93180YC-EX",
            "9.3",
            "standard"
        )
        
        assert isinstance(key, str)
        assert len(key) > 0
    
    def test_cache_entry_storage(self, validation_service):
        """Test storing and retrieving cache entries."""
        entry = ValidationCacheEntry(
            validation_id="test-123",
            config_hash="abc123",
            hardware_model="Nexus 93180YC-EX",
            nxos_version="9.3",
            validation_level="standard",
            result=ValidationResult(is_valid=True),
            timestamp=datetime.now()
        )
        
        validation_service._cache["test-key"] = entry
        
        retrieved = validation_service._cache["test-key"]
        assert retrieved.validation_id == "test-123"
        assert retrieved.hit_count == 0
    
    def test_statistics_tracking(self, validation_service):
        """Test that statistics are tracked correctly."""
        validation_service._statistics.total_validations += 1
        validation_service._statistics.successful_validations += 1
        
        assert validation_service._statistics.total_validations == 1
        assert validation_service._statistics.successful_validations == 1
    
    def test_catalog_loader_initialization(self, validation_service):
        """Test that catalog loader is initialized."""
        assert validation_service._catalog is not None
        # Catalog should be able to load hardware profiles
        profiles = validation_service._catalog.list_hardware_profiles()
        assert len(profiles) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
