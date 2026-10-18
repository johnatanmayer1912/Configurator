"""QA Pass 1 & 2 regression tests — v2.9.0 export, parser, version templates."""

from core.config_parser import parse_running_config
from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine
from core.import_wizard import ConfigBuilderEngine
from utils.export_paths import build_file_prefix, pair_batch_folder


PEER_LINK_CONFIG = """
hostname DC-LEAF-01-A
feature vpc
feature lacp
vpc domain 100
interface port-channel1
  switchport mode trunk
  vpc peer-link
interface Ethernet1/53
  channel-group 1 mode active
  no shutdown
interface Ethernet1/54
  channel-group 1 mode active
  no shutdown
"""


def test_parse_peer_link_members_from_running_config():
    parsed = parse_running_config(PEER_LINK_CONFIG)
    assert parsed.vpc_domain_id == 100
    assert "Ethernet1/53" in parsed.vpc_peer_link_interfaces
    assert "Ethernet1/54" in parsed.vpc_peer_link_interfaces


def test_vpc_arp_sync_in_all_version_renders():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    for version in ("9.3", "10.2", "10.3", "7.0"):
        result = engine.apply_scenario(
            "vpc_leaf_pair",
            "DC-LEAF-01-A",
            "HQ",
            "10.10.10.10/24",
            "10.10.10.1",
            overrides={"nxos_version": version},
        )
        cfg = config_engine.build_config(result["device"])
        assert "ip arp synchronize" in cfg, version
        if version == "7.0":
            assert "role priority 4096" in cfg
            assert "\n  peer-gateway\n" not in cfg
            assert "auto-recovery" not in cfg.split("vpc domain")[1].split("!")[0]
        else:
            assert "role priority 4096" in cfg
            assert "peer-gateway" in cfg


def test_legacy_template_storm_control_on_access():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    for version in ("9.3", "7.0"):
        result = engine.apply_scenario(
            "standalone_access",
            "ACCESS-01",
            "LAB",
            "10.10.10.10/24",
            "10.10.10.1",
            overrides={"nxos_version": version},
        )
        cfg = config_engine.build_config(result["device"])
        assert "storm-control broadcast" in cfg, version
        if version == "9.3":
            assert "interface Ethernet1/49" in cfg


def test_builder_spine_ignores_vpc_redundancy():
    engine = ConfigBuilderEngine()
    rec = engine.recommend(
        {
            "device_role": "spine",
            "redundancy": "vpc",
            "fabric": "no",
            "environment": "lab",
            "site_name": "HQ",
            "hostname": "SPINE-01",
            "mgmt_ip": "10.0.0.1/24",
            "mgmt_gw": "10.0.0.254",
        }
    )
    assert rec["scenario_id"] == "vpc_core_pair"
    assert rec["wizard"]["generate_pair"] is True


def test_builder_vxlan_standalone_uses_leaf_not_pair():
    engine = ConfigBuilderEngine()
    rec = engine.recommend(
        {
            "device_role": "leaf",
            "redundancy": "standalone",
            "fabric": "yes",
            "environment": "lab",
            "site_name": "HQ",
            "hostname": "LEAF-01",
            "mgmt_ip": "10.0.0.1/24",
            "mgmt_gw": "10.0.0.254",
        }
    )
    assert rec["scenario_id"] == "standalone_leaf"
    assert rec["wizard"]["generate_pair"] is False
    assert "vxlan" in rec["wizard"]["overrides"]["features"]


def test_export_naming_pair_folder():
    folder = pair_batch_folder("SITE_A", "vpc_leaf_pair", "20260621_180000")
    assert folder == "SITE_A_vpc_leaf_pair_20260621_180000"
    prefix = build_file_prefix("SITE_A", "vpc_leaf_pair", "SW-01", "20260621_180000")
    assert prefix == "SW-01_20260621_180000"
