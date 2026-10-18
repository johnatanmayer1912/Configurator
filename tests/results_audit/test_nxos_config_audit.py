"""
Results-Audit Tests: NX-OS Configuration Validation
===================================================

These tests perform deep auditing of generated NX-OS configurations,
checking for duplicates, inconsistencies, completeness, and semantic correctness.

This is the RESULTS-AUDIT layer - independent of UI flow tests.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from tests.results_audit.config_audit_framework import (
    ConfigurationAuditor,
    ConfigurationArtifact,
    AuditSeverity,
    AuditCategory
)
import json


client = TestClient(app)


class TestNXOSConfigAudit:
    """Audit tests for NX-OS configuration outputs."""
    
    def test_duplicate_interface_detection(self):
        """
        RESULTS-AUDIT: Detect duplicate interface definitions in generated config.
        
        This test deliberately generates a config with duplicate interfaces
        and verifies the auditor catches them.
        """
        # Deliberately create a config with duplicate interfaces
        config_with_duplicates = """
hostname TEST-SWITCH
feature lacp
feature lldp
interface Ethernet1/1
  description Server Port
  switchport access vlan 100
interface Ethernet1/1
  description Duplicate Port
  switchport access vlan 200
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config_with_duplicates,
            source="test_duplicate_detection",
            metadata={"hostname": "TEST-SWITCH"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify duplicate interface was detected
        duplicate_findings = [f for f in findings if f.category == AuditCategory.DUPLICATE and "interface" in f.description.lower()]
        assert len(duplicate_findings) > 0, "AUDIT FAILURE: Duplicate interface not detected"
        assert any(f.severity == AuditSeverity.CRITICAL for f in duplicate_findings), "AUDIT FAILURE: Duplicate interface not marked as CRITICAL"
    
    def test_duplicate_vlan_detection(self):
        """
        RESULTS-AUDIT: Detect duplicate VLAN definitions in generated config.
        
        This test deliberately generates a config with duplicate VLANs
        and verifies the auditor catches them.
        """
        config_with_duplicate_vlans = """
hostname TEST-SWITCH
vlan 100
  name Data
vlan 100
  name Duplicate-Data
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config_with_duplicate_vlans,
            source="test_duplicate_detection",
            metadata={"hostname": "TEST-SWITCH"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify duplicate VLAN was detected
        duplicate_findings = [f for f in findings if f.category == AuditCategory.DUPLICATE and "vlan" in f.description.lower()]
        assert len(duplicate_findings) > 0, "AUDIT FAILURE: Duplicate VLAN not detected"
    
    def test_missing_vpc_commands(self):
        """
        RESULTS-AUDIT: Detect missing required vPC commands.
        
        This test verifies that when vPC is enabled, all required commands
        are present in the generated configuration.
        """
        config_missing_vpc = """
hostname TEST-SWITCH
feature vpc
vpc domain 100
  role priority 100
  peer-keepalive destination 10.10.10.2
  peer-link port-channel1
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config_missing_vpc,
            source="test_missing_required",
            metadata={"hostname": "TEST-SWITCH", "vpc_enabled": True}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # This config actually has the required commands, so should pass
        # Let's test a config that's actually missing commands
        config_really_missing = """
hostname TEST-SWITCH
feature vpc
vpc domain 100
  role priority 100
"""
        
        artifact2 = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config_really_missing,
            source="test_missing_required",
            metadata={"hostname": "TEST-SWITCH", "vpc_enabled": True}
        )
        
        auditor2 = ConfigurationAuditor()
        auditor2.add_artifact(artifact2)
        findings2 = auditor2.audit_all()
        
        # Verify missing vPC commands were detected
        missing_findings = [f for f in findings2 if f.category == AuditCategory.MISSING_REQUIRED]
        assert len(missing_findings) > 0, "AUDIT FAILURE: Missing vPC commands not detected"
        
        # Check for specific missing commands
        missing_descriptions = [f.description for f in missing_findings]
        assert any("peer-keepalive" in desc.lower() for desc in missing_descriptions), "AUDIT FAILURE: Missing peer-keepalive not detected"
        assert any("peer-link" in desc.lower() for desc in missing_descriptions), "AUDIT FAILURE: Missing peer-link not detected"
    
    def test_real_deployment_config_audit(self):
        """
        RESULTS-AUDIT: Audit a real deployment configuration from the API.
        
        This test calls the actual API, generates a configuration, and audits
        the result for errors, duplicates, and completeness.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "AUDIT-TEST-01",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "TEST",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "base_access_vlan": 100,  # Use valid VLAN range
                    "access_vlan_count": 4,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_tor"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"API call failed: {response.text}"
        
        result = response.json()
        assert "results" in result, "No results in response"
        assert len(result["results"]) > 0, "No switches in results"
        
        # Extract the generated configuration
        switch_result = result["results"][0]
        assert "device_config" in switch_result, "No device_config in result"
        
        # Debug: print the device_config structure
        print(f"\n=== DEVICE_CONFIG STRUCTURE ===")
        print(json.dumps(switch_result["device_config"], indent=2))
        
        # Check for config in different possible locations
        config = None
        if "config" in switch_result["device_config"]:
            config = switch_result["device_config"]["config"]
        elif "interfaces" in switch_result["device_config"]:
            # Build config from interfaces
            interfaces = switch_result["device_config"]["interfaces"]
            config_lines = [f"hostname {switch_result['hostname']}"]
            for iface in interfaces:
                # Try different possible keys for interface name
                if_name = (iface.get('port_name') or 
                          iface.get('interface') or 
                          iface.get('name') or 
                          f"Ethernet1/{iface.get('port', 'Unknown')}")
                config_lines.append(f"interface {if_name}")
                if iface.get('description'):
                    config_lines.append(f"  description {iface['description']}")
                if iface.get('mode'):
                    config_lines.append(f"  switchport mode {iface['mode']}")
                if iface.get('vlan'):
                    config_lines.append(f"  switchport access vlan {iface['vlan']}")
            config = "\n".join(config_lines)
        
        # If still no config, try to use port_map
        if config is None and "port_map" in switch_result["device_config"]:
            port_map = switch_result["device_config"]["port_map"]
            if "ports" in port_map:
                config_lines = [f"hostname {switch_result['hostname']}"]
                for port in port_map["ports"]:
                    if_name = port.get('port_name', f"Ethernet1/{port.get('port', 'Unknown')}")
                    config_lines.append(f"interface {if_name}")
                    if port.get('description'):
                        config_lines.append(f"  description {port['description']}")
                    if port.get('mode'):
                        config_lines.append(f"  switchport mode {port['mode']}")
                    if port.get('vlan'):
                        config_lines.append(f"  switchport access vlan {port['vlan']}")
                config = "\n".join(config_lines)
        
        assert config is not None, "Could not extract config from device_config"
        
        # Audit the configuration
        artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config,
            source=f"generate_deployment:{switch_result['hostname']}",
            metadata={
                "hostname": switch_result["hostname"],
                "model": deployment_input["switches"][0]["model"],
                "vpc_enabled": False  # No vPC in this test
            }
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Get summary
        summary = auditor.get_summary()
        
        # Log results
        print(f"\n=== CONFIG AUDIT RESULTS FOR {switch_result['hostname']} ===")
        print(f"Total findings: {summary['total_findings']}")
        print(f"Critical findings: {summary['critical_findings']}")
        print(f"High findings: {summary['high_findings']}")
        
        for finding in findings:
            print(f"  [{finding.severity.value}] {finding.category.value}: {finding.description}")
            print(f"    Location: {finding.location}")
            print(f"    Evidence: {finding.evidence}")
        
        # Print the actual config for debugging
        print(f"\n=== GENERATED CONFIG ===")
        print(config)
        
        # Assert no critical or high findings (config should be clean)
        critical_findings = [f for f in findings if f.severity == AuditSeverity.CRITICAL]
        high_findings = [f for f in findings if f.severity == AuditSeverity.HIGH]
        
        assert len(critical_findings) == 0, f"AUDIT FAILURE: {len(critical_findings)} CRITICAL findings in generated config"
        assert len(high_findings) == 0, f"AUDIT FAILURE: {len(high_findings)} HIGH findings in generated config"
    
    def test_config_consistency_with_port_map(self):
        """
        RESULTS-AUDIT: Verify consistency between config and port map.
        
        This test generates both a config and port map, then verifies
        that interface assignments are consistent between them.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "CONSISTENCY-TEST-01",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "TEST",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "base_access_vlan": 100,  # Use valid VLAN range
                    "access_vlan_count": 4,
                    "interface_count": 0,  # Let system auto-assign
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf_tor"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        assert response.status_code == 200, f"API call failed: {response.text}"
        
        result = response.json()
        switch_result = result["results"][0]
        
        # Extract both config and port map
        config = None
        if "device_config" in switch_result:
            if "config" in switch_result["device_config"]:
                config = switch_result["device_config"]["config"]
            elif "interfaces" in switch_result["device_config"]:
                # Build config from interfaces
                interfaces = switch_result["device_config"]["interfaces"]
                config_lines = [f"hostname {switch_result['hostname']}"]
                for iface in interfaces:
                    config_lines.append(f"interface {iface.get('port_name', iface.get('port', 'Unknown'))}")
                    if iface.get('description'):
                        config_lines.append(f"  description {iface['description']}")
                    if iface.get('mode'):
                        config_lines.append(f"  switchport mode {iface['mode']}")
                    if iface.get('vlan'):
                        config_lines.append(f"  switchport access vlan {iface['vlan']}")
                config = "\n".join(config_lines)
        
        port_map = None
        if "device_config" in switch_result and "port_map" in switch_result["device_config"]:
            port_map = switch_result["device_config"]["port_map"]
        elif "port_map" in switch_result:
            port_map = switch_result["port_map"]
        
        assert config is not None, "Could not extract config"
        assert port_map is not None, "Could not extract port map"
        
        # Audit both artifacts
        config_artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config,
            source=f"generate_deployment:{switch_result['hostname']}",
            metadata={"hostname": switch_result["hostname"]}
        )
        
        port_map_artifact = ConfigurationArtifact(
            artifact_type="port_map",
            content=json.dumps(port_map),
            source=f"generate_deployment:{switch_result['hostname']}",
            metadata={"hostname": switch_result["hostname"]}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(config_artifact)
        auditor.add_artifact(port_map_artifact)
        findings = auditor.audit_all()
        
        # Check for consistency findings
        consistency_findings = [f for f in findings if f.category == AuditCategory.INCONSISTENCY]
        
        print(f"\n=== CONSISTENCY AUDIT RESULTS ===")
        print(f"Consistency findings: {len(consistency_findings)}")
        
        for finding in consistency_findings:
            print(f"  [{finding.severity.value}] {finding.description}")
        
        # Assert no critical inconsistencies
        critical_inconsistencies = [f for f in consistency_findings if f.severity == AuditSeverity.CRITICAL]
        assert len(critical_inconsistencies) == 0, f"AUDIT FAILURE: {len(critical_inconsistencies)} CRITICAL inconsistencies between config and port map"
    
    def test_semantic_correctness_vpc_without_feature(self):
        """
        RESULTS-AUDIT: Detect vPC configuration without feature vpc enabled.
        
        This test verifies that the auditor catches the semantic error of
        configuring vPC without enabling the vPC feature first.
        """
        config_semantic_error = """
hostname TEST-SWITCH
vpc domain 100
  role priority 100
  peer-keepalive destination 10.10.10.2
  peer-link port-channel1
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config_semantic_error,
            source="test_semantic_error",
            metadata={"hostname": "TEST-SWITCH", "model": "Nexus 93180YC-EX"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify semantic error was detected
        semantic_findings = [f for f in findings if f.category == AuditCategory.SEMANTIC_ERROR]
        assert len(semantic_findings) > 0, "AUDIT FAILURE: Semantic error not detected"
        
        # Check for specific error
        error_descriptions = [f.description for f in semantic_findings]
        assert any("feature vpc" in desc.lower() for desc in error_descriptions), "AUDIT FAILURE: Missing feature vpc not detected"
    
    def test_semantic_correctness_invalid_vlan(self):
        """
        RESULTS-AUDIT: Detect invalid VLAN IDs.
        
        This test verifies that the auditor catches VLAN IDs outside the valid range (1-4094).
        """
        config_invalid_vlan = """
hostname TEST-SWITCH
vlan 5000
  name Invalid-VLAN
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config_invalid_vlan,
            source="test_semantic_error",
            metadata={"hostname": "TEST-SWITCH", "model": "Nexus 93180YC-EX"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify semantic error was detected
        semantic_findings = [f for f in findings if f.category == AuditCategory.SEMANTIC_ERROR]
        assert len(semantic_findings) > 0, "AUDIT FAILURE: Invalid VLAN not detected"
        
        # Check for specific error
        error_descriptions = [f.description for f in semantic_findings]
        assert any("vlan" in desc.lower() and "invalid" in desc.lower() for desc in error_descriptions), "AUDIT FAILURE: Invalid VLAN error not detected"
    
    def test_completeness_missing_hostname(self):
        """
        RESULTS-AUDIT: Detect missing hostname in configuration.
        
        This test verifies that the auditor catches missing hostname command.
        """
        config_missing_hostname = """
feature lacp
feature lldp
interface Ethernet1/1
  description Server Port
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="nxos_config",
            content=config_missing_hostname,
            source="test_completeness",
            metadata={"hostname": "TEST-SWITCH", "model": "Nexus 93180YC-EX"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify missing hostname was detected
        missing_findings = [f for f in findings if f.category == AuditCategory.MISSING_REQUIRED]
        assert len(missing_findings) > 0, "AUDIT FAILURE: Missing hostname not detected"
        
        # Check for specific error
        error_descriptions = [f.description for f in missing_findings]
        assert any("hostname" in desc.lower() for desc in error_descriptions), "AUDIT FAILURE: Hostname error not detected"
