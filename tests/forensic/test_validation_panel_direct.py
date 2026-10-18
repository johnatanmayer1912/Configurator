"""
FORENSIC CRITICAL TEST - Validation Panel Direct DOM Test
=========================================================

This test directly validates the validation panel behavior by calling
the JavaScript functions and inspecting the DOM state.

This bypasses the wizard navigation and directly tests the core bug fix:
- showValidationPanel([]) should dismiss the panel
- dismissValidationPanel() should clear errors and hide panels
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


class TestValidationPanelDirect:
    """Direct DOM tests for validation panel (forensic level)."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_showValidationPanel_empty_array_dismisses_panel(self, page):
        """
        FORENSIC TEST: Call showValidationPanel([]) directly and verify panel is dismissed.
        
        This is the core fix for the contradictory state bug.
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # First, show panel with errors to make it visible
        page.evaluate("""
            () => {
                showValidationPanel([
                    {message: 'Test error', location: 'Test location'}
                ]);
            }
        """)
        time.sleep(1)
        
        # Verify panel is visible
        validation_panel = page.locator("#validationPanel")
        expect(validation_panel).to_be_visible()
        
        # FORENSIC TEST: Call showValidationPanel with empty array
        page.evaluate("""
            () => {
                showValidationPanel([]);
            }
        """)
        time.sleep(1)
        
        # FORENSIC ASSERTION: Panel should not have 'visible' class
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert not has_visible_class, "FORENSIC FAILURE: Panel still has 'visible' class after empty errors"
        
        # FORENSIC CHECK: validationErrors should be cleared
        errors_count = page.evaluate("() => validationErrors.length")
        assert errors_count == 0, f"FORENSIC FAILURE: validationErrors not cleared, count={errors_count}"
    
    def test_dismissValidationPanel_clears_errors_and_hides_panel(self, page):
        """
        FORENSIC TEST: Verify dismissValidationPanel() clears errors and hides panel.
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Show panel with errors
        page.evaluate("""
            () => {
                showValidationPanel([
                    {message: 'Test error 1', location: 'Test location 1'},
                    {message: 'Test error 2', location: 'Test location 2'}
                ]);
            }
        """)
        time.sleep(1)
        
        # Verify panel is visible
        validation_panel = page.locator("#validationPanel")
        expect(validation_panel).to_be_visible()
        
        # Verify errors count
        errors_count = page.evaluate("() => validationErrors.length")
        assert errors_count == 2, f"FORENSIC FAILURE: Expected 2 errors, got {errors_count}"
        
        # FORENSIC TEST: Call dismissValidationPanel
        page.evaluate("""
            () => {
                dismissValidationPanel();
            }
        """)
        time.sleep(1)
        
        # FORENSIC ASSERTION: Panel should not have 'visible' class
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert not has_visible_class, "FORENSIC FAILURE: Panel still has 'visible' class after dismiss"
        
        # FORENSIC CHECK: validationErrors should be cleared
        errors_count = page.evaluate("() => validationErrors.length")
        assert errors_count == 0, f"FORENSIC FAILURE: validationErrors not cleared, count={errors_count}"
    
    def test_dismiss_button_click_calls_function(self, page):
        """
        FORENSIC TEST: Verify clicking the dismiss button calls dismissValidationPanel().
        """
        page.goto("http://127.0.0.1:9000")
        page.wait_for_load_state("networkidle")
        
        # Show panel with errors
        page.evaluate("""
            () => {
                showValidationPanel([
                    {message: 'Test error', location: 'Test location'}
                ]);
            }
        """)
        time.sleep(1)
        
        # Verify panel is visible
        validation_panel = page.locator("#validationPanel")
        expect(validation_panel).to_be_visible()
        
        # FORENSIC TEST: Click the dismiss button
        page.click(".dismiss-btn")
        time.sleep(1)
        
        # FORENSIC ASSERTION: Panel should not have 'visible' class
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert not has_visible_class, "FORENSIC FAILURE: Panel still has 'visible' class after dismiss button click"
        
        # FORENSIC CHECK: validationErrors should be cleared
        errors_count = page.evaluate("() => validationErrors.length")
        assert errors_count == 0, f"FORENSIC FAILURE: validationErrors not cleared, count={errors_count}"
    
    def test_no_contradictory_state_after_empty_errors(self, page):
        """
        FORENSIC TEST: Verify no contradictory state after showing panel with empty errors.
        
        This tests the specific bug: "0 configuration issues" + "Configuration Issues" warning.
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
        
        # Verify panel is visible with count
        validation_panel = page.locator("#validationPanel")
        expect(validation_panel).to_be_visible()
        count_text = page.locator("#validationCount").text_content()
        assert count_text == "1", f"FORENSIC FAILURE: Expected count 1, got {count_text}"
        
        # FORENSIC TEST: Call showValidationPanel with empty array
        page.evaluate("""
            () => {
                showValidationPanel([]);
            }
        """)
        time.sleep(1)
        
        # FORENSIC ASSERTION: Panel should not have 'visible' class (no contradictory state)
        has_visible_class = validation_panel.evaluate("el => el.classList.contains('visible')")
        assert not has_visible_class, "FORENSIC FAILURE: Panel has 'visible' class with empty errors - contradictory state"
        
        # FORENSIC CHECK: validationErrors should be cleared
        errors_count = page.evaluate("() => validationErrors.length")
        assert errors_count == 0, f"FORENSIC FAILURE: validationErrors not cleared after empty array, count={errors_count}"
        
        # FORENSIC CHECK: Verify no contradictory state in DOM
        # If panel was visible with count 0, that would be the bug
        is_visible = validation_panel.is_visible()
        if is_visible:
            count_text = page.locator("#validationCount").text_content()
            panel_title = page.locator("#validationPanel h4").text_content()
            pytest.fail(f"FORENSIC FAILURE: Contradictory state detected - count={count_text}, title={panel_title}")
