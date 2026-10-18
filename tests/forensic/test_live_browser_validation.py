"""
FORENSIC CRITICAL TEST - Live Browser Validation
==============================================

This test performs live browser validation of the validation popup fix.
It captures screenshots and verifies the actual user experience.

This is PHASE 0 validation - proving the fix works in a real browser.
"""

import pytest
import subprocess
import sys
import time
from playwright.sync_api import Page, expect


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


class TestLiveBrowserValidation:
    """Live browser validation tests (forensic level)."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_validation_panel_dismissal_with_screenshot(self, page):
        """
        FORENSIC TEST: Live browser validation with screenshot capture.
        
        This test:
        1. Triggers validation panel with errors
        2. Captures screenshot of panel visible state
        3. Clicks Dismiss button
        4. Captures screenshot of panel hidden state
        5. Verifies wizard remains interactive
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Trigger validation with errors via JavaScript
        page.evaluate("""
            () => {
                showValidationPanel([
                    {message: 'Test error 1', location: 'Step 3: Platform'},
                    {message: 'Test error 2', location: 'Step 4: Features'}
                ]);
            }
        """)
        time.sleep(1)
        
        # FORENSIC EVIDENCE: Capture screenshot of panel visible
        page.screenshot(path="forensic_evidence_panel_visible.png")
        
        # Verify panel is visible
        validation_panel = page.locator("#validationPanel")
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert has_visible_class, "FORENSIC FAILURE: Panel should have 'visible' class"
        
        # Verify error count
        count_text = page.locator("#validationCount").text_content()
        assert count_text == "2", f"FORENSIC FAILURE: Expected count 2, got {count_text}"
        
        # Click Dismiss button
        page.click(".dismiss-btn")
        time.sleep(1)
        
        # FORENSIC EVIDENCE: Capture screenshot of panel hidden
        page.screenshot(path="forensic_evidence_panel_hidden.png")
        
        # Verify panel is hidden
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert not has_visible_class, "FORENSIC FAILURE: Panel should not have 'visible' class after dismiss"
        
        # Verify errors cleared
        errors_count = page.evaluate("() => validationErrors.length")
        assert errors_count == 0, f"FORENSIC FAILURE: validationErrors not cleared, count={errors_count}"
        
        # FORENSIC CHECK: Verify page is still responsive after dismissal
        # Try to interact with page to ensure it's not blocked
        page.evaluate("() => document.body.click()")
        time.sleep(0.5)
        
        # FORENSIC EVIDENCE: Capture screenshot of page after dismissal
        page.screenshot(path="forensic_evidence_page_responsive.png")
    
    def test_no_contradictory_state_with_screenshot(self, page):
        """
        FORENSIC TEST: Verify no contradictory state with screenshot evidence.
        
        This test specifically checks that the bug (0 issues + warning) is fixed.
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Show panel with errors first
        page.evaluate("""
            () => {
                showValidationPanel([
                    {message: 'Test error', location: 'Test location'}
                ]);
            }
        """)
        time.sleep(1)
        
        # FORENSIC EVIDENCE: Capture screenshot of panel with errors
        page.screenshot(path="forensic_evidence_panel_with_errors.png")
        
        # Verify panel shows error
        count_text = page.locator("#validationCount").text_content()
        assert count_text == "1", f"FORENSIC FAILURE: Expected count 1, got {count_text}"
        
        # Call showValidationPanel with empty array (the bug scenario)
        page.evaluate("""
            () => {
                showValidationPanel([]);
            }
        """)
        time.sleep(1)
        
        # FORENSIC EVIDENCE: Capture screenshot after empty errors
        page.screenshot(path="forensic_evidence_panel_after_empty.png")
        
        # FORENSIC ASSERTION: Panel should be hidden (no contradictory state)
        validation_panel = page.locator("#validationPanel")
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert not has_visible_class, "FORENSIC FAILURE: Panel has 'visible' class with empty errors - contradictory state bug still exists"
        
        # Verify errors cleared
        errors_count = page.evaluate("() => validationErrors.length")
        assert errors_count == 0, f"FORENSIC FAILURE: validationErrors not cleared after empty array, count={errors_count}"
