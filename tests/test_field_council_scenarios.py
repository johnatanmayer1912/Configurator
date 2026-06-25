"""Field Engineer Council acceptance tests — S1–S8 scenarios (v3.4.0)."""

from core.config_parser import parse_running_config
from core.engine import ConfigEngine
from core.import_wizard import ConfigBuilderEngine
from core.scenario_engine import ScenarioEngine


def _cfg(scenario_id: str, hostname: str, **overrides):
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        scenario_id,
        hostname,
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides=overrides or None,
    )
    config = ConfigEngine().build_config(result["device"])
    return result, config


def test_s1_vpc_core_pair_institutional():
    result, cfg = _cfg("vpc_core_pair", "CORE1-VPC")
    assert "peer-gateway" in cfg
    assert "interface port-channel20" in cfg
    assert "cfs eth distribute" in cfg
    assert "description SPARE" not in cfg
    assert "interface Ethernet1/7" not in cfg or "no shutdown" in cfg.split("Ethernet1/7")[1].split("interface")[0]
    sec = result["pair"]["secondary"]["device"]
    assert sec.hostname == "CORE1-VPC-B"
    assert sec.vpc.local_keepalive_ip == "1.1.1.2"


def test_s2_vpc_leaf_pair_infra_only_by_default():
    result, cfg = _cfg("vpc_leaf_pair", "DC-LEAF-01-A")
    assert "feature vpc" in cfg
    assert "vpc domain" in cfg
    assert "interface port-channel1" in cfg
    access = [i for i in result["device"].interfaces if i.mode == "access"]
    assert len(access) == 0
    assert "Access_Port_" not in cfg
    assert result["device"].vpc.peer_link_id == 1


def test_s2_vpc_leaf_interface_plan_storm_on_access_po():
    plans = [
        {
            "interface": "Ethernet1/5",
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 100,
            "vlan_name": "FABRIC_100",
        }
    ]
    result, cfg = _cfg("vpc_leaf_pair", "DC-LEAF-01-A", interface_plans=plans)
    assert "interface port-channel10" in cfg
    assert "storm-control broadcast" in _block(cfg, "port-channel10")
    sec_cfg = ConfigEngine().build_config(result["pair"]["secondary"]["device"])
    assert "interface port-channel10" in sec_cfg
    assert "channel-group 10 mode active" in _block(sec_cfg, "Ethernet1/5")


def _block(cfg: str, name: str) -> str:
    marker = f"interface {name}"
    start = cfg.find(marker)
    end = cfg.find("\ninterface ", start + 1)
    return cfg[start:end if end > 0 else len(cfg)]


def test_s3_standalone_leaf_no_vpc():
    _, cfg = _cfg("standalone_leaf", "DC-LEAF-STAGE-01")
    assert "vpc domain" not in cfg
    assert "INTENT_" not in cfg


def test_s4_standalone_access_uplinks_and_storm():
    _, cfg = _cfg("standalone_access", "ACCESS-SW-01")
    assert "storm-control broadcast" in cfg
    assert "interface Ethernet1/49" in cfg
    assert "switchport mode trunk" in cfg.split("Ethernet1/49")[1].split("interface")[0]


def test_s4b_vpc_access_pair_1g():
    result, cfg = _cfg("vpc_access_pair", "ACCESS-SW-01-A")
    assert "feature vpc" in cfg
    assert "interface port-channel1" in cfg
    assert result["pair"]["secondary"]["device"].hostname == "ACCESS-SW-01-B"
    assert "vpc domain" in cfg
    access = [i for i in result["device"].interfaces if i.mode == "access"]
    assert len(access) == 0


def test_s5_mgmt_oob_minimal():
    _, cfg = _cfg("mgmt_oob", "NXOS-SW-01")
    assert "interface mgmt0" in cfg
    assert "vpc domain" not in cfg
    assert cfg.count("feature ") <= 8


def test_s6_hardened_preset_cli():
    _, cfg = _cfg(
        "vpc_core_pair",
        "CORE1-VPC",
        security_tier="hardened",
        snmp_trap_host_1="10.0.0.50",
        snmp_v3_user="monitor",
        site_location="DC1-Rack-A",
    )
    assert "no ip domain-lookup" in cfg
    assert "copp profile strict" in cfg
    assert "logging source-interface mgmt0" in cfg


def test_s7_config_builder_paste_peer_link():
    running = """
hostname DC-LEAF-01-A
feature vpc
vpc domain 100
interface port-channel1
  vpc peer-link
interface Ethernet1/53
  channel-group 1 mode active
interface Ethernet1/54
  channel-group 1 mode active
"""
    parsed = parse_running_config(running)
    assert parsed.vpc_domain_id == 100
    assert "Ethernet1/53" in parsed.vpc_peer_link_interfaces
    assert "Ethernet1/54" in parsed.vpc_peer_link_interfaces
    rec = ConfigBuilderEngine().recommend(
        {
            "start_mode": "paste",
            "running_config": running,
            "device_role": "leaf",
            "redundancy": "vpc",
            "environment": "production",
            "site_name": "HQ_DC",
            "hostname": "DC-LEAF-01-A",
            "mgmt_ip": "10.10.10.10/24",
            "mgmt_gw": "10.10.10.1",
        }
    )
    assert rec["scenario_id"] == "vpc_leaf_pair"
    assert rec["wizard"]["generate_pair"] is True
    det = rec.get("detection") or {}
    assert "Ethernet1/53" in det.get("vpc_peer_link_interfaces", [])


def test_s8_pair_secondary_hostname_and_keepalive():
    result, _ = _cfg("vpc_leaf_pair", "DC-LEAF-01-A")
    sec = result["pair"]["secondary"]["device"]
    assert sec.hostname == "DC-LEAF-01-B"
    pri = result["device"]
    assert pri.vpc.local_keepalive_ip == sec.vpc.remote_keepalive_ip
    assert pri.vpc.remote_keepalive_ip == sec.vpc.local_keepalive_ip


def test_s9_spine_core_40g_no_vpc():
    result, cfg = _cfg("spine_core", "CORE-SPINE-01")
    assert "vpc domain" not in cfg
    assert result["device"].model == "Nexus 9336C-FX2"


def test_speed_tier_models():
    engine = ScenarioEngine()
    cases = [
        ("vpc_core_pair", "Nexus 9336C-FX2"),
        ("vpc_leaf_pair", "Nexus 93180YC-EX"),
        ("vpc_access_pair", "Nexus 9348GC-FXP"),
        ("standalone_access", "Nexus 9348GC-FXP"),
    ]
    for scen, model in cases:
        r = engine.apply_scenario(scen, "TEST-01", "HQ", "10.10.10.10/24", "10.10.10.1")
        assert r["device"].model == model


def test_vxlan_leaf_peer_topology_without_core_downlinks():
    result, cfg = _cfg("vxlan_evpn_leaf", "LEAF-VX-01-A")
    assert "feature nv overlay" in cfg
    assert result["device"].port_channels
    assert any(po.vpc_peer_link for po in result["device"].port_channels)
    assert "Connected_to_NET_LEAF_10G" not in cfg
    assert "Connected_to_NET_LEAF_1G" not in cfg
    assert result["device"].baseline_options


def test_tacacs_server_renders_when_filled():
    catalog = ScenarioEngine().catalog
    scenario = catalog.get_scenario("vpc_core_pair")
    features = list(scenario["defaults"]["features"]) + ["aaa_tacacs"]
    _, cfg = _cfg(
        "vpc_core_pair",
        "CORE1-VPC",
        security_tier="hardened",
        features=features,
        tacacs_server_1="10.0.0.10",
        tacacs_key="01020304",
    )
    assert "aaa group server tacacs+ ACS-TACACS" in cfg
    assert "tacacs-server host 10.0.0.10" in cfg
