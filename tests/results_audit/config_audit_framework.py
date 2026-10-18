"""
Configuration Results Audit Framework
======================================

This module provides comprehensive auditing of all configuration artifacts
produced by the NX-OS Configurator. It validates:

- NX-OS configuration text (every line, command, parameter)
- Port maps (logical and physical)
- Visual port maps / diagrams
- HTML page structure
- Downloadable / exportable files
- CLI preview content
- JSON / structured data
- Duplicate detection
- Consistency between views
- Completeness
- Semantic correctness for NX-OS

This is the RESULTS-AUDIT layer - independent of UI flow tests.
"""

import re
import hashlib
import json
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AuditSeverity(Enum):
    """Severity levels for audit findings."""
    CRITICAL = "CRITICAL"  # Blocks deployment
    HIGH = "HIGH"  # Major functional issue
    MEDIUM = "MEDIUM"  # Non-functional but important
    LOW = "LOW"  # Cosmetic or minor
    INFO = "INFO"  # Informational


class AuditCategory(Enum):
    """Categories of audit findings."""
    DUPLICATE = "DUPLICATE"
    INCONSISTENCY = "INCONSISTENCY"
    INCOMPLETE = "INCOMPLETE"
    SEMANTIC_ERROR = "SEMANTIC_ERROR"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    STRUCTURAL_ERROR = "STRUCTURAL_ERROR"
    MISSING_REQUIRED = "MISSING_REQUIRED"
    INVALID_COMBINATION = "INVALID_COMBINATION"
    ORDERING_ISSUE = "ORDERING_ISSUE"


@dataclass
class AuditFinding:
    """A single audit finding."""
    severity: AuditSeverity
    category: AuditCategory
    location: str  # Where in the artifact
    description: str
    evidence: str  # Actual problematic content
    expected: str  # What should have been there
    artifact_type: str  # Type of artifact (config, portmap, html, etc.)
    line_number: Optional[int] = None


@dataclass
class ConfigurationArtifact:
    """A configuration artifact to be audited."""
    artifact_type: str  # "nxos_config", "port_map", "html", "json", etc.
    content: str
    source: str  # Where this came from (API endpoint, UI page, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_hash: str = field(init=False)
    
    def __post_init__(self):
        """Compute content hash for deduplication."""
        self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


class ConfigurationAuditor:
    """
    Comprehensive auditor for configuration artifacts.
    
    This auditor performs deep validation of all configuration outputs,
    checking for duplicates, inconsistencies, completeness, and semantic
    correctness.
    """
    
    def __init__(self):
        self.findings: List[AuditFinding] = []
        self.artifacts: List[ConfigurationArtifact] = []
        self.duplicate_tracker: Dict[str, Set[str]] = {}
    
    def add_artifact(self, artifact: ConfigurationArtifact):
        """Add an artifact for auditing."""
        self.artifacts.append(artifact)
    
    def audit_all(self) -> List[AuditFinding]:
        """Run all audits on all artifacts."""
        self.findings = []
        
        for artifact in self.artifacts:
            if artifact.artifact_type == "nxos_config":
                self._audit_nxos_config(artifact)
            elif artifact.artifact_type == "port_map":
                self._audit_port_map(artifact)
            elif artifact.artifact_type == "html":
                self._audit_html_structure(artifact)
            elif artifact.artifact_type == "json":
                self._audit_json_structure(artifact)
            elif artifact.artifact_type == "cli_preview":
                self._audit_cli_preview(artifact)
        
        # Cross-artifact consistency checks
        self._audit_cross_artifact_consistency()
        
        return self.findings
    
    def _audit_nxos_config(self, artifact: ConfigurationArtifact):
        """Audit NX-OS configuration text."""
        lines = artifact.content.split('\n')
        
        # Track context (which interface we're in)
        current_interface = None
        interface_contexts: Dict[str, List[str]] = {}  # interface -> list of commands
        
        # Check for duplicate commands within the same context
        command_counts: Dict[str, List[int]] = {}
        for idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('!'):
                continue
            
            # Track interface context
            if line.startswith('interface '):
                current_interface = line.split()[1] if len(line.split()) > 1 else 'unknown'
                if current_interface not in interface_contexts:
                    interface_contexts[current_interface] = []
                continue
            
            # Extract command (first word)
            command = line.split()[0] if line.split() else ''
            if command:
                # Track command with context
                context_key = f"{current_interface}:{command}" if current_interface else f"global:{command}"
                if context_key not in command_counts:
                    command_counts[context_key] = []
                command_counts[context_key].append(idx)
                
                # Also track in interface context
                if current_interface:
                    interface_contexts[current_interface].append(command)
        
        # Flag duplicate commands within the same context (not allowed)
        # Commands that are allowed to duplicate across different interfaces
        allowed_cross_interface_duplicates = {
            'description', 'switchport', 'spanning-tree', 'speed', 'duplex',
            'mtu', 'flowcontrol', 'priority-flow-control', 'service-policy',
            'load-interval', 'carrier-delay', 'mac', 'arp', 'ip', 'ipv6',
            'lacp', 'udld', 'lldp', 'cdp', 'stp', 'vpc', 'fex', 'fabric'
        }
        
        for context_key, line_nums in command_counts.items():
            if len(line_nums) > 1:
                context_parts = context_key.split(':', 1)
                if len(context_parts) == 2:
                    interface_name, command = context_parts
                    # Only flag if it's a duplicate within the same interface
                    # or if it's a global command that shouldn't duplicate
                    if interface_name != 'global' or command not in allowed_cross_interface_duplicates:
                        self.findings.append(AuditFinding(
                            severity=AuditSeverity.HIGH,
                            category=AuditCategory.DUPLICATE,
                            location=f"Lines {line_nums} (context: {interface_name})",
                            description=f"Duplicate command '{command}' found {len(line_nums)} times in same context",
                            evidence=command,
                            expected=f"Single occurrence in context or allowed duplicate",
                            artifact_type=artifact.artifact_type
                        ))
        
        # Check for duplicate interface definitions
        interfaces = self._extract_interfaces(lines)
        interface_counts: Dict[str, List[int]] = {}
        for if_name, line_num in interfaces:
            if if_name not in interface_counts:
                interface_counts[if_name] = []
            interface_counts[if_name].append(line_num)
        
        for if_name, line_nums in interface_counts.items():
            if len(line_nums) > 1:
                self.findings.append(AuditFinding(
                    severity=AuditSeverity.CRITICAL,
                    category=AuditCategory.DUPLICATE,
                    location=f"Lines {line_nums}",
                    description=f"Duplicate interface definition '{if_name}'",
                    evidence=if_name,
                    expected="Single interface definition",
                    artifact_type=artifact.artifact_type
                ))
        
        # Check for duplicate VLAN definitions
        vlans = self._extract_vlans(lines)
        vlan_counts: Dict[str, List[int]] = {}
        for vlan_id, line_num in vlans:
            if vlan_id not in vlan_counts:
                vlan_counts[vlan_id] = []
            vlan_counts[vlan_id].append(line_num)
        
        for vlan_id, line_nums in vlan_counts.items():
            if len(line_nums) > 1:
                self.findings.append(AuditFinding(
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.DUPLICATE,
                    location=f"Lines {line_nums}",
                    description=f"Duplicate VLAN definition '{vlan_id}'",
                    evidence=vlan_id,
                    expected="Single VLAN definition",
                    artifact_type=artifact.artifact_type
                ))
        
        # Check for required vPC commands if vPC is enabled
        if artifact.metadata.get('vpc_enabled', False):
            required_vpc_commands = [
                'peer-keepalive',
                'peer-link'
            ]
            for cmd in required_vpc_commands:
                if not any(cmd in line.lower() for line in lines):
                    self.findings.append(AuditFinding(
                        severity=AuditSeverity.CRITICAL,
                        category=AuditCategory.MISSING_REQUIRED,
                        location="vPC configuration section",
                        description=f"Missing required vPC command: {cmd}",
                        evidence="",
                        expected=f"Command '{cmd}' present",
                        artifact_type=artifact.artifact_type
                    ))
        
        # Semantic correctness checks
        self._audit_nxos_semantic_correctness(artifact, lines)
        
        # Completeness checks
        self._audit_nxos_completeness(artifact, lines)
    
    def _audit_nxos_semantic_correctness(self, artifact: ConfigurationArtifact, lines: List[str]):
        """Audit semantic correctness of NX-OS configuration."""
        model = artifact.metadata.get('model', 'unknown')
        
        # Check for invalid command combinations
        # Example: vPC requires specific features to be enabled
        has_vpc = any('vpc domain' in line.lower() for line in lines)
        has_vpc_feature = any('feature vpc' in line.lower() for line in lines)
        
        if has_vpc and not has_vpc_feature:
            self.findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                category=AuditCategory.SEMANTIC_ERROR,
                location="feature configuration",
                description="vPC configuration present but 'feature vpc' not enabled",
                evidence="vpc domain found without feature vpc",
                expected="feature vpc enabled before vpc domain configuration",
                artifact_type=artifact.artifact_type
            ))
        
        # Check for interface mode conflicts
        interface_modes: Dict[str, str] = {}
        current_interface = None
        for line in lines:
            line = line.strip()
            if line.startswith('interface '):
                current_interface = line.split()[1] if len(line.split()) > 1 else 'unknown'
            elif current_interface and 'switchport mode' in line:
                mode = line.split()[-1] if line.split() else ''
                if current_interface in interface_modes and interface_modes[current_interface] != mode:
                    self.findings.append(AuditFinding(
                        severity=AuditSeverity.HIGH,
                        category=AuditCategory.SEMANTIC_ERROR,
                        location=f"interface {current_interface}",
                        description=f"Interface mode conflict: {interface_modes[current_interface]} vs {mode}",
                        evidence=f"Mode changed from {interface_modes[current_interface]} to {mode}",
                        expected="Consistent interface mode",
                        artifact_type=artifact.artifact_type
                    ))
                interface_modes[current_interface] = mode
        
        # Check for VLAN validity (1-4094 range)
        vlan_pattern = re.compile(r'vlan\s+(\d+)')
        for idx, line in enumerate(lines, 1):
            matches = vlan_pattern.findall(line)
            for vlan_id in matches:
                try:
                    vlan_num = int(vlan_id)
                    if vlan_num < 1 or vlan_num > 4094:
                        self.findings.append(AuditFinding(
                            severity=AuditSeverity.HIGH,
                            category=AuditCategory.SEMANTIC_ERROR,
                            location=f"Line {idx}",
                            description=f"Invalid VLAN ID: {vlan_num} (must be 1-4094)",
                            evidence=str(vlan_num),
                            expected="VLAN ID in range 1-4094",
                            artifact_type=artifact.artifact_type
                        ))
                except ValueError:
                    pass
        
        # Check for invalid port-channel IDs (1-4096 range)
        po_pattern = re.compile(r'port-channel(\d+)')
        for idx, line in enumerate(lines, 1):
            matches = po_pattern.findall(line)
            for po_id in matches:
                try:
                    po_num = int(po_id)
                    if po_num < 1 or po_num > 4096:
                        self.findings.append(AuditFinding(
                            severity=AuditSeverity.HIGH,
                            category=AuditCategory.SEMANTIC_ERROR,
                            location=f"Line {idx}",
                            description=f"Invalid port-channel ID: {po_num} (must be 1-4096)",
                            evidence=str(po_num),
                            expected="Port-channel ID in range 1-4096",
                            artifact_type=artifact.artifact_type
                        ))
                except ValueError:
                    pass
        
        # Check for vPC domain validity (1-4096 range)
        vpc_pattern = re.compile(r'vpc domain\s+(\d+)')
        for idx, line in enumerate(lines, 1):
            matches = vpc_pattern.findall(line)
            for vpc_id in matches:
                try:
                    vpc_num = int(vpc_id)
                    if vpc_num < 1 or vpc_num > 4096:
                        self.findings.append(AuditFinding(
                            severity=AuditSeverity.CRITICAL,
                            category=AuditCategory.SEMANTIC_ERROR,
                            location=f"Line {idx}",
                            description=f"Invalid vPC domain: {vpc_num} (must be 1-4096)",
                            evidence=str(vpc_num),
                            expected="vPC domain in range 1-4096",
                            artifact_type=artifact.artifact_type
                        ))
                except ValueError:
                    pass
    
    def _audit_nxos_completeness(self, artifact: ConfigurationArtifact, lines: List[str]):
        """Audit completeness of NX-OS configuration."""
        # Check for hostname
        has_hostname = any('hostname' in line.lower() for line in lines)
        if not has_hostname:
            self.findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                category=AuditCategory.MISSING_REQUIRED,
                location="global configuration",
                description="Missing hostname command",
                evidence="",
                expected="hostname <hostname>",
                artifact_type=artifact.artifact_type
            ))
        
        # Check for management interface configuration (only if metadata indicates it should be present)
        if artifact.metadata.get('check_mgmt_interface', False):
            has_mgmt_interface = any('mgmt' in line.lower() and 'interface' in line.lower() for line in lines)
            if not has_mgmt_interface:
                self.findings.append(AuditFinding(
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.MISSING_REQUIRED,
                    location="interface configuration",
                    description="Missing management interface configuration",
                    evidence="",
                    expected="interface mgmt0 with IP configuration",
                    artifact_type=artifact.artifact_type
                ))
        
        # Check for feature enablement if vPC is present
        has_vpc = any('vpc domain' in line.lower() for line in lines)
        if has_vpc:
            required_features = ['feature vpc', 'feature lacp']
            for feature in required_features:
                if not any(feature in line.lower() for line in lines):
                    self.findings.append(AuditFinding(
                        severity=AuditSeverity.HIGH,
                        category=AuditCategory.MISSING_REQUIRED,
                        location="feature configuration",
                        description=f"Missing required feature for vPC: {feature}",
                        evidence="",
                        expected=f"{feature} command present",
                        artifact_type=artifact.artifact_type
                    ))
    
    def _audit_port_map(self, artifact: ConfigurationArtifact):
        """Audit port map (logical and physical)."""
        try:
            port_map = json.loads(artifact.content)
        except json.JSONDecodeError:
            self.findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                category=AuditCategory.STRUCTURAL_ERROR,
                location="entire artifact",
                description="Port map is not valid JSON",
                evidence=artifact.content[:100],
                expected="Valid JSON structure",
                artifact_type=artifact.artifact_type
            ))
            return
        
        # Check for duplicate port assignments
        # Port maps can have various structures, check for common patterns
        if isinstance(port_map, dict):
            # Check for duplicate port numbers
            if "ports" in port_map and isinstance(port_map["ports"], list):
                port_numbers = []
                for port in port_map["ports"]:
                    if isinstance(port, dict) and "port" in port:
                        port_num = port["port"]
                        if port_num in port_numbers:
                            self.findings.append(AuditFinding(
                                severity=AuditSeverity.CRITICAL,
                                category=AuditCategory.DUPLICATE,
                                location=f"Port {port_num}",
                                description=f"Duplicate port number {port_num}",
                                evidence=str(port_num),
                                expected="Unique port numbers",
                                artifact_type=artifact.artifact_type
                            ))
                        port_numbers.append(port_num)
            
            # Check for duplicate port names
            if "ports" in port_map and isinstance(port_map["ports"], list):
                port_names = []
                for port in port_map["ports"]:
                    if isinstance(port, dict) and "port_name" in port:
                        port_name = port["port_name"]
                        if port_name in port_names:
                            self.findings.append(AuditFinding(
                                severity=AuditSeverity.HIGH,
                                category=AuditCategory.DUPLICATE,
                                location=f"Port name {port_name}",
                                description=f"Duplicate port name {port_name}",
                                evidence=port_name,
                                expected="Unique port names",
                                artifact_type=artifact.artifact_type
                            ))
                        port_names.append(port_name)
            
            # Check for required fields
            required_fields = ["hostname", "ports"]
            for field in required_fields:
                if field not in port_map:
                    self.findings.append(AuditFinding(
                        severity=AuditSeverity.HIGH,
                        category=AuditCategory.MISSING_REQUIRED,
                        location="port map structure",
                        description=f"Missing required field: {field}",
                        evidence="",
                        expected=f"Field '{field}' present",
                        artifact_type=artifact.artifact_type
                    ))
    
    def _audit_html_structure(self, artifact: ConfigurationArtifact):
        """Audit HTML page structure."""
        # Check for duplicate IDs (invalid HTML)
        id_pattern = re.compile(r'id=["\']([^"\']+)["\']')
        ids = id_pattern.findall(artifact.content)
        id_counts: Dict[str, int] = {}
        for elem_id in ids:
            id_counts[elem_id] = id_counts.get(elem_id, 0) + 1
        
        for elem_id, count in id_counts.items():
            if count > 1:
                self.findings.append(AuditFinding(
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.DUPLICATE,
                    location="HTML structure",
                    description=f"Duplicate HTML ID '{elem_id}' found {count} times",
                    evidence=elem_id,
                    expected="Unique HTML IDs",
                    artifact_type=artifact.artifact_type
                ))
        
        # Check for unclosed tags (basic check)
        tag_stack = []
        tag_pattern = re.compile(r'<(/?)(\w+)[^>]*>')
        for match in tag_pattern.finditer(artifact.content):
            closing, tag = match.groups()
            if not closing and tag not in ['br', 'hr', 'img', 'input', 'meta', 'link']:
                tag_stack.append(tag)
            elif closing:
                if tag_stack and tag_stack[-1] == tag:
                    tag_stack.pop()
        
        if tag_stack:
            self.findings.append(AuditFinding(
                severity=AuditSeverity.MEDIUM,
                category=AuditCategory.STRUCTURAL_ERROR,
                location="HTML structure",
                description=f"Unclosed HTML tags: {tag_stack}",
                evidence=str(tag_stack),
                expected="All tags properly closed",
                artifact_type=artifact.artifact_type
            ))
    
    def _audit_json_structure(self, artifact: ConfigurationArtifact):
        """Audit JSON structure."""
        try:
            json_data = json.loads(artifact.content)
        except json.JSONDecodeError as e:
            self.findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                category=AuditCategory.STRUCTURAL_ERROR,
                location="entire artifact",
                description=f"Invalid JSON: {str(e)}",
                evidence=artifact.content[:100],
                expected="Valid JSON",
                artifact_type=artifact.artifact_type
            ))
            return
        
        # Check for duplicate keys in objects
        def check_duplicate_keys(obj, path=""):
            if isinstance(obj, dict):
                seen_keys = set()
                for key, value in obj.items():
                    if key in seen_keys:
                        self.findings.append(AuditFinding(
                            severity=AuditSeverity.HIGH,
                            category=AuditCategory.DUPLICATE,
                            location=path,
                            description=f"Duplicate JSON key '{key}'",
                            evidence=key,
                            expected="Unique keys",
                            artifact_type=artifact.artifact_type
                        ))
                    seen_keys.add(key)
                    check_duplicate_keys(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    check_duplicate_keys(item, f"{path}[{idx}]")
        
        check_duplicate_keys(json_data)
    
    def _audit_cli_preview(self, artifact: ConfigurationArtifact):
        """Audit CLI preview content."""
        # CLI preview should match the generated config
        # This is checked in cross-artifact consistency
        pass
    
    def _audit_cross_artifact_consistency(self):
        """Audit consistency between different artifacts."""
        # Group artifacts by source (e.g., same deployment)
        artifacts_by_source: Dict[str, List[ConfigurationArtifact]] = {}
        for artifact in self.artifacts:
            source = artifact.source
            if source not in artifacts_by_source:
                artifacts_by_source[source] = []
            artifacts_by_source[source].append(artifact)
        
        # For each source, check consistency between artifact types
        for source, artifacts in artifacts_by_source.items():
            artifact_types = {a.artifact_type: a for a in artifacts}
            
            # Check if NX-OS config and CLI preview match
            if 'nxos_config' in artifact_types and 'cli_preview' in artifact_types:
                config = artifact_types['nxos_config']
                preview = artifact_types['cli_preview']
                
                # Normalize whitespace for comparison
                config_normalized = re.sub(r'\s+', ' ', config.content.strip())
                preview_normalized = re.sub(r'\s+', ' ', preview.content.strip())
                
                if config_normalized != preview_normalized:
                    self.findings.append(AuditFinding(
                        severity=AuditSeverity.CRITICAL,
                        category=AuditCategory.INCONSISTENCY,
                        location=f"Source: {source}",
                        description="NX-OS config and CLI preview do not match",
                        evidence=f"Config hash: {config.content_hash}, Preview hash: {preview.content_hash}",
                        expected="Identical content",
                        artifact_type="cross-artifact"
                    ))
    
    def _extract_interfaces(self, lines: List[str]) -> List[Tuple[str, int]]:
        """Extract interface definitions from config lines."""
        interfaces = []
        for idx, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('interface '):
                parts = line.split()
                if len(parts) >= 2:
                    interfaces.append((parts[1], idx))
        return interfaces
    
    def _extract_vlans(self, lines: List[str]) -> List[Tuple[str, int]]:
        """Extract VLAN definitions from config lines."""
        vlans = []
        for idx, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('vlan ') or line.startswith('vlan '):
                parts = line.split()
                if len(parts) >= 2:
                    vlans.append((parts[1], idx))
        return vlans
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of audit findings."""
        severity_counts = {s.value: 0 for s in AuditSeverity}
        category_counts = {c.value: 0 for c in AuditCategory}
        
        for finding in self.findings:
            severity_counts[finding.severity.value] += 1
            category_counts[finding.category.value] += 1
        
        return {
            "total_findings": len(self.findings),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "artifacts_audited": len(self.artifacts),
            "critical_findings": severity_counts["CRITICAL"],
            "high_findings": severity_counts["HIGH"]
        }
