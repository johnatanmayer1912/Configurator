"""UI/UX mandatory — prevent focus-loss re-render on text inputs (v3.7.4 regression)."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

PLANNER_JS = ROOT / "static" / "interface-planner.js"
STATIC_JS = ROOT / "static"


@pytest.mark.mandatory
def test_interface_planner_uses_structural_rerender_guard():
    src = PLANNER_JS.read_text(encoding="utf-8")
    assert "STRUCTURAL_PLAN_FIELDS" in src
    assert "STRUCTURAL_PLAN_FIELDS.has(field)" in src
    assert "renderInterfacePlanner()" in src


@pytest.mark.mandatory
def test_interface_planner_no_inline_oninput_rerender():
    """Inline oninput→updateInterfacePlan caused full innerHTML rebuild every keystroke."""
    src = PLANNER_JS.read_text(encoding="utf-8")
    assert 'oninput="updateInterfacePlan' not in src
    assert 'onchange="updateInterfacePlan' not in src


@pytest.mark.mandatory
def test_interface_planner_delegated_events_and_data_fields():
    src = PLANNER_JS.read_text(encoding="utf-8")
    assert "initInterfacePlannerEvents" in src
    assert 'data-field="description"' in src
    assert "addEventListener(\"input\"" in src
    assert "syncInterfacePlansFromDom" in src


@pytest.mark.mandatory
def test_no_static_js_rebuilds_dom_on_input_handlers():
    """Scan static/*.js for innerHTML assignment inside update handlers (anti-pattern)."""
    offenders: list[str] = []
    for path in STATIC_JS.glob("*.js"):
        if path.name == "interface-planner.js":
            continue  # covered above; structural re-render is guarded
        text = path.read_text(encoding="utf-8")
        if ".innerHTML" in text and "oninput=" in text and "interface-planner" not in path.name:
            # roadmap/app rebuild on click only — flag only if same line couples oninput+innerHTML
            for line in text.splitlines():
                if "oninput=" in line and ".innerHTML" in line:
                    offenders.append(f"{path.name}: {line.strip()[:80]}")
    assert not offenders, "Possible input focus-loss patterns:\n" + "\n".join(offenders)
