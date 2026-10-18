"""Mandatory v4.1 — vPC Link Planner (downlinks + uplinks) across 40G / 10G / 1G."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from core.engine import ConfigEngine
from core.link_resolver import fiber_uplink_pool, resolve_link_plans
from core.catalog_loader import CatalogLoader
from core.scenario_engine import ScenarioEngine

client = TestClient(app)
ROOT_CATALOG = CatalogLoader()


def _cfg(scenario_id, hostname, **overrides):
    result = ScenarioEngine().apply_scenario(
        scenario_id,
        hostname,
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides=overrides or None,
    )
    cfg = ConfigEngine().build_config(result["device"])
    return result, cfg


def _block(cfg: str, name: str) -> str:
    marker = f"interface {name}"
    start = cfg.find(marker)
    assert start >= 0, f"{name} missing"
    end = cfg.find("\ninterface ", start + 1)
    return cfg[start : end if end > 0 else len(cfg)]


@pytest.mark.mandatory
def test_fiber_uplink_pool_excludes_vpc_reserved_ports():
    hw = ROOT_CATALOG.get_hardware_profile("Nexus 93180YC-EX")
    pool = fiber_uplink_pool(hw)
    # vpc_keepalive is Ethernet1/49-50, vpc_peer_link is Ethernet1/51-52
    # fiber uplink pool should be Ethernet1/53-54 (vpc_uplink_start/end)
    assert "Ethernet1/53" in pool
    assert "Ethernet1/54" in pool
    assert "Ethernet1/49" not in pool  # reserved for keepalive
    assert "Ethernet1/50" not in pool  # reserved for keepalive
    assert "Ethernet1/51" not in pool  # reserved for peer-link
    assert "Ethernet1/52" not in pool  # reserved for peer-link


@pytest.mark.mandatory
def test_40g_core_custom_downlink_members_render():
    _, cfg = _cfg(
        "vpc_core_pair",
        "CORE1-VPC-A",
        downlinks=[
            {
                "id": "downlink_10g_leaf",
                "enabled": True,
                "po_id": 20,
                "vpc_id": 20,
                "description": "Connected_to_CUSTOM_10G",
                "members": ["Ethernet1/5", "Ethernet1/6"],
            },
            {
                "id": "downlink_1g_leaf",
                "enabled": True,
                "po_id": 21,
                "vpc_id": 21,
                "description": "Connected_to_CUSTOM_1G",
                "members": ["Ethernet1/7", "Ethernet1/8"],
            },
        ],
        downlink_options={"downlink_10g_leaf": True, "downlink_1g_leaf": True},
    )
    assert "Connected_to_CUSTOM_10G" in cfg
    assert "channel-group 20 mode active" in _block(cfg, "Ethernet1/5")
    assert "channel-group 21 mode active" in _block(cfg, "Ethernet1/7")


@pytest.mark.mandatory
def test_10g_leaf_default_fiber_uplink_po30():
    _, cfg = _cfg("vpc_leaf_pair", "DC-LEAF-01-A", uplink_options={"uplink_fiber_pair": True})
    assert "interface port-channel30" in cfg
    assert "vpc 30" in _block(cfg, "port-channel30")
    # Fiber uplink uses Ethernet1/53-54 (vpc_uplink_start/end), not Ethernet1/49-50 (keepalive)
    assert "channel-group 30 mode active" in _block(cfg, "Ethernet1/53")
    assert "channel-group 30 mode active" in _block(cfg, "Ethernet1/54")


@pytest.mark.mandatory
def test_1g_access_custom_uplink_members():
    _, cfg = _cfg(
        "vpc_access_pair",
        "ACCESS-SW-01-A",
        uplinks=[
            {
                "id": "uplink_fiber_pair",
                "enabled": True,
                "po_id": 30,
                "vpc_id": 30,
                "description": "Connected_to_SPINE_CUSTOM",
                "members": ["Ethernet1/49", "Ethernet1/51"],
                "mode": "trunk",
            }
        ],
        uplink_options={"uplink_fiber_pair": True},
    )
    assert "Connected_to_SPINE_CUSTOM" in cfg
    assert "channel-group 30 mode active" in _block(cfg, "Ethernet1/51")


@pytest.mark.mandatory
def test_40g_core_spine_uplink_when_enabled():
    _, cfg = _cfg(
        "vpc_core_pair",
        "CORE1-VPC-A",
        uplink_options={"uplink_core_spine": True},
        uplinks=[
            {
                "id": "uplink_core_spine",
                "enabled": True,
                "po_id": 10,
                "vpc_id": 10,
                "description": "Connected_to_SPINE",
                "members": ["Ethernet1/31", "Ethernet1/32"],
                "mode": "trunk",
            }
        ],
    )
    assert "interface port-channel10" in cfg
    assert "vpc 10" in _block(cfg, "port-channel10")


@pytest.mark.mandatory
def test_standalone_access_uses_bare_uplink_trunks_not_po():
    _, cfg = _cfg("standalone_access", "ACCESS-SW-01", uplink_options={"uplink_fiber_pair": True})
    assert "interface port-channel30" not in cfg
    assert "interface Ethernet1/49" in cfg
    assert "switchport mode trunk" in _block(cfg, "Ethernet1/49")


@pytest.mark.mandatory
def test_link_planner_dom_contracts():
    html = (ROOT / "templates/web/index.html").read_text(encoding="utf-8") if (ROOT := pytest.importorskip("pathlib").Path(__file__).resolve().parents[2]) else ""
    assert 'id="cardVpcLinks"' in html
    assert 'id="downlinkPlanBody"' in html
    assert 'id="uplinkPlanBody"' in html
    js = (ROOT / "static/vpc-link-planner.js").read_text(encoding="utf-8")
    assert "getLinkPlannerPayload" in js
    assert "fiberUplinkPool" in js


@pytest.mark.mandatory
def test_catalog_exposes_uplink_presets():
    res = client.get("/catalog")
    assert res.status_code == 200
    data = res.json()
    assert any(p["id"] == "uplink_fiber_pair" for p in data.get("uplink_presets", []))
    row = next(r for r in data["config_matrix"] if r["scenario_id"] == "vpc_leaf_pair")
    assert "uplink_fiber_pair" in row.get("uplink_presets", [])


@pytest.mark.mandatory
def test_matrix_uplink_presets_resolve_for_all_vpc_tiers():
    hw_leaf = ROOT_CATALOG.get_hardware_profile("Nexus 93180YC-EX")
    for scenario_id in ("vpc_core_pair", "vpc_leaf_pair", "vpc_access_pair"):
        uplinks = resolve_link_plans(
            scenario_id=scenario_id,
            defaults={"uplink_options": {"uplink_fiber_pair": scenario_id != "vpc_core_pair", "uplink_core_spine": scenario_id == "vpc_core_pair"}},
            catalog=ROOT_CATALOG,
            hw_profile=hw_leaf if scenario_id != "vpc_core_pair" else ROOT_CATALOG.get_hardware_profile("Nexus 9336C-FX2"),
            kind="uplink",
        )
        if scenario_id == "vpc_core_pair":
            assert any(u.get("id") == "uplink_core_spine" for u in uplinks)
        else:
            assert any(u.get("id") == "uplink_fiber_pair" for u in uplinks)
