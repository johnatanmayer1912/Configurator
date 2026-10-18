"""P1/P2 field gap regressions — UI contracts, layout, legacy, storm, HSRP."""

from pathlib import Path

import pytest

from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "templates" / "web" / "index.html"
STYLES = ROOT / "static" / "styles.css"
APP_JS = ROOT / "static" / "app.js"
TEMPLATE = ROOT / "templates" / "nxos_base.j2"


@pytest.mark.mandatory
def test_storm_control_on_access_port_channel_in_template():
    src = TEMPLATE.read_text(encoding="utf-8")
    assert "po.mode == 'access'" in src
    idx = src.find("po.mode == 'access'")
    block = src[idx : idx + 800]
    assert "storm-control broadcast" in block


@pytest.mark.mandatory
def test_leaf_vpc_access_po_has_storm_control():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "interface_plans": [
                {
                    "interface": "Ethernet1/5",
                    "preset": "access_vlan",
                    "vpc_port_channel": True,
                    "mode": "access",
                    "vlan_id": 100,
                }
            ],
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    start = cfg.find("interface port-channel10")
    assert start >= 0
    end = cfg.find("\ninterface ", start + 1)
    po_block = cfg[start : end if end > 0 else len(cfg)]
    assert "storm-control broadcast" in po_block


@pytest.mark.mandatory
def test_index_export_pair_label_and_preview_note():
    html = INDEX.read_text(encoding="utf-8")
    assert "Export primary + secondary files" in html
    assert "generatePairNote" in html
    assert "Live preview always shows this switch" in html


@pytest.mark.mandatory
def test_index_vxlan_expert_callout():
    html = INDEX.read_text(encoding="utf-8")
    assert "VXLAN/EVPN Leaf" in html
    assert "expert-vxlan-note" in html


@pytest.mark.mandatory
def test_index_hsrp_gateway_card():
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="cardHsrpGateway"' in html
    assert 'id="hsrp_vlan_id"' in html
    assert 'id="hsrp_svi_ip"' in html


@pytest.mark.mandatory
def test_index_hardened_secrets_modal():
    html = INDEX.read_text(encoding="utf-8")
    assert "hardenedSecretsModal" in html
    assert "requestBuild" in html
    js = APP_JS.read_text(encoding="utf-8")
    assert "needsHardenedSecretsConfirm" in js
    assert "confirmHardenedBuild" in js


@pytest.mark.mandatory
def test_styles_responsive_min_width():
    """UX-001: body supports narrow viewports (320px+), not locked to 1024px."""
    css = STYLES.read_text(encoding="utf-8")
    assert "min-width: 320px" in css
    assert "min-width: 1024px" not in css


@pytest.mark.mandatory
def test_expert_scenario_grid_lists_hardware():
    js = APP_JS.read_text(encoding="utf-8")
    assert "expertHardwareNote" in js
    assert "catalog.hardware" in js


@pytest.mark.mandatory
def test_legacy_70_vpc_leaf_renders():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"nxos_version": "7.0"},
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "hostname DC-LEAF-01-A" in cfg
    assert "feature vpc" in cfg or "vpc domain" in cfg


@pytest.mark.mandatory
def test_hsrp_svi_from_overrides_renders():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "custom_vlans": [{"id": 250, "name": "GW_250"}],
            "custom_svis": [{"vlan_id": 250, "ip_address": "10.100.100.2/24"}],
            "features": [
                "interface_vlan",
                "lldp",
                "lacp",
                "vpc",
                "hsrp",
                "storm_control",
                "ntp",
                "logging",
            ],
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "hsrp" in cfg.lower()
    assert "10.100.100" in cfg
