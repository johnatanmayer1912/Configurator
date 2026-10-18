"""Full API surface coverage — all 24 endpoints, auth enforcement, util routes.

Covers: /validate, /generate-config, /intent/*, /history, /system/paths,
        /builder/*, /checkpoints/*, /util/expand-range, /util/diff-config,
        /catalog sub-routes, 403/401 auth enforcement.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


# ─────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────

MINIMAL_DEVICE = {
    "hostname": "TEST-SW-01",
    "mgmt_ip": "10.0.0.1/24",
    "mgmt_gw": "10.0.0.254",
    "model": "Generic",
    "vlans": [{"id": 10, "name": "DATA"}],
    "interfaces": [],
    "svis": [],
    "static_routes": [],
    "vpc": None,
    "enabled_features": ["interface_vlan", "lacp"],
}

MINIMAL_INTENT = {
    "hostname": "TEST-LEAF-01",
    "site_name": "HQ_DC",
    "role": "leaf",
    "model": "Generic",
    "mgmt_ip": "10.0.0.1/24",
    "mgmt_gw": "10.0.0.254",
    "redundancy_mode": "standalone",
    "security_tier": "standard",
}


# ─────────────────────────────────────────────────────────
#  Auth enforcement
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_catalog_endpoints_are_public_no_auth_required():
    """/catalog/* routes are read-only public catalog data — no auth required."""
    for path in ["/catalog", "/catalog/scenarios", "/catalog/hardware", "/catalog/features"]:
        res = client.get(path)
        assert res.status_code == 200, (
            f"{path} must be accessible without auth; got {res.status_code}"
        )


@pytest.mark.mandatory
def test_non_loopback_gets_403_on_privileged_mutation_endpoint():
    """/validate is a privileged endpoint — non-loopback must get 403."""
    with patch("api.main._is_loopback", return_value=False):
        res = client.post("/validate", json=MINIMAL_DEVICE)
    assert res.status_code == 403, (
        f"/validate must reject non-loopback client; got {res.status_code}"
    )


@pytest.mark.mandatory
def test_non_loopback_gets_403_on_scenario_preview():
    """/scenario/preview is privileged — non-loopback must get 403."""
    with patch("api.main._is_loopback", return_value=False):
        res = client.post(
            "/scenario/preview",
            json={
                "scenario_id": "vpc_leaf_pair",
                "hostname": "TEST-LEAF-01",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
            },
        )
    assert res.status_code == 403


@pytest.mark.mandatory
def test_bad_auth_token_returns_401_when_token_configured():
    """When CONFIG_AUTH_TOKEN is set and loopback client sends wrong token, 401 returned."""
    with patch("api.main._is_loopback", return_value=True):
        with patch("api.main._auth_token", return_value="secret-token"):
            res = client.post(
                "/validate",
                json=MINIMAL_DEVICE,
                headers={"x-config-auth-token": "wrong-token"},
            )
    assert res.status_code == 401


@pytest.mark.mandatory
def test_correct_auth_token_passes_through():
    """Loopback client with correct token must proceed past auth gate."""
    with patch("api.main._is_loopback", return_value=True):
        with patch("api.main._auth_token", return_value="secret-token"):
            res = client.post(
                "/validate",
                json=MINIMAL_DEVICE,
                headers={"x-config-auth-token": "secret-token"},
            )
    assert res.status_code == 200


# ─────────────────────────────────────────────────────────
#  Catalog sub-routes
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_catalog_versions_returns_list(_mock):
    res = client.get("/catalog/versions")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) and len(data) >= 1
    for v in data:
        assert "id" in v or "label" in v or isinstance(v, str)


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_catalog_scenarios_returns_list(_mock):
    res = client.get("/catalog/scenarios")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) and len(data) >= 8
    ids = {s["id"] for s in data}
    assert "vpc_leaf_pair" in ids
    assert "vpc_core_pair" in ids
    assert "vxlan_evpn_leaf" in ids


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_catalog_hardware_returns_all_profiles(_mock):
    res = client.get("/catalog/hardware")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) and len(data) >= 6
    display_names = {p.get("display_name") for p in data}
    assert "Nexus 93180YC-EX" in display_names
    assert "Nexus 9364C-GX" in display_names
    assert "Nexus 92348GC-X" in display_names
    assert "Generic" in display_names


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_catalog_features_returns_all_feature_ids(_mock):
    res = client.get("/catalog/features")
    assert res.status_code == 200
    data = res.json()
    features = data if isinstance(data, list) else data.get("features", [])
    feature_ids = {f["id"] if isinstance(f, dict) else f for f in features}
    assert "bfd" in feature_ids
    assert "vpc_orphan_suspend" in feature_ids
    assert "aaa_tacacs" in feature_ids
    assert "vxlan" in feature_ids


# ─────────────────────────────────────────────────────────
#  /validate
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_validate_accepts_valid_device(_mock):
    res = client.post("/validate", json=MINIMAL_DEVICE)
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["status"] in ("pass", "fail", "warn")


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_validate_returns_compliance_findings(_mock):
    res = client.post("/validate", json=MINIMAL_DEVICE)
    assert res.status_code == 200
    data = res.json()
    assert "compliance_findings" in data


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_validate_rejects_bad_hostname(_mock):
    bad = dict(MINIMAL_DEVICE, hostname="bad_hostname_underscore")
    res = client.post("/validate", json=bad)
    assert res.status_code == 422


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_validate_rejects_missing_cidr(_mock):
    bad = dict(MINIMAL_DEVICE, mgmt_ip="10.0.0.1")
    res = client.post("/validate", json=bad)
    assert res.status_code == 422


# ─────────────────────────────────────────────────────────
#  /generate-config
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_generate_config_returns_success(_mock, tmp_path):
    with patch("api.main.pipeline.execute") as mock_exec:
        mock_exec.return_value = {
            "message": "Config saved",
            "files": ["test_config.txt"],
            "output_dir": str(tmp_path),
        }
        res = client.post("/generate-config", json=MINIMAL_DEVICE)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "export" in data


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_generate_config_saves_checkpoint(_mock, tmp_path):
    with patch("api.main.checkpoints.save_checkpoint") as mock_ckpt:
        with patch("api.main.pipeline.execute") as mock_exec:
            mock_exec.return_value = {
                "message": "Config saved",
                "files": [],
                "output_dir": str(tmp_path),
            }
            client.post("/generate-config", json=MINIMAL_DEVICE)
    mock_ckpt.assert_called_once()


# ─────────────────────────────────────────────────────────
#  /intent/preview
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_preview_access_role(_mock):
    payload = dict(MINIMAL_INTENT, role="access", redundancy_mode="standalone")
    res = client.post("/intent/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "profile_name" in data
    assert "ACCESS" in data["profile_name"].upper()
    assert "summary_lines" in data
    assert any("Role:" in line or "role" in line.lower() for line in data["summary_lines"])


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_preview_leaf_role(_mock):
    payload = dict(MINIMAL_INTENT, role="leaf", redundancy_mode="standalone")
    res = client.post("/intent/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "LEAF" in data["profile_name"].upper()


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_preview_spine_role(_mock):
    payload = dict(MINIMAL_INTENT, role="spine", redundancy_mode="standalone")
    res = client.post("/intent/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "SPINE" in data["profile_name"].upper()


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_preview_vpc_mode_policy_flag(_mock):
    payload = dict(MINIMAL_INTENT, role="leaf", redundancy_mode="vpc")
    res = client.post("/intent/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["policy_flags"].get("vpc_enabled") == "yes"


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_preview_hardened_tier(_mock):
    payload = dict(MINIMAL_INTENT, role="access", security_tier="hardened")
    res = client.post("/intent/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["policy_flags"].get("security_tier") == "hardened"


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_preview_invalid_role_422(_mock):
    payload = dict(MINIMAL_INTENT, role="firewall")
    res = client.post("/intent/preview", json=payload)
    assert res.status_code == 422


# ─────────────────────────────────────────────────────────
#  /intent/generate
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_generate_returns_export(_mock, tmp_path):
    with patch("api.main.pipeline.execute") as mock_exec:
        mock_exec.return_value = {
            "message": "Intent config saved",
            "files": ["test_intent_config.txt"],
            "output_dir": str(tmp_path),
        }
        payload = dict(MINIMAL_INTENT, role="leaf")
        res = client.post("/intent/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "export" in data
    assert "profile_name" in data
    assert "summary_lines" in data


# ─────────────────────────────────────────────────────────
#  /history
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_history_returns_list(_mock):
    res = client.get("/history")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_history_filename_filter(_mock):
    res = client.get("/history?hostname=NONEXISTENT_HOST_XYZ")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_history_file_not_found_returns_404(_mock):
    res = client.get("/history/no_such_file_xyz.txt")
    assert res.status_code == 404


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_history_path_traversal_rejected(_mock):
    res = client.get("/history/../../etc/passwd")
    assert res.status_code in (400, 404)


# ─────────────────────────────────────────────────────────
#  /system/paths
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_system_paths_returns_required_keys(_mock):
    res = client.get("/system/paths")
    assert res.status_code == 200
    data = res.json()
    assert "app_dir" in data
    assert "vault_dir" in data
    assert "checkpoints_dir" in data
    assert "version" in data


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_system_paths_version_matches_version_file(_mock):
    from pathlib import Path as _Path
    version_file = _Path(__file__).resolve().parents[2] / "VERSION"
    expected = version_file.read_text(encoding="utf-8").strip()
    res = client.get("/system/paths")
    assert res.json()["version"] == expected


# ─────────────────────────────────────────────────────────
#  /builder/*
# ─────────────────────────────────────────────────────────

SAMPLE_RUNNING_CONFIG = """
version 9.3(5)
hostname DC-LEAF-99
feature vpc
feature lacp
!
interface Ethernet1/49
  description Peer-Link-Member
  channel-group 1 mode active
interface Ethernet1/50
  description Peer-Link-Member
  channel-group 1 mode active
interface port-channel1
  description vPC PEER-LINK
  switchport mode trunk
  vpc peer-link
interface mgmt0
  ip address 10.0.0.5/24
"""


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_builder_parse_returns_structured_hints(_mock):
    res = client.post("/builder/parse", json={"running_config": SAMPLE_RUNNING_CONFIG})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Response is nested: {parsed: {...}, suggested_answers: {...}, summary: [...]}
    assert "parsed" in data or "suggested_answers" in data or "summary" in data


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_builder_parse_extracts_hostname(_mock):
    res = client.post("/builder/parse", json={"running_config": SAMPLE_RUNNING_CONFIG})
    assert res.status_code == 200
    data = res.json()
    # hostname lives inside suggested_answers or the summary
    hostname_found = (
        data.get("suggested_answers", {}).get("hostname") == "DC-LEAF-99"
        or any("DC-LEAF-99" in line for line in data.get("summary", []))
        or data.get("parsed", {}).get("hostname") == "DC-LEAF-99"
    )
    assert hostname_found, f"Hostname DC-LEAF-99 must be extracted from running config; got: {data}"


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_builder_questions_returns_question_list(_mock):
    res = client.post("/builder/questions", json={"answers": {}})
    assert res.status_code == 200
    data = res.json()
    assert "questions" in data
    assert isinstance(data["questions"], list)


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_builder_recommend_with_vpc_hints(_mock):
    res = client.post(
        "/builder/recommend",
        json={
            "answers": {
                "has_vpc": True,
                "role": "leaf",
                "speed": "10G",
            }
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "scenario_id" in data or "recommendation" in data or "scenario" in data


# ─────────────────────────────────────────────────────────
#  /checkpoints
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_checkpoints_list_returns_list(_mock):
    res = client.get("/checkpoints")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_checkpoint_not_found_returns_404(_mock):
    res = client.get("/checkpoints/no_such_checkpoint_xyz.json")
    assert res.status_code == 404


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_checkpoint_restore_preview_not_found_404(_mock):
    res = client.post("/checkpoints/no_such_checkpoint_xyz.json/restore-preview")
    assert res.status_code == 404


# ─────────────────────────────────────────────────────────
#  /util/expand-range
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_util_expand_range_basic(_mock):
    res = client.get("/util/expand-range?range_str=Ethernet1/1-4")
    assert res.status_code == 200
    data = res.json()
    assert "expanded" in data
    assert data["expanded"] == ["Ethernet1/1", "Ethernet1/2", "Ethernet1/3", "Ethernet1/4"]


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_util_expand_range_comma_separated(_mock):
    res = client.get("/util/expand-range?range_str=Ethernet1/1,Ethernet1/3")
    assert res.status_code == 200
    expanded = res.json()["expanded"]
    assert "Ethernet1/1" in expanded
    assert "Ethernet1/3" in expanded


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_util_expand_range_single_interface(_mock):
    res = client.get("/util/expand-range?range_str=Ethernet1/48")
    assert res.status_code == 200
    assert res.json()["expanded"] == ["Ethernet1/48"]


# ─────────────────────────────────────────────────────────
#  /util/diff-config
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_util_diff_config_returns_diff_and_count(_mock):
    baseline = "hostname OLD-HOST\nfeature lacp\n"
    proposed = "hostname NEW-HOST\nfeature lacp\nfeature vpc\n"
    res = client.post("/util/diff-config", json={"baseline": baseline, "proposed": proposed})
    assert res.status_code == 200
    data = res.json()
    assert "diff" in data
    assert "lines_added" in data
    assert data["lines_added"] >= 0


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_util_diff_config_empty_inputs(_mock):
    res = client.post("/util/diff-config", json={"baseline": "", "proposed": ""})
    assert res.status_code == 200
    data = res.json()
    assert data["lines_added"] == 0


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_util_diff_config_detects_additions(_mock):
    baseline = "hostname LEAF-01\n"
    proposed = "hostname LEAF-01\nfeature vpc\nfeature lacp\n"
    res = client.post("/util/diff-config", json={"baseline": baseline, "proposed": proposed})
    assert res.status_code == 200
    data = res.json()
    assert data["lines_added"] >= 1
    assert "vpc" in data["diff"] or "lacp" in data["diff"]
