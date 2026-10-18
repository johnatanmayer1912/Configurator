"""Validation Service - Orchestrate configuration validation pipeline.

This service provides a robust, validated approach to configuration validation
across all hardware models, NX-OS versions, and deployment scenarios. It ensures
data integrity through strict validation, clear contracts, and comprehensive
error handling.

Architecture Principles:
- Single source of truth for validation orchestration
- Clear data contracts with validation
- Hardware-agnostic validation pipeline
- Comprehensive error handling and logging
- Testable and maintainable code structure
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json

from core.config_parser import (
    parse_running_config, 
    ParsedConfig, 
    ValidationResult, 
    ValidationError, 
    ValidationWarning,
    RemediationSuggestion,
    ValidationSeverity
)
from core.catalog_loader import CatalogLoader

logger = logging.getLogger(__name__)


@dataclass
class ValidationCacheEntry:
    """Cached validation result with metadata"""
    validation_id: str
    config_hash: str
    hardware_model: str
    nxos_version: str
    validation_level: str
    result: ValidationResult
    timestamp: datetime
    hit_count: int = 0


@dataclass
class ValidationStatistics:
    """Validation statistics for monitoring and reporting"""
    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_validation_time_ms: float = 0.0
    last_validation_time: Optional[datetime] = None


@dataclass
class ValidationReport:
    """Comprehensive validation report for export and analysis"""
    validation_id: str
    timestamp: str
    hardware_model: str
    nxos_version: str
    validation_level: str
    is_valid: bool
    severity: str
    error_count: int
    warning_count: int
    suggestion_count: int
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    detected_role: str = ""
    detected_features: List[str] = field(default_factory=list)
    hostname: str = ""
    mgmt_ip: str = ""
    vlans: List[Dict[str, Any]] = field(default_factory=list)
    vpc_domain_id: Optional[int] = None


class ValidationService:
    """Orchestrate configuration validation pipeline with caching and statistics."""
    
    def __init__(self):
        """Initialize validation service with cache and statistics."""
        self._cache: Dict[str, ValidationCacheEntry] = {}
        self._statistics = ValidationStatistics()
        self._catalog = CatalogLoader()
    
    def _generate_config_hash(self, config_text: str) -> str:
        """Generate hash for configuration caching."""
        return hashlib.sha256(config_text.encode()).hexdigest()
    
    def _generate_cache_key(self, config_hash: str, hardware_model: str, 
                          nxos_version: str, validation_level: str) -> str:
        """Generate cache key for validation result."""
        key_parts = [config_hash, hardware_model, nxos_version, validation_level]
        return hashlib.sha256("|".join(key_parts).encode()).hexdigest()
    
    def validate_config(self, config_text: str, hardware_model: str, 
                      nxos_version: str = "9.3", validation_level: str = "comprehensive",
                      baseline_options: List[str] = None) -> ValidationResult:
        """
        Validate configuration with caching and comprehensive pipeline.
        
        Args:
            config_text: NX-OS running-config text
            hardware_model: Hardware model name (e.g., "Nexus 9336C-FX2")
            nxos_version: NX-OS version (e.g., "9.3")
            validation_level: Validation depth (basic, standard, comprehensive)
            baseline_options: List of baseline options for compliance checking
        
        Returns:
            ValidationResult with errors, warnings, and suggestions
        """
        start_time = datetime.now()
        baseline_options = baseline_options or []
        
        # Update statistics
        self._statistics.total_validations += 1
        self._statistics.last_validation_time = start_time
        
        # Check cache
        config_hash = self._generate_config_hash(config_text)
        cache_key = self._generate_cache_key(config_hash, hardware_model, 
                                            nxos_version, validation_level)
        
        if cache_key in self._cache:
            self._statistics.cache_hits += 1
            cache_entry = self._cache[cache_key]
            cache_entry.hit_count += 1
            logger.info(f"VALIDATION_CACHE_HIT", validation_id=cache_entry.validation_id,
                       cache_key=cache_key, hit_count=cache_entry.hit_count)
            return cache_entry.result
        
        self._statistics.cache_misses += 1
        
        try:
            # Parse configuration
            parsed = parse_running_config(config_text)
            
            # Get hardware profile
            hw_profile = self._catalog.get_hardware_profile(hardware_model)
            
            # Initialize validation result
            validation_result = ValidationResult()
            
            # Perform validation based on level
            if validation_level in ["standard", "comprehensive"]:
                syntax_result = parsed.validate_syntax(config_text)
                validation_result.errors.extend(syntax_result.errors)
                validation_result.warnings.extend(syntax_result.warnings)
            
            if validation_level == "comprehensive":
                if hw_profile:
                    port_result = parsed.validate_port_mapping(hw_profile)
                    validation_result.errors.extend(port_result.errors)
                    validation_result.warnings.extend(port_result.warnings)
                    
                    vlan_result = parsed.validate_vlan_ranges(hw_profile)
                    validation_result.errors.extend(vlan_result.errors)
                    validation_result.warnings.extend(vlan_result.warnings)
                
                vpc_result = parsed.validate_vpc_consistency()
                validation_result.errors.extend(vpc_result.errors)
                validation_result.warnings.extend(vpc_result.warnings)
                
                feature_result = parsed.validate_feature_compatibility(nxos_version)
                validation_result.warnings.extend(feature_result.warnings)
                
                if baseline_options:
                    baseline_result = parsed.validate_baseline_compliance(baseline_options)
                    validation_result.warnings.extend(baseline_result.warnings)
                
                security_result = parsed.validate_security_policies()
                validation_result.warnings.extend(security_result.warnings)
                
                suggestions = parsed.suggest_fixes()
                validation_result.suggestions = suggestions
            
            # Cache result
            cache_entry = ValidationCacheEntry(
                validation_id=validation_result.validation_id,
                config_hash=config_hash,
                hardware_model=hardware_model,
                nxos_version=nxos_version,
                validation_level=validation_level,
                result=validation_result,
                timestamp=start_time
            )
            self._cache[cache_key] = cache_entry
            
            # Update statistics
            if validation_result.is_valid:
                self._statistics.successful_validations += 1
            else:
                self._statistics.failed_validations += 1
            
            validation_time = (datetime.now() - start_time).total_seconds() * 1000
            self._statistics.average_validation_time_ms = (
                (self._statistics.average_validation_time_ms * (self._statistics.total_validations - 1) + 
                 validation_time) / self._statistics.total_validations
            )
            
            logger.info(f"VALIDATION_COMPLETE", validation_id=validation_result.validation_id,
                       is_valid=validation_result.is_valid, severity=validation_result.severity,
                       error_count=len(validation_result.errors),
                       warning_count=len(validation_result.warnings),
                       validation_time_ms=validation_time)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"VALIDATION_ERROR", error=str(e), exc_info=True)
            # Return error result
            error_result = ValidationResult()
            error_result.is_valid = False
            error_result.severity = "critical"
            error_result.errors.append(ValidationError(
                error_code="VALIDATION_EXCEPTION",
                message=f"Validation failed with exception: {str(e)}",
                severity=ValidationSeverity.CRITICAL
            ))
            return error_result
    
    def validate_deployment(self, deployment_config: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """
        Validate multi-switch deployment configuration.
        
        Args:
            deployment_config: Deployment configuration with switches, vpc_pairs, uplinks
        
        Returns:
            Dictionary mapping hostname to ValidationResult
        """
        results = {}
        
        switches = deployment_config.get("switches", [])
        vpc_pairs = deployment_config.get("vpc_pairs", [])
        
        # Validate each switch
        for switch_config in switches:
            hostname = switch_config.get("hostname", "unknown")
            hardware_model = switch_config.get("model", "Generic")
            nxos_version = switch_config.get("nxos_version", "9.3")
            
            # For deployment validation, we need to construct a config from the switch config
            # This is a simplified version - in production, you'd have the actual config text
            # For now, we'll validate the switch configuration parameters
            result = ValidationResult()
            
            # Validate hostname
            if not hostname or len(hostname) < 2:
                result.errors.append(ValidationError(
                    error_code="INVALID_HOSTNAME",
                    message="Hostname must be at least 2 characters",
                    severity=ValidationSeverity.HIGH
                ))
            
            # Validate management IP
            mgmt_ip = switch_config.get("mgmt_ip", "")
            if not mgmt_ip or "/" not in mgmt_ip:
                result.errors.append(ValidationError(
                    error_code="INVALID_MGMT_IP",
                    message="Management IP must include CIDR notation",
                    severity=ValidationSeverity.HIGH
                ))
            
            # Validate vPC domain if present
            vpc_domain = switch_config.get("vpc_domain")
            if vpc_domain:
                try:
                    domain_int = int(vpc_domain)
                    if domain_int < 1 or domain_int > 4096:
                        result.errors.append(ValidationError(
                            error_code="INVALID_VPC_DOMAIN",
                            message=f"vPC domain {domain_int} is outside valid range (1-4096)",
                            severity=ValidationSeverity.CRITICAL
                        ))
                except ValueError:
                    result.errors.append(ValidationError(
                        error_code="INVALID_VPC_DOMAIN",
                        message=f"vPC domain must be a valid integer",
                        severity=ValidationSeverity.CRITICAL
                    ))
            
            results[hostname] = result
        
        # Validate vPC pair consistency
        vpc_domains = set()
        for vpc_pair in vpc_pairs:
            domain = vpc_pair.get("domain")
            if domain:
                if domain in vpc_domains:
                    for hostname in results:
                        results[hostname].errors.append(ValidationError(
                            error_code="DUPLICATE_VPC_DOMAIN",
                            message=f"vPC domain {domain} is used in multiple pairs",
                            severity=ValidationSeverity.CRITICAL
                        ))
                vpc_domains.add(domain)
        
        return results
    
    def get_validation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get validation history from cache.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of validation history entries
        """
        history = []
        
        for cache_entry in sorted(self._cache.values(), 
                                 key=lambda x: x.timestamp, reverse=True)[:limit]:
            history.append({
                "validation_id": cache_entry.validation_id,
                "hardware_model": cache_entry.hardware_model,
                "nxos_version": cache_entry.nxos_version,
                "validation_level": cache_entry.validation_level,
                "is_valid": cache_entry.result.is_valid,
                "severity": cache_entry.result.severity,
                "error_count": len(cache_entry.result.errors),
                "warning_count": len(cache_entry.result.warnings),
                "timestamp": cache_entry.timestamp.isoformat(),
                "hit_count": cache_entry.hit_count
            })
        
        return history
    
    def generate_validation_report(self, validation_id: str) -> Optional[ValidationReport]:
        """
        Generate comprehensive validation report.
        
        Args:
            validation_id: Validation result ID
        
        Returns:
            ValidationReport or None if not found
        """
        # Find cache entry by validation_id
        cache_entry = None
        for entry in self._cache.values():
            if entry.validation_id == validation_id:
                cache_entry = entry
                break
        
        if not cache_entry:
            logger.warning(f"VALIDATION_NOT_FOUND", validation_id=validation_id)
            return None
        
        result = cache_entry.result
        
        # Build report
        report = ValidationReport(
            validation_id=validation_id,
            timestamp=cache_entry.timestamp.isoformat(),
            hardware_model=cache_entry.hardware_model,
            nxos_version=cache_entry.nxos_version,
            validation_level=cache_entry.validation_level,
            is_valid=result.is_valid,
            severity=result.severity,
            error_count=len(result.errors),
            warning_count=len(result.warnings),
            suggestion_count=len(result.suggestions)
        )
        
        # Add errors
        for error in result.errors:
            report.errors.append({
                "line_number": error.line_number,
                "line_content": error.line_content,
                "error_code": error.error_code,
                "message": error.message,
                "severity": error.severity.value,
                "suggestion": error.suggestion,
                "fix_command": error.fix_command
            })
        
        # Add warnings
        for warning in result.warnings:
            report.warnings.append({
                "line_number": warning.line_number,
                "line_content": warning.line_content,
                "warning_code": warning.warning_code,
                "message": warning.message,
                "severity": warning.severity.value,
                "suggestion": warning.suggestion
            })
        
        # Add suggestions
        for suggestion in result.suggestions:
            report.suggestions.append({
                "issue_code": suggestion.issue_code,
                "description": suggestion.description,
                "complexity": suggestion.complexity,
                "commands": suggestion.commands,
                "estimated_time": suggestion.estimated_time,
                "risk_level": suggestion.risk_level
            })
        
        return report
    
    def get_statistics(self) -> ValidationStatistics:
        """Get validation statistics."""
        return self._statistics
    
    def clear_cache(self) -> None:
        """Clear validation cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"VALIDATION_CACHE_CLEARED", entries_removed=cache_size)
    
    def clear_cache_by_hardware(self, hardware_model: str) -> int:
        """
        Clear cache entries for specific hardware model.
        
        Args:
            hardware_model: Hardware model to clear from cache
        
        Returns:
            Number of entries removed
        """
        keys_to_remove = [k for k, v in self._cache.items() 
                         if v.hardware_model == hardware_model]
        
        for key in keys_to_remove:
            del self._cache[key]
        
        logger.info(f"VALIDATION_CACHE_CLEARED_BY_HARDWARE", hardware_model=hardware_model,
                   entries_removed=len(keys_to_remove))
        return len(keys_to_remove)


# Global validation service instance
_validation_service = None

def get_validation_service() -> ValidationService:
    """Get global validation service instance."""
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service
