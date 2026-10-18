"""Test configuration validation functionality."""

import pytest
from fastapi.testclient import TestClient
from api.main import app


def test_config_upload_endpoint_exists():
    """Test that the /config/upload endpoint exists and is accessible."""
    client = TestClient(app)
    
    # Test with minimal valid config
    config_text = """
hostname TEST-SWITCH
feature lacp
feature lldp
interface Ethernet1/1
  description Test Interface
  no shutdown
"""
    
    response = client.post("/config/upload", json={
        "config_text": config_text,
        "hardware_model": "Nexus 9336C-FX2",
        "nxos_version": "9.3",
        "validation_level": "comprehensive"
    })
    
    # Should return 200
    assert response.status_code == 200
    result = response.json()
    
    # Check response structure
    assert "validation_id" in result
    assert "is_valid" in result
    assert "errors" in result
    assert "warnings" in result
    assert "suggestions" in result
    assert "severity" in result
    assert "detected_role" in result
    assert "detected_features" in result


def test_config_upload_with_vpc_errors():
    """Test configuration upload with vPC configuration errors."""
    client = TestClient(app)
    
    # Config with vPC domain but no peer-link
    config_text = """
hostname TEST-SWITCH
feature vpc
vpc domain 100
"""
    
    response = client.post("/config/upload", json={
        "config_text": config_text,
        "hardware_model": "Nexus 9336C-FX2",
        "nxos_version": "9.3",
        "validation_level": "comprehensive"
    })
    
    assert response.status_code == 200
    result = response.json()
    
    # Should detect vPC errors
    assert result["is_valid"] == False
    assert len(result["errors"]) > 0
    
    # Check for specific error codes
    error_codes = [e["error_code"] for e in result["errors"]]
    assert "MISSING_PEER_LINK" in error_codes or "MISSING_KEEPALIVE_IPS" in error_codes


def test_config_upload_with_vlan_errors():
    """Test configuration upload with VLAN range errors."""
    client = TestClient(app)
    
    # Config with reserved VLAN
    config_text = """
hostname TEST-SWITCH
vlan 999
  name Reserved_VLAN
"""
    
    response = client.post("/config/upload", json={
        "config_text": config_text,
        "hardware_model": "Nexus 9336C-FX2",
        "nxos_version": "9.3",
        "validation_level": "comprehensive"
    })
    
    assert response.status_code == 200
    result = response.json()
    
    # Should detect VLAN error (999 is reserved in hardware profile)
    assert result["is_valid"] == False
    assert len(result["errors"]) > 0


def test_config_upload_basic_validation_level():
    """Test basic validation level (syntax only)."""
    client = TestClient(app)
    
    config_text = """
hostname TEST-SWITCH
feature lacp
"""
    
    response = client.post("/config/upload", json={
        "config_text": config_text,
        "hardware_model": "Nexus 9336C-FX2",
        "nxos_version": "9.3",
        "validation_level": "basic"
    })
    
    assert response.status_code == 200
    result = response.json()
    
    # Basic validation should be less strict
    # May have warnings but fewer errors than comprehensive


def test_config_upload_security_warnings():
    """Test security policy validation."""
    client = TestClient(app)
    
    # Config with both NX-API and bash (security risk)
    config_text = """
hostname switch
feature nxapi
feature bash-shell
"""
    
    response = client.post("/config/upload", json={
        "config_text": config_text,
        "hardware_model": "Nexus 9336C-FX2",
        "nxos_version": "9.3",
        "validation_level": "comprehensive"
    })
    
    assert response.status_code == 200
    result = response.json()
    
    # Should detect security warning
    warning_codes = [w["warning_code"] for w in result["warnings"]]
    assert "SECURITY_RISK_NXAPI_BASH" in warning_codes or "DEFAULT_HOSTNAME" in warning_codes


def test_config_templates_endpoints():
    """Test template endpoints (placeholders for Phase 4)."""
    client = TestClient(app)
    
    # List templates
    response = client.get("/config/templates")
    assert response.status_code == 200
    result = response.json()
    assert "templates" in result
    assert "message" in result
    
    # Save template (placeholder)
    response = client.post("/config/templates")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
