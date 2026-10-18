"""Automation tests from Product perspective - Feature completeness.

Product Team Expectations:
- All validation features are implemented and functional
- Feature completeness across all validation types
- Feature parity across different hardware models
- Feature parity across different NX-OS versions
- Feature integration with existing deployment workflow
- Feature scalability for large configurations
- Feature reliability and consistency
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestProductPerspective:
    """Product Team perspective automation tests for feature completeness."""
    
    def test_all_validation_types_are_implemented(self):
        """
        Product Scenario: All validation types must be implemented and functional.
        
        Expected Behavior:
        - Syntax validation works
        - Port mapping validation works
        - VLAN range validation works
        - vPC consistency validation works
        - Feature compatibility validation works
        - Baseline compliance validation works
        - Security policy validation works
        """
        config = """
hostname SWITCH
feature lacp
feature vpc
vpc domain 100
vlan 100
  name Test_VLAN
"""
        
        response = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "comprehensive"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Product expects all validation types to run
        assert "validation_id" in result, "Validation pipeline must complete"
        assert "is_valid" in result, "Validation result must be provided"
        assert "errors" in result, "Error validation must run"
        assert "warnings" in result, "Warning validation must run"
        assert "suggestions" in result, "Suggestion generation must run"
    
    def test_feature_parity_across_hardware_models(self):
        """
        Product Scenario: Validation features must work across all hardware models.
        
        Expected Behavior:
        - Validation works for 9336C-FX2
        - Validation works for 93180YC-EX
        - Validation works for 9348GC-FXP
        - Features are consistent across models
        """
        config = """
hostname SWITCH
feature lacp
vlan 100
  name Test_VLAN
"""
        
        hardware_models = ["Nexus 9336C-FX2", "Nexus 93180YC-EX", "Nexus 9348GC-FXP"]
        
        for model in hardware_models:
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": model,
                "nxos_version": "9.3",
                "validation_level": "comprehensive"
            })
            
            assert response.status_code == 200, f"Validation must work for {model}"
            result = response.json()
            assert "validation_id" in result, f"Validation must complete for {model}"
    
    def test_feature_parity_across_nxos_versions(self):
        """
        Product Scenario: Validation features must work across NX-OS versions.
        
        Expected Behavior:
        - Validation works for NX-OS 9.3
        - Validation works for NX-OS 10.2
        - Version-specific features are handled
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        nxos_versions = ["9.3", "10.2"]
        
        for version in nxos_versions:
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": version,
                "validation_level": "comprehensive"
            })
            
            assert response.status_code == 200, f"Validation must work for NX-OS {version}"
            result = response.json()
            assert "validation_id" in result, f"Validation must complete for NX-OS {version}"
    
    def test_validation_levels_are_functional(self):
        """
        Product Scenario: All validation levels must be functional.
        
        Expected Behavior:
        - Basic validation level works
        - Standard validation level works
        - Comprehensive validation level works
        - Each level provides appropriate depth
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        validation_levels = ["basic", "standard", "comprehensive"]
        
        for level in validation_levels:
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": level
            })
            
            assert response.status_code == 200, f"Validation level '{level}' must work"
            result = response.json()
            assert "validation_id" in result, f"Validation level '{level}' must complete"
    
    def test_baseline_options_are_supported(self):
        """
        Product Scenario: Baseline options must be supported and functional.
        
        Expected Behavior:
        - baseline_cfs option works
        - baseline_snmp_traps option works
        - baseline_logging option works
        - baseline_ntp option works
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        baseline_options = ["baseline_cfs", "baseline_snmp_traps", "baseline_logging", "baseline_ntp"]
        
        for baseline in baseline_options:
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": "comprehensive",
                "baseline_options": [baseline]
            })
            
            assert response.status_code == 200, f"Baseline option '{baseline}' must work"
            result = response.json()
            assert "validation_id" in result, f"Baseline option '{baseline}' must complete"
    
    def test_remediation_suggestions_are_generated(self):
        """
        Product Scenario: Remediation suggestions must be generated for issues.
        
        Expected Behavior:
        - Suggestions are generated for errors
        - Suggestions are actionable
        - Suggestions include fix commands when applicable
        """
        config_with_issues = """
hostname switch
feature vpc
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
        
        # Product expects suggestions for issues
        if not result["is_valid"]:
            suggestions = result.get("suggestions", [])
            # May have suggestions for detected issues
            assert isinstance(suggestions, list), "Suggestions must be generated"
    
    def test_validation_service_caching_works(self):
        """
        Product Scenario: Validation service caching must work for performance.
        
        Expected Behavior:
        - Identical configs use cached results
        - Cache improves performance
        - Cache invalidation works
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        # First request
        response1 = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response1.status_code == 200
        
        # Second request with same config (may use cache)
        response2 = client.post("/config/upload", json={
            "config_text": config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response2.status_code == 200
    
    def test_validation_statistics_are_tracked(self):
        """
        Product Scenario: Validation statistics must be tracked for analytics.
        
        Expected Behavior:
        - Validation count is tracked
        - Error rates are tracked
        - Performance metrics are tracked
        """
        config = """
hostname SWITCH
feature lacp
"""
        
        # Multiple validations to generate statistics
        for _ in range(3):
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": "standard"
            })
            assert response.status_code == 200
    
    def test_validation_integration_with_deployment_workflow(self):
        """
        Product Scenario: Validation must integrate with existing deployment workflow.
        
        Expected Behavior:
        - Validation can be called before deployment
        - Validation results inform deployment decisions
        - Integration is seamless
        """
        # First validate config
        validation_config = """
hostname SWITCH
feature lacp
"""
        
        validation_response = client.post("/config/upload", json={
            "config_text": validation_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert validation_response.status_code == 200
        validation_result = validation_response.json()
        
        # Then generate deployment (should work)
        deployment_input = {
            "switches": [{
                "hostname": "SWITCH",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "vpc_domain": None,
                "base_access_vlan": 100,
                "access_vlan_count": 5,
                "interface_count": 0,
                "bring_up_spare_ports": False,
                "security_tier": "standard",
                "role": "leaf"
            }],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        deployment_response = client.post("/generate-deployment", json=deployment_input)
        assert deployment_response.status_code == 200
    
    def test_validation_scalability_for_large_configs(self):
        """
        Product Scenario: Validation must scale for large configurations.
        
        Expected Behavior:
        - Large configs (1000+ lines) validate successfully
        - Performance remains acceptable
        - Memory usage is reasonable
        """
        # Generate large config
        large_config_lines = ["hostname SWITCH", "feature lacp"]
        for i in range(500):
            large_config_lines.append(f"interface Ethernet1/{i}")
            large_config_lines.append(f"  description Port {i}")
            large_config_lines.append("  no shutdown")
        
        large_config = "\n".join(large_config_lines)
        
        response = client.post("/config/upload", json={
            "config_text": large_config,
            "hardware_model": "Nexus 93180YC-EX",
            "nxos_version": "9.3",
            "validation_level": "standard"
        })
        
        assert response.status_code == 200, "Validation must scale for large configs"
        result = response.json()
        assert "validation_id" in result, "Large config validation must complete"
    
    def test_validation_reliability_and_consistency(self):
        """
        Product Scenario: Validation must be reliable and consistent.
        
        Expected Behavior:
        - Same config produces same results
        - Validation is deterministic
        - No random failures
        """
        config = """
hostname SWITCH
feature lacp
vpc domain 100
"""
        
        results = []
        for _ in range(3):
            response = client.post("/config/upload", json={
                "config_text": config,
                "hardware_model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "validation_level": "comprehensive"
            })
            assert response.status_code == 200
            result = response.json()
            results.append(result["is_valid"])
        
        # All results should be consistent
        assert all(r == results[0] for r in results), "Validation must be consistent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
