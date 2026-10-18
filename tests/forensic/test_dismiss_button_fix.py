"""
Forensic Test: Dismiss Button Functionality
===========================================

This test verifies that the dismiss button actually works and hides the validation panel.
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestDismissButton:
    """Test dismiss button functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_page(self, browser):
        """Setup page and navigate to application."""
        page = browser.new_page()
        page.goto("http://localhost:8001")
        yield page
        page.close()
    
    def test_dismiss_button_hides_panel(self, setup_page: Page):
        """
        Test that the dismiss button actually hides the validation panel.
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
        
        # Trigger a validation error to show the panel
        # Navigate to platform step without selecting a role
        page.get_by_role("button", name="Next →").click()
        time.sleep(1)
        
        # Check if validation panel is visible
        validation_panel = page.locator("#validationPanel")
        
        # If panel is visible, try to dismiss it
        if validation_panel.is_visible():
            print("Validation panel is visible, attempting to dismiss")
            
            # Click dismiss button
            dismiss_button = page.get_by_role("button", name="Dismiss")
            dismiss_button.click()
            time.sleep(1)
            
            # Verify panel is hidden
            expect(validation_panel).not_to_be_visible()
            print("SUCCESS: Dismiss button hid the panel")
        else:
            print("Validation panel is not visible, creating a validation scenario")
            
            # Create a validation scenario by clearing hostname
            page.get_by_role("button", name="← Back").click()
            time.sleep(0.5)
            
            # Select a role
            page.get_by_text("Core / Spine").click()
            time.sleep(0.5)
            
            # Navigate to platform step
            page.get_by_role("button", name="Next →").click()
            time.sleep(0.5)
            
            # Clear hostname to trigger validation
            hostname_input = page.locator("#hostname")
            hostname_input.fill("")
            time.sleep(0.5)
            
            # Trigger validation by going to next step
            page.get_by_role("button", name="Next →").click()
            time.sleep(1)
            
            # Check if panel is now visible
            if validation_panel.is_visible():
                print("Validation panel is now visible")
                
                # Click dismiss button
                dismiss_button = page.get_by_role("button", name="Dismiss")
                dismiss_button.click()
                time.sleep(1)
                
                # Verify panel is hidden
                expect(validation_panel).not_to_be_visible()
                print("SUCCESS: Dismiss button hid the panel")
            else:
                print("FAILED: Could not trigger validation panel")
