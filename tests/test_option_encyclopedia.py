"""Tests for option encyclopedia and new baseline options."""

from core.catalog_loader import CatalogLoader
from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine


def test_catalog_includes_option_help():
    catalog = CatalogLoader()
    help_map = catalog.get_option_help()
    assert "mode_core" in help_map
    assert "baseline_no_dns_lookup" in help_map
    assert help_map["hostname"]["summary"]


def test_no_dns_lookup_in_generated_config():
    engine = ScenarioEngine()
    config_engine = ConfigEngine()
    result = engine.apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "NETWORK_NAME",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "baseline_options": [
                "baseline_cfs",
                "baseline_copp",
                "baseline_no_dns_lookup",
            ],
        },
    )
    cfg = config_engine.build_config(result["device"])
    assert "no ip domain-lookup" in cfg
