"""Tests for Config Builder parser and export naming."""

from core.config_parser import parse_running_config
from core.import_wizard import ConfigBuilderEngine
from utils.export_paths import build_file_prefix, pair_batch_folder


SAMPLE_CONFIG = """
hostname DC-LEAF-01-A
feature interface-vlan
feature vpc
feature lacp
vlan 10
  name USERS
interface mgmt0
  ip address 10.10.10.10/24
vrf context management
  ip route 0.0.0.0/0 10.10.10.1
vpc domain 100
  peer-keepalive destination 10.255.255.2 source 10.255.255.1 vrf management
interface Ethernet1/1
  switchport mode access
  no shutdown
interface Ethernet1/2
  switchport mode access
  no shutdown
ntp server 10.255.255.254
logging server 10.255.255.254 6
"""


def test_parse_running_config_extracts_core_fields():
    parsed = parse_running_config(SAMPLE_CONFIG)
    assert parsed.hostname == "DC-LEAF-01-A"
    assert parsed.mgmt_ip == "10.10.10.10/24"
    assert parsed.mgmt_gw == "10.10.10.1"
    assert parsed.vpc_domain_id == 100
    assert "vpc" in parsed.features
    assert parsed.has_vpc
    assert parsed.detect_role() == "leaf"


def test_builder_recommend_vpc_leaf_from_paste():
    engine = ConfigBuilderEngine()
    answers = {
        "start_mode": "paste",
        "running_config": SAMPLE_CONFIG,
        "device_role": "leaf",
        "redundancy": "vpc",
        "environment": "production",
        "site_name": "HQ_DC",
        "hostname": "DC-LEAF-01-A",
        "mgmt_ip": "10.10.10.10/24",
        "mgmt_gw": "10.10.10.1",
    }
    rec = engine.recommend(answers)
    assert rec["scenario_id"] == "vpc_leaf_pair"
    assert rec["wizard"]["generate_pair"] is True
    assert rec["wizard"]["overrides"]["security_tier"] == "hardened"


def test_export_file_prefix_includes_site_and_scenario():
    prefix = build_file_prefix("HQ_DC", "vpc_leaf_pair", "DC-LEAF-01-A", "20260621_120000")
    assert prefix.startswith("HQ_DC_vpc_leaf_pair_DC-LEAF-01-A_")
    folder = pair_batch_folder("HQ_DC", "vpc_leaf_pair", "20260621_120000")
    assert folder == "HQ_DC_vpc_leaf_pair_20260621_120000"
