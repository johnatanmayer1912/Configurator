"""
Forensic Test: Release Notes Modal Dismiss
==========================================

This test verifies that the release notes modal close button actually works.
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestReleaseNotesModal:
    """Test release notes modal dismiss functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_page(self, browser):
        """Setup page and navigate to application."""
        page = browser.new_page()
        page.goto("http://localhost:8001")
        yield page
        page.close()
    
    def test_release_notes_modal_close_button(self, setup_page: Page):
        """
        Test that the release notes modal close button actually hides the modal.
        """
        page = setup_page
        
        # Wait for page to load
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        time.sleep(2)
        
        # Check if release notes modal is visible
        release_notes_modal = page.locator("#releaseNotesModal")
        
        if release_notes_modal.is_visible():
            print("Release notes modal is visible, attempting to close")
            
            # First dismiss the modal itself since it has higher z-index
            close_button = release_notes_modal.get_by_role("button", name="Close", exact=True)
            close_button.click()
            time.sleep(1)
            
            # Verify modal is hidden
            expect(release_notes_modal).not_to_be_visible()
            print("SUCCESS: Close button hid the modal")
            
            # Also dismiss validation panel if it's still visible
            validation_panel = page.locator("#validationPanel")
            if validation_panel.is_visible():
                print("Validation panel still visible, dismissing it")
                dismiss_button = validation_panel.get_by_role("button", name="Dismiss")
                dismiss_button.click()
                time.sleep(1)
                expect(validation_panel).not_to_be_visible()
                print("SUCCESS: Dismiss button hid the validation panel")
        else:
            print("Release notes modal is not visible, opening it to test")
            
            # Open release notes modal
            page.get_by_role("menuitem", name="What's New").click()
            time.sleep(1)
            
            # Verify modal is now visible
            expect(release_notes_modal).to_be_visible()
            print("Release notes modal is now visible")
            
            # Click Close button
            close_button = release_notes_modal.get_by_role("button", name="Close", exact=True)
            close_button.click()
            time.sleep(1)
            
            # Verify modal is hidden
            expect(release_notes_modal).not_to_be_visible()
            print("SUCCESS: Close button hid the modal")
    
    def test_release_notes_modal_escape_key(self, setup_page: Page):
        """
        Test that pressing Escape closes the release notes modal.
        """
        page = setup_page
        
        # Wait for page to load
        expect(page).to_have_title("NX-OS Configurator | Configuration Authority")
        time.sleep(2)
        
        # Dismiss release notes modal if visible
        release_notes_modal = page.locator("#releaseNotesModal")
        if release_notes_modal.is_visible():
            close_button = release_notes_modal.get_by_role("button", name="Close", exact=True)
            close_button.click()
            time.sleep(1)
        
        # Open Actions dropdown
        actions_dropdown = page.get_by_role("button", name="Actions")
        actions_dropdown.click()
        time.sleep(1)
        
        # Open release notes modal
        page.get_by_role("menuitem", name="What's New").click()
        time.sleep(1)
        
        # Verify modal is visible
        expect(release_notes_modal).to_be_visible()
        
        # Press Escape key
        page.keyboard.press("Escape")
        time.sleep(1)
        
        # Verify modal is hidden
        expect(release_notes_modal).not_to_be_visible()
        print("SUCCESS: Escape key closed the modal")
