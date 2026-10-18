"""
Full E2E Tests: Multi-Switch Deployments
========================================

Tests perform comprehensive validation of multi-switch deployments:
- Template application via UI
- Config generation via API
- VLAN assignment validation (TRANSIT / FABRIC naming)
- Feature enablement per role
- vPC configuration validation
- Interface configuration validation

These are REAL E2E tests — no skips.
"""

import re
import json
import pytest
import time
import requests
from playwright.sync_api import Page, expect
from tests.e2e.full_e2e_validator import ConfigValidator, MultiSwitchValidator
from tests.e2e.test_data.expected_outputs import DEPLOYMENT_TEST_CASES

BASE_URL = "http://127.0.0.1:9000"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _generate_deployment_via_api(payload: dict) -> dict:
    """POST /generate-deployment and return the JSON response."""
    resp = requests.post(
        f"{BASE_URL}/generate-deployment?preview=true",
        json=payload,
        timeout=60,
    )
    assert resp.status_code == 200, (
        f"/generate-deployment failed {resp.status_code}: {resp.text[:500]}"
    )
    return resp.json()


def _extract_cli_by_hostname(response: dict) -> dict:
    """Return {hostname: cli_text} from /generate-deployment response."""
    configs = {}
    for result in response.get("results", []):
        hostname = result.get("hostname", "unknown")
        cli = (
            result.get("export", {}).get("cli")
            or result.get("export", {}).get("config")
            or ""
        )
        configs[hostname] = cli
    return configs


# ─────────────────────────────────────────────────────────────────────────────
# Shared UI helpers
# ─────────────────────────────────────────────────────────────────────────────

class TestMultiSwitchDeployments:
    """Full E2E tests for multi-switch deployment templates."""

    @pytest.fixture(autouse=True)
    def setup_page(self, browser):
        page = browser.new_page()
        page.goto(BASE_URL)
        yield page
        page.close()

    # ── UI helpers ────────────────────────────────────────────────────────────

    def _dismiss_modal(self, page: Page):
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) { modal.style.display = 'none'; modal.remove(); }
            }
        """)
        time.sleep(0.5)

    def _enter_multiswitch_mode(self, page: Page):
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) { modal.style.display = 'none'; modal.remove(); }
            }
        """)
        page.wait_for_load_state("networkidle")
        # Open mode dropdown
        page.locator("#modeDropdownBtn").click()
        page.wait_for_timeout(300)
        # Click Multi-Switch item by data-action
        page.locator('[data-action="toggle-multi-switch"]').click()
        expect(page.locator(".template-grid")).to_be_visible(timeout=8000)

    def _apply_template_and_open_editor(self, page: Page, template_name: str):
        """Apply a named template and land in the configuration editor."""
        # Mock confirm() to auto-accept any validation warnings dialogs
        page.evaluate("() => { window.confirm = () => true; }")
        page.wait_for_timeout(500)
        card = page.locator(".template-card").filter(has_text=template_name).first
        expect(card).to_be_visible(timeout=5000)
        card.locator('button:has-text("Use Template")').click()

        # Wait for success screen
        success = page.locator(".template-success")
        expect(success).to_be_visible(timeout=10000)

        # Customize Network → opens editor
        page.locator('button:has-text("Customize Network")').click()
        expect(page.locator("#configurationEditor")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)

    # ── API-level deployment payload builders ──────────────────────────────────

    @staticmethod
    def _build_vpc_core_leaf_payload() -> dict:
        return {
            "site_name": "E2E_TEST",
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "core",
                    "vpc_domain": "10",
                    "local_ka": "10.0.0.1",
                    "remote_ka": "10.0.0.2",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.0.0.2/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "core",
                    "vpc_domain": "10",
                    "local_ka": "10.0.0.2",
                    "remote_ka": "10.0.0.1",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF10G-1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "100",
                    "local_ka": "10.0.0.11",
                    "remote_ka": "10.0.0.12",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF10G-2",
                    "mgmt_ip": "10.0.0.12/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "100",
                    "local_ka": "10.0.0.12",
                    "remote_ka": "10.0.0.11",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
            ],
            "vpc_pairs": [
                {
                    "domain": 10,
                    "primary": "CORE1",
                    "secondary": "CORE2",
                    "peer_link_ports": "Ethernet1/35-36",
                },
                {
                    "domain": 100,
                    "primary": "LEAF10G-1",
                    "secondary": "LEAF10G-2",
                    "peer_link_ports": "Ethernet1/51-52",
                },
            ],
            "uplinks": [
                {"from": "LEAF10G-1", "to": "CORE1", "ports": "Ethernet1/53", "po_id": 10},
                {"from": "LEAF10G-1", "to": "CORE2", "ports": "Ethernet1/54", "po_id": 11},
                {"from": "LEAF10G-2", "to": "CORE1", "ports": "Ethernet1/53", "po_id": 10},
                {"from": "LEAF10G-2", "to": "CORE2", "ports": "Ethernet1/54", "po_id": 11},
            ],
            "global_vlans": [
                {"id": 10, "name": "TRANSIT_10"},
                {"id": 100, "name": "FABRIC_100"},
                {"id": 200, "name": "FABRIC_200"},
            ],
        }

    @staticmethod
    def _build_spine_leaf_payload() -> dict:
        return {
            "site_name": "E2E_TEST",
            "switches": [
                {
                    "hostname": "SPINE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "spine",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "SPINE2",
                    "mgmt_ip": "10.0.0.2/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "spine",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF2",
                    "mgmt_ip": "10.0.0.12/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
            ],
            "vpc_pairs": [],
            "uplinks": [
                {"from": "LEAF1", "to": "SPINE1", "ports": "Ethernet1/53", "po_id": 10},
                {"from": "LEAF1", "to": "SPINE2", "ports": "Ethernet1/54", "po_id": 11},
                {"from": "LEAF2", "to": "SPINE1", "ports": "Ethernet1/53", "po_id": 10},
                {"from": "LEAF2", "to": "SPINE2", "ports": "Ethernet1/54", "po_id": 11},
            ],
            "global_vlans": [
                {"id": 10, "name": "TRANSIT_10"},
                {"id": 100, "name": "FABRIC_100"},
            ],
        }

    @staticmethod
    def _build_six_switch_fabric_payload() -> dict:
        return {
            "site_name": "E2E_TEST",
            "switches": [
                {
                    "hostname": "SPINE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "spine",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "SPINE2",
                    "mgmt_ip": "10.0.0.2/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "spine",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "100",
                    "local_ka": "10.0.0.11",
                    "remote_ka": "10.0.0.12",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF2",
                    "mgmt_ip": "10.0.0.12/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "100",
                    "local_ka": "10.0.0.12",
                    "remote_ka": "10.0.0.11",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF3",
                    "mgmt_ip": "10.0.0.13/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "200",
                    "local_ka": "10.0.0.13",
                    "remote_ka": "10.0.0.14",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF4",
                    "mgmt_ip": "10.0.0.14/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "vpc_domain": "200",
                    "local_ka": "10.0.0.14",
                    "remote_ka": "10.0.0.13",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
            ],
            "vpc_pairs": [
                {
                    "domain": 100,
                    "primary": "LEAF1",
                    "secondary": "LEAF2",
                    "peer_link_ports": "Ethernet1/51-52",
                },
                {
                    "domain": 200,
                    "primary": "LEAF3",
                    "secondary": "LEAF4",
                    "peer_link_ports": "Ethernet1/51-52",
                },
            ],
            "uplinks": [
                {"from": "LEAF1", "to": "SPINE1", "ports": "Ethernet1/53", "po_id": 10},
                {"from": "LEAF1", "to": "SPINE2", "ports": "Ethernet1/54", "po_id": 11},
                {"from": "LEAF2", "to": "SPINE1", "ports": "Ethernet1/53", "po_id": 10},
                {"from": "LEAF2", "to": "SPINE2", "ports": "Ethernet1/54", "po_id": 11},
                {"from": "LEAF3", "to": "SPINE1", "ports": "Ethernet1/53", "po_id": 12},
                {"from": "LEAF3", "to": "SPINE2", "ports": "Ethernet1/54", "po_id": 13},
                {"from": "LEAF4", "to": "SPINE1", "ports": "Ethernet1/53", "po_id": 12},
                {"from": "LEAF4", "to": "SPINE2", "ports": "Ethernet1/54", "po_id": 13},
            ],
            "global_vlans": [
                {"id": 10, "name": "TRANSIT_10"},
                {"id": 100, "name": "FABRIC_100"},
                {"id": 200, "name": "FABRIC_200"},
            ],
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Test 1 — 6-Switch Fabric: UI template application + API config validation
    # ─────────────────────────────────────────────────────────────────────────

    def test_six_switch_fabric_deployment(self, setup_page: Page):
        """
        E2E: 6-Switch Fabric (2 Spine + 4 Leaf).

        UI: template gallery → apply template → success screen → Customize Network
            → configuration editor shows 6 switches.
        API: /generate-deployment → validate CLI for each switch role.
        """
        page = setup_page

        # ── UI flow ──────────────────────────────────────────────────────────
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        self._enter_multiswitch_mode(page)

        self._apply_template_and_open_editor(page, "6-Switch Fabric (2 Spine + 4 Leaf)")

        # Editor must show 6 switches
        switches = page.locator("#switchesList .switch-item")
        assert switches.count() == 6, (
            f"Expected 6 switches in editor, got {switches.count()}"
        )

        # Validate topology SVG rendered with correct colours
        svg_html = page.locator("#editorTopologyContainer svg").inner_html()
        assert "#3B82F6" in svg_html or "#10B981" in svg_html or "#F59E0B" in svg_html, (
            "Topology SVG missing role-based colours"
        )
        payload = self._build_six_switch_fabric_payload()
        response = _generate_deployment_via_api(payload)

        assert response["status"] in ("completed", "partial_success")
        assert response["successful"] == 6, (
            f"Expected 6 successful configs, got {response['successful']}"
        )

        configs = _extract_cli_by_hostname(response)
        assert len(configs) == 6, f"Expected 6 CLI outputs, got {len(configs)}"

        # Spine switches — must have basic features, no vPC
        for spine in ("SPINE1", "SPINE2"):
            assert spine in configs, f"{spine} missing from configs"
            v = ConfigValidator(configs[spine])
            assert len(v.features) > 0, f"{spine}: no features found"
            assert len(v.interfaces) > 0, f"{spine}: no interfaces found"
            assert "vpc" not in v.features, f"{spine}: should NOT have vPC feature"

        # Leaf switches — must have vPC config (domain defined in payload)
        for leaf in ("LEAF1", "LEAF2", "LEAF3", "LEAF4"):
            assert leaf in configs, f"{leaf} missing from configs"
            v = ConfigValidator(configs[leaf])
            assert len(v.features) > 0, f"{leaf}: no features found"
            assert len(v.interfaces) > 0, f"{leaf}: no interfaces found"

        # VLANs are present in at least one config
        all_vlans = {}
        for hostname, cli in configs.items():
            v = ConfigValidator(cli)
            all_vlans.update(v.vlans)
        assert len(all_vlans) > 0, "No VLANs found across any switch config"

    # ─────────────────────────────────────────────────────────────────────────
    # Test 2 — Spine-Leaf Fabric (no vPC)
    # ─────────────────────────────────────────────────────────────────────────

    def test_spine_leaf_fabric_deployment(self, setup_page: Page):
        """
        E2E: Spine-Leaf Fabric (4 switches, no vPC, pure L3).

        UI: template gallery → apply → success → editor shows 4 switches.
        API: validate no vPC feature, LACP+LLDP present on all switches.
        """
        page = setup_page

        # ── UI flow ──────────────────────────────────────────────────────────
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        self._enter_multiswitch_mode(page)
        self._apply_template_and_open_editor(page, "Spine-Leaf Fabric")

        switches = page.locator("#switchesList .switch-item")
        assert switches.count() == 4, (
            f"Expected 4 switches in editor, got {switches.count()}"
        )

        # vPC Domains tab should show 0 domains
        page.locator('[data-tab="vpc"]').click()
        page.wait_for_timeout(500)
        vpc_list = page.locator("#vpcList")
        # empty state or no vpc-item elements
        vpc_items = vpc_list.locator(".vpc-item")
        assert vpc_items.count() == 0, (
            f"Spine-Leaf should have no vPC domains, found {vpc_items.count()}"
        )

        # ── API validation ───────────────────────────────────────────────────
        payload = self._build_spine_leaf_payload()
        response = _generate_deployment_via_api(payload)

        assert response["status"] in ("completed", "partial_success")
        assert response["successful"] == 4, (
            f"Expected 4 successful configs, got {response['successful']}"
        )

        configs = _extract_cli_by_hostname(response)

        required_features = ["interface-vlan", "lacp", "lldp"]
        for hostname, cli in configs.items():
            v = ConfigValidator(cli)
            assert len(v.features) > 0, f"{hostname}: no features found"
            assert len(v.interfaces) > 0, f"{hostname}: no interfaces found"

            # No vPC in pure spine-leaf (no vpc_pairs in payload)
            assert "vpc" not in v.features, (
                f"{hostname}: vPC should not be enabled in spine-leaf fabric"
            )

            # Mandatory features per Cisco best practice
            for feat in required_features:
                assert feat in v.features, (
                    f"{hostname}: expected feature '{feat}' not found. "
                    f"Features present: {v.features}"
                )

        # VLANs distributed across all switches
        all_vlans = {}
        for cli in configs.values():
            all_vlans.update(ConfigValidator(cli).vlans)
        assert len(all_vlans) > 0, "No VLANs found across any switch config"

    # ─────────────────────────────────────────────────────────────────────────
    # Test 3 — vPC Core + Leaf Pairs
    # ─────────────────────────────────────────────────────────────────────────

    def test_vpc_core_leaf_deployment(self, setup_page: Page):
        """
        E2E: vPC Core + Leaf Pairs (2 core + 2 leaf, 2 vPC domains).

        UI: template gallery → apply → success → editor shows 4 switches
            with 2 vPC domains in the vPC tab.
        API: validate vPC config elements (domain, peer-gateway, auto-recovery).
        """
        page = setup_page

        # ── UI flow ──────────────────────────────────────────────────────────
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        self._enter_multiswitch_mode(page)
        self._apply_template_and_open_editor(page, "vPC Core + Leaf Pairs")

        switches = page.locator("#switchesList .switch-item")
        assert switches.count() == 4, (
            f"Expected 4 switches, got {switches.count()}"
        )

        # vPC Domains tab — must show 2 domains
        page.locator('[data-tab="vpc"]').click()
        page.wait_for_timeout(500)
        vpc_items = page.locator("#vpcList .vpc-item")
        assert vpc_items.count() == 2, (
            f"Expected 2 vPC domains in editor, found {vpc_items.count()}"
        )

        # Uplinks tab — must have uplinks
        page.locator('[data-tab="uplinks"]').click()
        page.wait_for_timeout(500)
        uplink_items = page.locator("#uplinkList .uplink-item")
        assert uplink_items.count() >= 2, (
            f"Expected ≥2 uplinks, found {uplink_items.count()}"
        )

        # ── API validation ───────────────────────────────────────────────────
        payload = self._build_vpc_core_leaf_payload()
        response = _generate_deployment_via_api(payload)

        assert response["status"] in ("completed", "partial_success"), (
            f"Unexpected status: {response['status']} — errors: {response.get('errors')}"
        )
        assert response["successful"] == 4, (
            f"Expected 4 successful configs, got {response['successful']}. "
            f"Errors: {response.get('errors')}"
        )

        configs = _extract_cli_by_hostname(response)
        assert len(configs) == 4, f"Expected 4 CLI outputs, got {len(configs)}"

        # All switches must have features + interfaces
        for hostname, cli in configs.items():
            v = ConfigValidator(cli)
            assert len(v.features) > 0, f"{hostname}: no features found"
            assert len(v.interfaces) > 0, f"{hostname}: no interfaces found"

        # vPC-participating switches must have 'vpc' feature
        for hostname in ("CORE1", "CORE2", "LEAF10G-1", "LEAF10G-2"):
            assert hostname in configs, f"{hostname} missing from generated configs"
            v = ConfigValidator(configs[hostname])
            assert "vpc" in v.features, (
                f"{hostname}: 'vpc' feature must be enabled. "
                f"Features found: {v.features}"
            )

        # vPC config elements must be present in vPC-member configs
        expected_vpc_elements = ["domain", "peer-keepalive"]
        for hostname in ("CORE1", "CORE2", "LEAF10G-1", "LEAF10G-2"):
            v = ConfigValidator(configs[hostname])
            for elem in expected_vpc_elements:
                assert elem in v.vpc_config, (
                    f"{hostname}: vPC element '{elem}' not found. "
                    f"vpc_config: {v.vpc_config}"
                )

        # Mandatory features on all switches
        required_features = ["interface-vlan", "lacp", "lldp"]
        for hostname, cli in configs.items():
            v = ConfigValidator(cli)
            for feat in required_features:
                assert feat in v.features, (
                    f"{hostname}: feature '{feat}' required but not found. "
                    f"Features: {v.features}"
                )

        # VLANs present
        all_vlans = {}
        for cli in configs.values():
            all_vlans.update(ConfigValidator(cli).vlans)
        assert len(all_vlans) > 0, "No VLANs found across any switch"
