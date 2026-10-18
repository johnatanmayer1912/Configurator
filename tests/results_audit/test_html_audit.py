"""
Results-Audit Tests: HTML Structure Validation
=============================================

These tests perform deep auditing of HTML page structures,
checking for duplicate IDs, unclosed tags, structural problems.

This is the RESULTS-AUDIT layer - independent of UI flow tests.
"""

import pytest
from tests.results_audit.config_audit_framework import (
    ConfigurationAuditor,
    ConfigurationArtifact,
    AuditSeverity
)


class TestHTMLAudit:
    """Audit tests for HTML page structures."""
    
    def test_duplicate_html_ids(self):
        """
        RESULTS-AUDIT: Detect duplicate HTML IDs.
        
        This test deliberately creates HTML with duplicate IDs
        and verifies the auditor catches them.
        """
        html_with_duplicate_ids = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <div id="main-content">Content 1</div>
    <div id="main-content">Content 2</div>
</body>
</html>
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="html",
            content=html_with_duplicate_ids,
            source="test_duplicate_ids",
            metadata={"page_name": "test_page"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify duplicate ID was detected
        duplicate_findings = [f for f in findings if f.category.value == "DUPLICATE"]
        assert len(duplicate_findings) > 0, "AUDIT FAILURE: Duplicate HTML ID not detected"
        assert any("main-content" in f.description for f in duplicate_findings), "AUDIT FAILURE: Specific duplicate ID not detected"
    
    def test_unclosed_html_tags(self):
        """
        RESULTS-AUDIT: Detect unclosed HTML tags.
        
        This test deliberately creates HTML with unclosed tags
        and verifies the auditor catches them.
        """
        html_with_unclosed_tags = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <div>Content
    <p>Another paragraph</div>
</body>
</html>
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="html",
            content=html_with_unclosed_tags,
            source="test_unclosed_tags",
            metadata={"page_name": "test_page"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Verify unclosed tag was detected
        structure_findings = [f for f in findings if f.category.value == "STRUCTURAL_ERROR"]
        assert len(structure_findings) > 0, "AUDIT FAILURE: Unclosed HTML tag not detected"
        assert any("tag" in f.description.lower() for f in structure_findings), "AUDIT FAILURE: Tag error not properly described"
    
    def test_valid_html_structure(self):
        """
        RESULTS-AUDIT: Validate clean HTML structure.
        
        This test verifies that properly structured HTML passes audit.
        """
        valid_html = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <div id="main-content">Content</div>
    <div id="sidebar">Sidebar</div>
</body>
</html>
"""
        
        artifact = ConfigurationArtifact(
            artifact_type="html",
            content=valid_html,
            source="test_valid_structure",
            metadata={"page_name": "test_page"}
        )
        
        auditor = ConfigurationAuditor()
        auditor.add_artifact(artifact)
        findings = auditor.audit_all()
        
        # Should have no critical or high findings
        critical_findings = [f for f in findings if f.severity == AuditSeverity.CRITICAL]
        high_findings = [f for f in findings if f.severity == AuditSeverity.HIGH]
        
        assert len(critical_findings) == 0, f"AUDIT FAILURE: {len(critical_findings)} CRITICAL findings in valid HTML"
        assert len(high_findings) == 0, f"AUDIT FAILURE: {len(high_findings)} HIGH findings in valid HTML"
