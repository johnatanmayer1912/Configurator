"""Product architect — scenario catalog, matrix parity, vPC tier declarations."""

import pytest

from core.catalog_loader import CatalogLoader
from core.scenario_engine import ScenarioEngine


@pytest.mark.mandatory
def test_config_matrix_matches_scenario_catalog():
    catalog = CatalogLoader()
    scenario_ids = {s["id"] for s in catalog.list_scenarios()}
    matrix_ids = {m["scenario_id"] for m in catalog.list_config_matrix()}
    assert scenario_ids == matrix_ids


@pytest.mark.mandatory
def test_all_vpc_pair_scenarios_declared():
    engine = ScenarioEngine()
    ids = {s["id"] for s in engine.catalog.list_scenarios()}
    assert {"vpc_core_pair", "vpc_leaf_pair", "vpc_access_pair"}.issubset(ids)


@pytest.mark.mandatory
@pytest.mark.parametrize(
    "scenario_id,redundancy,pair_mode,role",
    [
        ("vpc_core_pair", "vpc", True, "spine"),
        ("vpc_leaf_pair", "vpc", True, "leaf"),
        ("vpc_access_pair", "vpc", True, "access"),
        ("standalone_access", "standalone", False, "access"),
    ],
)
def test_vpc_tier_scenario_metadata(scenario_id, redundancy, pair_mode, role):
    catalog = CatalogLoader()
    sc = catalog.get_scenario(scenario_id)
    assert sc is not None
    assert sc.get("redundancy") == redundancy
    assert bool(sc.get("pair_mode")) is pair_mode
    assert sc.get("role") == role


@pytest.mark.mandatory
def test_vpc_pair_scenarios_default_infra_only():
    catalog = CatalogLoader()
    for sid in ("vpc_core_pair", "vpc_leaf_pair", "vpc_access_pair"):
        sc = catalog.get_scenario(sid)
        defaults = sc.get("defaults") or {}
        assert defaults.get("interface_count") == 0, f"{sid} should be infra-only"
        assert defaults.get("bring_up_spare_ports") is False, f"{sid} spare ports off"


@pytest.mark.mandatory
def test_interface_presets_catalog_for_planner():
    catalog = CatalogLoader()
    presets = catalog.list_interface_presets()
    ids = {p["id"] for p in presets}
    assert {"access_vlan", "trunk_all", "trunk_custom", "bring_up", "custom"}.issubset(ids)
    assert catalog.get_interface_po_start() >= 10
