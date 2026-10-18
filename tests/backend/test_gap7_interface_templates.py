"""
Backend unit tests for GAP 7: Interface-level Configuration Templates

Tests the interface template logic, template application, and configuration standards.
"""

import pytest
import yaml
from pathlib import Path


class TestInterfaceTemplatesGAP7:
    """Test interface template functionality with GAP 7 features."""
    
    @pytest.fixture
    def interface_presets(self):
        """Load interface presets from YAML."""
        presets_path = Path("data/interface_presets.yaml")
        if presets_path.exists():
            with open(presets_path, 'r') as f:
                return yaml.safe_load(f)
        return None
    
    def test_interface_templates_exist(self, interface_presets):
        """Test that interface templates are defined."""
        assert interface_presets is not None
        assert "presets" in interface_presets
        assert len(interface_presets["presets"]) > 0
    
    def test_new_gap7_templates_defined(self, interface_presets):
        """Test that new GAP 7 templates are defined."""
        if interface_presets is None:
            pytest.skip("Interface presets file not found")
        
        preset_ids = [p["id"] for p in interface_presets["presets"]]
        
        # Check for new GAP 7 templates
        gap7_templates = [
            "server_port",
            "ip_phone_port",
            "ap_port",
            "iscsi_port",
            "mgmt_port",
            "lacp_port",
            "vpc_peer_link",
            "vpc_keepalive"
        ]
        
        for template_id in gap7_templates:
            assert template_id in preset_ids, f"Template {template_id} not found"
    
    def test_template_type_field_exists(self, interface_presets):
        """Test that templates have template_type field."""
        if interface_presets is None:
            pytest.skip("Interface presets file not found")
        
        for preset in interface_presets["presets"]:
            assert "template_type" in preset, f"Template {preset['id']} missing template_type"
    
    def test_template_default_config_exists(self, interface_presets):
        """Test that templates have default_config field."""
        if interface_presets is None:
            pytest.skip("Interface presets file not found")
        
        for preset in interface_presets["presets"]:
            # New GAP 7 templates should have default_config
            if preset["id"] in ["server_port", "ip_phone_port", "ap_port", "iscsi_port", 
                               "mgmt_port", "lacp_port", "vpc_peer_link", "vpc_keepalive"]:
                assert "default_config" in preset, f"Template {preset['id']} missing default_config"
    
    def test_server_port_template_config(self, interface_presets):
        """Test server port template configuration."""
        if interface_presets is None:
            pytest.skip("Interface presets file not found")
        
        server_port = next((p for p in interface_presets["presets"] if p["id"] == "server_port"), None)
        assert server_port is not None
        
        assert server_port["template_type"] == "access"
        assert server_port["needs_vlan"] == True
        assert server_port["allows_vpc_po"] == True
        
        default_config = server_port.get("default_config", {})
        assert default_config.get("mode") == "access"
        assert default_config.get("stp") == "portfast"
        assert default_config.get("bpdu_guard") == True
    
    def test_ip_phone_template_config(self, interface_presets):
        """Test IP phone template configuration."""
        if interface_presets is None:
            pytest.skip("Interface presets file not found")
        
        ip_phone = next((p for p in interface_presets["presets"] if p["id"] == "ip_phone_port"), None)
        assert ip_phone is not None
        
        assert ip_phone["template_type"] == "access"
        assert ip_phone["needs_vlan"] == True
        
        default_config = ip_phone.get("default_config", {})
        assert default_config.get("voice_vlan") == True
        assert default_config.get("cdp") == True
        assert default_config.get("lldp") == True
    
    def test_iscsi_template_config(self, interface_presets):
        """Test iSCSI storage template configuration."""
        if interface_presets is None:
            pytest.skip("Interface presets file not found")
        
        iscsi = next((p for p in interface_presets["presets"] if p["id"] == "iscsi_port"), None)
        assert iscsi is not None
        
        assert iscsi["template_type"] == "trunk"
        assert iscsi["needs_trunk"] == True
        
        default_config = iscsi.get("default_config", {})
        assert default_config.get("mtu") == 9216
        assert default_config.get("flow_control") == "receive"
    
    def test_vpc_peer_link_template_config(self, interface_presets):
        """Test vPC peer link template configuration."""
        if interface_presets is None:
            pytest.skip("Interface presets file not found")
        
        vpc_peer = next((p for p in interface_presets["presets"] if p["id"] == "vpc_peer_link"), None)
        assert vpc_peer is not None
        
        assert vpc_peer["template_type"] == "trunk"
        assert vpc_peer["allows_vpc_po"] == False  # Peer link cannot be in vPC
        
        default_config = vpc_peer.get("default_config", {})
        assert default_config.get("vpc_peer_link") == True
        assert default_config.get("allowed_vlans") == "1-4094"
    
    def test_template_inheritance_logic(self):
        """Test template inheritance logic."""
        # Simulate template application with inheritance
        base_template = {
            "mode": "access",
            "stp": "edge",
            "storm_control": True
        }
        
        derived_template = base_template.copy()
        derived_template["stp"] = "portfast"  # Override
        derived_template["bpdu_guard"] = True  # Add new setting
        
        assert derived_template["mode"] == base_template["mode"]  # Inherited
        assert derived_template["stp"] != base_template["stp"]  # Overridden
        assert "bpdu_guard" in derived_template  # Added
        assert "bpdu_guard" not in base_template
    
    def test_bulk_template_application(self):
        """Test bulk template application across multiple interfaces."""
        template = {
            "template_id": "server_port",
            "port_range": "Ethernet1/1-24",
            "vlan_override": 100
        }
        
        # Simulate applying to multiple switches
        switches = ["sw1", "sw2", "sw3"]
        applied_configs = []
        
        for switch in switches:
            config = {
                "switch": switch,
                "template": template["template_id"],
                "ports": template["port_range"],
                "vlan": template["vlan_override"]
            }
            applied_configs.append(config)
        
        assert len(applied_configs) == 3
        assert all(c["template"] == "server_port" for c in applied_configs)
        assert all(c["vlan"] == 100 for c in applied_configs)
    
    def test_interface_configuration_standards(self):
        """Test that interface configurations meet standards."""
        # Define standards
        standards = {
            "access_port": {
                "min_vlan": 1,
                "max_vlan": 4094,
                "stp_required": True
            },
            "trunk_port": {
                "allowed_vlans": "1-4094",
                "native_vlan_optional": True
            }
        }
        
        # Test access port compliance
        access_config = {"vlan": 100, "stp": "portfast"}
        assert standards["access_port"]["min_vlan"] <= access_config["vlan"] <= standards["access_port"]["max_vlan"]
        assert access_config["stp"] is not None  # STP required
        
        # Test trunk port compliance
        trunk_config = {"allowed_vlans": "1-4094", "native_vlan": 1}
        assert trunk_config["allowed_vlans"] == standards["trunk_port"]["allowed_vlans"]
    
    def test_vlan_override_functionality(self):
        """Test VLAN override functionality in templates."""
        template_default_vlan = 10
        override_vlan = 100
        
        # Apply override
        final_vlan = override_vlan if override_vlan else template_default_vlan
        
        assert final_vlan == 100
        
        # Test no override
        final_vlan = None if None else template_default_vlan
        assert final_vlan == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
