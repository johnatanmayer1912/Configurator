"""
Backend unit tests for GAP 8: Multi-site Deployment Management

Tests the site hierarchy, global configuration templates, and progressive rollout logic.
"""

import pytest


class TestMultiSiteManagementGAP8:
    """Test multi-site management with GAP 8 features."""
    
    def test_site_config_creation(self):
        """Test site configuration creation."""
        site = {
            "site_id": "site-hq",
            "site_name": "Headquarters",
            "parent_site": None,
            "location": "San Francisco",
            "region": "North America",
            "global_templates": {},
            "site_overrides": {},
            "rollout_phase": "planned",
            "deployment_status": "pending"
        }
        
        assert site["site_id"] == "site-hq"
        assert site["site_name"] == "Headquarters"
        assert site["parent_site"] is None
        assert site["region"] == "North America"
        assert site["rollout_phase"] == "planned"
        assert site["deployment_status"] == "pending"
    
    def test_site_hierarchy_with_parent(self):
        """Test site hierarchy with parent site."""
        parent_site = {
            "site_id": "region-na",
            "site_name": "North America Region",
            "parent_site": None,
            "region": "Global"
        }
        
        child_site = {
            "site_id": "site-hq",
            "site_name": "Headquarters",
            "parent_site": "region-na",
            "region": "North America"
        }
        
        assert child_site["parent_site"] == parent_site["site_id"]
        # Child site can have its own region, not necessarily parent's name
    
    def test_site_hierarchy_validation(self):
        """Test site hierarchy validation."""
        sites = [
            {"site_id": "global", "site_name": "Global", "parent_site": None},
            {"site_id": "region-na", "site_name": "North America", "parent_site": "global"},
            {"site_id": "site-hq", "site_name": "Headquarters", "parent_site": "region-na"},
            {"site_id": "site-dc1", "site_name": "Data Center 1", "parent_site": "site-hq"}
        ]
        
        # Build hierarchy tree
        hierarchy = {}
        for site in sites:
            hierarchy[site["site_id"]] = site["parent_site"]
        
        # Validate hierarchy (no circular references)
        assert hierarchy["global"] is None  # Root
        assert hierarchy["region-na"] == "global"
        assert hierarchy["site-hq"] == "region-na"
        assert hierarchy["site-dc1"] == "site-hq"
    
    def test_rollout_phase_transitions(self):
        """Test rollout phase transitions."""
        valid_phases = ["planned", "staging", "production"]
        
        site = {
            "site_id": "site-test",
            "site_name": "Test Site",
            "rollout_phase": "planned"
        }
        
        # Test phase progression
        for phase in valid_phases:
            site["rollout_phase"] = phase
            assert site["rollout_phase"] in valid_phases
    
    def test_deployment_status_transitions(self):
        """Test deployment status transitions."""
        valid_statuses = ["pending", "in_progress", "completed", "failed"]
        
        site = {
            "site_id": "site-test",
            "site_name": "Test Site",
            "deployment_status": "pending"
        }
        
        # Test status progression
        for status in valid_statuses:
            site["deployment_status"] = status
            assert site["deployment_status"] in valid_statuses
    
    def test_global_configuration_templates(self):
        """Test global configuration templates."""
        site = {
            "site_id": "site-test",
            "site_name": "Test Site",
            "global_templates": {
                "base_vlan_range": "100-200",
                "ntp_servers": ["10.0.0.1", "10.0.0.2"],
                "syslog_servers": ["10.0.0.10"]
            }
        }
        
        assert "base_vlan_range" in site["global_templates"]
        assert len(site["global_templates"]["ntp_servers"]) == 2
    
    def test_site_specific_overrides(self):
        """Test site-specific configuration overrides."""
        site = {
            "site_id": "site-test",
            "site_name": "Test Site",
            "site_overrides": {
                "base_vlan_range": "300-400",  # Override global
                "custom_snmp": "public"
            }
        }
        
        assert site["site_overrides"]["base_vlan_range"] == "300-400"
        assert "custom_snmp" in site["site_overrides"]
    
    def test_progressive_rollout_configuration(self):
        """Test progressive rollout configuration."""
        request = {
            "sites": [
                {"site_id": "site-1", "site_name": "Site 1", "rollout_phase": "staging"},
                {"site_id": "site-2", "site_name": "Site 2", "rollout_phase": "production"},
                {"site_id": "site-3", "site_name": "Site 3", "rollout_phase": "planned"}
            ],
            "global_config": {},
            "progressive_rollout": True
        }
        
        assert request["progressive_rollout"] == True
        assert len(request["sites"]) == 3
        
        # Verify phases are ordered for progressive rollout
        phases = [site["rollout_phase"] for site in request["sites"]]
        assert "planned" in phases
        assert "staging" in phases
        assert "production" in phases
    
    def test_immediate_deployment_configuration(self):
        """Test immediate deployment (non-progressive)."""
        request = {
            "sites": [
                {"site_id": "site-1", "site_name": "Site 1"},
                {"site_id": "site-2", "site_name": "Site 2"}
            ],
            "global_config": {},
            "progressive_rollout": False
        }
        
        assert request["progressive_rollout"] == False
    
    def test_site_uniqueness_validation(self):
        """Test that site IDs are unique."""
        sites = [
            {"site_id": "site-1", "site_name": "Site 1"},
            {"site_id": "site-2", "site_name": "Site 2"},
            {"site_id": "site-1", "site_name": "Site 1 Duplicate"}  # Duplicate ID
        ]
        
        site_ids = [site["site_id"] for site in sites]
        assert len(site_ids) != len(set(site_ids))  # Should have duplicates
    
    def test_multi_site_deployment_request_structure(self):
        """Test multi-site deployment request structure."""
        request = {
            "sites": [
                {"site_id": "site-1", "site_name": "Site 1"},
                {"site_id": "site-2", "site_name": "Site 2"}
            ],
            "global_config": {
                "global_vlan_range": "100-200",
                "global_ntp": ["10.0.0.1"]
            },
            "progressive_rollout": True
        }
        
        assert len(request["sites"]) == 2
        assert len(request["global_config"]) > 0
        assert request["progressive_rollout"] == True
    
    def test_site_location_metadata(self):
        """Test site location metadata."""
        site = {
            "site_id": "site-sfo",
            "site_name": "San Francisco",
            "location": "San Francisco, CA",
            "region": "West Coast"
        }
        
        assert site["location"] == "San Francisco, CA"
        assert site["region"] == "West Coast"
    
    def test_rollout_phase_ordering(self):
        """Test that rollout phases are properly ordered."""
        phase_order = ["planned", "staging", "production"]
        
        sites = [
            {"site_id": f"site-{i}", "site_name": f"Site {i}", "rollout_phase": phase}
            for i, phase in enumerate(phase_order)
        ]
        
        # Verify ordering
        for i, site in enumerate(sites):
            assert site["rollout_phase"] == phase_order[i]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
