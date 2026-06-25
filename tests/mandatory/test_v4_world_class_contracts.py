"""v4.0 world-class release contracts — P0/P1/P2 gaps, change package, port map, vault, fabric."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from core.engine import ConfigEngine
from core.import_wizard import ConfigBuilderEngine
from core.scenario_engine import ScenarioEngine
from utils.change_package import build_manifest, render_change_package_md, write_package_artifacts

ROOT = Path(__file__).resolve().parents[2]
client = TestClient(app)

LEAF_PAIR_PAYLOAD = {
    "scenario_id": "vpc_leaf_pair",
    "hostname": "DC-LEAF-01-A",
    "site_name": "HQ_DC",
    "mgmt_ip": "10.10.10.10/24",
    "mgmt_gw": "10.10.10.1",
    "generate_pair": True,
    "overrides": {
        "model": "Nexus 93180YC-EX",
        "nxos_version": "9.3",
        "local_keepalive_ip": "10.255.255.1",
        "remote_keepalive_ip": "10.255.255.2",
    },
}


# ── P0: Change package ─────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_change_package_manifest_schema():
    m = build_manifest(
        version="4.0.0",
        site_name="HQ",
        scenario_id="vpc_leaf_pair",
        scenario_name="vPC Leaf",
        nxos_version="9.3",
        hosts=[{"hostname": "A", "vpc_role": "primary"}],
        files=["a_config.txt"],
        output_dir="/tmp/out",
        pair_mode=True,
        lab_ready=True,
    )
    assert m["schema_version"] == 1
    assert m["pair_mode"] is True
    assert "lab_ready" in m


@pytest.mark.mandatory
def test_change_package_md_renders_rollback_section():
    m = build_manifest(
        version="4.0.0",
        site_name="HQ",
        scenario_id="vpc_leaf_pair",
        scenario_name="Leaf",
        nxos_version="9.3",
        hosts=[],
        files=[],
        output_dir="/tmp",
        pair_mode=True,
    )
    md = render_change_package_md(m)
    assert "Rollback reminder" in md
    assert "vPC pair notes" in md


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_scenario_generate_writes_change_package(_mock, tmp_path):
    payload = {**LEAF_PAIR_PAYLOAD, "overrides": {**LEAF_PAIR_PAYLOAD["overrides"], "export_dir": str(tmp_path)}}
    res = client.post("/scenario/generate", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    export = data["export"]
    assert "change_package" in export
    out_dir = Path(export["output_dir"])
    assert (out_dir / "manifest.json").is_file()
    assert (out_dir / "CHANGE_PACKAGE.md").is_file()
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["scenario_id"] == "vpc_leaf_pair"
    assert len(manifest.get("hosts", [])) >= 2


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_scenario_generate_writes_device_json(_mock, tmp_path):
    payload = {
        **LEAF_PAIR_PAYLOAD,
        "generate_pair": False,
        "overrides": {**LEAF_PAIR_PAYLOAD["overrides"], "export_dir": str(tmp_path)},
    }
    res = client.post("/scenario/generate", json=payload)
    assert res.status_code == 200
    files = res.json()["export"]["files"]
    assert any(f.endswith("_device.json") for f in files)


# ── P0: Config Builder end-to-end ────────────────────────────────────────

@pytest.mark.mandatory
def test_config_builder_recommend_vpc_leaf():
    engine = ConfigBuilderEngine()
    rec = engine.recommend({
        "device_role": "leaf",
        "redundancy": "vpc",
        "environment": "lab",
        "fabric": "no",
        "site_name": "HQ",
        "hostname": "LEAF-01-A",
    })
    assert rec.get("scenario_id") == "vpc_leaf_pair"


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_builder_parse_to_recommend_flow(_mock):
    sample = "hostname TEST-LEAF\nfeature vpc\ninterface mgmt0\n ip address 10.0.0.1/24\n"
    parse_res = client.post("/builder/parse", json={"running_config": sample})
    assert parse_res.status_code == 200
    rec_res = client.post(
        "/builder/recommend",
        json={"answers": {"device_role": "leaf", "redundancy": "vpc", "hostname": "TEST-LEAF"}},
    )
    assert rec_res.status_code == 200
    assert "scenario_id" in rec_res.json()


# ── P0: Checkpoint restore contract (API + UI hooks) ─────────────────────

@pytest.mark.mandatory
def test_checkpoint_restore_ui_contracts_in_app_js():
    src = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "async function restoreCheckpoint" in src
    assert "vpc_ka_ints" in src
    assert "goToStep(4)" in src


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_checkpoint_restore_preview_returns_checkpoint_shape(_mock):
    from api.main import checkpoints
    from models.device_model import Device

    device = Device(
        hostname="CKPT-TEST",
        mgmt_ip="10.0.0.1/24",
        mgmt_gw="10.0.0.254",
        model="Generic",
    )
    path = checkpoints.save_checkpoint(device, label="test")
    filename = os.path.basename(path)
    res = client.post(f"/checkpoints/{filename}/restore-preview")
    assert res.status_code == 200
    data = res.json()
    assert data["checkpoint"]["hostname"] == "CKPT-TEST"


# ── P0: Wizard DOM / hero path contracts ─────────────────────────────────

@pytest.mark.mandatory
def test_wizard_dom_has_port_map_editor():
    html = (ROOT / "templates" / "web" / "index.html").read_text(encoding="utf-8")
    assert "portMapEditorPanel" in html
    assert "customPortMapToggle" in html
    assert "port-map-editor.js" in html


@pytest.mark.mandatory
def test_wizard_dom_has_vault_filters():
    html = (ROOT / "templates" / "web" / "index.html").read_text(encoding="utf-8")
    assert "vaultSiteFilter" in html
    assert "vaultScenarioFilter" in html
    assert "vaultTypeFilter" in html


@pytest.mark.mandatory
def test_first_run_hint_present():
    html = (ROOT / "templates" / "web" / "index.html").read_text(encoding="utf-8")
    assert 'id="firstRunHint"' in html


# ── P1: VXLAN/EVPN fabric template ───────────────────────────────────────

@pytest.mark.mandatory
def test_vxlan_evpn_fabric_renders_nve_and_bgp():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vxlan_evpn_leaf",
        "VXLAN-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "feature nv overlay" in cfg
    assert "interface nve1" in cfg
    assert "router bgp" in cfg
    assert "member vni" in cfg


# ── P1: Intent + scenario topology parity ────────────────────────────────

@pytest.mark.mandatory
def test_intent_vpc_leaf_gets_peer_link_from_hardware():
    from models.intent_model import BlueprintIntent

    engine = ScenarioEngine()
    intent = BlueprintIntent(
        hostname="INTENT-LEAF",
        site_name="HQ",
        role="leaf",
        model="Nexus 93180YC-EX",
        mgmt_ip="10.0.0.1/24",
        mgmt_gw="10.0.0.254",
        redundancy_mode="vpc",
    )
    device, _ = engine.intent_engine.resolve(intent)
    engine.enrich_intent_topology(device, intent)
    assert device.vpc is not None
    assert len(device.vpc.peer_link_interfaces) >= 2


# ── P1: TACACS+ live block when server configured ───────────────────────

@pytest.mark.mandatory
def test_tacacs_live_block_when_server_and_key_set():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "standalone_access",
        "ACCESS-01",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "features": ["interface_vlan", "aaa_tacacs"],
            "tacacs_server_1": "10.1.1.1",
            "tacacs_key": "7 encrypted",
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "aaa group server tacacs+" in cfg
    assert "10.1.1.1" in cfg
    assert "! aaa group" not in cfg.split("aaa group")[0][-20:]


# ── P1: Vault API filters ────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_history_supports_site_and_artifact_filters(_mock):
    res = client.get("/history?site=NONEXISTENT_SITE_XYZ&artifact_type=manifest")
    assert res.status_code == 200
    assert res.json() == []


# ── P2: parse-running-config-diff ────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_parse_running_config_diff(_mock):
    baseline = "hostname OLD\nfeature lacp\n"
    proposed = "hostname NEW\nfeature lacp\nfeature vpc\n"
    res = client.post(
        "/util/parse-running-config-diff",
        json={"running_config": baseline, "proposed": proposed},
    )
    assert res.status_code == 200
    data = res.json()
    assert "parsed" in data
    assert "diff" in data


# ── P2: Accessibility CSS contracts ──────────────────────────────────────

@pytest.mark.mandatory
def test_styles_include_focus_visible_and_reduced_motion():
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css


# ── S-HERO scenarios smoke (all 8 scenarios + pair export) ───────────────

SCENARIO_IDS = [
    "standalone_access",
    "vpc_access_pair",
    "standalone_leaf",
    "vpc_leaf_pair",
    "spine_core",
    "vpc_core_pair",
    "mgmt_oob",
    "vxlan_evpn_leaf",
]


@pytest.mark.mandatory
@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
def test_all_scenarios_render_non_trivial_config(scenario_id):
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        scenario_id,
        "SMOKE-01",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "hostname SMOKE-01" in cfg
    assert len(cfg) > 200


@pytest.mark.mandatory
def test_write_package_artifacts_creates_files(tmp_path):
    m = build_manifest(
        version="4.0.0",
        site_name="HQ",
        scenario_id="test",
        scenario_name="Test",
        nxos_version="9.3",
        hosts=[],
        files=[],
        output_dir=str(tmp_path),
    )
    written = write_package_artifacts(str(tmp_path), m)
    assert "manifest.json" in written
    assert "CHANGE_PACKAGE.md" in written
