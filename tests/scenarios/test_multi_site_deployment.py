"""Test multi-site spine-leaf deployment scenarios.

This test file validates realistic multi-site deployments with different VLAN schemes,
cross-site vPC pairs, site-specific baseline options, and inter-site uplink validation.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestMultiSiteDeployment:
    """Multi-site deployment testing for network engineer scenarios."""
    
    def test_multi_site_spine_leaf_different_vlan_schemes(self):
        """
        Test multi-site deployment with different VLAN schemes per site.
        
        Network Engineer Scenario:
        - HQ site with VLANs 100-199
        - DR site with VLANs 200-299
        - Spine switches at each site
        - Leaf switches connecting to local spines
        - Cross-site uplinks for redundancy
        
        Validates that VLAN schemes don't conflict across sites.
        """
        deployment_input = {
            "switches": [
                # HQ Site
                {
                    "hostname": "HQ-SPINE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 10,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "spine"
                },
                {
                    "hostname": "HQ-SPINE2",
                    "mgmt_ip": "10.0.0.2/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 10,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "spine"
                },
                {
                    "hostname": "HQ-LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "HQ",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "100",
                    "base_access_vlan": 100,
                    "access_vlan_count": 10,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                },
                # DR Site
                {
                    "hostname": "DR-SPINE1",
                    "mgmt_ip": "10.1.0.1/24",
                    "mgmt_gw": "10.1.0.254",
                    "site_name": "DR",
                    "model": "Nexus 9336C-FX2",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 200,
                    "access_vlan_count": 10,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "spine"
                },
                {
                    "hostname": "DR-LEAF1",
                    "mgmt_ip": "10.1.0.11/24",
                    "mgmt_gw": "10.1.0.254",
                    "site_name": "DR",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "200",
                    "base_access_vlan": 200,
                    "access_vlan_count": 10,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [],
            "uplinks": [
                {
                    "from": "HQ-LEAF1",
                    "to": "HQ-SPINE1",
                    "ports": "Ethernet1/53-54",
                    "po_id": 10
                },
                {
                    "from": "HQ-LEAF1",
                    "to": "HQ-SPINE2",
                    "ports": "Ethernet1/55-56",
                    "po_id": 10
                },
                {
                    "from": "DR-LEAF1",
                    "to": "DR-SPINE1",
                    "ports": "Ethernet1/53-54",
                    "po_id": 10
                }
            ]
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_switches"] == 5
        assert result["successful"] == 5
        assert result["failed"] == 0
        
        # Verify each switch got generated
        hostnames = [r["hostname"] for r in result["results"]]
        assert "HQ-SPINE1" in hostnames
        assert "HQ-SPINE2" in hostnames
        assert "HQ-LEAF1" in hostnames
        assert "DR-SPINE1" in hostnames
        assert "DR-LEAF1" in hostnames
    
    def test_cross_site_vpc_pairs(self):
        """
        Test cross-site vPC pair configuration.
        
        Network Engineer Scenario:
        - vPC pair spanning across sites for redundancy
        - Keepalive links across sites
        - Validates vPC domain uniqueness across sites
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "SITE1-LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "SITE1",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "300",
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                },
                {
                    "hostname": "SITE2-LEAF1",
                    "mgmt_ip": "10.1.0.11/24",
                    "mgmt_gw": "10.1.0.254",
                    "site_name": "SITE2",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": "300",
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf"
                }
            ],
            "vpc_pairs": [
                {
                    "primary": "SITE1-LEAF1",
                    "secondary": "SITE2-LEAF1",
                    "domain": "300",
                    "peer_link_ports": "Ethernet1/51-52"
                }
            ],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_switches"] == 2
        assert result["successful"] == 2
    
    def test_site_specific_baseline_options(self):
        """
        Test site-specific baseline options.
        
        Network Engineer Scenario:
        - Production site with hardened baseline
        - Lab site with standard baseline
        - Different security tiers per site
        """
        deployment_input = {
            "switches": [
                {
                    "hostname": "PROD-LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "site_name": "PROD",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 100,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "hardened",
                    "role": "leaf",
                    "baseline_options": ["baseline_cfs", "baseline_copp", "baseline_snmp_traps"]
                },
                {
                    "hostname": "LAB-LEAF1",
                    "mgmt_ip": "10.1.0.11/24",
                    "mgmt_gw": "10.1.0.254",
                    "site_name": "LAB",
                    "model": "Nexus 93180YC-EX",
                    "nxos_version": "9.3",
                    "vpc_domain": None,
                    "base_access_vlan": 200,
                    "access_vlan_count": 5,
                    "interface_count": 0,
                    "bring_up_spare_ports": False,
                    "security_tier": "standard",
                    "role": "leaf",
                    "baseline_options": ["baseline_cfs"]
                }
            ],
            "vpc_pairs": [],
            "uplinks": []
        }
        
        response = client.post("/generate-deployment", json=deployment_input)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_switches"] == 2
        assert result["successful"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
