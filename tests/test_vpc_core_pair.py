"""Tests for vPC Core Pair (40G) scenario — CORE1_VPC template alignment."""

from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine


def test_vpc_core_pair_uses_9336c_peer_and_keepalive_ports():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1_VPC",
        "NETWORK_NAME",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    vpc = result["device"].vpc
    assert vpc is not None
    assert vpc.peer_link_interfaces == ["Ethernet1/35", "Ethernet1/36"]
    assert vpc.keepalive_interfaces == ["Ethernet1/33", "Ethernet1/34"]
    assert vpc.keepalive_vrf == "VPC_Keep_Alive"
    assert vpc.peer_link_id == 1
    assert vpc.keepalive_po_id == 2


def test_vpc_core_pair_renders_institutional_baseline_and_downlinks():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1_VPC",
        "NETWORK_NAME",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    cfg = config_engine.build_config(result["device"])
    assert "cfs eth distribute" in cfg
    assert "cli alias name wr copy running startup" in cfg
    assert "peer-switch" in cfg
    assert "delay restore 150" in cfg
    assert "interface port-channel20" in cfg
    assert "Connected_to_NET_LEAF_10G_SW1+SW2" in cfg
    assert "interface port-channel21" in cfg
    assert "Connected_to_NET_LEAF_1G_SW1+SW2" in cfg
    assert "Ethernet1/35" in cfg
    assert "channel-group 1 mode active" in cfg
    assert "vrf context VPC_Keep_Alive" in cfg
    assert "role priority 1000" in cfg
    assert "system-priority 20000" in cfg


def test_vpc_core_pair_secondary_swaps_keepalive():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1_VPC",
        "NETWORK_NAME",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    secondary = result["pair"]["secondary"]["device"]
    assert secondary.vpc.local_keepalive_ip == "1.1.1.2"
    assert secondary.vpc.remote_keepalive_ip == "1.1.1.1"
    assert secondary.vpc.role_priority == 2000


def test_downlink_toggle_disables_port_channel():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1_VPC",
        "NETWORK_NAME",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"downlink_options": {"downlink_10g_leaf": False, "downlink_1g_leaf": True}},
    )
    cfg = config_engine.build_config(result["device"])
    assert "port-channel20" not in cfg
    assert "port-channel21" in cfg


def test_unused_ports_bare_no_switchport_no_spare_description():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"bring_up_spare_ports": True},
    )
    cfg = config_engine.build_config(result["device"])
    assert "description SPARE" not in cfg
    # Sample bare port block
    assert "interface Ethernet1/7\n  no shutdown" in cfg
