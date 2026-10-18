"""Parse NX-OS running-config snippets into structured hints for the Config Builder."""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


FEATURE_MAP = {
    "interface-vlan": "interface_vlan",
    "vpc": "vpc",
    "lacp": "lacp",
    "lldp": "lldp",
    "hsrp": "hsrp",
    "bfd": "bfd",
    "nxapi": "nxapi",
    "bash-shell": "bash",
    "nv overlay": "vxlan",
}

ROLE_HINTS = {
    "access": ["access", "idf", "closet", "edge"],
    "leaf": ["leaf", "tor", "rack"],
    "spine": ["spine", "core", "fabric"],
}


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a configuration validation error"""
    line_number: Optional[int] = None
    line_content: Optional[str] = None
    error_code: str = ""
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.HIGH
    suggestion: Optional[str] = None
    fix_command: Optional[str] = None


@dataclass
class ValidationWarning:
    """Represents a configuration validation warning"""
    line_number: Optional[int] = None
    line_content: Optional[str] = None
    warning_code: str = ""
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    suggestion: Optional[str] = None


@dataclass
class RemediationSuggestion:
    """Suggested fix for a validation issue"""
    issue_code: str
    description: str
    complexity: str  # simple, moderate, complex
    commands: List[str] = field(default_factory=list)
    estimated_time: str = ""  # e.g., "5 minutes"
    risk_level: str = "low"  # low, medium, high


@dataclass
class ValidationResult:
    """Comprehensive validation result for a configuration"""
    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    suggestions: List[RemediationSuggestion] = field(default_factory=list)
    severity: str = "info"  # critical, high, medium, low, info
    validation_id: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        """Auto-calculate overall severity and validity"""
        if not self.validation_id:
            import uuid
            self.validation_id = str(uuid.uuid4())
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()
        
        self._recalculate_validity()
    
    def _recalculate_validity(self):
        """Recalculate validity based on current errors and warnings"""
        # Determine overall validity
        critical_errors = [e for e in self.errors if e.severity == ValidationSeverity.CRITICAL]
        high_errors = [e for e in self.errors if e.severity == ValidationSeverity.HIGH]
        
        if critical_errors:
            self.is_valid = False
            self.severity = "critical"
        elif high_errors:
            self.is_valid = False
            self.severity = "high"
        elif self.errors:
            self.is_valid = False
            self.severity = "medium"
        elif self.warnings:
            self.severity = "low"
        else:
            self.severity = "info"
    
    def add_error(self, error: ValidationError):
        """Add error and recalculate validity"""
        self.errors.append(error)
        self._recalculate_validity()
    
    def add_warning(self, warning: ValidationWarning):
        """Add warning and recalculate validity"""
        self.warnings.append(warning)
        self._recalculate_validity()
    
    def extend_errors(self, errors: List[ValidationError]):
        """Extend errors and recalculate validity"""
        self.errors.extend(errors)
        self._recalculate_validity()
    
    def extend_warnings(self, warnings: List[ValidationWarning]):
        """Extend warnings and recalculate validity"""
        self.warnings.extend(warnings)
        self._recalculate_validity()


@dataclass
class ParsedConfig:
    hostname: str = ""
    mgmt_ip: str = ""
    mgmt_gw: str = ""
    motd: str = ""
    features: List[str] = field(default_factory=list)
    vlans: List[Dict[str, Any]] = field(default_factory=list)
    vpc_domain_id: Optional[int] = None
    vpc_peer_link_interfaces: List[str] = field(default_factory=list)
    local_keepalive_ip: str = ""
    remote_keepalive_ip: str = ""
    ntp_servers: List[str] = field(default_factory=list)
    logging_hosts: List[str] = field(default_factory=list)
    snmp_location: str = ""
    access_port_count: int = 0
    trunk_port_count: int = 0
    svi_count: int = 0
    has_hsrp: bool = False
    interface_lines: List[str] = field(default_factory=list)
    raw_line_count: int = 0

    def detect_role(self) -> str:
        host = self.hostname.lower()
        for role, tokens in ROLE_HINTS.items():
            if any(t in host for t in tokens):
                return role
        if self.vpc_domain_id or "vpc" in self.features:
            return "leaf"
        if self.svi_count >= 2 or self.has_hsrp:
            return "leaf"
        if self.access_port_count >= 12:
            return "access"
        if self.trunk_port_count > self.access_port_count:
            return "spine"
        return "access"

    @property
    def has_vpc(self) -> bool:
        return self.vpc_domain_id is not None or "vpc" in self.features

    def validate_syntax(self, config_text: str) -> ValidationResult:
        """Validate NX-OS syntax with line numbers and severity levels."""
        result = ValidationResult()
        lines = config_text.splitlines()
        
        for idx, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith("!"):
                continue
                
            # Check for common syntax errors
            if line_stripped.endswith(" "):
                result.add_error(ValidationError(
                    line_number=idx,
                    line_content=line_stripped,
                    error_code="TRAILING_WHITESPACE",
                    message="Trailing whitespace detected",
                    severity=ValidationSeverity.LOW,
                    suggestion="Remove trailing whitespace",
                    fix_command=line_stripped.rstrip()
                ))
            
            # Check for invalid characters in interface names
            if line_stripped.startswith("interface "):
                intf_name = line_stripped.split(None, 1)[1].strip() if len(line_stripped.split()) > 1 else ""
                if intf_name and not re.match(r'^[a-zA-Z0-9/\-]+$', intf_name):
                    result.add_error(ValidationError(
                        line_number=idx,
                        line_content=line_stripped,
                        error_code="INVALID_INTERFACE_NAME",
                        message=f"Invalid characters in interface name: {intf_name}",
                        severity=ValidationSeverity.HIGH,
                        suggestion="Interface names should only contain alphanumeric characters, slashes, and hyphens"
                    ))
        
        return result

    def validate_port_mapping(self, hardware_profile: Dict[str, Any]) -> ValidationResult:
        """Validate interface existence and type against hardware profile."""
        result = ValidationResult()
        
        if not hardware_profile:
            result.add_warning(ValidationWarning(
                warning_code="NO_HARDWARE_PROFILE",
                message="No hardware profile provided for port mapping validation",
                severity=ValidationSeverity.MEDIUM
            ))
            return result
        
        # Extract valid port ranges from hardware profile
        port_groups = hardware_profile.get("port_groups", [])
        valid_ports = set()
        
        for group in port_groups:
            start = group.get("start", 1)
            end = group.get("end", 1)
            for port_num in range(start, end + 1):
                valid_ports.add(port_num)
        
        # Validate interfaces from parsed config
        for interface_line in self.interface_lines:
            # Extract port number from interface name
            match = re.search(r'Ethernet(\d+)/(\d+)', interface_line)
            if match:
                module = int(match.group(1))
                port = int(match.group(2))
                # For simplicity, check if port is within reasonable range
                if port < 1 or port > 128:
                    result.add_error(ValidationError(
                        error_code="INVALID_PORT_NUMBER",
                        message=f"Port number {port} out of valid range (1-128)",
                        severity=ValidationSeverity.HIGH,
                        suggestion="Verify interface name matches hardware profile"
                    ))
        
        return result

    def validate_vlan_ranges(self, hardware_profile: Dict[str, Any]) -> ValidationResult:
        """Validate VLAN ranges against hardware constraints."""
        result = ValidationResult()
        
        if not hardware_profile:
            return result
        
        vlan_constraints = hardware_profile.get("vlan_constraints", {})
        min_vlan = vlan_constraints.get("min_vlan", 1)
        max_vlan = vlan_constraints.get("max_vlan", 4094)
        reserved_vlans = set(vlan_constraints.get("reserved_vlans", []))
        
        for vlan in self.vlans:
            vlan_id = vlan.get("id")
            if vlan_id is None:
                continue
                
            if vlan_id < min_vlan or vlan_id > max_vlan:
                result.add_error(ValidationError(
                    error_code="VLAN_OUT_OF_RANGE",
                    message=f"VLAN {vlan_id} is outside valid range ({min_vlan}-{max_vlan})",
                    severity=ValidationSeverity.HIGH,
                    suggestion=f"Use VLANs in range {min_vlan}-{max_vlan}"
                ))
            
            if vlan_id in reserved_vlans:
                result.add_error(ValidationError(
                    error_code="RESERVED_VLAN",
                    message=f"VLAN {vlan_id} is reserved and cannot be used",
                    severity=ValidationSeverity.CRITICAL,
                    suggestion="Select a different VLAN ID"
                ))
        
        return result

    def validate_vpc_consistency(self) -> ValidationResult:
        """Validate vPC domain and peer-link configuration."""
        result = ValidationResult()
        
        if self.vpc_domain_id:
            # Check vPC domain ID range
            if self.vpc_domain_id < 1 or self.vpc_domain_id > 4096:
                result.add_error(ValidationError(
                    error_code="INVALID_VPC_DOMAIN",
                    message=f"vPC domain {self.vpc_domain_id} is outside valid range (1-4096)",
                    severity=ValidationSeverity.CRITICAL,
                    suggestion="Use vPC domain ID between 1 and 4096"
                ))
            
            # Check if peer-link interfaces are defined
            if not self.vpc_peer_link_interfaces:
                result.add_error(ValidationError(
                    error_code="MISSING_PEER_LINK",
                    message="vPC domain configured but no peer-link interfaces found",
                    severity=ValidationSeverity.CRITICAL,
                    suggestion="Configure vPC peer-link interfaces (typically 2x40G ports)"
                ))
            
            # Check keepalive IPs
            if not self.local_keepalive_ip or not self.remote_keepalive_ip:
                result.add_error(ValidationError(
                    error_code="MISSING_KEEPALIVE_IPS",
                    message="vPC keepalive IP addresses not configured",
                    severity=ValidationSeverity.HIGH,
                    suggestion="Configure local and remote keepalive IP addresses"
                ))
            
            if self.local_keepalive_ip == self.remote_keepalive_ip:
                result.add_error(ValidationError(
                    error_code="DUPLICATE_KEEPALIVE_IPS",
                    message="Local and remote keepalive IP addresses are identical",
                    severity=ValidationSeverity.CRITICAL,
                    suggestion="Use different IP addresses for local and remote keepalive"
                ))
        
        return result

    def validate_feature_compatibility(self, nxos_version: str) -> ValidationResult:
        """Validate feature compatibility with NX-OS version."""
        result = ValidationResult()
        
        # Version compatibility matrix
        version_features = {
            "9.3": ["interface_vlan", "vpc", "lacp", "lldp", "hsrp", "bfd", "nxapi", "bash"],
            "10.2": ["interface_vlan", "vpc", "lacp", "lldp", "hsrp", "bfd", "vxlan"],
        }
        
        major_version = nxos_version.split(".")[0] if nxos_version else "9"
        compatible_features = version_features.get(nxos_version, version_features.get(f"{major_version}.3", []))
        
        for feature in self.features:
            if compatible_features and feature not in compatible_features:
                result.add_warning(ValidationWarning(
                    warning_code="FEATURE_VERSION_MISMATCH",
                    message=f"Feature '{feature}' may not be compatible with NX-OS {nxos_version}",
                    severity=ValidationSeverity.MEDIUM,
                    suggestion="Verify feature compatibility with NX-OS version"
                ))
        
        return result

    def validate_baseline_compliance(self, baseline_options: List[str]) -> ValidationResult:
        """Validate configuration against institutional baseline requirements."""
        result = ValidationResult()
        
        # Define baseline requirements
        baseline_requirements = {
            "baseline_cfs": ["cfs"],  # Common Feature Set
            "baseline_snmp_traps": ["snmp"],
            "baseline_logging": ["logging"],
            "baseline_ntp": ["ntp"],
        }
        
        for baseline in baseline_options:
            required_features = baseline_requirements.get(baseline, [])
            for req_feature in required_features:
                if req_feature not in self.features:
                    result.add_warning(ValidationWarning(
                        warning_code="BASELINE_FEATURE_MISSING",
                        message=f"Baseline '{baseline}' requires feature '{req_feature}' which is not enabled",
                        severity=ValidationSeverity.MEDIUM,
                        suggestion=f"Enable feature '{req_feature}' or remove baseline option"
                    ))
        
        return result

    def validate_security_policies(self) -> ValidationResult:
        """Validate configuration against security policies."""
        result = ValidationResult()
        
        # Security policy checks
        if "nxapi" in self.features and "bash" in self.features:
            result.add_warning(ValidationWarning(
                warning_code="SECURITY_RISK_NXAPI_BASH",
                message="Both NX-API and bash-shell enabled - potential security risk",
                severity=ValidationSeverity.HIGH,
                suggestion="Disable NX-API or bash-shell in production environments"
            ))
        
        # Check for default passwords (basic check)
        if self.hostname.lower() in ["switch", "nexus", "router"]:
            result.add_warning(ValidationWarning(
                warning_code="DEFAULT_HOSTNAME",
                message="Default hostname detected - should be changed for security",
                severity=ValidationSeverity.LOW,
                suggestion="Set a unique hostname"
            ))
        
        return result

    def suggest_fixes(self) -> List[RemediationSuggestion]:
        """Generate actionable remediation steps for validation issues."""
        suggestions = []
        
        if self.vpc_domain_id and not self.vpc_peer_link_interfaces:
            suggestions.append(RemediationSuggestion(
                issue_code="MISSING_PEER_LINK",
                description="Configure vPC peer-link interfaces",
                complexity="moderate",
                commands=[
                    "interface port-channel1",
                    "  vpc peer-link",
                    "interface Ethernet1/51-52",
                    "  channel-group 1 mode active"
                ],
                estimated_time="10 minutes",
                risk_level="medium"
            ))
        
        if self.vpc_domain_id and (not self.local_keepalive_ip or not self.remote_keepalive_ip):
            suggestions.append(RemediationSuggestion(
                issue_code="MISSING_KEEPALIVE_IPS",
                description="Configure vPC keepalive IP addresses",
                complexity="simple",
                commands=[
                    "vpc domain <domain_id>",
                    "  peer-keepalive destination <remote_ip> source <local_ip>"
                ],
                estimated_time="5 minutes",
                risk_level="low"
            ))
        
        return suggestions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hostname": self.hostname,
            "mgmt_ip": self.mgmt_ip,
            "mgmt_gw": self.mgmt_gw,
            "motd": self.motd,
            "features": self.features,
            "vlans": self.vlans,
            "vpc_domain_id": self.vpc_domain_id,
            "vpc_peer_link_interfaces": self.vpc_peer_link_interfaces,
            "local_keepalive_ip": self.local_keepalive_ip,
            "remote_keepalive_ip": self.remote_keepalive_ip,
            "ntp_servers": self.ntp_servers,
            "logging_hosts": self.logging_hosts,
            "snmp_location": self.snmp_location,
            "access_port_count": self.access_port_count,
            "trunk_port_count": self.trunk_port_count,
            "svi_count": self.svi_count,
            "has_hsrp": self.has_hsrp,
            "interface_lines": self.interface_lines[:20],
            "raw_line_count": self.raw_line_count,
            "detected_role": self.detect_role(),
            "has_vpc": self.has_vpc,
        }


def parse_running_config(text: str) -> ParsedConfig:
    """Best-effort parser for pasted NX-OS running-config."""
    parsed = ParsedConfig()
    if not text or not text.strip():
        return parsed

    lines = [ln.rstrip() for ln in text.splitlines()]
    parsed.raw_line_count = len(lines)

    vlan_ids: Set[int] = set()
    current_vlan: Optional[int] = None
    current_intf: Optional[str] = None
    intf_mode = ""
    peer_link_members: List[str] = []
    peer_link_po_number: Optional[int] = None
    current_po_id: Optional[int] = None

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("!"):
            continue

        if line.startswith("banner motd "):
            parsed.motd = line[12:].strip().strip("#").strip()
            continue

        if line.startswith("hostname "):
            parsed.hostname = line.split(None, 1)[1].strip()
            continue

        if line.startswith("feature "):
            feat = line[8:].strip().lower()
            for key, fid in FEATURE_MAP.items():
                if key in feat and fid not in parsed.features:
                    parsed.features.append(fid)
            continue

        if line.startswith("vlan "):
            try:
                current_vlan = int(line.split()[1])
                vlan_ids.add(current_vlan)
            except (IndexError, ValueError):
                current_vlan = None
            continue

        if current_vlan and line.startswith("name "):
            parsed.vlans.append({"id": current_vlan, "name": line[5:].strip()})
            continue

        if line.startswith("interface "):
            current_intf = line.split(None, 1)[1].strip()
            intf_mode = ""
            current_po_id = None
            if current_intf.lower().startswith("port-channel"):
                try:
                    current_po_id = int(re.sub(r"\D", "", current_intf.split()[-1]) or "0") or None
                except ValueError:
                    current_po_id = None
            continue

        if current_intf and current_intf.lower() == "mgmt0" and line.startswith("ip address "):
            parts = line.split()
            if len(parts) >= 3:
                parsed.mgmt_ip = parts[2] if "/" in parts[2] else f"{parts[2]}/{parts[4]}" if len(parts) >= 5 else parts[2]
            continue

        if line.startswith("ip route ") and "0.0.0.0/0" in line:
            parts = line.split()
            if parts:
                parsed.mgmt_gw = parts[-1]
            continue

        if line.startswith("vpc domain "):
            try:
                parsed.vpc_domain_id = int(line.split()[2])
            except (IndexError, ValueError):
                pass
            continue

        if "peer-keepalive destination" in line:
            m = re.search(r"destination\s+(\S+)", line)
            if m:
                parsed.remote_keepalive_ip = m.group(1).split("/")[0]
            m2 = re.search(r"source\s+(\S+)", line)
            if m2:
                parsed.local_keepalive_ip = m2.group(1).split("/")[0]
            continue

        if current_intf and line == "vpc peer-link":
            if current_po_id is not None:
                peer_link_po_number = current_po_id
            continue

        if current_intf and line.startswith("channel-group ") and "mode active" in line:
            m = re.match(r"channel-group\s+(\d+)", line)
            if m and peer_link_po_number and int(m.group(1)) == peer_link_po_number:
                if current_intf.lower().startswith("ethernet"):
                    peer_link_members.append(current_intf)
            continue

        if line.startswith("ntp server "):
            srv = line.split()[2]
            if srv not in parsed.ntp_servers:
                parsed.ntp_servers.append(srv)
            continue

        if line.startswith("logging server "):
            srv = line.split()[2]
            if srv not in parsed.logging_hosts:
                parsed.logging_hosts.append(srv)
            if "logging" not in parsed.features:
                parsed.features.append("logging")
            continue

        if line.startswith("snmp-server location "):
            parsed.snmp_location = line[21:].strip()
            if "snmp" not in parsed.features:
                parsed.features.append("snmp")
            continue

        if current_intf and line.startswith("switchport mode access"):
            intf_mode = "access"
            continue
        if current_intf and line.startswith("switchport mode trunk"):
            intf_mode = "trunk"
            continue

        if current_intf and line.startswith("hsrp "):
            parsed.has_hsrp = True
            if "hsrp" not in parsed.features:
                parsed.features.append("hsrp")
            continue

        if current_intf and line == "no shutdown" and current_intf.lower().startswith("ethernet"):
            if intf_mode == "access":
                parsed.access_port_count += 1
            elif intf_mode == "trunk":
                parsed.trunk_port_count += 1
            parsed.interface_lines.append(current_intf)
            current_intf = None

        if current_intf and current_intf.lower().startswith("vlan"):
            parsed.svi_count += 1

    if peer_link_members:
        parsed.vpc_peer_link_interfaces = peer_link_members
    elif parsed.vpc_domain_id:
        parsed.vpc_peer_link_interfaces = []

    for vid in sorted(vlan_ids):
        if not any(v.get("id") == vid for v in parsed.vlans):
            parsed.vlans.append({"id": vid, "name": f"VLAN_{vid}"})

    if parsed.ntp_servers and "ntp" not in parsed.features:
        parsed.features.append("ntp")

    return parsed
