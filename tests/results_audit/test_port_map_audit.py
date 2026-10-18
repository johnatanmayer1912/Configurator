"""
Results-Audit Tests: Port Map Validation
========================================

These tests perform deep auditing of port maps and visual diagrams,
checking for duplicates, inconsistencies, completeness, and structural problems.

This is the RESULTS-AUDIT layer - independent of UI flow tests.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from tests.results_audit.config_audit_framework import (
    ConfigurationAuditor,
    ConfigurationArtifact,
    AuditSeverity
)
import json


client = TestClient(app)


class TestPortMapAudit:
    """Audit tests for port map outputs."""
    
    def test_duplicate_port_assignments(self):
        """
        RESULTS-AUDIT: Detect duplicate port assignments in port map.
        
        This test deliberately creates a port map with duplicate port numbers
        and verifies the auditor catches them.
        """
        port_map_with_duplicates = {
            "hostname": "TEST-SWITCH",
            "ports": [
                {"port": 1, "port_name": "Ethernet1/1", "type": "uplink"},
                {"port": 2, "port_name": "Ethernet1/2", "type": "uplink"},
                {"port": 1, "port_name": "Ethernet1/1", "type": "uplink"}  # Duplicate port number
            ]
        }
        
        artifact = ConfigurationArtifact(
            artifact_type="port_map",
            content=json.dumps(port_map_with_duplicates),
            source="test_duplicate_detection",
            metadata={"hostname": "TEST-SWITCH"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify duplicate port number was detected
        duplicate_findings = [f for f in findings if f.category.value == "DUPLICATE"]
        assert len(duplicate_findings) > 0, "AUDIT FAILURE: Duplicate port number not detected"
    
    def test_port_map_json_structure(self):
        """
        RESULTS-AUDIT: Validate port map JSON structure.
        
        This test verifies that the port map has valid JSON structure
        and required fields are present.
        """
        invalid_port_map = "{invalid json structure"
        
        artifact = ConfigurationArtifact(
            artifact_type="port_map",
            content=invalid_port_map,
            source="test_json_structure",
            metadata={"hostname": "TEST-SWITCH"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify JSON structure error was detected
        structure_findings = [f for f in findings if f.category.value == "STRUCTURAL_ERROR"]
        assert len(structure_findings) > 0, "AUDIT FAILURE: Invalid JSON not detected"
        assert any("json" in f.description.lower() for f in structure_findings), "AUDIT FAILURE: JSON error not properly described"
    
    def test_real_deployment_port_map_audit(self):
        """
        RESULTS-AUDIT: Audit a real deployment port map from the API.
        
        This test calls the actual API, generates a port map, and audits
        the result for errors, duplicates, and structural problems.
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "PORTMAP-AUDIT-01",
                    "mgmt_ip": "10.10.10.1/24",
                    "mgmt_gw": "10.10.10.1",
                    "site_name": "TEST",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "base_access_vlan": 100,
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
        switch_result = result["results"][0]
        
        # Extract port map
        port_map = None
        if "device_config" in switch_result and "port_map" in switch_result["device_config"]:
            port_map = switch_result["device_config"]["port_map"]
        elif "port_map" in switch_result:
            port_map = switch_result["port_map"]
        
        assert port_map is not None, "Could not extract port map"
        
        # Audit the port map
        artifact = ConfigurationArtifact(
            artifact_type="port_map",
            content=json.dumps(port_map),
            source=f"generate_deployment:{switch_result['hostname']}",
            metadata={"hostname": switch_result["hostname"]}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Get summary
        summary = auditor.get_summary()
        
        # Log results
        print(f"\n=== PORT MAP AUDIT RESULTS FOR {switch_result['hostname']} ===")
        print(f"Total findings: {summary['total_findings']}")
        print(f"Critical findings: {summary['critical_findings']}")
        print(f"High findings: {summary['high_findings']}")
        
        for finding in findings:
            print(f"  [{finding.severity.value}] {finding.category.value}: {finding.description}")
        
        # Assert no critical or high findings (port map should be clean)
        critical_findings = [f for f in findings if f.severity == AuditSeverity.CRITICAL]
        high_findings = [f for f in findings if f.severity == AuditSeverity.HIGH]
        
        assert len(critical_findings) == 0, f"AUDIT FAILURE: {len(critical_findings)} CRITICAL findings in port map"
        assert len(high_findings) == 0, f"AUDIT FAILURE: {len(high_findings)} HIGH findings in port map"
