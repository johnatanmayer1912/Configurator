"""Legacy 7.x template + two-pass deployment wiring regressions."""

import re

import pytest
from fastapi.testclient import TestClient

from api.main import app
from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine
from core.deployment_wiring import wire_core_leaf_downlinks
from core.catalog_loader import CatalogLoader
from models.device_model import Device

client = TestClient(app)


@pytest.mark.mandatory
def test_legacy_70_renders_keepalive_port_channel_with_no_switchport():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "nxos_version": "7.0",
            "local_ka": "10.255.255.1/24",
            "remote_ka": "10.255.255.2",
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "interface port-channel2" in cfg
    ka_start = cfg.find("interface port-channel2")
    ka_end = cfg.find("\ninterface ", ka_start + 1)
    block = cfg[ka_start:ka_end if ka_end > 0 else len(cfg)]
    assert "no switchport" in block
    assert "peer-keepalive" in cfg
    vpc_m = re.search(r"^vpc domain ", cfg, re.MULTILINE)
    assert vpc_m is not None
    assert cfg.find("interface port-channel2") < vpc_m.start()


@pytest.mark.mandatory
def test_legacy_70_peer_link_trunk_allowed_vlan():
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
    assert "switchport trunk allowed vlan" in cfg


@pytest.mark.mandatory
def test_two_pass_wiring_core_before_leaf():
    """Leaf uplinks must be wired when core appears first in switch list."""
    catalog = CatalogLoader()
    core = type("SC", (), {
        "hostname": "CORE1",
        "model": "Nexus 9336C-FX2",
        "role": "core",
    })()
    leaf = type("SC", (), {
        "hostname": "LEAF1",
        "model": "Nexus 93180YC-EX",
        "role": "leaf",
    })()
    core_dev = Device(hostname="CORE1", mgmt_ip="10.0.0.1/24", mgmt_gw="10.0.0.254", model=core.model)
    leaf_dev = Device(hostname="LEAF1", mgmt_ip="10.0.0.2/24", mgmt_gw="10.0.0.254", model=leaf.model)
    by_hn = {"CORE1": core_dev, "LEAF1": leaf_dev}

    wire_core_leaf_downlinks(by_hn, [core, leaf], catalog, request_id="test")

    assert leaf_dev.uplink_config, "Leaf should have uplink_config after pass-2 wiring"
    assert any("to CORE1" in (u.get("description") or "") for u in leaf_dev.uplink_config)
    assert core_dev.downlink_config, "Core should have downlink_config after pass-2 wiring"


@pytest.mark.mandatory
def test_deployment_core_first_switch_order_wires_leaf():
    """Integration: generate-deployment with core listed before leaf."""
    payload = {
        "switches": [
            {
                "hostname": "SPINE1",
                "mgmt_ip": "10.0.1.1/24",
                "mgmt_gw": "10.0.1.254",
                "site_name": "HQ",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
                "role": "spine",
                "vpc_pl_ints": "",
                "baseline_options": [],
                "vlans": [],
            },
            {
                "hostname": "LEAF1",
                "mgmt_ip": "10.0.2.1/24",
                "mgmt_gw": "10.0.1.254",
                "site_name": "HQ",
                "model": "Nexus 93180YC-EX",
                "nxos_version": "9.3",
                "role": "leaf",
                "vpc_pl_ints": "",
                "baseline_options": [],
                "vlans": [],
            },
        ],
        "vpc_pairs": [],
        "uplinks": [],
    }
    res = client.post("/generate-deployment?preview=true", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    leaf_result = next(r for r in data["results"] if r["hostname"] == "LEAF1")
    uplinks = leaf_result.get("device_config", {}).get("uplink_config") or []
    assert len(uplinks) >= 1, "Leaf uplink_config should be populated when core is processed first"
