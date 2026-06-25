"""Tests for Configuration Studio remarks — no false-positive token scan."""

from core.catalog_loader import CatalogLoader
from core.config_remarks import ConfigRemarksEngine, build_cli_blocks
from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine


def test_config_matrix_has_all_scenarios():
    catalog = CatalogLoader()
    scenario_ids = {s["id"] for s in catalog.list_scenarios()}
    matrix_ids = {m["scenario_id"] for m in catalog.list_config_matrix()}
    assert scenario_ids == matrix_ids


def test_hardware_profiles_have_speed_badges():
    catalog = CatalogLoader()
    for profile in catalog.list_hardware_profiles():
        if profile["display_name"] == "Generic":
            continue
        assert profile.get("primary_speed_label")
        assert profile.get("device_class")


def test_lab_ready_with_defaults_no_false_positive_tokens():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    remarks = ConfigRemarksEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    cfg = config_engine.build_config(result["device"])
    analysis = remarks.analyze(result["device"], cfg, {"site_name": "HQ_DC"})
    messages = " ".join(r.get("message", "") for r in analysis["remarks"])
    assert analysis["lab_ready"] is True
    assert analysis["pending_count"] == 0
    for noise in ("FATAL", "CRITICAL", "ACCESS", "POST", "PASTE", "BPDU", "USER_10", "INTENT_SVI"):
        assert noise not in messages


def test_production_snmp_not_in_config_without_hosts():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    remarks = ConfigRemarksEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    cfg = config_engine.build_config(result["device"])
    assert "SNMP_SERVER_HOST1" not in cfg
    analysis = remarks.analyze(result["device"], cfg, {"site_name": "HQ_DC"})
    assert not any(r.get("token") == "SNMP_SERVER_HOST1" for r in analysis["remarks"])


def test_remarks_clear_when_snmp_fields_set():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    remarks = ConfigRemarksEngine()
    overrides = {
        "snmp_trap_host_1": "10.0.0.50",
        "snmp_v3_user": "monitor",
        "site_location": "DC1-Rack-A",
        "site_name": "HQ_DC",
    }
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides=overrides,
    )
    cfg = config_engine.build_config(result["device"])
    assert "10.0.0.50" in cfg
    analysis = remarks.analyze(result["device"], cfg, overrides)
    assert not any(r.get("token") == "SNMP_SERVER_HOST1" for r in analysis["remarks"])


def test_spare_ports_no_shutdown_in_core_config():
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
    assert cfg.count("no shutdown") >= 10
    # Bare spare block: interface + no shutdown only (no routed no switchport)
    assert "interface Ethernet1/5\n  no shutdown" in cfg or "interface Ethernet1/10\n  no shutdown" in cfg


def test_cli_blocks_include_vpc_for_core():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    blocks = build_cli_blocks(result["device"], overrides={"downlink_options": {"downlink_10g_leaf": True}})
    ids = {b["id"] for b in blocks}
    assert "vpc_domain" in ids
    assert "downlink_10g_leaf" in ids


def test_boot_image_in_render():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"nxos_version": "9.3"},
    )
    cfg = config_engine.build_config(result["device"])
    assert "boot nxos bootflash:/nxos.9.3.5.bin" in cfg
