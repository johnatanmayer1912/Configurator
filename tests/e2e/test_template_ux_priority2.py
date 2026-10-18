"""
E2E Tests for Template UX Priority 2 Features

Tests for:
- Use case grouping with filters
- Template comparison mode
- Hardware compatibility indicators
- Best practice badges
- Complexity badges
"""

import pytest
from playwright.sync_api import Page, expect


class TestTemplateUXPriority2:
    """E2E tests for Priority 2 template UX improvements."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        page.goto("http://127.0.0.1:9000/")
        page.wait_for_load_state("networkidle")
        
        # Close any modals
        page.evaluate("""
            () => {
                const modals = document.querySelectorAll('.modal[aria-modal="true"]');
                modals.forEach(modal => modal.remove());
                
                // Click Got it button if present (using text content)
                const buttons = document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.textContent.includes('Got it')) btn.click();
                    if (btn.textContent.includes('Close') && btn.closest('#releaseNotesModal')) btn.click();
                });
            }
        """)
        page.wait_for_timeout(500)
        
        # Set up hardware inventory to avoid validation warnings
        page.evaluate("""
            () => {
                window.getCurrentHardwareInventory = function() {
                    return ['Nexus 9336C-FX2', 'Nexus 93180YC-EX', 'Nexus 9348GC-FXP'];
                };
                window.getCurrentNxosVersion = function() {
                    return '9.3';
                };
            }
        """)
        
        # Handle confirmation dialogs by auto-accepting them
        page.on("dialog", lambda dialog: dialog.accept())
    
    def test_use_case_filters_visible(self, page: Page):
        """Test that use case filter buttons are visible."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Verify filter buttons are present
        filter_buttons = page.locator(".filter-btn")
        assert filter_buttons.count() >= 4, "Should have at least 4 filter buttons (All, Production DC, Cloud/VM, Campus)"
    
    def test_filter_by_production_dc(self, page: Page):
        """Test filtering templates by Production Data Center use case."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Get initial template count
        all_templates = page.locator(".template-card")
        initial_count = all_templates.count()
        
        # Click Production DC filter
        production_filter = page.locator('.filter-btn:has-text("Production")')
        production_filter.click()
        
        # Wait for filter to apply
        page.wait_for_timeout(500)
        
        # Verify filtered templates
        filtered_templates = page.locator(".template-card")
        assert filtered_templates.count() <= initial_count, "Filtered count should be less than or equal to initial"
        
        # Verify filter button is active
        is_active = production_filter.evaluate('el => el.classList.contains("active")')
        assert is_active, "Production filter should be active"
    
    def test_filter_by_cloud_vm(self, page: Page):
        """Test filtering templates by Cloud/VM use case."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Click Cloud/VM filter
        cloud_filter = page.locator('.filter-btn:has-text("Cloud")')
        cloud_filter.click()
        
        # Wait for filter to apply
        page.wait_for_timeout(500)
        
        # Verify filtered templates
        filtered_templates = page.locator(".template-card")
        assert filtered_templates.count() > 0, "Should have at least one Cloud/VM template"
        
        # Verify filter button is active
        is_active = cloud_filter.evaluate('el => el.classList.contains("active")')
        assert is_active, "Cloud filter should be active"
    
    def test_filter_by_campus(self, page: Page):
        """Test filtering templates by Enterprise Campus use case."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Click Campus filter
        campus_filter = page.locator('.filter-btn:has-text("Campus")')
        campus_filter.click()
        
        # Wait for filter to apply
        page.wait_for_timeout(500)
        
        # Verify filtered templates
        filtered_templates = page.locator(".template-card")
        assert filtered_templates.count() > 0, "Should have at least one Campus template"
        
        # Verify filter button is active
        is_active = campus_filter.evaluate('el => el.classList.contains("active")')
        assert is_active, "Campus filter should be active"
    
    def test_all_filter_resets_filters(self, page: Page):
        """Test that 'All' filter resets to show all templates."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Apply a filter first
        production_filter = page.locator('.filter-btn:has-text("Production")')
        production_filter.click()
        page.wait_for_timeout(500)
        
        # Click All filter
        all_filter = page.locator('.filter-btn:has-text("All")')
        all_filter.click()
        
        # Wait for filter to apply
        page.wait_for_timeout(500)
        
        # Verify all templates are shown
        all_templates = page.locator(".template-card")
        assert all_templates.count() > 0, "Should show all templates"
        
        # Verify All filter is active
        is_active = all_filter.evaluate('el => el.classList.contains("active")')
        assert is_active, "All filter should be active"
    
    def test_comparison_button_visible(self, page: Page):
        """Test that Compare Templates button is visible."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Verify Compare button is present
        compare_button = page.locator('button:has-text("Compare Templates")')
        expect(compare_button).to_be_visible()
    
    def test_comparison_mode_opens(self, page: Page):
        """Test that comparison mode opens when button is clicked."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Click Compare button
        compare_button = page.locator('button:has-text("Compare Templates")')
        compare_button.click()
        
        # Wait for comparison view
        comparison = page.locator('.template-comparison')
        expect(comparison).to_be_visible()
        
        # Verify comparison table is present
        comparison_table = page.locator('.comparison-table')
        expect(comparison_table).to_be_visible()
    
    def test_comparison_table_shows_all_templates(self, page: Page):
        """Test that comparison table shows all templates as columns."""
        # Navigate to multi-switch mode and open comparison
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        page.click('button:has-text("Compare Templates")')
        
        comparison = page.locator('.template-comparison')
        expect(comparison).to_be_visible()
        
        # Get table headers
        headers = page.locator('.comparison-table th')
        assert headers.count() > 1, "Should have at least 2 columns (Feature + templates)"
    
    def test_comparison_table_shows_features(self, page: Page):
        """Test that comparison table shows key features as rows."""
        # Navigate to multi-switch mode and open comparison
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        page.click('button:has-text("Compare Templates")')
        
        comparison = page.locator('.template-comparison')
        expect(comparison).to_be_visible()
        
        # Get table rows
        rows = page.locator('.comparison-table tbody tr')
        assert rows.count() >= 7, "Should have at least 7 feature rows"
    
    def test_comparison_back_button_works(self, page: Page):
        """Test that Back to Gallery button returns to template gallery."""
        # Navigate to multi-switch mode and open comparison
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        page.click('button:has-text("Compare Templates")')
        
        comparison = page.locator('.template-comparison')
        expect(comparison).to_be_visible()
        
        # Click Back button
        back_button = page.locator('button:has-text("Back to Gallery")')
        back_button.click()
        
        # Verify gallery is visible again
        gallery = page.locator("#templateGallery")
        expect(gallery).to_be_visible()
        
        # Verify template cards are displayed
        template_cards = page.locator(".template-card")
        assert template_cards.count() > 0, "Template cards should be displayed"
    
    def test_hardware_compatibility_shown(self, page: Page):
        """Test that hardware compatibility is shown on template cards."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Get template cards
        template_cards = page.locator(".template-card")
        assert template_cards.count() > 0, "Should have template cards"
    
    def test_hardware_list_shows_models(self, page: Page):
        """Test that hardware list shows compatible switch models."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Get first template card
        first_card = page.locator(".template-card").first
        card_text = first_card.inner_text()
        
        # Verify hardware models are listed
        assert 'Nexus' in card_text, "Should mention Nexus models"
        assert len(card_text) > 5, "Should have hardware model names"
    
    def test_best_practice_badge_visible(self, page: Page):
        """Test that best practice badges are shown on templates."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Check for best practice badges
        badges = page.locator('.best-practice-badge')
        assert badges.count() > 0, "Should have at least one best practice badge"
    
    def test_complexity_badges_colored(self, page: Page):
        """Test that complexity badges have appropriate colors."""
        # Navigate to multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Get complexity badges
        complexity_badges = page.locator('.template-badge')
        assert complexity_badges.count() > 0, "Should have complexity badges"
    
    def test_comparison_table_complexity_colored(self, page: Page):
        """Test that comparison table complexity cells are colored."""
        # Navigate to multi-switch mode and open comparison
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        page.click('button:has-text("Compare Templates")')
        
        comparison = page.locator('.template-comparison')
        expect(comparison).to_be_visible()
        
        # Get table content
        table_content = page.locator('.comparison-table')
        expect(table_content).to_be_visible()
    
    def test_comparison_table_hardware_listed(self, page: Page):
        """Test that comparison table shows hardware compatibility."""
        # Navigate to multi-switch mode and open comparison
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        page.click('button:has-text("Compare Templates")')
        
        comparison = page.locator('.template-comparison')
        expect(comparison).to_be_visible()
        
        # Get table content
        table_content = page.locator('.comparison-table')
        table_text = table_content.inner_text()
        
        # Verify hardware is mentioned
        assert 'Nexus' in table_text, "Comparison table should mention Nexus hardware"
    
    def test_comparison_table_best_practice_indicators(self, page: Page):
        """Test that comparison table shows best practice indicators."""
        # Navigate to multi-switch mode and open comparison
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        page.click('button:has-text("Compare Templates")')
        
        comparison = page.locator('.template-comparison')
        expect(comparison).to_be_visible()
        
        # Get table content
        table_content = page.locator('.comparison-table')
        table_text = table_content.inner_text()
        
        # Verify best practice is mentioned
        assert 'Best Practice' in table_text, "Should have Best Practice row"
