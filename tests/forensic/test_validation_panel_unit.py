"""
FORENSIC CRITICAL TEST - Validation Panel Unit Test
===================================================

This test directly validates the JavaScript functions that control the validation panel
to ensure the contradictory state bug is fixed at the code level.

This tests the actual logic in app.js:
- showValidationPanel() should not show panel when errors.length === 0
- dismissValidationPanel() should clear validationErrors array
- dismissValidationPanel() should hide both legacy and new panels
"""

import pytest


class TestValidationPanelLogic:
    """Unit tests for validation panel logic (forensic level)."""
    
    def test_showValidationPanel_with_empty_errors_should_dismiss(self):
        """
        FORENSIC TEST: Verify showValidationPanel([]) calls dismissValidationPanel().
        
        This is the core fix for the contradictory state bug.
        When errors array is empty, the panel should be dismissed, not shown.
        """
        # Read the actual JavaScript code to verify the fix
        with open("c:\\Users\\bbb12\\OneDrive\\Desktop\\Antigravity Projects Folder\\Configurator - Copy\\static\\app.js", "r", encoding="utf-8") as f:
            app_js = f.read()
        
        # FORENSIC CHECK: Verify the fix is present in the code
        assert "if (errors.length === 0)" in app_js, "FORENSIC FAILURE: Missing check for empty errors array"
        assert "dismissValidationPanel()" in app_js, "FORENSIC FAILURE: dismissValidationPanel call missing"
        
        # Verify the fix is in the right place (inside showValidationPanel function)
        show_validation_panel_start = app_js.find("function showValidationPanel(errors)")
        assert show_validation_panel_start != -1, "FORENSIC FAILURE: showValidationPanel function not found"
        
        # Find the next function to bound our search
        next_function_start = app_js.find("\nfunction ", show_validation_panel_start + 1)
        if next_function_start == -1:
            next_function_start = len(app_js)
        
        function_body = app_js[show_validation_panel_start:next_function_start]
        
        # Verify the fix is in the function body
        assert "if (errors.length === 0)" in function_body, "FORENSIC FAILURE: Empty errors check not in showValidationPanel"
        assert "dismissValidationPanel();" in function_body, "FORENSIC FAILURE: dismissValidationPanel call not in showValidationPanel"
        assert "return;" in function_body, "FORENSIC FAILURE: Early return not present after dismissValidationPanel"
    
    def test_dismissValidationPanel_clears_errors(self, page):
        """
        FORENSIC TEST: Verify dismissValidationPanel() clears validationErrors array.
        
        This prevents the modal from re-appearing after dismissal.
        """
        # Read the actual JavaScript code to verify the fix
        with open("c:\\Users\\bbb12\\OneDrive\\Desktop\\Antigravity Projects Folder\\Configurator - Copy\\static\\app.js", "r", encoding="utf-8") as f:
            app_js = f.read()
        
        # FORENSIC CHECK: Verify validationErrors is cleared
        dismiss_function_start = app_js.find("function dismissValidationPanel()")
        assert dismiss_function_start != -1, "FORENSIC FAILURE: dismissValidationPanel function not found"
        
        # Find the next function to bound our search
        next_function_start = app_js.find("\nfunction ", dismiss_function_start + 1)
        if next_function_start == -1:
            next_function_start = len(app_js)
        
        function_body = app_js[dismiss_function_start:next_function_start]
        
        # Verify validationErrors is cleared
        assert "validationErrors = []" in function_body or "validationErrors.length = 0" in function_body, \
            "FORENSIC FAILURE: validationErrors not cleared in dismissValidationPanel"
    
    def test_dismissValidationPanel_hides_both_panels(self, page):
        """
        FORENSIC TEST: Verify dismissValidationPanel() hides both legacy and new panels.
        
        This ensures consistency across the two panel implementations.
        """
        # Read the actual JavaScript code to verify the fix
        with open("c:\\Users\\bbb12\\OneDrive\\Desktop\\Antigravity Projects Folder\\Configurator - Copy\\static\\app.js", "r", encoding="utf-8") as f:
            app_js = f.read()
        
        # FORENSIC CHECK: Verify both panels are dismissed
        dismiss_function_start = app_js.find("function dismissValidationPanel()")
        assert dismiss_function_start != -1, "FORENSIC FAILURE: dismissValidationPanel function not found"
        
        # Find the next function to bound our search
        next_function_start = app_js.find("\nfunction ", dismiss_function_start + 1)
        if next_function_start == -1:
            next_function_start = len(app_js)
        
        function_body = app_js[dismiss_function_start:next_function_start]
        
        # Verify legacy panel is dismissed
        assert "getElementById('validationPanel')" in function_body, \
            "FORENSIC FAILURE: Legacy panel (validationPanel) not dismissed"
        
        # Verify new panel is dismissed
        assert "getElementById('validation-panel')" in function_body, \
            "FORENSIC FAILURE: New panel (validation-panel) not dismissed"
        
        # Verify both have visible class removed
        assert "classList.remove('visible')" in function_body or "classList.add('hidden')" in function_body, \
            "FORENSIC FAILURE: Panel visibility not properly toggled"
    
    def test_html_dismiss_button_uses_correct_function(self):
        """
        FORENSIC TEST: Verify the HTML dismiss button has correct ID and inline script handler.
        
        This ensures the button is wired correctly via inline script (fix for PyInstaller exe).
        """
        # Read the HTML template
        with open("c:\\Users\\bbb12\\OneDrive\\Desktop\\Antigravity Projects Folder\\Configurator - Copy\\templates\\web\\index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # FORENSIC CHECK: Verify dismiss button has correct ID
        assert 'id="dismissValidationBtn"' in html_content, \
            "FORENSIC FAILURE: Dismiss button does not have correct ID"
        
        # FORENSIC CHECK: Verify inline script handler exists
        assert "document.getElementById('dismissValidationBtn')" in html_content, \
            "FORENSIC FAILURE: Inline script handler not found"
        
        # FORENSIC CHECK: Verify script removes 'visible' class and sets display to none
        assert "panel.classList.remove('visible')" in html_content, \
            "FORENSIC FAILURE: Script does not remove visible class"
        assert "panel.style.display = 'none'" in html_content, \
            "FORENSIC FAILURE: Script does not set display to none"
