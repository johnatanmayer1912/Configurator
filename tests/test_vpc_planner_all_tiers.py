"""Extensive QA — Interface Planner vPC port-channels on 40G / 10G / 1G pairs."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from core.engine import ConfigEngine
from core.interface_customizer import validate_interface_plans
from core.scenario_engine import ScenarioEngine

client = TestClient(app)

TIER_SCENARIOS = [
    ("vpc_core_pair", "CORE1-VPC-A", "Nexus 9336C-FX2", "Ethernet1/15"),
    ("vpc_leaf_pair", "DC-LEAF-01-A", "Nexus 93180YC-EX", "Ethernet1/5"),
    ("vpc_access_pair", "ACCESS-SW-01-A", "Nexus 9348GC-FXP", "Ethernet1/10"),
]

ACCESS_PLAN = {
    "interface": None,  # filled per tier
    "preset": "access_vlan",
    "mode": "access",
    "vlan_id": 250,
    "vlan_name": "SERVERS",
    "description": "Host_Port",
}

TRUNK_PLAN = {
    "interface": None,
    "preset": "trunk_custom",
    "mode": "trunk",
    "trunk_vlans": "10,20,30",
    "description": "Multi_Trunk",
}


def _apply(scenario_id, hostname, port, **extra):
    plan = {**ACCESS_PLAN, "interface": port, **extra}
    return ScenarioEngine().apply_scenario(
        scenario_id,
        hostname,
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"interface_plans": [plan]},
    )


def _block(cfg: str, name: str) -> str:
    marker = f"interface {name}"
    start = cfg.find(marker)
    assert start >= 0, f"{name} missing from config"
    end = cfg.find("\ninterface ", start + 1)
    return cfg[start:end if end > 0 else len(cfg)]


@pytest.mark.parametrize("scenario_id,hostname,model,port", TIER_SCENARIOS)
def test_vpc_po_explicit_flag_all_tiers(scenario_id, hostname, model, port):
    result = _apply(scenario_id, hostname, port, vpc_port_channel=True)
    pri = result["device"]
    sec = result["pair"]["secondary"]["device"]
    cfg = ConfigEngine().build_config(pri)
    sec_cfg = ConfigEngine().build_config(sec)

    assert any(po.number == 10 for po in pri.port_channels)
    assert "interface port-channel10" in cfg
    assert "vpc 10" in _block(cfg, "port-channel10")
    assert "switchport access vlan 250" in _block(cfg, "port-channel10")
    assert "channel-group 10 mode active" in _block(cfg, port)
    assert "interface port-channel10" in sec_cfg
    assert "channel-group 10 mode active" in _block(sec_cfg, port)


@pytest.mark.parametrize("scenario_id,hostname,model,port", TIER_SCENARIOS)
def test_vpc_po_implicit_without_flag_all_tiers(scenario_id, hostname, model, port):
    """UI used to omit vpc_port_channel — backend must still build Po on pair scenarios."""
    plan = {**ACCESS_PLAN, "interface": port}
    result = ScenarioEngine().apply_scenario(
        scenario_id,
        hostname,
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"interface_plans": [plan]},
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "interface port-channel10" in cfg
    assert f"interface {port}" in cfg


@pytest.mark.parametrize("scenario_id,hostname,model,port", TIER_SCENARIOS)
def test_trunk_vpc_po_all_tiers(scenario_id, hostname, model, port):
    plan = {**TRUNK_PLAN, "interface": port, "vpc_port_channel": True}
    result = ScenarioEngine().apply_scenario(
        scenario_id,
        hostname,
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"interface_plans": [plan]},
    )
    cfg = ConfigEngine().build_config(result["device"])
    po_blk = _block(cfg, "port-channel10")
    assert "switchport mode trunk" in po_blk
    assert "switchport trunk allowed vlan 10,20,30" in po_blk
    assert "vpc 10" in po_blk


def test_40g_core_downlink_member_reserved():
    result = ScenarioEngine().apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    device = result["device"]
    warnings = validate_interface_plans(
        device,
        {
            "interface_plans": [
                {
                    "interface": "Ethernet1/2",
                    "preset": "access_vlan",
                    "vlan_id": 100,
                    "vpc_port_channel": True,
                }
            ]
        },
        vpc_pair=True,
    )
    assert any("Ethernet1/2" in w and "reserved" in w for w in warnings)
    cfg = ConfigEngine().build_config(device)
    assert "interface port-channel10" not in cfg


def test_missing_vlan_warns_before_apply():
    result = ScenarioEngine().apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    warnings = validate_interface_plans(
        result["device"],
        {
            "interface_plans": [
                {
                    "interface": "Ethernet1/8",
                    "preset": "access_vlan",
                    "vpc_port_channel": True,
                    "mode": "access",
                }
            ]
        },
        vpc_pair=True,
    )
    assert any("VLAN ID" in w for w in warnings)


@patch("api.main._enforce_privileged_access")
def test_api_preview_40g_vpc_po_without_generate_pair_flag(_mock):
    """generate_pair only controls export — planner must still render Po in preview."""
    payload = {
        "scenario_id": "vpc_core_pair",
        "hostname": "CORE1-VPC",
        "site_name": "HQ_DC",
        "mgmt_ip": "10.10.10.10/24",
        "mgmt_gw": "10.10.10.1",
        "generate_pair": False,
        "overrides": {
            "interface_plans": [
                {
                    "interface": "Ethernet1/15",
                    "preset": "access_vlan",
                    "vlan_id": 250,
                    "vlan_name": "SERVERS",
                    "description": "Test",
                }
            ],
        },
    }
    res = client.post("/scenario/preview", json=payload)
    assert res.status_code == 200
    cfg = res.json()["config_preview"]
    assert "interface port-channel10" in cfg
    assert "interface Ethernet1/15" in cfg


@patch("api.main._enforce_privileged_access")
def test_api_generate_pair_includes_secondary_po(_mock):
    payload = {
        "scenario_id": "vpc_access_pair",
        "hostname": "ACCESS-SW-01-A",
        "site_name": "HQ",
        "mgmt_ip": "10.10.10.10/24",
        "mgmt_gw": "10.10.10.1",
        "generate_pair": True,
        "overrides": {
            "interface_plans": [
                {
                    "interface": "Ethernet1/12",
                    "preset": "access_vlan",
                    "vpc_port_channel": True,
                    "vlan_id": 55,
                    "vlan_name": "USERS",
                }
            ],
        },
    }
    res = client.post("/scenario/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "interface port-channel10" in data["config_preview"]
    sec = data["pair_preview"]["secondary_config_preview"]
    assert "interface port-channel10" in sec
    assert "channel-group 10 mode active" in sec
