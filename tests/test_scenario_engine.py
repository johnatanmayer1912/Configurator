"""Zero-trust regression tests for scenario engine and templates."""

from core.catalog_loader import CatalogLoader
from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine


def test_all_scenarios_render_valid_feature_lines():
    catalog = CatalogLoader()
    engine = ScenarioEngine(catalog)
    config_engine = ConfigEngine()
    for scenario in catalog.list_scenarios():
        result = engine.apply_scenario(
            scenario["id"], "TEST-SW-01", "LAB", "10.10.10.10/24", "10.10.10.1"
        )
        cfg = config_engine.build_config(result["device"])
        assert "feature interface-vlanfeature" not in cfg, scenario["id"]
        if "interface_vlan" in result["enabled_features"]:
            assert "feature interface-vlan" in cfg, scenario["id"]


def test_vpc_leaf_pair_uses_hardware_peer_link_ports():
    catalog = CatalogLoader()
    engine = ScenarioEngine(catalog)
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"peer_link_interfaces": "Ethernet1/53, Ethernet1/54"},
    )
    vpc = result["device"].vpc
    assert vpc is not None
    assert "Ethernet1/53" in vpc.peer_link_interfaces
    assert "Ethernet1/49" not in vpc.peer_link_interfaces


def test_vpc_pair_secondary_hostname():
    catalog = CatalogLoader()
    engine = ScenarioEngine(catalog)
    result = engine.apply_scenario(
        "vpc_leaf_pair", "DC-LEAF-01-A", "HQ", "10.10.10.10/24", "10.10.10.1"
    )
    assert result["pair"]["secondary"]["hostname"] == "DC-LEAF-01-B"
