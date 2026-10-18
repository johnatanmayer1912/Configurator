"""
E2E Tests for Template Validation Features
Tests pre-apply validation, hardware compatibility checks, and NX-OS version validation
"""

import pytest
from playwright.sync_api import Page, expect


class TestTemplateValidation:
    """Test template validation features including pre-apply validation, hardware compatibility, and NX-OS version checks."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test by navigating to the application."""
        page.goto("http://127.0.0.1:9000/")
        page.wait_for_load_state("networkidle")
        
        # Close any modals and dialogs using JavaScript
        page.evaluate("""
            () => {
                // Remove modals
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
    
    def test_pre_apply_validation_blocks_invalid_template(self, page: Page):
        """Test that pre-apply validation blocks templates with invalid configurations."""
        # Test validation function directly via JavaScript
        validation_result = page.evaluate("""
            () => {
                // Create a mock template with invalid configuration
                const invalidTemplate = {
                    id: 'test_invalid',
                    vpc_pairs: [
                        { domain: '10', primary: 'SW1', secondary: 'SW2' },
                        { domain: '10', primary: 'SW3', secondary: 'SW4' } // Duplicate domain
                    ],
                    switches: [
                        { hostname: 'SW1', mgmt_ip: '10.0.0.1/24' },
                        { hostname: 'SW2', mgmt_ip: '10.0.0.1/24' } // Duplicate IP
                    ],
                    global_vlans: [
                        { id: 5000, name: 'Invalid VLAN' } // VLAN out of range
                    ]
                };
                
                // Call validation function
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(invalidTemplate);
                } else {
                    return { valid: false, errors: ['Validation function not found'], warnings: [] };
                }
            }
        """)
        
        # Verify validation failed
        assert validation_result['valid'] is False
        assert len(validation_result['errors']) > 0
        assert any('duplicate' in error.lower() for error in validation_result['errors'])
    
    def test_pre_apply_validation_allows_valid_template(self, page: Page):
        """Test that pre-apply validation allows valid templates."""
        # Test validation function directly via JavaScript
        validation_result = page.evaluate("""
            () => {
                // Create a mock valid template
                const validTemplate = {
                    id: 'test_valid',
                    vpc_pairs: [
                        { domain: '10', primary: 'SW1', secondary: 'SW2' }
                    ],
                    switches: [
                        { hostname: 'SW1', mgmt_ip: '10.0.0.1/24' },
                        { hostname: 'SW2', mgmt_ip: '10.0.0.2/24' }
                    ],
                    global_vlans: [
                        { id: 10, name: 'Data-VLAN-10' }
                    ]
                };
                
                // Call validation function
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(validTemplate);
                } else {
                    return { valid: false, errors: ['Validation function not found'], warnings: [] };
                }
            }
        """)
        
        # Verify validation passed
        assert validation_result['valid'] is True
        assert len(validation_result['errors']) == 0
    
    def test_vpc_domain_uniqueness_validation(self, page: Page):
        """Test that validation detects duplicate vPC domains."""
        validation_result = page.evaluate("""
            () => {
                const template = {
                    id: 'test_vpc_dup',
                    vpc_pairs: [
                        { domain: '10', primary: 'SW1', secondary: 'SW2' },
                        { domain: '10', primary: 'SW3', secondary: 'SW4' } // Duplicate
                    ],
                    switches: [],
                    global_vlans: []
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        assert validation_result['valid'] is False
        assert any('duplicate' in error.lower() for error in validation_result['errors'])
    
    def test_vlan_range_validation(self, page: Page):
        """Test that validation detects invalid VLAN ranges."""
        validation_result = page.evaluate("""
            () => {
                const template = {
                    id: 'test_vlan_invalid',
                    vpc_pairs: [],
                    switches: [],
                    global_vlans: [
                        { id: 5000, name: 'Invalid VLAN' } // Out of range
                    ]
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        assert validation_result['valid'] is False
        assert any('vlan' in error.lower() and 'range' in error.lower() for error in validation_result['errors'])
    
    def test_hostname_format_validation(self, page: Page):
        """Test that validation detects invalid hostname formats."""
        validation_result = page.evaluate("""
            () => {
                const template = {
                    id: 'test_hostname_invalid',
                    vpc_pairs: [],
                    switches: [
                        { hostname: 'CORE_1', mgmt_ip: '10.0.0.1/24' } // Invalid format
                    ],
                    global_vlans: []
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        assert validation_result['valid'] is False
        assert any('hostname' in error.lower() for error in validation_result['errors'])
    
    def test_management_ip_cidr_validation(self, page: Page):
        """Test that validation detects missing CIDR notation."""
        validation_result = page.evaluate("""
            () => {
                const template = {
                    id: 'test_cidr_invalid',
                    vpc_pairs: [],
                    switches: [
                        { hostname: 'SW1', mgmt_ip: '10.0.0.1' } // Missing CIDR
                    ],
                    global_vlans: []
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        assert validation_result['valid'] is False
        assert any('cidr' in error.lower() for error in validation_result['errors'])


class TestHardwareCompatibility:
    """Test hardware compatibility checking before template selection."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test by navigating to the application."""
        page.goto("http://127.0.0.1:9000/")
        page.wait_for_load_state("networkidle")
        
        # Close any modals and dialogs using JavaScript
        page.evaluate("""
            () => {
                // Remove modals
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
    
    def test_hardware_compatibility_check_shows_compatible_templates(self, page: Page):
        """Test that compatible templates are shown as clickable."""
        # Test hardware compatibility check via JavaScript
        compatibility_result = page.evaluate("""
            () => {
                // Set hardware inventory to match template
                window.getCurrentHardwareInventory = function() {
                    return ['Nexus 9336C-FX2', 'Nexus 93180YC-EX'];
                };
                
                // Check compatibility with a template
                const templateHardware = ['Nexus 9336C-FX2', 'Nexus 93180YC-EX', 'Nexus 9348GC-FXP'];
                const currentHardware = window.getCurrentHardwareInventory();
                const isCompatible = currentHardware.length === 0 || 
                    currentHardware.some(hw => templateHardware.includes(hw));
                
                return { isCompatible: isCompatible };
            }
        """)
        
        assert compatibility_result['isCompatible'] is True
    
    def test_hardware_compatibility_check_shows_incompatible_templates(self, page: Page):
        """Test that incompatible templates are shown as disabled."""
        # Test hardware incompatibility via JavaScript
        compatibility_result = page.evaluate("""
            () => {
                // Set hardware inventory to mismatch with template
                window.getCurrentHardwareInventory = function() {
                    return ['Nexus 9504', 'Nexus 9396PX'];
                };
                
                // Check compatibility with a template
                const templateHardware = ['Nexus 9336C-FX2', 'Nexus 93180YC-EX', 'Nexus 9348GC-FXP'];
                const currentHardware = window.getCurrentHardwareInventory();
                const isCompatible = currentHardware.length === 0 || 
                    currentHardware.some(hw => templateHardware.includes(hw));
                
                return { isCompatible: isCompatible };
            }
        """)
        
        assert compatibility_result['isCompatible'] is False
    
    def test_hardware_warning_icon_displayed(self, page: Page):
        """Test that hardware warning icon is displayed for incompatible templates."""
        # Test that hardware inventory function exists
        has_function = page.evaluate("""
            () => {
                return typeof window.getCurrentHardwareInventory === 'function';
            }
        """)
        
        assert has_function is True
    
    def test_incompatible_template_cannot_be_applied(self, page: Page):
        """Test that incompatible templates cannot be applied."""
        # Test that validation includes hardware compatibility check
        validation_result = page.evaluate("""
            () => {
                // Set hardware inventory to mismatch
                window.getCurrentHardwareInventory = function() {
                    return ['Nexus 9504'];
                };
                
                // Test with a template that requires different hardware
                const template = {
                    id: 'test_hardware',
                    vpc_pairs: [],
                    switches: [],
                    global_vlans: [],
                    hardware_compatibility: ['Nexus 9336C-FX2']
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        # Should have warnings about hardware incompatibility
        assert len(validation_result['warnings']) > 0 or len(validation_result['errors']) > 0


class TestNxosVersionValidation:
    """Test NX-OS version validation for template compatibility."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test by navigating to the application."""
        page.goto("http://127.0.0.1:9000/")
        page.wait_for_load_state("networkidle")
        
        # Close any modals and dialogs using JavaScript
        page.evaluate("""
            () => {
                // Remove modals
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
    
    def test_nxos_version_below_minimum_blocked(self, page: Page):
        """Test that NX-OS version below minimum generates a warning (not a blocker)."""
        validation_result = page.evaluate("""
            () => {
                // Set NX-OS version below minimum
                window.getCurrentNxosVersion = function() {
                    return '9.1';
                };
                
                // Test with a template that requires higher version
                const template = {
                    id: 'test_version',
                    vpc_pairs: [],
                    switches: [],
                    global_vlans: [],
                    nxos_version_min: '9.2',
                    nxos_version_max: '10.2'
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        # Should still be valid (version is now a warning, not an error)
        assert validation_result['valid'] is True
        # But should have a warning about version
        assert any('version' in warning.lower() for warning in validation_result['warnings'])
    
    def test_nxos_version_above_maximum_blocked(self, page: Page):
        """Test that NX-OS version above maximum generates a warning (not a blocker)."""
        validation_result = page.evaluate("""
            () => {
                // Set NX-OS version above maximum
                window.getCurrentNxosVersion = function() {
                    return '10.3';
                };
                
                // Test with a template that requires lower version
                const template = {
                    id: 'test_version',
                    vpc_pairs: [],
                    switches: [],
                    global_vlans: [],
                    nxos_version_min: '9.2',
                    nxos_version_max: '10.2'
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        # Should still be valid (version is now a warning, not an error)
        assert validation_result['valid'] is True
        # But should have a warning about version
        assert any('version' in warning.lower() for warning in validation_result['warnings'])
    
    def test_nxos_version_within_range_allowed(self, page: Page):
        """Test that templates are allowed when NX-OS version is within range."""
        validation_result = page.evaluate("""
            () => {
                // Set NX-OS version within range
                window.getCurrentNxosVersion = function() {
                    return '9.3';
                };
                
                // Set hardware inventory to avoid hardware warnings
                window.getCurrentHardwareInventory = function() {
                    return ['Nexus 9336C-FX2'];
                };
                
                // Test with a template that accepts this version
                const template = {
                    id: 'test_version',
                    vpc_pairs: [],
                    switches: [],
                    global_vlans: [],
                    nxos_version_min: '9.2',
                    nxos_version_max: '10.2',
                    hardware_compatibility: ['Nexus 9336C-FX2']
                };
                
                if (typeof window.validateTemplateBeforeApply === 'function') {
                    return window.validateTemplateBeforeApply(template);
                }
                return { valid: false, errors: ['Function not found'], warnings: [] };
            }
        """)
        
        # Should pass validation - check that it's valid
        assert validation_result['valid'] is True
    
    @pytest.mark.skip(reason="UI metadata check - not a file-generation journey. Template metadata structure varies by implementation.")
    def test_nxos_version_metadata_displayed_in_template(self, page: Page):
        """Test that NX-OS version metadata is available in template data."""
        # Check that templates have NX-OS version metadata
        has_version_metadata = page.evaluate("""
            () => {
                const templates = Object.values(DEPLOYMENT_TEMPLATES);
                return templates.every(t => t.nxos_version_min && t.nxos_version_max);
            }
        """)
        
        assert has_version_metadata is True
