"""Mandatory v5 — professional UX, link allocator, cable plan, admin Po map, DOM contracts."""

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from core.cable_plan import build_cable_plan, render_cable_plan_md
from core.catalog_loader import CatalogLoader
from core.hostname_rules import suggest_hostname, validate_hostname, validate_site_code
from core.link_allocator import (
    build_reserved_inventory,
    port_budget,
    suggest_members,
    validate_link_row,
)
from core.po_map_store import load_po_map, next_free_po, ranges_for_model, save_po_map
from core.version_diff import compare_versions

ROOT = Path(__file__).resolve().parents[2]
client = TestClient(app)
CATALOG = CatalogLoader()


@pytest.mark.mandatory
def test_po_collision_detects_and_suggests_next_id():
    inv = build_reserved_inventory(
        model="Nexus 9336C-FX2",
        peer_link_interfaces=["Ethernet1/53", "Ethernet1/54"],
        keepalive_interfaces=["Ethernet1/51"],
        link_rows=[
            {"enabled": True, "po_id": 20, "members": ["Ethernet1/1", "Ethernet1/2"], "description": "Downlink A"},
        ],
    )
    result = validate_link_row(
        {"po_id": 20, "members": ["Ethernet1/3", "Ethernet1/4"], "link_kind": "downlink"},
        inv,
        "Nexus 9336C-FX2",
    )
    assert result["valid"] is False
    assert any(c["type"] == "po_id" for c in result["conflicts"])
    assert result["suggestions"]["next_po_id"] == 21


@pytest.mark.mandatory
def test_member_port_collision_detected():
    inv = build_reserved_inventory(
        model="Nexus 93180YC-EX",
        link_rows=[{"enabled": True, "po_id": 30, "members": ["Ethernet1/49", "Ethernet1/50"]}],
    )
    result = validate_link_row(
        {"po_id": 31, "members": ["Ethernet1/49"], "link_kind": "uplink"},
        inv,
        "Nexus 93180YC-EX",
    )
    assert result["valid"] is False
    assert any(c["type"] == "member" for c in result["conflicts"])


@pytest.mark.mandatory
def test_suggest_members_fiber_skips_reserved():
    hw = CATALOG.get_hardware_profile("Nexus 93180YC-EX")
    inv = build_reserved_inventory(
        model="Nexus 93180YC-EX",
        peer_link_interfaces=hw.get("vpc_peer_link") or [],
        keepalive_interfaces=hw.get("vpc_keepalive") or [],
    )
    ports = suggest_members(hw_profile=hw, pool="fiber", count=2, inventory=inv)
    assert len(ports) == 2
    assert all(p.startswith("Ethernet1/") for p in ports)
    for p in (hw.get("vpc_peer_link") or []) + (hw.get("vpc_keepalive") or []):
        assert p not in ports


@pytest.mark.mandatory
def test_port_budget_reports_free_count():
    hw = CATALOG.get_hardware_profile("Nexus 9336C-FX2")
    inv = build_reserved_inventory(
        model="Nexus 9336C-FX2",
        peer_link_interfaces=["Ethernet1/53", "Ethernet1/54"],
        keepalive_interfaces=["Ethernet1/51"],
    )
    budget = port_budget(hw, inv)
    assert budget["total_ports"] == hw["total_ports"]
    assert budget["free_count"] > 0
    assert budget["free_count"] < budget["total_ports"]


@pytest.mark.mandatory
def test_po_map_covers_all_catalog_hardware_models():
    data = load_po_map()
    models = data.get("models") or {}
    hw_names = [h["display_name"] for h in CATALOG.list_hardware_profiles()]
    for name in hw_names:
        assert name in models or any(name in k for k in models), f"Po map missing model {name}"


@pytest.mark.mandatory
def test_po_map_save_roundtrip(tmp_path):
    with patch("core.po_map_store.get_app_dir", return_value=str(tmp_path)):
        saved = save_po_map(
            {
                "models": {
                    "Nexus 9336C-FX2": {"planner": [10, 19]},
                }
            }
        )
        assert saved["models"]["Nexus 9336C-FX2"]["planner"] == [10, 19]
        reloaded = load_po_map()
        assert reloaded["models"]["Nexus 9336C-FX2"]["planner"] == [10, 19]


@pytest.mark.mandatory
def test_next_free_po_respects_role_range():
    used = [1, 2, 10, 11]
    n = next_free_po(used, "Nexus 93180YC-EX", "uplink")
    rng = ranges_for_model("Nexus 93180YC-EX").get("uplink", [30, 39])
    assert rng[0] <= n <= rng[1]
    assert n not in used


@pytest.mark.mandatory
def test_cable_plan_markdown_installer_friendly():
    plan = build_cable_plan(
        hostname="CORE1-VPC-A",
        model="Nexus 9336C-FX2",
        site_name="HQ_DC",
        scenario_name="vPC Core Pair",
        pair_hostname="CORE1-VPC-B",
        port_channels=[
            {
                "number": 1,
                "description": "vPC peer-link",
                "member_interfaces": ["Ethernet1/53", "Ethernet1/54"],
                "vpc_peer_link": True,
            },
            {
                "number": 20,
                "description": "Connected_to_LEAF_PAIR",
                "member_interfaces": ["Ethernet1/1", "Ethernet1/2"],
                "link_kind": "downlink",
            },
        ],
    )
    md = render_cable_plan_md(plan)
    assert "CORE1-VPC-A" in md
    assert "Ethernet1/53" in md
    assert "Wiring table" in md
    assert len(plan["rows"]) >= 2


@pytest.mark.mandatory
def test_hostname_rules_pair_hint():
    ok, hints = validate_hostname("DC-LEAF-01", role="leaf", pair=True)
    assert ok
    assert any("A" in h for h in hints)


@pytest.mark.mandatory
def test_site_code_validation():
    assert validate_site_code("HQ_DC")[0] is True
    assert validate_site_code("")[0] is False
    assert suggest_hostname("HQ_DC", "leaf", pair=True).endswith("-A")


@pytest.mark.mandatory
def test_version_diff_between_trains():
    versions = CATALOG.list_versions()
    if len(versions) < 2:
        pytest.skip("Need 2+ catalog versions")
    a, b = versions[0]["id"], versions[1]["id"]
    diff = compare_versions(a, b, CATALOG)
    assert "from" in diff
    assert "to" in diff
    assert isinstance(diff.get("changes"), list)


@patch("api.main._enforce_privileged_access")
@pytest.mark.mandatory
def test_api_validate_link(_auth):
    res = client.post(
        "/util/validate-link",
        json={
            "model": "Nexus 9336C-FX2",
            "row": {"po_id": 1, "members": [], "link_kind": "uplink"},
            "peer_link_interfaces": ["Ethernet1/53", "Ethernet1/54"],
            "keepalive_interfaces": ["Ethernet1/51"],
            "link_rows": [],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["valid"] is False


@patch("api.main._enforce_privileged_access")
@pytest.mark.mandatory
def test_api_port_budget(_auth):
    res = client.post(
        "/util/port-budget",
        json={
            "model": "Nexus 93180YC-EX",
            "row": {},
            "peer_link_interfaces": [],
            "keepalive_interfaces": [],
            "link_rows": [],
        },
    )
    assert res.status_code == 200
    assert "free_count" in res.json()


@patch("api.main._enforce_privileged_access")
@pytest.mark.mandatory
def test_api_hostname_hints(_auth):
    res = client.get("/util/hostname-hints?hostname=CORE1-VPC-A&site=HQ_DC&role=spine&pair=true")
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert "suggestion" in data


@patch("api.main._enforce_privileged_access")
@pytest.mark.mandatory
def test_api_po_map_get(_auth):
    res = client.get("/admin/po-map")
    assert res.status_code == 200
    assert "models" in res.json()


@pytest.mark.mandatory
def test_release_notes_public():
    res = client.get("/release/notes")
    assert res.status_code == 200
    data = res.json()
    assert "version" in data
    assert "excerpt" in data


@pytest.mark.mandatory
def test_v5_wizard_dom_contracts():
    html = (ROOT / "templates/web/index.html").read_text(encoding="utf-8")
    required_ids = [
        "configurePathBanner",
        "configurePathDetail",
        "configurePathMore",
        "readinessMeter",
        "capacityHint",
        "topologyPanel",
        "releaseNotesModal",
        "poConflictModal",
        "fabricQuestionnaireModal",
        "undoControl",
        "versionDiffBox",
        "hostname_hint_box",
        "trainingModeToggle",
    ]
    for rid in required_ids:
        assert f'id="{rid}"' in html, f"Missing DOM id {rid}"
    assert "grid-2-equal" in html
    assert 'class="select-full-label"' in html


@pytest.mark.mandatory
def test_v5_static_js_contracts():
    scripts = [
        "wizard-enhancements.js",
        "fabric-questionnaire.js",
        "topology-view.js",
        "vpc-link-planner.js",
        "admin-po-map.js",
    ]
    for name in scripts:
        text = (ROOT / "static" / name).read_text(encoding="utf-8")
        assert len(text) > 100, f"{name} missing or empty"
    planner = (ROOT / "static/vpc-link-planner.js").read_text(encoding="utf-8")
    assert "showPoConflictDialog" in planner
    assert "refreshCapacityHint" in planner
    roadmap = (ROOT / "static/roadmap.js").read_text(encoding="utf-8")
    assert "toggleConfigurePathDetail" in roadmap


@pytest.mark.mandatory
def test_admin_page_dom():
    admin = (ROOT / "templates/web/admin.html").read_text(encoding="utf-8")
    assert "admin-po-map.js" in admin
    assert "poMapEditor" in admin


@pytest.mark.mandatory
def test_styles_grid_equal_columns():
    css = (ROOT / "static/styles.css").read_text(encoding="utf-8")
    assert "grid-2-equal" in css
    assert "minmax(0, 1fr) minmax(0, 1fr)" in css
    assert "select-full-label" in css
    assert "panel-title-row" in css


@pytest.mark.mandatory
def test_css_semantic_tokens_are_defined():
    """Regression: components reference --text/--muted/--border/--surface/--accent/--warn.

    These must be defined in :root or text/borders render invisible (the
    'I don't see anything' defect).
    """
    css = (ROOT / "static/styles.css").read_text(encoding="utf-8")
    for token in ("--text:", "--muted:", "--border:", "--surface:", "--accent:", "--warn:"):
        assert token in css, f"Semantic token {token} not defined in :root"


@pytest.mark.mandatory
def test_topology_svg_has_visible_styling():
    """Regression: topology nodes rendered as invisible black boxes (no CSS)."""
    css = (ROOT / "static/styles.css").read_text(encoding="utf-8")
    for sel in (".topology-host", ".topo-node", ".topo-label", ".topo-link", ".topo-legend"):
        assert sel in css, f"Topology selector {sel} missing — diagram will be unreadable"
    # Per-node-type fills must exist so each role is distinguishable
    for node_cls in (".topo-node.core", ".topo-node.leaf", ".topo-node.spine"):
        assert node_cls in css, f"{node_cls} fill/stroke missing"
    assert "fill: var(--text-primary)" in css  # labels must be readable


@pytest.mark.mandatory
def test_topology_renderer_uses_styled_classes():
    js = (ROOT / "static/topology-view.js").read_text(encoding="utf-8")
    assert 'class="topo-node' in js
    assert 'class="topo-label"' in js
    assert 'class="topo-link' in js
    # must read planner state read-only (no mutating payload call)
    assert "getLinkPlannerPayload" not in js


@pytest.mark.mandatory
def test_ghost_button_and_utilities_defined():
    """Regression: .btn-ghost (undo, row remove, details) was unstyled."""
    css = (ROOT / "static/styles.css").read_text(encoding="utf-8")
    for sel in (".btn-ghost", ".questionnaire-nav", ".full-width", ".link-empty-state"):
        assert sel in css, f"Utility class {sel} not defined"


# ─────────────────────────────────────────────────────────
#  Regression guards for v5 correctness fixes
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_link_planner_preserves_preset_id_in_dom():
    """Regression: render must write tr.dataset.id so sync keeps stable preset ids."""
    js = (ROOT / "static/vpc-link-planner.js").read_text(encoding="utf-8")
    assert "tr.dataset.id = row.id" in js, "renderLinkSection must persist stable row id"
    assert "tr.dataset.id ||" in js, "syncLinkPlannerFromDom must read tr.dataset.id"


@pytest.mark.mandatory
def test_topology_view_is_read_only():
    """Regression: topology must not mutate planner state via getLinkPlannerPayload."""
    js = (ROOT / "static/topology-view.js").read_text(encoding="utf-8")
    assert "getLinkPlannerPayload" not in js, "topology must read linkPlannerRows, not mutate via payload"
    assert "linkPlannerRows" in js


@pytest.mark.mandatory
def test_admin_token_propagation_contracts():
    """Regression: admin link/back-link must carry the session token (CONFIG_AUTH_TOKEN)."""
    index = (ROOT / "templates/web/index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "static/app.js").read_text(encoding="utf-8")
    admin_html = (ROOT / "templates/web/admin.html").read_text(encoding="utf-8")
    admin_js = (ROOT / "static/admin-po-map.js").read_text(encoding="utf-8")
    assert 'id="adminLink"' in index
    assert "propagateTokenToAdminLink" in app_js
    assert 'id="backToWizard"' in admin_html
    assert "propagateTokenToBackLink" in admin_js
    assert "Access denied" in admin_js  # graceful 401/403 handling


@pytest.mark.mandatory
def test_readiness_meter_called_on_all_paths():
    """Regression: meter update must precede early returns in renderActionRequired."""
    js = (ROOT / "static/config-studio.js").read_text(encoding="utf-8")
    idx_meter = js.find("updateReadinessMeter")
    idx_return = js.find("Ready for lab paste — no blockers")
    assert idx_meter != -1 and idx_return != -1
    assert idx_meter < idx_return, "readiness meter must update before the early-return branch"


# ─────────────────────────────────────────────────────────
#  Edge cases — allocator, cable plan, version diff, hostname
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_validate_link_excludes_self_no_false_conflict():
    """Editing a row must not flag the row against its own existing entry."""
    inv = build_reserved_inventory(
        model="Nexus 9336C-FX2",
        link_rows=[{"enabled": True, "po_id": 20, "members": ["Ethernet1/1", "Ethernet1/2"]}],
    )
    result = validate_link_row(
        {"po_id": 20, "members": ["Ethernet1/1", "Ethernet1/2"], "link_kind": "downlink"},
        inv,
        "Nexus 9336C-FX2",
        exclude_self_po=20,
    )
    assert result["valid"] is True, result["conflicts"]


@pytest.mark.mandatory
def test_next_free_po_falls_back_when_role_range_exhausted():
    rng = ranges_for_model("Nexus 9336C-FX2").get("downlink", [20, 21])
    used = list(range(rng[0], rng[1] + 1))
    n = next_free_po(used, "Nexus 9336C-FX2", "downlink")
    assert n not in used
    assert n >= 1


@pytest.mark.mandatory
def test_port_budget_zero_free_when_all_consumed():
    hw = {"total_ports": 4, "vpc_peer_link": [], "vpc_keepalive": [], "port_groups": []}
    inv = build_reserved_inventory(
        model="Generic",
        link_rows=[{"enabled": True, "po_id": 10, "members": [f"Ethernet1/{i}" for i in range(1, 5)]}],
    )
    budget = port_budget(hw, inv)
    assert budget["free_count"] == 0
    assert budget["total_ports"] == 4


@pytest.mark.mandatory
def test_cable_plan_handles_no_port_channels():
    plan = build_cable_plan(
        hostname="ACCESS-SW-01",
        model="Nexus 92348GC-X",
        site_name="HQ_DC",
        scenario_name="Standalone access",
        port_channels=[],
    )
    md = render_cable_plan_md(plan)
    assert plan["rows"] == []
    assert "Wiring table" in md
    assert "ACCESS-SW-01" in md


@pytest.mark.mandatory
def test_version_diff_unknown_id_returns_warning():
    diff = compare_versions("does-not-exist", "also-missing", CATALOG)
    assert diff["changes"] == []
    assert "warning" in diff


@pytest.mark.mandatory
def test_hostname_underscore_normalization_hint():
    ok, hints = validate_hostname("DC_LEAF_01", role="leaf")
    assert ok is True
    assert any("hyphen" in h.lower() for h in hints)


@pytest.mark.mandatory
def test_suggest_members_access_and_core_pools():
    hw = CATALOG.get_hardware_profile("Nexus 9336C-FX2")
    inv = build_reserved_inventory(model="Nexus 9336C-FX2")
    core = suggest_members(hw_profile=hw, pool="core", count=2, inventory=inv)
    access = suggest_members(hw_profile=hw, pool="access", count=3, inventory=inv)
    assert len(core) == 2
    assert len(access) == 3
    assert all(p.startswith("Ethernet1/") for p in core + access)


@pytest.mark.mandatory
@pytest.mark.skipif(
  not (ROOT / "tests" / "e2e").exists(),
  reason="Playwright E2E folder not present — DOM contracts cover wizard shell",
)
def test_playwright_e2e_smoke_placeholder():
    """L-005: full browser gate when tests/e2e/playwright suite is added."""
    e2e = list((ROOT / "tests" / "e2e").glob("*.py"))
    assert e2e, "Add tests/e2e/*.py for Playwright gate"
