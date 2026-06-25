"""Field engineer — vPC interface planner mandatory regression (40G / 10G / 1G)."""

import pytest

from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine

TIER_SCENARIOS = [
    ("vpc_core_pair", "CORE1-VPC-A", "Ethernet1/15"),
    ("vpc_leaf_pair", "DC-LEAF-01-A", "Ethernet1/5"),
    ("vpc_access_pair", "ACCESS-SW-01-A", "Ethernet1/10"),
]

ACCESS_PLAN = {
    "preset": "access_vlan",
    "mode": "access",
    "vlan_id": 250,
    "vlan_name": "SERVERS",
    "description": "Mandatory_QA_Host",
}


def _apply(scenario_id: str, hostname: str, port: str, **plan_extra):
    plan = {**ACCESS_PLAN, "interface": port, **plan_extra}
    return ScenarioEngine().apply_scenario(
        scenario_id,
        hostname,
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"interface_plans": [plan]},
    )


def _block(cfg: str, name: str) -> str:
    start = cfg.find(f"interface {name}")
    assert start >= 0, f"{name} missing"
    end = cfg.find("\ninterface ", start + 1)
    return cfg[start : end if end > 0 else len(cfg)]


@pytest.mark.mandatory
@pytest.mark.parametrize("scenario_id,hostname,port", TIER_SCENARIOS)
def test_vpc_po_created_all_tiers_implicit_flag(scenario_id, hostname, port):
    """Planner may omit vpc_port_channel — backend must still build Po on pair scenarios."""
    result = _apply(scenario_id, hostname, port)
    cfg = ConfigEngine().build_config(result["device"])
    assert "interface port-channel10" in cfg
    assert f"interface {port}" in cfg
    assert "vpc 10" in _block(cfg, "port-channel10")
    assert "channel-group 10 mode active" in _block(cfg, port)


@pytest.mark.mandatory
@pytest.mark.parametrize("scenario_id,hostname,port", TIER_SCENARIOS)
def test_vpc_po_mirrored_on_secondary(scenario_id, hostname, port):
    result = _apply(scenario_id, hostname, port, vpc_port_channel=True)
    sec = result["pair"]["secondary"]["device"]
    sec_cfg = ConfigEngine().build_config(sec)
    assert "interface port-channel10" in sec_cfg
    assert "channel-group 10 mode active" in _block(sec_cfg, port)


@pytest.mark.mandatory
def test_40g_core_downlink_port_reserved_from_planner():
    result = ScenarioEngine().apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "interface_plans": [
                {
                    "interface": "Ethernet1/2",
                    "preset": "access_vlan",
                    "vlan_id": 100,
                    "vpc_port_channel": True,
                }
            ]
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "interface port-channel10" not in cfg
    assert result.get("planner_warnings")


@pytest.mark.mandatory
def test_missing_vlan_surfaces_planner_warning():
    result = ScenarioEngine().apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "interface_plans": [
                {
                    "interface": "Ethernet1/8",
                    "preset": "access_vlan",
                    "vpc_port_channel": True,
                    "mode": "access",
                }
            ]
        },
    )
    warnings = result.get("planner_warnings") or []
    assert any("VLAN ID" in w for w in warnings)
