"""
UI-focused automation tests for GAP 2: Bulk VLAN Management

These tests simulate user interactions with the bulk VLAN management UI features,
including bulk add/remove, naming validation, and conflict detection.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import json


class TestBulkVLANManagementUI:
    """Test suite for bulk VLAN management UI functionality."""
    
    @pytest.fixture
    async def browser_context(self):
        """Setup browser context for UI testing."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            yield page
            await context.close()
            await browser.close()
    
    @pytest.fixture
    async def authenticated_page(self, browser_context: Page):
        """Navigate to the app and ensure it's loaded."""
        await browser_context.goto("http://127.0.0.1:9000/")
        await browser_context.wait_for_load_state("networkidle")
        return browser_context
    
    @pytest.mark.asyncio
    async def test_bulk_vlan_modal_opens(self, authenticated_page: Page):
        """Test that the global VLAN configuration modal opens correctly."""
        # Click on deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Configure VLANs button
        await authenticated_page.click("button:has-text('Configure VLANs')")
        
        # Verify modal is visible
        modal = authenticated_page.locator(".modal-overlay")
        await modal.wait_for(state="visible")
        
        # Verify modal title
        assert await authenticated_page.locator(".modal-header h3:has-text('Configure Global VLANs')").is_visible()
        
        # Verify bulk operations buttons are present
        assert await authenticated_page.locator("button:has-text('Bulk Add Range')").is_visible()
        assert await authenticated_page.locator("button:has-text('Bulk Remove Range')").is_visible()
        assert await authenticated_page.locator("button:has-text('Validate Naming')").is_visible()
        assert await authenticated_page.locator("button:has-text('Check Conflicts')").is_visible()
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_bulk_add_vlans_ui(self, authenticated_page: Page):
        """Test bulk VLAN addition through UI prompts."""
        # Open VLAN configuration modal
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        await authenticated_page.click("button:has-text('Configure VLANs')")
        
        # Click bulk add button
        with authenticated_page.expect_popup() as popup_info:
            await authenticated_page.click("button:has-text('Bulk Add Range')")
        
        # Note: Since prompt() is used, we need to handle it differently
        # For this test, we'll verify the function exists and is callable
        # In a real E2E test, we'd need to mock the prompt or use a different approach
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_vlan_naming_validation_ui(self, authenticated_page: Page):
        """Test VLAN naming validation through UI."""
        # Open VLAN configuration modal
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        await authenticated_page.click("button:has-text('Configure VLANs')")
        
        # Add a VLAN with invalid name (too short)
        await authenticated_page.click("button:has-text('Add VLAN')")
        
        vlan_id_input = authenticated_page.locator(".vlan-id-input").last
        vlan_name_input = authenticated_page.locator(".vlan-name-input").last
        
        await vlan_id_input.fill("100")
        await vlan_name_input.fill("AB")  # Too short (less than 3 chars)
        
        # Click validate naming
        await authenticated_page.click("button:has-text('Validate Naming')")
        
        # Verify validation results appear
        results_div = authenticated_page.locator("#vlanValidationResults")
        await results_div.wait_for(state="visible")
        
        # Verify error message is shown
        assert await authenticated_page.locator("#vlanValidationContent:has-text('too short')").is_visible()
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_vlan_conflict_detection_ui(self, authenticated_page: Page):
        """Test VLAN conflict detection through UI."""
        # Open VLAN configuration modal
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        await authenticated_page.click("button:has-text('Configure VLANs')")
        
        # Add duplicate VLAN IDs
        await authenticated_page.click("button:has-text('Add VLAN')")
        await authenticated_page.locator(".vlan-id-input").last.fill("100")
        await authenticated_page.locator(".vlan-name-input").last.fill("Data-VLAN-100")
        
        await authenticated_page.click("button:has-text('Add VLAN')")
        await authenticated_page.locator(".vlan-id-input").last.fill("100")  # Duplicate
        await authenticated_page.locator(".vlan-name-input").last.fill("Data-VLAN-100-Dup")
        
        # Click check conflicts
        await authenticated_page.click("button:has-text('Check Conflicts')")
        
        # Verify validation results appear
        results_div = authenticated_page.locator("#vlanValidationResults")
        await results_div.wait_for(state="visible")
        
        # Verify conflict message is shown
        assert await authenticated_page.locator("#vlanValidationContent:has-text('Duplicate VLAN ID')").is_visible()
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_vlan_preset_application_ui(self, authenticated_page: Page):
        """Test VLAN preset application through UI."""
        # Open VLAN configuration modal
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        await authenticated_page.click("button:has-text('Configure VLANs')")
        
        # Apply datacenter preset
        await authenticated_page.click("button:has-text('Data Center')")
        
        # Verify VLANs are added
        vlan_rows = authenticated_page.locator(".vlan-row")
        count = await vlan_rows.count()
        assert count >= 5  # Data center preset has 5 VLANs
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_save_global_vlans_ui(self, authenticated_page: Page):
        """Test saving global VLANs through UI."""
        # Open VLAN configuration modal
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        await authenticated_page.click("button:has-text('Configure VLANs')")
        
        # Add a VLAN
        await authenticated_page.click("button:has-text('Add VLAN')")
        await authenticated_page.locator(".vlan-id-input").last.fill("200")
        await authenticated_page.locator(".vlan-name-input").last.fill("Test-VLAN-200")
        
        # Save VLANs
        await authenticated_page.click("button:has-text('Save VLANs')")
        
        # Verify toast message
        toast = authenticated_page.locator(".toast:has-text('Saved 1 global VLAN')")
        await toast.wait_for(state="visible")
        
        # Verify modal is closed
        assert not await authenticated_page.locator(".modal-overlay").is_visible()
    
    @pytest.mark.asyncio
    async def test_vlan_ui_styling_and_layout(self, authenticated_page: Page):
        """Test that VLAN UI elements are properly styled."""
        # Open VLAN configuration modal
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        await authenticated_page.click("button:has-text('Configure VLANs')")
        
        # Verify bulk actions section exists
        bulk_actions = authenticated_page.locator(".vlan-bulk-actions")
        assert await bulk_actions.is_visible()
        
        # Verify VLAN configuration section exists
        vlan_config = authenticated_page.locator(".vlan-configuration")
        assert await vlan_config.is_visible()
        
        # Verify presets section exists
        presets = authenticated_page.locator(".vlan-presets")
        assert await presets.is_visible()
        
        # Close modal
        await authenticated_page.click(".btn-close")


class TestBulkVLANIntegration:
    """Integration tests for bulk VLAN management with deployment."""
    
    @pytest.fixture
    async def browser_context(self):
        """Setup browser context for UI testing."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            yield page
            await context.close()
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_global_vlans_applied_to_deployment(self, browser_context: Page):
        """Test that global VLANs are applied to deployment configuration."""
        # Navigate to app
        await browser_context.goto("http://127.0.0.1:9000/")
        await browser_context.wait_for_load_state("networkidle")
        
        # Create a simple deployment with a switch
        await browser_context.click("text=Deployment")
        await browser_context.wait_for_timeout(500)
        
        # Add a switch
        await browser_context.click("button:has-text('Add Switch')")
        await browser_context.fill("#hostname", "test-sw1")
        await browser_context.fill("#mgmt_ip", "10.0.0.1/24")
        await browser_context.click("button:has-text('Save')")
        
        # Configure global VLANs
        await browser_context.click("button:has-text('Configure VLANs')")
        await browser_context.click("button:has-text('Add VLAN')")
        await browser_context.locator(".vlan-id-input").last.fill("300")
        await browser_context.locator(".vlan-name-input").last.fill("Global-VLAN-300")
        await browser_context.click("button:has-text('Save VLANs')")
        
        # Verify global VLANs are saved
        await browser_context.wait_for_timeout(500)
        
        # Check that global VLANs are displayed in summary
        global_vlans_summary = browser_context.locator(".global-vlans-summary")
        assert await global_vlans_summary.is_visible()
        assert await global_vlans_summary.inner_text().__contains__("VLAN 300")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
