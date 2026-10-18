"""Config Matrix Unit Tests

Tests the scenario × model configuration matrix including:
- Matrix structure validation
- Scenario to model mapping
- Baseline defaults validation
- Uplink/downlink preset validation
"""

import pytest
import yaml
from pathlib import Path


class TestConfigMatrix:
    """Test config matrix data structure and validation."""
    
    @pytest.fixture
    def config_matrix(self):
        """Load config matrix from YAML file."""
        matrix_path = Path(__file__).resolve().parents[1] / "data" / "config_matrix.yaml"
        with open(matrix_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data
    
    def test_matrix_structure(self, config_matrix):
        """Test that matrix has correct structure."""
        assert "matrix" in config_matrix, "Matrix must have 'matrix' key"
        assert isinstance(config_matrix["matrix"], list), "Matrix must be a list"
        assert len(config_matrix["matrix"]) > 0, "Matrix must have at least one entry"
    
    def test_matrix_entry_required_fields(self, config_matrix):
        """Test that each matrix entry has required fields."""
        required_fields = [
            "scenario_id",
            "speed_tier",
            "device_class",
            "supported_models",
            "default_model",
            "default_nxos",
            "vpc_ports_from",
            "baseline_defaults",
            "downlink_presets",
            "uplink_presets"
        ]
        
        for entry in config_matrix["matrix"]:
            for field in required_fields:
                assert field in entry, f"Matrix entry missing required field: {field}"
    
    def test_scenario_id_uniqueness(self, config_matrix):
        """Test that scenario IDs are unique."""
        scenario_ids = [entry["scenario_id"] for entry in config_matrix["matrix"]]
        assert len(scenario_ids) == len(set(scenario_ids)), "Scenario IDs must be unique"
    
    def test_supported_models_is_list(self, config_matrix):
        """Test that supported_models is a list."""
        for entry in config_matrix["matrix"]:
            assert isinstance(entry["supported_models"], list), "supported_models must be a list"
            assert len(entry["supported_models"]) > 0, "supported_models must have at least one model"
    
    def test_default_model_in_supported_models(self, config_matrix):
        """Test that default_model is in supported_models."""
        for entry in config_matrix["matrix"]:
            assert entry["default_model"] in entry["supported_models"], \
                f"default_model {entry['default_model']} must be in supported_models"
    
    def test_vpc_ports_from_values(self, config_matrix):
        """Test that vpc_ports_from has valid values."""
        valid_values = ["hardware_profile", "none"]
        
        for entry in config_matrix["matrix"]:
            assert entry["vpc_ports_from"] in valid_values, \
                f"vpc_ports_from must be one of {valid_values}"
    
    def test_baseline_defaults_is_list(self, config_matrix):
        """Test that baseline_defaults is a list."""
        for entry in config_matrix["matrix"]:
            assert isinstance(entry["baseline_defaults"], list), "baseline_defaults must be a list"
    
    def test_downlink_presets_is_list(self, config_matrix):
        """Test that downlink_presets is a list."""
        for entry in config_matrix["matrix"]:
            assert isinstance(entry["downlink_presets"], list), "downlink_presets must be a list"
    
    def test_uplink_presets_is_list(self, config_matrix):
        """Test that uplink_presets is a list."""
        for entry in config_matrix["matrix"]:
            assert isinstance(entry["uplink_presets"], list), "uplink_presets must be a list"
    
    def test_known_scenarios_exist(self, config_matrix):
        """Test that known scenarios exist in matrix."""
        expected_scenarios = [
            "vpc_core_pair",
            "vpc_leaf_pair",
            "standalone_leaf",
            "standalone_access",
            "vpc_access_pair",
            "spine_core",
            "vxlan_evpn_leaf",
            "mgmt_oob"
        ]
        
        scenario_ids = [entry["scenario_id"] for entry in config_matrix["matrix"]]
        
        for scenario in expected_scenarios:
            assert scenario in scenario_ids, f"Expected scenario {scenario} not found in matrix"
    
    def test_vpc_core_pair_configuration(self, config_matrix):
        """Test vpc_core_pair specific configuration."""
        vpc_core = next((e for e in config_matrix["matrix"] if e["scenario_id"] == "vpc_core_pair"), None)
        assert vpc_core is not None, "vpc_core_pair must exist"
        
        assert vpc_core["speed_tier"] == "40G"
        assert vpc_core["device_class"] == "core"
        assert "Nexus 9336C-FX2" in vpc_core["supported_models"]
        assert vpc_core["default_model"] == "Nexus 9336C-FX2"
        assert vpc_core["vpc_ports_from"] == "hardware_profile"
    
    def test_vpc_leaf_pair_configuration(self, config_matrix):
        """Test vpc_leaf_pair specific configuration."""
        vpc_leaf = next((e for e in config_matrix["matrix"] if e["scenario_id"] == "vpc_leaf_pair"), None)
        assert vpc_leaf is not None, "vpc_leaf_pair must exist"
        
        assert vpc_leaf["speed_tier"] == "10G"
        assert vpc_leaf["device_class"] == "leaf_10g"
        assert "Nexus 93180YC-EX" in vpc_leaf["supported_models"]
        assert vpc_leaf["default_model"] == "Nexus 93180YC-EX"
    
    def test_spine_core_configuration(self, config_matrix):
        """Test spine_core specific configuration."""
        spine = next((e for e in config_matrix["matrix"] if e["scenario_id"] == "spine_core"), None)
        assert spine is not None, "spine_core must exist"
        
        assert spine["speed_tier"] == "40G"
        assert spine["device_class"] == "core"
        assert spine["vpc_ports_from"] == "none"  # Spines don't use vPC
    
    def test_mgmt_oob_configuration(self, config_matrix):
        """Test mgmt_oob specific configuration."""
        mgmt = next((e for e in config_matrix["matrix"] if e["scenario_id"] == "mgmt_oob"), None)
        assert mgmt is not None, "mgmt_oob must exist"
        
        assert mgmt["speed_tier"] == "Multi"
        assert mgmt["device_class"] == "hybrid"
        assert mgmt["default_model"] == "Generic"
        assert mgmt["vpc_ports_from"] == "none"
    
    def test_baseline_defaults_content(self, config_matrix):
        """Test that baseline defaults contain expected values."""
        expected_baseline_options = [
            "baseline_cfs",
            "baseline_copp",
            "baseline_no_pwd_check",
            "baseline_snmp_traps",
            "baseline_spanning_tree",
            "baseline_cli_aliases"
        ]
        
        for entry in config_matrix["matrix"]:
            for option in entry["baseline_defaults"]:
                assert option.startswith("baseline_"), f"Baseline option should start with 'baseline_': {option}"
    
    def test_speed_tier_values(self, config_matrix):
        """Test that speed_tier has valid values."""
        valid_speeds = ["1G", "10G", "40G", "Multi"]
        
        for entry in config_matrix["matrix"]:
            assert entry["speed_tier"] in valid_speeds, \
                f"speed_tier must be one of {valid_speeds}"
    
    def test_device_class_values(self, config_matrix):
        """Test that device_class has valid values."""
        valid_classes = ["core", "leaf_10g", "leaf_1g", "hybrid"]
        
        for entry in config_matrix["matrix"]:
            assert entry["device_class"] in valid_classes, \
                f"device_class must be one of {valid_classes}"
    
    def test_nxos_version_format(self, config_matrix):
        """Test that NX-OS version follows expected format."""
        for entry in config_matrix["matrix"]:
            version = entry["default_nxos"]
            # Should be in format like "9.3" or "10.2"
            assert isinstance(version, str), "NX-OS version must be a string"
            parts = version.split(".")
            assert len(parts) >= 2, "NX-OS version should have major.minor format"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
