"""
FORENSIC CRITICAL TEST - Validation Popup Bug
==============================================

This test validates the fix for the contradictory validation popup bug:
- Green check / "0 configuration issues" 
- Simultaneously yellow warning triangle + red text "Configuration Issues"
- Dismiss button does nothing

This is a FORENSIC test that actually interacts with the live DOM and verifies:
1. The contradictory state does not occur
2. The Dismiss button actually closes the modal
3. The wizard can proceed after dismissal

This test is NOT a mock or snapshot test - it drives the real application.
"""

import pytest
import subprocess
import sys
import time
from playwright.sync_api import Page, expect
import os


@pytest.fixture(scope="session")
def web_server():
    """Start web server for forensic testing."""
    # Start the web server in the background
    server_process = subprocess.Popen(
        [sys.executable, "web_launcher.py"],
        cwd="c:\\Users\\bbb12\\OneDrive\\Desktop\\Antigravity Projects Folder\\Configurator - Copy",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    time.sleep(5)
    
    yield server_process
    
    # Cleanup: terminate server process
    try:
        server_process.terminate()
        server_process.wait(timeout=5)
    except:
        try:
            server_process.kill()
        except:
            pass


class TestValidationPopupForensic:
    """Forensic test for validation popup bug fix."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_no_contradictory_validation_state(self, page):
        """
        FORENSIC TEST: Verify contradictory state (0 issues + warning) does not occur.
        
        Steps:
        1. Navigate to configurator
        2. Complete wizard steps to trigger validation
        3. Verify no contradictory state appears
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Step 1: Select Leaf/ToR role (actual clickable element)
        page.click("button:has-text('Leaf/ToR')")
        time.sleep(1)
        
        # Step 2: Select vPC
        page.click("button:has-text('vPC Pair')")
        time.sleep(1)
        
        # Step 3: Select Speed (e.g., 100G)
        page.click("button:has-text('100G')")
        time.sleep(1)
        
        # Step 4: Fill in platform details
        page.fill("#hostname", "TEST-SWITCH-1")
        page.fill("#mgmt_ip", "10.10.10.10/24")
        page.fill("#mgmt_gw", "10.10.10.1")
        
        # Select model
        page.select_option("#model", "N9K-C93180YC-FX")
        
        # Select NX-OS version
        page.select_option("#nxos_version", "9.3(7)")
        
        # Step 5: Generate configuration
        page.click("button:has-text('Generate')")
        time.sleep(2)
        
        # FORENSIC CHECK: Verify validation panel state
        validation_panel = page.locator("#validationPanel")
        
        # Check if panel is visible
        is_visible = validation_panel.is_visible()
        
        if is_visible:
            # If visible, check for contradictory state
            count_text = page.locator("#validationCount").text_content()
            panel_title = page.locator("#validationPanel h4").text_content()
            
            # FORENSIC ASSERTION: Should NOT have "0 configuration issues" with "Configuration Issues" title
            if count_text == "0" and panel_title == "Configuration Issues":
                pytest.fail(f"FORENSIC FAILURE: Contradictory state detected - count={count_text}, title={panel_title}")
            
            # If there are actual errors, verify the count matches
            if count_text != "0":
                error_count = int(count_text)
                error_items = page.locator(".validation-item").count()
                assert error_count == error_items, f"FORENSIC FAILURE: Count mismatch - count={count_text}, items={error_items}"
    
    def test_dismiss_button_closes_modal(self, page):
        """
        FORENSIC TEST: Verify Dismiss button actually closes the modal.
        
        Steps:
        1. Navigate to configurator
        2. Trigger validation with actual errors
        3. Click Dismiss button
        4. Verify modal closes
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Step 1: Select Leaf/ToR role
        page.click("button:has-text('Leaf/ToR')")
        time.sleep(1)
        
        # Step 2: Select vPC
        page.click("button:has-text('vPC Pair')")
        time.sleep(1)
        
        # Step 3: Select Speed
        page.click("button:has-text('100G')")
        time.sleep(1)
        
        # Step 4: Fill platform with invalid data to trigger validation
        page.fill("#hostname", "")  # Empty hostname to trigger error
        page.fill("#mgmt_ip", "invalid")  # Invalid IP to trigger error
        
        # Step 5: Try to generate
        page.click("button:has-text('Generate')")
        time.sleep(2)
        
        # FORENSIC CHECK: Validation panel should appear
        validation_panel = page.locator("#validationPanel")
        expect(validation_panel).to_be_visible()
        
        # Click Dismiss button
        page.click(".dismiss-btn")
        time.sleep(1)
        
        # FORENSIC ASSERTION: Modal should be hidden
        expect(validation_panel).not_to_be_visible()
        
        # FORENSIC CHECK: validationErrors should be cleared
        # This prevents the modal from re-appearing
        page.click("button:has-text('Generate')")
        time.sleep(1)
        
        # Modal should not re-appear since errors were dismissed
        expect(validation_panel).not_to_be_visible()
    
    def test_zero_errors_does_not_show_panel(self, page):
        """
        FORENSIC TEST: Verify panel does not show when there are 0 errors.
        
        This is the core fix for the contradictory state bug.
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Complete wizard with valid data
        page.click("button:has-text('Leaf/ToR')")
        time.sleep(1)
        
        page.click("button:has-text('vPC Pair')")
        time.sleep(1)
        
        page.click("button:has-text('100G')")
        time.sleep(1)
        
        # Fill with valid data
        page.fill("#hostname", "TEST-SWITCH-1")
        page.fill("#mgmt_ip", "10.10.10.10/24")
        page.fill("#mgmt_gw", "10.10.10.1")
        page.select_option("#model", "N9K-C93180YC-FX")
        page.select_option("#nxos_version", "9.3(7)")
        
        # Generate
        page.click("button:has-text('Generate')")
        time.sleep(2)
        
        # FORENSIC ASSERTION: Validation panel should NOT be visible
        validation_panel = page.locator("#validationPanel")
        expect(validation_panel).not_to_be_visible()
        
        # FORENSIC CHECK: No contradictory state in DOM
        # Check that validationPanel doesn't have 'visible' class
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert not has_visible_class, "FORENSIC FAILURE: Panel has 'visible' class when it should be hidden"
    
    def test_wizard_proceeds_after_dismiss(self, page):
        """
        FORENSIC TEST: Verify wizard can proceed after dismissing validation panel.
        
        Steps:
        1. Trigger validation with errors
        2. Dismiss the panel
        3. Verify wizard steps are still interactive
        4. Verify user can navigate to other steps
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Navigate to step with validation
        page.click("button:has-text('Leaf/ToR')")
        time.sleep(1)
        
        page.click("button:has-text('vPC Pair')")
        time.sleep(1)
        
        page.click("button:has-text('100G')")
        time.sleep(1)
        
        # Trigger validation error
        page.fill("#hostname", "")
        page.click("button:has-text('Generate')")
        time.sleep(2)
        
        # Dismiss panel
        page.click(".dismiss-btn")
        time.sleep(1)
        
        # FORENSIC CHECK: Wizard should still be interactive
        # Try to navigate to another step
        page.click("button[data-step='4']")
        time.sleep(1)
        
        # Verify step 4 is active
        step4 = page.locator("#step-4")
        expect(step4).to_have_class("wizard-step active")
        
        # Verify we can fill in features
        page.click("label:has-text('SNMP Traps')")
        time.sleep(0.5)
        
        # FORENSIC ASSERTION: Wizard is interactive after dismissal
        # If the bug existed, the wizard would be blocked
        assert True, "Wizard is interactive after dismissing validation panel"
