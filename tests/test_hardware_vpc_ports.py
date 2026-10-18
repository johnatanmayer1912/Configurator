"""Hardware profile vPC port mapping and leaf keepalive CLI validation."""

from pathlib import Path

import yaml

from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine


def _load_hardware_profiles():
    path = Path(__file__).resolve().parents[1] / "hardware_profiles.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))["profiles"]


def test_each_hardware_profile_has_distinct_vpc_ports():
    profiles = _load_hardware_profiles()
    vpc_models = [
        p for p in profiles
        if p.get("vpc_peer_link") and p.get("vpc_keepalive")
    ]
    assert len(vpc_models) >= 2
    by_model = {}
    for p in vpc_models:
        name = p["display_name"]
        by_model[name] = {
            "peer": tuple(p["vpc_peer_link"]),
            "keepalive": tuple(p["vpc_keepalive"]),
        }
    assert by_model["Nexus 9336C-FX2"]["peer"] == ("Ethernet1/35", "Ethernet1/36")
    assert by_model["Nexus 9336C-FX2"]["keepalive"] == ("Ethernet1/33", "Ethernet1/34")
    assert by_model["Nexus 93180YC-EX"]["peer"] == ("Ethernet1/51", "Ethernet1/52")
    assert by_model["Nexus 93180YC-EX"]["keepalive"] == ("Ethernet1/49", "Ethernet1/50")
    assert by_model["Nexus 9348GC-FXP"]["peer"] == ("Ethernet1/51", "Ethernet1/52")
    assert by_model["Nexus 9348GC-FXP"]["keepalive"] == ("Ethernet1/47", "Ethernet1/48")
    for name, ports in by_model.items():
        overlap = set(ports["peer"]) & set(ports["keepalive"])
        assert not overlap, f"{name}: peer-link and keepalive must not overlap"


def test_scenario_engine_uses_hardware_vpc_ports_per_model():
    engine = ScenarioEngine()
    cases = [
        ("vpc_core_pair", "Nexus 9336C-FX2", ("Ethernet1/35", "Ethernet1/36"), ("Ethernet1/33", "Ethernet1/34")),
        ("vpc_leaf_pair", "Nexus 93180YC-EX", ("Ethernet1/51", "Ethernet1/52"), ("Ethernet1/49", "Ethernet1/50")),
        ("vpc_access_pair", "Nexus 9348GC-FXP", ("Ethernet1/51", "Ethernet1/52"), ("Ethernet1/47", "Ethernet1/48")),
    ]
    for scenario_id, model, peer, keepalive in cases:
        result = engine.apply_scenario(
            scenario_id,
            "TEST-SW-01",
            "HQ",
            "10.10.10.10/24",
            "10.10.10.1",
            overrides={"model": model},
        )
        vpc = result["device"].vpc
        assert tuple(vpc.peer_link_interfaces) == peer
        assert tuple(vpc.keepalive_interfaces) == keepalive


def test_leaf_keepalive_ports_are_lag_members_not_bare():
    result = ScenarioEngine().apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    device = result["device"]
    for port in ("Ethernet1/49", "Ethernet1/50"):
        intf = next(i for i in device.interfaces if i.name == port)
        assert intf.channel_group == 2
        assert intf.mode == "routed"
        assert "KEEPALIVE" in (intf.description or "")

    cfg = ConfigEngine().build_config(device)
    for port in ("Ethernet1/49", "Ethernet1/50"):
        block_start = cfg.index(f"interface {port}")
        block = cfg[block_start:block_start + 200]
        assert "channel-group 2 mode active" in block
        assert "description Part_Of_Vpc_KEEPALIVE" in block


def test_leaf_no_default_access_ports_use_interface_planner_instead():
    """Infra-only leaf — access via interface_plans when needed."""
    result = ScenarioEngine().apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    for port in ("Ethernet1/43", "Ethernet1/44"):
        intf = next((i for i in result["device"].interfaces if i.name == port), None)
        assert intf is None or intf.mode == "bare"
    result2 = ScenarioEngine().apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "interface_plans": [
                {
                    "interface": "Ethernet1/43",
                    "preset": "access_vlan",
                    "vpc_port_channel": True,
                    "mode": "access",
                    "vlan_id": 100,
                }
            ]
        },
    )
    intf = next(i for i in result2["device"].interfaces if i.name == "Ethernet1/43")
    assert intf.channel_group == 10
