"""OCD Level UI Validations for v6.0.0"""
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates" / "web"
STATIC = ROOT / "static"
INDEX_HTML = TEMPLATES / "index.html"
LINK_PLANNER_JS = STATIC / "vpc-link-planner.js"
STYLES_CSS = STATIC / "styles.css"

@pytest.mark.mandatory
def test_index_html_exists_and_contains_core_elements():
    """Verify index.html structure is robust."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    
    # Must have strict html structure
    assert "<!DOCTYPE html>" in content
    
    # Check all critical IDs and classes for interaction
    critical_ids = [
        "toast", "buildVersion", "offlineBadge",
        "trainingModeToggle", "adminLink", "wizardTipBox",
        "firstRunHint", "step-1", "step-2", "step-3", "step-4", "step-5",
        "modeGrid", "scenarioGrid", "vpcChoiceGrid", "speedGrid",
        "configurePathBanner", "presetStrip", "topologyPanel"
    ]
    for element_id in critical_ids:
        assert f'id="{element_id}"' in content or f"id='{element_id}'" in content, f"Missing critical ID: {element_id}"

@pytest.mark.mandatory
def test_vpc_link_planner_ocd_fixes():
    """Verify the v6.0.0 Link Planner Bugfixes are in place."""
    js_content = LINK_PLANNER_JS.read_text(encoding="utf-8")
    
    # Verify editable preset label is present
    assert 'class="link-plan-label-input"' in js_content, "Link plan label must be an editable input"
    
    # Verify expand logic is bound inline to guarantee execution
    assert 'onclick="expandLinkMembers(this)"' in js_content, "Expand button must have inline onclick binding"
    
    # Verify expand logic has warning rather than silent fail
    assert 'Please enter a range to expand.' in js_content, "Expand must notify user on empty input"

@pytest.mark.mandatory
def test_macos_steve_jobs_aesthetics():
    """Verify Steve Jobs / macOS styling variables are present."""
    css_content = STYLES_CSS.read_text(encoding="utf-8")
    
    assert "--bg-primary: #1c1c1e;" in css_content, "Must use macOS dark mode background"
    assert "SF Pro Text" in css_content, "Must use macOS SF Pro Text typography"
    assert "--radius-sm: 6px;" in css_content, "Must use refined border radii"
    assert "backdrop-filter: blur(20px);" in css_content, "Panels must use macOS glassmorphism"
