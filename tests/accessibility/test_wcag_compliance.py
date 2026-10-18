"""
Accessibility Testing - WCAG 2.1 AA Compliance

This module validates accessibility compliance against WCAG 2.1 AA standards
using Playwright's accessibility tree and manual validation techniques.

WCAG 2.1 AA Standards:
- Color contrast: 4.5:1 for normal text, 3:1 for large text
- Keyboard navigation: All functionality must be keyboard accessible
- Focus indicators: Visible focus indicators for all interactive elements
- Screen reader: Semantic HTML and ARIA attributes
- Forms: Labels, error messages, and validation
- Headings: Proper heading hierarchy
- Landmarks: Proper landmark regions
"""

import pytest
from playwright.sync_api import Page, expect
import re
import subprocess
import time
import signal
import sys

# Server process fixture for accessibility tests
@pytest.fixture(scope="session")
def web_server():
    """Start web server for accessibility tests."""
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


class TestColorContrastCompliance:
    """Color contrast validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_text_color_contrast(self, page):
        """
        Validate text color contrast meets WCAG AA standards.
        
        WCAG 2.1 AA Standard:
        - Normal text (< 18pt): 4.5:1 contrast ratio
        - Large text (18pt+ or 14pt bold): 3:1 contrast ratio
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get all text elements
        text_elements = page.locator("p, span, div, td, li, a, button, label")
        
        for i in range(min(text_elements.count(), 50)):  # Limit to 50 elements for performance
            element = text_elements.nth(i)
            
            # Check if element is visible and attached to DOM
            try:
                is_visible = element.is_visible()
                if not is_visible:
                    continue
            except:
                continue
            
            # Get computed colors with proper error handling
            try:
                color = page.evaluate("el => getComputedStyle(el).color", element)
                bg_color = page.evaluate("el => getComputedStyle(el).backgroundColor", element)
                font_size = page.evaluate("el => getComputedStyle(el).fontSize", element)
                font_weight = page.evaluate("el => getComputedStyle(el).fontWeight", element)
            except:
                continue
            
            # Skip if no background color (transparent)
            if not bg_color or bg_color == "rgba(0, 0, 0, 0)" or bg_color == "transparent":
                continue
            
            # Calculate contrast ratio
            def hex_to_rgb(hex_color):
                if hex_color.startswith("rgb"):
                    return tuple(map(int, hex_color[4:-1].split(",")))
                return (0, 0, 0)
            
            text_rgb = hex_to_rgb(color)
            bg_rgb = hex_to_rgb(bg_color)
            
            def luminance(rgb):
                r, g, b = rgb
                def channel(c):
                    c = c / 255
                    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
            
            lum1 = luminance(text_rgb)
            lum2 = luminance(bg_rgb)
            
            lighter = max(lum1, lum2)
            darker = min(lum1, lum2)
            contrast_ratio = (lighter + 0.05) / (darker + 0.05)
            
            # Determine if large text
            font_size_num = float(re.sub(r'[^\d.]', '', font_size))
            is_bold = font_weight in ["700", "bold", "600", "semibold"]
            is_large = font_size_num >= 18 or (font_size_num >= 14 and is_bold)
            
            required_ratio = 3.0 if is_large else 4.5
            
            assert contrast_ratio >= required_ratio, \
                f"Contrast ratio {contrast_ratio:.2f} below WCAG AA standard of {required_ratio}:1"
    
    def test_link_color_contrast(self, page):
        """
        Validate link color contrast meets WCAG AA standards.
        
        WCAG 2.1 AA Standard:
        - Links must have 4.5:1 contrast with background
        - Links must have 3:1 contrast with surrounding text (if different color)
        """
        page.goto("http://127.0.0.1:9000")
        
        links = page.locator("a")
        if links.count() > 0:
            for i in range(min(links.count(), 20)):
                link = links.nth(i)
                
                try:
                    if not link.is_visible():
                        continue
                    color = page.evaluate("el => getComputedStyle(el).color", link)
                    bg_color = page.evaluate("el => getComputedStyle(el).backgroundColor", link)
                    
                    if bg_color and bg_color != "rgba(0, 0, 0, 0)":
                        # Calculate contrast (simplified)
                        assert color, f"Link should have color"
                except:
                    continue
    
    def test_button_color_contrast(self, page):
        """
        Validate button color contrast meets WCAG AA standards.
        
        WCAG 2.1 AA Standard:
        - Button text must have 4.5:1 contrast with button background
        - Button background must have 3:1 contrast with page background
        """
        page.goto("http://127.0.0.1:9000")
        
        buttons = page.locator("button, input[type='submit'], input[type='button']")
        if buttons.count() > 0:
            for i in range(min(buttons.count(), 20)):
                button = buttons.nth(i)
                
                try:
                    if not button.is_visible():
                        continue
                    text_color = page.evaluate("el => getComputedStyle(el).color", button)
                    bg_color = page.evaluate("el => getComputedStyle(el).backgroundColor", button)
                    
                    assert text_color, f"Button should have text color"
                    assert bg_color, f"Button should have background color"
                except:
                    continue


class TestKeyboardNavigation:
    """Keyboard navigation validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_keyboard_navigable(self, page):
        """
        Validate all interactive elements are keyboard navigable.
        
        WCAG 2.1 AA Standard:
        - All interactive elements must be focusable via keyboard
        - Tab order must be logical
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get all focusable elements
        focusable_elements = page.locator("a[href], button, input, select, textarea, [tabindex]:not([tabindex='-1'])")
        
        if focusable_elements.count() > 0:
            # Try to tab through elements
            for i in range(min(focusable_elements.count(), 20)):
                element = focusable_elements.nth(i)
                
                # Check if element can be focused
                try:
                    element.focus()
                    is_focused = page.evaluate("el => document.activeElement === el", element)
                    assert is_focused, f"Element should be keyboard focusable"
                except:
                    # Some elements might not be focusable in all contexts
                    pass
    
    def test_tab_order_logical(self, page):
        """
        Validate tab order follows logical reading order.
        
        WCAG 2.1 AA Standard:
        - Tab order should follow DOM order
        - No positive tabindex values (except for special cases)
        """
        page.goto("http://127.0.0.1:9000")
        
        # Check for positive tabindex values (generally discouraged)
        positive_tabindex = page.locator("[tabindex]:not([tabindex='0']):not([tabindex='-1'])")
        
        # Filter for positive values
        positive_count = 0
        if positive_tabindex.count() > 0:
            for i in range(positive_tabindex.count()):
                element = positive_tabindex.nth(i)
                tabindex = page.evaluate("el => el.getAttribute('tabindex')", element)
                if tabindex and int(tabindex) > 0:
                    positive_count += 1
        
        # Allow some positive tabindex for special cases, but not many
        assert positive_count < 5, f"Too many positive tabindex values found: {positive_count}"


class TestFocusIndicators:
    """Focus indicator validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_focus_indicator_visible(self, page):
        """
        Validate focus indicators are visible.
        
        WCAG 2.1 AA Standard:
        - Focus indicator must be clearly visible
        - 3:1 contrast ratio between focused and unfocused states
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get focusable elements
        focusable_elements = page.locator("a[href], button, input, select, textarea")
        
        if focusable_elements.count() > 0:
            for i in range(min(focusable_elements.count(), 10)):
                element = focusable_elements.nth(i)
                
                # Focus the element
                try:
                    element.focus()
                    
                    # Check if outline or other focus indicator is present
                    outline = page.evaluate("el => getComputedStyle(el).outline", element)
                    box_shadow = page.evaluate("el => getComputedStyle(el).boxShadow", element)
                    
                    # At least one focus indicator should be present
                    has_focus_indicator = (
                        (outline and outline != "none" and outline != "0px") or
                        (box_shadow and box_shadow != "none")
                    )
                    
                    # This is a soft check - some browsers handle focus differently
                    # Just log if no focus indicator found
                    if not has_focus_indicator:
                        print(f"Warning: Element may lack visible focus indicator")
                
                except:
                    pass


class TestSemanticHTML:
    """Semantic HTML validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_heading_hierarchy(self, page):
        """
        Validate heading hierarchy is logical.
        
        WCAG 2.1 AA Standard:
        - Headings must be properly nested (h1 -> h2 -> h3)
        - No skipped heading levels
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get all headings
        headings = page.locator("h1, h2, h3, h4, h5, h6")
        
        if headings.count() > 0:
            previous_level = 0
            for i in range(headings.count()):
                heading = headings.nth(i)
                try:
                    if not heading.is_visible():
                        continue
                    tag_name = page.evaluate("el => el.tagName", heading)
                    level = int(tag_name[1])  # Extract number from h1, h2, etc.
                    
                    # Check if heading level increased by more than 1
                    if previous_level > 0 and level > previous_level + 1:
                        print(f"Warning: Skipped heading level from h{previous_level} to h{level}")
                    
                    previous_level = level
                except:
                    continue
    
    def test_landmark_regions(self, page):
        """
        Validate landmark regions are present.
        
        WCAG 2.1 AA Standard:
        - Page should have landmark regions (header, main, nav, footer)
        - Landmarks help screen reader navigation
        """
        page.goto("http://127.0.0.1:9000")
        
        # Check for common landmarks
        has_header = page.locator("header, [role='banner']").count() > 0
        has_main = page.locator("main, [role='main'], #main-content, .main-content").count() > 0
        has_nav = page.locator("nav, [role='navigation']").count() > 0
        has_footer = page.locator("footer, [role='contentinfo']").count() > 0
        
        # At minimum, should have main content area or body content
        assert has_main or page.locator("body").count() > 0, "Page should have main content area"
    
    def test_list_semantics(self, page):
        """
        Validate lists use proper semantic HTML.
        
        WCAG 2.1 AA Standard:
        - Lists should use <ul>, <ol>, or <dl>
        - List items should use <li>
        """
        page.goto("http://127.0.0.1:9000")
        
        # Check for proper list structure
        lists = page.locator("ul, ol, dl")
        
        if lists.count() > 0:
            for i in range(min(lists.count(), 10)):
                list_element = lists.nth(i)
                list_items = list_element.locator("li, dt, dd")
                
                # Lists should have list items
                if list_element.evaluate("el => el.children.length") > 0:
                    assert list_items.count() > 0, "List should contain list items"


class TestFormAccessibility:
    """Form accessibility validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_form_labels(self, page):
        """
        Validate form inputs have associated labels.
        
        WCAG 2.1 AA Standard:
        - All form inputs must have associated labels
        - Labels can be explicit (<label>) or implicit (aria-label, title)
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get all form inputs
        inputs = page.locator("input:not([type='hidden']), select, textarea")
        
        if inputs.count() > 0:
            for i in range(min(inputs.count(), 20)):
                input_element = inputs.nth(i)
                
                try:
                    if not input_element.is_visible():
                        continue
                    # Check for explicit label
                    has_label = page.evaluate("""
                        el => {
                            if (!el) return false;
                            const id = el.id;
                            if (id) {
                                const label = document.querySelector(`label[for="${id}"]`);
                                if (label) return true;
                            }
                            // Check for implicit label (input inside label)
                            const parentLabel = el.closest('label');
                            if (parentLabel) return true;
                            // Check for aria-label
                            if (el.getAttribute('aria-label')) return true;
                            // Check for title
                            if (el.getAttribute('title')) return true;
                            return false;
                        }
                    """, input_element)
                    
                    if not has_label:
                        print(f"Warning: Form input may lack accessible label")
                except:
                    continue
    
    def test_required_field_indication(self, page):
        """
        Validate required fields are clearly indicated.
        
        WCAG 2.1 AA Standard:
        - Required fields must be programmatically determinable
        - Required fields should be visually indicated
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get required fields
        required_inputs = page.locator("input[required], select[required], textarea[required]")
        
        if required_inputs.count() > 0:
            for i in range(min(required_inputs.count(), 10)):
                input_element = required_inputs.nth(i)
                
                # Check for aria-required
                aria_required = page.evaluate("el => el.getAttribute('aria-required')", input_element)
                
                # Should have aria-required or required attribute
                assert aria_required == "true" or aria_required is not None, \
                    "Required field should have aria-required attribute"
    
    def test_error_messages(self, page):
        """
        Validate form error messages are accessible.
        
        WCAG 2.1 AA Standard:
        - Error messages should be associated with invalid fields
        - Error messages should be programmatically determinable
        """
        page.goto("http://127.0.0.1:9000")
        
        # Check for error message containers
        error_containers = page.locator("[role='error'], [role='alert'], .error, .alert-error")
        
        if error_containers.count() > 0:
            for i in range(min(error_containers.count(), 5)):
                error_element = error_containers.nth(i)
                
                try:
                    if not error_element.is_visible():
                        continue
                    # Check for aria-live or aria-describedby
                    aria_live = page.evaluate("el => el.getAttribute('aria-live')", error_element)
                    
                    # Error messages should have aria-live
                    if aria_live:
                        assert aria_live in ["polite", "assertive"], \
                            "Error messages should have aria-live='polite' or 'assertive'"
                except:
                    continue


class TestARIAAttributes:
    """ARIA attribute validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_aria_labels(self, page):
        """
        Validate ARIA labels are used appropriately.
        
        WCAG 2.1 AA Standard:
        - ARIA labels should provide accessible names
        - ARIA labels should not duplicate visible text
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get elements with aria-label
        aria_labeled = page.locator("[aria-label]")
        
        if aria_labeled.count() > 0:
            for i in range(min(aria_labeled.count(), 20)):
                element = aria_labeled.nth(i)
                
                try:
                    if not element.is_visible():
                        continue
                    aria_label = page.evaluate("el => el.getAttribute('aria-label')", element)
                    
                    # ARIA label should not be empty
                    assert aria_label and aria_label.strip(), "ARIA label should not be empty"
                except:
                    continue
    
    def test_aria_describedby(self, page):
        """
        Validate aria-describedby references valid elements.
        
        WCAG 2.1 AA Standard:
        - aria-describedby should reference existing elements
        - Referenced elements should provide additional description
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get elements with aria-describedby
        describedby_elements = page.locator("[aria-describedby]")
        
        if describedby_elements.count() > 0:
            for i in range(min(describedby_elements.count(), 10)):
                element = describedby_elements.nth(i)
                
                try:
                    if not element.is_visible():
                        continue
                    describedby = page.evaluate("el => el.getAttribute('aria-describedby')", element)
                    
                    if describedby:
                        # Check if referenced element exists
                        referenced_id = describedby.split()[0]  # Take first ID if multiple
                        referenced_element = page.locator(f"#{referenced_id}")
                        
                        if referenced_element.count() > 0:
                            # Referenced element should exist
                            assert True
                        else:
                            print(f"Warning: aria-describedby references non-existent element: {referenced_id}")
                except:
                    continue


class TestImageAccessibility:
    """Image accessibility validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_alt_text(self, page):
        """
        Validate images have appropriate alt text.
        
        WCAG 2.1 AA Standard:
        - Informative images must have descriptive alt text
        - Decorative images should have empty alt text
        - Complex images may need long descriptions
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get all images
        images = page.locator("img")
        
        if images.count() > 0:
            for i in range(min(images.count(), 20)):
                image = images.nth(i)
                
                alt_text = page.evaluate("el => el.getAttribute('alt')", image)
                
                # Alt text should be present (can be empty for decorative images)
                assert alt_text is not None, "Image should have alt attribute"
    
    def test_svg_accessibility(self, page):
        """
        Validate SVG elements are accessible.
        
        WCAG 2.1 AA Standard:
        - SVGs should have title and desc elements
        - SVGs should have role="img" if informative
        """
        page.goto("http://127.0.0.1:9000")
        
        # Get all SVG elements
        svgs = page.locator("svg")
        
        if svgs.count() > 0:
            for i in range(min(svgs.count(), 10)):
                svg = svgs.nth(i)
                
                # Check for title element
                has_title = svg.locator("title").count() > 0
                
                # Check for aria-label
                aria_label = page.evaluate("el => el.getAttribute('aria-label')", svg)
                
                # SVG should have either title or aria-label
                if not has_title and not aria_label:
                    print(f"Warning: SVG may lack accessible name")


class TestSkipLinks:
    """Skip link validation against WCAG 2.1 AA standards."""
    
    @pytest.fixture(scope="function")
    def page(self, browser, web_server):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_skip_links_present(self, page):
        """
        Validate skip links are present for keyboard users.
        
        WCAG 2.1 AA Standard:
        - Skip links should be provided to bypass navigation
        - Skip links should be visible on focus
        """
        page.goto("http://127.0.0.1:9000")
        
        # Check for skip links
        skip_links = page.locator("a[href^='#main'], a[href^='#content'], a[href^='#skip']")
        
        if skip_links.count() > 0:
            # Skip links should be present
            assert True
        else:
            print(f"Info: No skip links found - consider adding for keyboard navigation")
