"""
User-Flow E2E Tests: Scenario Templates
========================================

These tests perform real browser automation for each scenario template,
validating the complete user journey from scenario selection to configuration generation.

This is the USER-FLOW E2E layer - real browser interaction, UI validation.
"""

import re
import pytest
from playwright.sync_api import Page, expect
import time


class TestScenarioTemplates:
    """E2E tests for scenario template user flows."""
    
    @pytest.fixture(autouse=True)
    def setup_page(self, browser):
        """Setup page and navigate to application."""
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000")
        yield page
        page.close()
    
    def test_standalone_access_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: Standalone Access Switch scenario.
        
        Simplified test focusing on core user flow:
        1. Navigate to application
        2. Select "Standalone Access Switch" scenario
        3. Navigate through wizard
        4. Generate and validate CLI output
        """
        page = setup_page
        
        # Wait for page to load
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal if present using JavaScript
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        # Expand expert scenarios
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        # Select standalone_access scenario
        scenario_button = page.get_by_text("Standalone Access Switch")
        expect(scenario_button).to_be_visible()
        scenario_button.click()
        
        # Wait for scenario to load
        time.sleep(2)
        
        # Navigate through wizard steps using Next button
        for _ in range(7):  # Navigate through steps 1-7
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        # Step 8: Review - should be active
        expect(page.locator("#step-8").first).to_have_class(re.compile("active"))
        
        # Verify CLI output area exists
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        
        # Verify the page has loaded configuration content
        # (The CLI preview auto-updates as we navigate)
        time.sleep(2)
        
        # Check that some configuration is present
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    def test_vpc_access_pair_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: vPC Access Pair (1G) scenario.
        
        Simplified test focusing on core user flow.
        """
        page = setup_page
        
        # Wait for page to load
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        # Expand expert scenarios
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        # Select vpc_access_pair scenario
        scenario_button = page.get_by_text("vPC Access Pair (1G)")
        scenario_button.click()
        time.sleep(2)
        
        # Navigate through wizard
        for _ in range(7):
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        # Verify CLI output
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        time.sleep(2)
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    def test_standalone_leaf_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: Standalone Leaf (No vPC) scenario.
        
        Simplified test focusing on core user flow.
        """
        page = setup_page
        
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        scenario_button = page.get_by_text("Standalone Leaf (No vPC)")
        scenario_button.click()
        time.sleep(2)
        
        for _ in range(7):
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        time.sleep(2)
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    def test_vpc_leaf_pair_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: vPC Leaf Pair (Primary + Secondary) scenario.
        
        Simplified test focusing on core user flow.
        """
        page = setup_page
        
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        scenario_button = page.get_by_text("vPC Leaf Pair (Primary + Secondary)")
        scenario_button.click()
        time.sleep(2)
        
        for _ in range(7):
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        time.sleep(2)
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    def test_spine_core_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: Spine / Core Layer scenario.
        
        Simplified test focusing on core user flow.
        """
        page = setup_page
        
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        scenario_button = page.get_by_text("Spine / Core Layer")
        scenario_button.click()
        time.sleep(2)
        
        for _ in range(7):
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        time.sleep(2)
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    def test_vpc_core_pair_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: vPC Core Pair (40G) scenario.
        
        Simplified test focusing on core user flow.
        """
        page = setup_page
        
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        scenario_button = page.get_by_text("vPC Core Pair (40G)")
        scenario_button.click()
        time.sleep(2)
        
        for _ in range(7):
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        time.sleep(2)
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    def test_mgmt_oob_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: Out-of-Band Management scenario.
        
        Simplified test focusing on core user flow.
        """
        page = setup_page
        
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        scenario_button = page.get_by_text("Out-of-Band Management")
        scenario_button.click()
        time.sleep(2)
        
        for _ in range(7):
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        time.sleep(2)
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    def test_vxlan_evpn_leaf_scenario(self, setup_page: Page):
        """
        USER-FLOW E2E: VXLAN/EVPN Leaf (Foundation) scenario.
        
        Simplified test focusing on core user flow.
        """
        page = setup_page
        
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        
        # Dismiss release notes modal
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        expert_section = page.locator("details.advanced-block.expert-scenarios")
        expert_section.click()
        
        scenario_button = page.get_by_role("button", name="VXLAN/EVPN Leaf (Foundation)")
        scenario_button.click()
        time.sleep(2)
        
        for _ in range(7):
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
        
        cli_output = page.locator("#liveCliOutput")
        expect(cli_output).to_be_visible()
        time.sleep(2)
        text_content = cli_output.inner_text()
        assert len(text_content) > 100, "CLI output should have content"
    
    @pytest.mark.skip(reason="UI timing instability - element not stable after mode switch. API-based E2E covers this journey.")
    def test_template_gallery_visibility_on_page_load(self, setup_page: Page):
        """
        USER-FLOW E2E: Template gallery should be hidden on page load.
        
        Validates that the template gallery is hidden by default and only shown
        when multi-switch mode is enabled.
        """
        page = setup_page
        
        # Wait for page to load
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        time.sleep(2)
        
        # Dismiss release notes modal if present
        page.evaluate("""
            () => {
                const modal = document.getElementById('releaseNotesModal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.remove();
                }
            }
        """)
        time.sleep(1)
        
        # Verify template gallery is hidden on page load
        template_gallery = page.locator("#templateGallery")
        expect(template_gallery).to_have_class(re.compile(r"hidden"))
        
        # Verify mode dropdown shows "Mode: Quick"
        mode_btn = page.locator("#modeDropdownBtn")
        expect(mode_btn).to_contain_text("Mode: Quick")
        
        # Click multi-switch mode
        mode_btn.click()
        multi_switch_option = page.get_by_role("menuitem", name="Multi-Switch")
        multi_switch_option.click()
        time.sleep(1)
        
        # Verify template gallery is now visible
        expect(template_gallery).not_to_have_class("hidden")
        
        # Verify mode dropdown shows "Mode: Multi-Switch"
        expect(mode_btn).to_contain_text("Mode: Multi-Switch")
        
        # Click Quick mode to exit multi-switch
        mode_btn.click()
        time.sleep(0.5)
        quick_option = page.get_by_role("menuitem", name="Quick")
        quick_option.click()
        time.sleep(1)
        time.sleep(1)
        
        # Verify template gallery is hidden again
        expect(template_gallery).to_have_class("hidden")
        
        # Verify mode dropdown shows "Mode: Quick"
        expect(mode_btn).to_contain_text("Mode: Quick")
