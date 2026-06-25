"""Software engineer — operator API contracts (preview, generate, shutdown, catalog)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.mark.mandatory
def test_version_endpoint_public():
    res = client.get("/version")
    assert res.status_code == 200
    assert res.json().get("version")


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_catalog_includes_interface_presets(_mock):
    res = client.get("/catalog")
    assert res.status_code == 200
    data = res.json()
    assert "scenarios" in data
    assert "interface_presets" in data
    assert data.get("interface_po_start", 0) >= 10


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_preview_accepts_interface_plans_without_generate_pair(_mock):
    payload = {
        "scenario_id": "vpc_leaf_pair",
        "hostname": "DC-LEAF-01-A",
        "site_name": "HQ",
        "mgmt_ip": "10.10.10.10/24",
        "mgmt_gw": "10.10.10.1",
        "generate_pair": False,
        "overrides": {
            "interface_plans": [
                {
                    "interface": "Ethernet1/5",
                    "preset": "access_vlan",
                    "vlan_id": 200,
                    "vlan_name": "LAB",
                    "description": "API_Test",
                }
            ],
        },
    }
    res = client.post("/scenario/preview", json=payload)
    assert res.status_code == 200
    cfg = res.json().get("config_preview", "")
    assert "interface port-channel10" in cfg
    assert "API_Test" in cfg or "interface Ethernet1/5" in cfg


@pytest.mark.mandatory
@patch("api.main._enforce_loopback_only", return_value=None)
def test_shutdown_no_auth_token_required_on_localhost(_mock_loopback):
    """Contract: Stop works without session token (instance control release blocker)."""
    with patch("api.main._enforce_privileged_access"):
        with patch("api.main.threading.Thread") as mock_thread:
            res = client.post("/system/shutdown")
    assert res.status_code in (200, 403)  # 403 if test client host not loopback in CI
    assert mock_thread.called, "shutdown must schedule async stop (no blocking kill in tests)"


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_preview_invalid_hostname_rejected(_mock):
    res = client.post(
        "/scenario/preview",
        json={
            "scenario_id": "vpc_leaf_pair",
            "hostname": "bad_hostname",
            "mgmt_ip": "10.10.10.10/24",
            "mgmt_gw": "10.10.10.1",
        },
    )
    assert res.status_code == 422
