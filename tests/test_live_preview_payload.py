"""Tests for live preview API payload extensions."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

PAYLOAD = {
    "scenario_id": "vpc_core_pair",
    "hostname": "CORE1-VPC",
    "site_name": "HQ_DC",
    "mgmt_ip": "10.10.10.10/24",
    "mgmt_gw": "10.10.10.1",
    "generate_pair": False,
    "overrides": {
        "model": "Nexus 9336C-FX2",
        "nxos_version": "9.3",
        "baseline_options": ["baseline_cli_aliases", "baseline_snmp_traps"],
        "downlink_options": {"downlink_10g_leaf": True, "downlink_1g_leaf": True},
    },
}


def test_catalog_matrix_endpoint():
    res = client.get("/catalog/matrix")
    assert res.status_code == 200
    data = res.json()
    assert "matrix" in data
    assert len(data["matrix"]) >= 7


@patch("api.main._enforce_privileged_access")
def test_preview_includes_studio_fields(_mock_auth):
    res = client.post("/scenario/preview", json=PAYLOAD)
    assert res.status_code == 200
    data = res.json()
    assert "action_required" in data
    assert "cli_blocks" in data
    assert "model_meta" in data
    assert data["model_meta"]["primary_speed_label"] == "40G"
    assert "config_preview" in data
    assert "Ethernet1/35" in data["config_preview"]
