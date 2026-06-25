"""Operator UX — wizard JS contracts for planner preflight and payload collection."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.mandatory
def test_interface_planner_preflight_hook_in_app_js():
    app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "interfacePlanPreflightErrors" in app_js
    assert "collectInterfacePlans" in app_js


@pytest.mark.mandatory
def test_build_scenario_payload_includes_interface_plans():
    app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "collectInterfacePlans" in app_js
    assert "interface_plans" in app_js or "collectInterfacePlans?.()" in app_js


@pytest.mark.mandatory
def test_roadmap_sets_generate_pair_for_vpc_scenarios():
    roadmap = (ROOT / "static" / "roadmap.js").read_text(encoding="utf-8")
    assert "generate_pair" in roadmap
    assert "pair_mode" in roadmap


@pytest.mark.mandatory
def test_planner_vpc_scenario_not_tied_to_export_toggle_only():
    planner = (ROOT / "static" / "interface-planner.js").read_text(encoding="utf-8")
    assert "isVpcPairScenario" in planner
    assert "wantsVpcPortChannel" in planner


@pytest.mark.mandatory
def test_configure_step_has_interface_planner_markup():
    html = (ROOT / "templates" / "web" / "index.html").read_text(encoding="utf-8")
    assert "interfacePlanList" in html
    assert "cardInterfacePlanner" in html
    assert "addInterfacePlanRow" in html
