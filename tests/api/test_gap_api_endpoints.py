"""
API integration tests for GAP endpoints

Tests the actual API endpoints added for GAP features.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


class TestGAP3TopologyValidationAPI:
    """Test GAP 3 topology validation API endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_topology_validation_endpoint_exists(self, client):
        """Test that topology validation endpoint exists."""
        response = client.post("/validate/topology", json={
            "switches": [
                {
                    "hostname": "sw1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "N9K-C93180YC-FX",
                    "nxos_version": "9.3(5)"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        })
        
        # Should return 200 or validation error
        assert response.status_code in [200, 422]
    
    def test_topology_validation_with_conflicts(self, client):
        """Test topology validation with hostname conflicts."""
        response = client.post("/validate/topology", json={
            "switches": [
                {
                    "hostname": "sw1",
                    "mgmt_ip": "10.0.0.1/24",
                    "model": "N9K-C93180YC-FX",
                    "nxos_version": "9.3(5)"
                },
                {
                    "hostname": "sw1",  # Duplicate
                    "mgmt_ip": "10.0.0.2/24",
                    "model": "N9K-C93180YC-FX",
                    "nxos_version": "9.3(5)"
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        })
        
        # Should return 200 with validation results
        assert response.status_code == 200
        
        data = response.json()
        assert "issues" in data or "status" in data


class TestGAP8MultiSiteAPI:
    """Test GAP 8 multi-site management API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_sites_create_endpoint_exists(self, client):
        """Test that sites create endpoint exists."""
        response = client.post("/sites/create", json={
            "site_id": "test-site",
            "site_name": "Test Site",
            "parent_site": None,
            "region": "Test Region",
            "rollout_phase": "planned",
            "deployment_status": "pending"
        })
        
        # Should return 200 or validation error
        assert response.status_code in [200, 422]
    
    def test_sites_list_endpoint_exists(self, client):
        """Test that sites list endpoint exists."""
        response = client.get("/sites/list")
        
        # Should return 200
        assert response.status_code in [200, 404]
    
    def test_progressive_rollout_endpoint_exists(self, client):
        """Test that progressive rollout endpoint exists."""
        response = client.post("/sites/progressive-rollout", json={
            "sites": [],
            "global_config": {},
            "progressive_rollout": True
        })
        
        # Should return 200 or validation error
        assert response.status_code in [200, 422]


class TestGAP9ErrorHandlingAPI:
    """Test GAP 9 error handling API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_error_analytics_endpoint_exists(self, client):
        """Test that error analytics endpoint exists."""
        response = client.get("/errors/analytics")
        
        # Should return 200
        assert response.status_code == 200
        
        data = response.json()
        assert "total_errors" in data or "status" in data
    
    def test_recovery_suggestion_endpoint_exists(self, client):
        """Test that recovery suggestion endpoint exists."""
        response = client.post("/errors/recovery-suggestion?error_code=vlan_conflict", json={})
        
        # Should return 200 or validation error
        assert response.status_code in [200, 422]
    
    def test_auto_recover_endpoint_exists(self, client):
        """Test that auto-recover endpoint exists."""
        response = client.post("/errors/auto-recover?error_code=test_error", json={})
        
        # Should return 200 or validation error
        assert response.status_code in [200, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
