"""vPC pair support across speed tiers — 40G core, 10G leaf, 1G access."""

from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine


def _cfg(scenario_id: str, hostname: str, **overrides):
    result = ScenarioEngine().apply_scenario(
        scenario_id,
        hostname,
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides=overrides or None,
    )
    return result, ConfigEngine().build_config(result["device"])


def _block(cfg: str, name: str) -> str:
    start = cfg.find(f"interface {name}")
    assert start >= 0, f"{name} missing from config"
    end = cfg.find("\ninterface ", start + 1)
    return cfg[start:end if end > 0 else len(cfg)]


def test_40g_vpc_core_pair_hardware_ports_and_downlinks():
    result, cfg = _cfg("vpc_core_pair", "CORE1-VPC")
    vpc = result["device"].vpc
    assert vpc.peer_link_interfaces == ["Ethernet1/35", "Ethernet1/36"]
    assert vpc.keepalive_interfaces == ["Ethernet1/33", "Ethernet1/34"]
    assert "interface port-channel20" in cfg
    assert "interface port-channel21" in cfg
    assert result["pair"]["secondary"]["device"].hostname == "CORE1-VPC-B"
    sec_cfg = ConfigEngine().build_config(result["pair"]["secondary"]["device"])
    assert "interface port-channel1" in sec_cfg
    assert "Ethernet1/35" in sec_cfg


def test_40g_vpc_core_infra_no_bulk_access():
    result, cfg = _cfg("vpc_core_pair", "CORE1-VPC")
    access = [i for i in result["device"].interfaces if i.mode == "access"]
    assert len(access) == 0
    assert "Access_Port_" not in cfg


def test_1g_vpc_access_pair_hardware_ports():
    result, cfg = _cfg("vpc_access_pair", "ACCESS-SW-01-A")
    vpc = result["device"].vpc
    assert vpc is not None
    assert vpc.peer_link_interfaces == ["Ethernet1/51", "Ethernet1/52"]
    assert vpc.keepalive_interfaces == ["Ethernet1/47", "Ethernet1/48"]
    assert "feature vpc" in cfg
    assert "interface port-channel1" in cfg
    assert "interface port-channel2" in cfg
    assert "interface Ethernet1/49" in cfg
    assert "switchport mode trunk" in _block(cfg, "Ethernet1/49")


def test_1g_vpc_access_pair_secondary_mirrored():
    result, _ = _cfg("vpc_access_pair", "ACCESS-SW-01-A")
    pri = result["device"]
    sec = result["pair"]["secondary"]["device"]
    assert sec.hostname == "ACCESS-SW-01-B"
    assert pri.vpc.local_keepalive_ip == sec.vpc.remote_keepalive_ip
    assert pri.vpc.remote_keepalive_ip == sec.vpc.local_keepalive_ip
    pri_pl = next(po for po in pri.port_channels if po.vpc_peer_link)
    sec_pl = next(po for po in sec.port_channels if po.vpc_peer_link)
    assert pri_pl.member_interfaces == sec_pl.member_interfaces == ["Ethernet1/51", "Ethernet1/52"]


def test_1g_vpc_access_infra_only_no_bulk_access():
    result, cfg = _cfg("vpc_access_pair", "ACCESS-SW-01-A")
    access = [i for i in result["device"].interfaces if i.mode == "access"]
    assert len(access) == 0
    assert "Access_Port_" not in cfg


def test_1g_standalone_still_no_vpc():
    result, cfg = _cfg("standalone_access", "ACCESS-SW-01")
    assert result["device"].vpc is None
    assert "vpc domain" not in cfg
    assert result["pair_mode"] is False


def test_1g_vpc_access_interface_planner_po_mirrored():
    plans = [
        {
            "interface": "Ethernet1/10",
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 20,
            "vlan_name": "USERS",
            "description": "Closet_Port_10",
        }
    ]
    result, cfg = _cfg("vpc_access_pair", "ACCESS-SW-01-A", interface_plans=plans)
    pri_po = next(po for po in result["device"].port_channels if po.number == 10)
    sec_po = next(po for po in result["pair"]["secondary"]["device"].port_channels if po.number == 10)
    assert pri_po.access_vlan == 20
    assert sec_po.access_vlan == 20
    assert "interface port-channel10" in cfg
    assert "vpc 10" in _block(cfg, "port-channel10")
    sec_cfg = ConfigEngine().build_config(result["pair"]["secondary"]["device"])
    assert "channel-group 10 mode active" in _block(sec_cfg, "Ethernet1/10")


def test_1g_vpc_reserved_peer_port_not_overridden_by_planner():
    plans = [
        {
            "interface": "Ethernet1/51",  # Changed from 53 to actual reserved peer-link port
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 99,
        }
    ]
    result, _ = _cfg(
        "vpc_access_pair",
        "ACCESS-SW-01-A",
        interface_plans=plans,
        uplink_options={"uplink_fiber_pair": False, "uplink_fiber_quad": False},
    )
    assert not any(po.number >= 10 for po in result["device"].port_channels)
    intf = next(i for i in result["device"].interfaces if i.name == "Ethernet1/51")
    assert intf.channel_group == 1


def test_all_tier_vpc_scenarios_declared_in_catalog():
    engine = ScenarioEngine()
    ids = {s["id"] for s in engine.catalog.list_scenarios()}
    assert {"vpc_core_pair", "vpc_leaf_pair", "vpc_access_pair"}.issubset(ids)


def test_40g_core_vpc_with_custom_model_override():
    result, _ = _cfg("vpc_core_pair", "CORE1-VPC", model="Nexus 9336C-FX2")
    assert result["device"].model == "Nexus 9336C-FX2"
    assert result["device"].vpc.peer_link_interfaces == ["Ethernet1/35", "Ethernet1/36"]
