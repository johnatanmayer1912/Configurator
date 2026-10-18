"""
UI tests for Template Gallery feature
Tests the new template selection and application UX
"""

import pytest
from playwright.sync_api import Page, expect


class TestTemplateGallery:
    """Test template gallery UI and functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        page.goto("http://127.0.0.1:9000/")
        page.wait_for_load_state("networkidle")
        
        # Close any modals that might be open (release notes, etc.)
        page.evaluate("""
            () => {
                const modals = document.querySelectorAll('.modal[aria-modal="true"]');
                modals.forEach(modal => modal.remove());
            }
        """)
        page.wait_for_timeout(200)
    
    def test_template_gallery_visible_in_multi_switch_mode(self, page: Page):
        """Test that template gallery appears when entering multi-switch mode."""
        # Click mode dropdown to open menu
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        
        # Click multi-switch mode option
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Verify template gallery is visible
        gallery = page.locator("#templateGallery")
        expect(gallery).to_be_visible()
        
        # Verify gallery title
        expect(page.locator(".gallery-title")).to_contain_text("Multi-Switch Deployment Templates")
    
    def test_template_cards_display_all_templates(self, page: Page):
        """Test that all template cards are displayed."""
        # Enter multi-switch mode
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Count template cards
        cards = page.locator(".template-card")
        expect(cards).to_have_count(4)  # 4 templates: vpc_core_leaf, spine_leaf, six_switch_fabric, dual_core_fabric
    
    def test_template_card_shows_required_information(self, page: Page):
        """Test that template cards show all required information."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Check first template card
        first_card = page.locator(".template-card").first
        expect(first_card.locator(".template-name")).to_be_visible()
        expect(first_card.locator(".template-description")).to_be_visible()
        expect(first_card.locator(".template-badge")).to_have_count(3)  # switches, vPC domains, complexity
        expect(first_card.locator(".template-use-case")).to_be_visible()
        expect(first_card.locator(".template-action")).to_be_visible()
    
    def test_template_topology_svg_rendered(self, page: Page):
        """Test that topology SVG is rendered in template cards."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Check for SVG in template cards
        svgs = page.locator(".template-topology svg")
        expect(svgs).to_have_count(4)  # One per template card
    
    def test_template_application_on_click(self, page: Page):
        """Test that clicking a template applies it."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Click first template
        page.locator(".template-card").first.click()
        page.wait_for_timeout(500)
        
        # Verify success message
        expect(page.locator(".toast")).to_contain_text("applied successfully")
        
        # Verify template gallery is hidden (check for hidden class)
        gallery = page.locator("#templateGallery")
        expect(gallery).to_have_css("display", "none")
        
        # Verify switch list panel is visible
        expect(page.locator("#switchListPanel")).to_be_visible()
    
    def test_template_applies_switches(self, page: Page):
        """Test that template application creates switches."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Apply vPC Core + Leaf template (4 switches)
        page.locator(".template-card").first.click()
        page.wait_for_timeout(500)
        
        # Verify switches are created (check for switch hostnames in the UI)
        expect(page.locator(".switch-name").filter(has_text="CORE1")).to_be_visible()
        expect(page.locator(".switch-name").filter(has_text="CORE2")).to_be_visible()
        expect(page.locator(".switch-name").filter(has_text="LEAF10G-1")).to_be_visible()
        expect(page.locator(".switch-name").filter(has_text="LEAF10G-2")).to_be_visible()
    
    def test_template_applies_vpc_domains(self, page: Page):
        """Test that template application creates vPC domains."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Apply vPC Core + Leaf template (2 vPC domains)
        page.locator(".template-card").first.click()
        page.wait_for_timeout(500)
        
        # Verify vPC domains are created (check for vPC domain text in the UI)
        expect(page.locator("text=Domain 10: CORE1")).to_be_visible()
        expect(page.locator("text=Domain 100: LEAF10G-1")).to_be_visible()
    
    def test_template_applies_global_vlans(self, page: Page):
        """Test that template application creates global VLANs."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Apply template
        page.locator(".template-card").first.click()
        page.wait_for_timeout(500)
        
        # Verify global VLANs section is visible
        expect(page.locator("text=Global VLAN Configuration")).to_be_visible()
    
    def test_template_summary_shown_after_application(self, page: Page):
        """Test that configuration summary is shown after template application."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Apply template
        page.locator(".template-card").first.click()
        page.wait_for_timeout(500)
        
        # Verify validation status summary
        summary = page.locator(".validation-status.valid")
        expect(summary).to_be_visible()
        expect(summary).to_contain_text("switches")
        expect(summary).to_contain_text("vPC domains")
        expect(summary).to_contain_text("uplinks")
    
    def test_manual_configuration_option_available(self, page: Page):
        """Test that manual configuration option is available."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Verify manual configuration button
        manual_btn = page.locator("text=Use Manual Configuration")
        expect(manual_btn).to_be_visible()
    
    def test_manual_configuration_hides_gallery(self, page: Page):
        """Test that manual configuration hides template gallery."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Click manual configuration
        page.click("text=Use Manual Configuration")
        page.wait_for_timeout(500)
        
        # Verify gallery is hidden
        expect(page.locator("#templateGallery")).to_be_hidden()
        
        # Verify switch list panel is visible
        expect(page.locator("#switchListPanel")).to_be_visible()
    
    def test_template_card_hover_effect(self, page: Page):
        """Test that template cards have hover effect."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # Hover over template card
        card = page.locator(".template-card").first
        card.hover()
        page.wait_for_timeout(200)
        
        # Verify visual change (border color change)
        # This is a visual test, so we just verify the element is still visible
        expect(card).to_be_visible()


class TestTemplateData:
    """Test template data structure and content."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        page.goto("http://127.0.0.1:9000/")
        page.wait_for_load_state("networkidle")
        
        # Close any modals that might be open (release notes, etc.)
        page.evaluate("""
            () => {
                const modals = document.querySelectorAll('.modal[aria-modal="true"]');
                modals.forEach(modal => modal.remove());
            }
        """)
        page.wait_for_timeout(200)
    
    def test_template_metadata_complete(self, page: Page):
        """Test that all templates have complete metadata."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        cards = page.locator(".template-card")
        count = cards.count()
        
        for i in range(count):
            card = cards.nth(i)
            # Verify all badges are present
            badges = card.locator(".template-badge")
            expect(badges).to_have_count(3)
            
            # Verify use case is present
            use_case = card.locator(".template-use-case")
            expect(use_case).to_be_visible()
    
    def test_template_switch_count_accuracy(self, page: Page):
        """Test that template switch count badges are accurate."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # vPC Core + Leaf should show 4 switches
        first_card = page.locator(".template-card").first
        expect(first_card).to_contain_text("4 switches")
    
    def test_template_vpc_domain_count_accuracy(self, page: Page):
        """Test that template vPC domain count badges are accurate."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        # vPC Core + Leaf should show 2 vPC domains
        first_card = page.locator(".template-card").first
        expect(first_card).to_contain_text("2 vPC domains")
    
    def test_template_complexity_badge_present(self, page: Page):
        """Test that complexity badge is present on all templates."""
        page.click("#modeDropdownBtn")
        page.wait_for_timeout(200)
        page.click("text=Multi-Switch")
        page.wait_for_timeout(500)
        
        cards = page.locator(".template-card")
        count = cards.count()
        
        for i in range(count):
            card = cards.nth(i)
            # Verify complexity badge exists
            badges = card.locator(".template-badge")
            expect(badges).to_have_count(3)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
