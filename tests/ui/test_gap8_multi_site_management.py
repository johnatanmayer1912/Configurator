"""
UI-focused automation tests for GAP 8: Multi-site Deployment Management

These tests simulate user interactions with the multi-site management UI features,
including site creation, hierarchy configuration, and progressive rollout.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class TestMultiSiteManagementUI:
    """Test suite for multi-site management UI functionality."""
    
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
    async def test_multi_site_button_visible(self, authenticated_page: Page):
        """Test that multi-site management button is visible in deployment panel."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Verify multi-site management section exists
        assert await authenticated_page.locator("h4:has-text('Multi-Site Management')").is_visible()
        assert await authenticated_page.locator("button:has-text('Manage Sites')").is_visible()
    
    @pytest.mark.asyncio
    async def test_multi_site_modal_opens(self, authenticated_page: Page):
        """Test that the multi-site management modal opens correctly."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Verify modal is visible
        modal = authenticated_page.locator(".modal-overlay")
        await modal.wait_for(state="visible")
        
        # Verify modal title
        assert await authenticated_page.locator(".modal-header h3:has-text('Multi-Site Management')").is_visible()
        
        # Verify site ID input exists
        assert await authenticated_page.locator("#siteId").is_visible()
        
        # Verify site name input exists
        assert await authenticated_page.locator("#siteName").is_visible()
        
        # Verify parent site input exists
        assert await authenticated_page.locator("#parentSite").is_visible()
        
        # Verify region input exists
        assert await authenticated_page.locator("#region").is_visible()
        
        # Verify rollout phase select exists
        assert await authenticated_page.locator("#rolloutPhase").is_visible()
        
        # Verify progressive rollout checkbox exists
        assert await authenticated_page.locator("#progressiveRollout").is_visible()
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_site_creation_with_required_fields(self, authenticated_page: Page):
        """Test site creation with required fields only."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Fill required fields
        await authenticated_page.fill("#siteId", "site-hq")
        await authenticated_page.fill("#siteName", "Headquarters")
        
        # Create site
        await authenticated_page.click("button:has-text('Create Site')")
        
        # Verify success toast
        toast = authenticated_page.locator(".toast:has-text('Headquarters')")
        await toast.wait_for(state="visible")
        
        # Verify modal is closed
        assert not await authenticated_page.locator(".modal-overlay").is_visible()
    
    @pytest.mark.asyncio
    async def test_site_creation_missing_required_fields(self, authenticated_page: Page):
        """Test site creation with missing required fields."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Try to create site without required fields
        await authenticated_page.click("button:has-text('Create Site')")
        
        # Verify error toast
        toast = authenticated_page.locator(".toast:has-text('Site ID and Site Name are required')")
        await toast.wait_for(state="visible", timeout=3000)
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_site_creation_with_parent_site(self, authenticated_page: Page):
        """Test site creation with parent site hierarchy."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Fill all fields including parent site
        await authenticated_page.fill("#siteId", "site-dc1")
        await authenticated_page.fill("#siteName", "Data Center 1")
        await authenticated_page.fill("#parentSite", "region-na")
        await authenticated_page.fill("#region", "North America")
        
        # Create site
        await authenticated_page.click("button:has-text('Create Site')")
        
        # Verify success toast
        toast = authenticated_page.locator(".toast:has-text('Data Center 1')")
        await toast.wait_for(state="visible")
    
    @pytest.mark.asyncio
    async def test_rollout_phase_selection(self, authenticated_page: Page):
        """Test rollout phase selection options."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Verify rollout phase options
        rollout_select = authenticated_page.locator("#rolloutPhase")
        options = await rollout_select.locator("option").all()
        
        expected_phases = ["Planned", "Staging", "Production"]
        option_texts = [await option.inner_text() for option in options]
        
        for phase in expected_phases:
            assert phase in option_texts, f"Phase '{phase}' not found in options"
        
        # Select different phase
        await rollout_select.select_option("staging")
        selected_value = await rollout_select.input_value()
        assert selected_value == "staging"
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_progressive_rollout_checkbox(self, authenticated_page: Page):
        """Test progressive rollout checkbox functionality."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Verify checkbox is unchecked by default
        progressive_checkbox = authenticated_page.locator("#progressiveRollout")
        assert not await progressive_checkbox.is_checked()
        
        # Check the checkbox
        await progressive_checkbox.check()
        assert await progressive_checkbox.is_checked()
        
        # Uncheck the checkbox
        await progressive_checkbox.uncheck()
        assert not await progressive_checkbox.is_checked()
        
        # Close modal
        await authenticated_page.click(".btn-close")
    
    @pytest.mark.asyncio
    async def test_progressive_rollout_execution(self, authenticated_page: Page):
        """Test progressive rollout execution through UI."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Enable progressive rollout
        progressive_checkbox = authenticated_page.locator("#progressiveRollout")
        await progressive_checkbox.check()
        
        # Execute progressive rollout
        await authenticated_page.click("button:has-text('Progressive Rollout')")
        
        # Verify success toast
        toast = authenticated_page.locator(".toast:has-text('enabled')")
        await toast.wait_for(state="visible")
        
        # Verify modal is closed
        assert not await authenticated_page.locator(".modal-overlay").is_visible()
    
    @pytest.mark.asyncio
    async def test_progressive_rollout_disabled(self, authenticated_page: Page):
        """Test progressive rollout when disabled."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Ensure progressive rollout is unchecked
        progressive_checkbox = authenticated_page.locator("#progressiveRollout")
        await progressive_checkbox.uncheck()
        
        # Execute rollout (without progressive)
        await authenticated_page.click("button:has-text('Progressive Rollout')")
        
        # Verify success toast mentions disabled
        toast = authenticated_page.locator(".toast:has-text('disabled')")
        await toast.wait_for(state="visible")
    
    @pytest.mark.asyncio
    async def test_site_creation_with_all_fields(self, authenticated_page: Page):
        """Test site creation with all optional fields populated."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Fill all fields
        await authenticated_page.fill("#siteId", "site-dr")
        await authenticated_page.fill("#siteName", "Disaster Recovery")
        await authenticated_page.fill("#parentSite", "region-eu")
        await authenticated_page.fill("#region", "Europe")
        
        # Select production phase
        rollout_select = authenticated_page.locator("#rolloutPhase")
        await rollout_select.select_option("production")
        
        # Enable progressive rollout
        progressive_checkbox = authenticated_page.locator("#progressiveRollout")
        await progressive_checkbox.check()
        
        # Create site
        await authenticated_page.click("button:has-text('Create Site')")
        
        # Verify success toast
        toast = authenticated_page.locator(".toast:has-text('Disaster Recovery')")
        await toast.wait_for(state="visible")
    
    @pytest.mark.asyncio
    async def test_multi_site_modal_cancel(self, authenticated_page: Page):
        """Test cancelling multi-site modal without saving."""
        # Navigate to deployment tab
        await authenticated_page.click("text=Deployment")
        await authenticated_page.wait_for_timeout(500)
        
        # Click on Manage Sites button
        await authenticated_page.click("button:has-text('Manage Sites')")
        
        # Fill some fields
        await authenticated_page.fill("#siteId", "site-test")
        await authenticated_page.fill("#siteName", "Test Site")
        
        # Click cancel
        await authenticated_page.click("button:has-text('Cancel')")
        
        # Verify modal is closed
        assert not await authenticated_page.locator(".modal-overlay").is_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
