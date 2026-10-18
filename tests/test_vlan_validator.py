"""VLAN Validator Unit Tests

Comprehensive test coverage for model-aware VLAN validation and propagation.
"""

import pytest
from core.vlan_validator import VLANValidator, VLANConstraints
from core.catalog_loader import CatalogLoader


class TestVLANConstraints:
    """Test VLANConstraints dataclass validation and methods"""
    
    def test_valid_constraints(self):
        """Test valid constraint initialization"""
        constraints = VLANConstraints(
            min_vlan=10,
            max_vlan=999,
            default_vlan_start=10,
            max_vlan_count=50,
            reserved_vlans=[1, 997, 998, 999]
        )
        assert constraints.min_vlan == 10
        assert constraints.max_vlan == 999
        assert constraints.default_vlan_start == 10
        assert constraints.max_vlan_count == 50
        assert len(constraints.reserved_vlans) == 4
    
    def test_invalid_min_vlan(self):
        """Test that invalid min_vlan raises ValueError"""
        with pytest.raises(ValueError, match="Invalid min_vlan"):
            VLANConstraints(min_vlan=0, max_vlan=999)
    
    def test_invalid_max_vlan(self):
        """Test that invalid max_vlan raises ValueError"""
        with pytest.raises(ValueError, match="Invalid max_vlan"):
            VLANConstraints(min_vlan=10, max_vlan=5000)
    
    def test_min_greater_than_max(self):
        """Test that min > max raises ValueError"""
        with pytest.raises(ValueError, match="min_vlan.*> max_vlan"):
            VLANConstraints(min_vlan=100, max_vlan=50)
    
    def test_default_vlan_out_of_range(self):
        """Test that default_vlan_start outside range raises ValueError"""
        with pytest.raises(ValueError, match="default_vlan_start.*outside range"):
            VLANConstraints(min_vlan=10, max_vlan=100, default_vlan_start=200)
    
    def test_invalid_vlan_count(self):
        """Test that max_vlan_count < 1 raises ValueError"""
        with pytest.raises(ValueError, match="max_vlan_count must be >= 1"):
            VLANConstraints(max_vlan_count=0)
    
    def test_invalid_reserved_vlan(self):
        """Test that invalid reserved VLAN raises ValueError"""
        with pytest.raises(ValueError, match="Invalid reserved VLAN"):
            VLANConstraints(reserved_vlans=[5000])
    
    def test_is_vlan_reserved(self):
        """Test VLAN reservation check"""
        constraints = VLANConstraints(reserved_vlans=[1, 997, 998, 999])
        assert constraints.is_vlan_reserved(1) is True
        assert constraints.is_vlan_reserved(997) is True
        assert constraints.is_vlan_reserved(10) is False
    
    def test_is_vlan_valid(self):
        """Test VLAN validity check"""
        constraints = VLANConstraints(min_vlan=10, max_vlan=999, reserved_vlans=[997])
        assert constraints.is_vlan_valid(10) is True
        assert constraints.is_vlan_valid(500) is True
        assert constraints.is_vlan_valid(5) is False  # Below min
        assert constraints.is_vlan_valid(1000) is False  # Above max
        assert constraints.is_vlan_valid(997) is False  # Reserved
    
    def test_get_available_vlan_range(self):
        """Test available VLAN range calculation"""
        constraints = VLANConstraints(min_vlan=10, max_vlan=999)
        assert constraints.get_available_vlan_range() == (10, 999)
    
    def test_clamp_vlan_count(self):
        """Test VLAN count clamping"""
        constraints = VLANConstraints(max_vlan_count=50)
        assert constraints.clamp_vlan_count(30) == 30
        assert constraints.clamp_vlan_count(100) == 50
        assert constraints.clamp_vlan_count(0) == 0


class TestVLANValidator:
    """Test VLANValidator with catalog integration"""
    
    @pytest.fixture
    def catalog(self):
        return CatalogLoader()
    
    @pytest.fixture
    def validator(self, catalog):
        return VLANValidator(catalog)
    
    def test_get_constraints_for_known_model(self, validator):
        """Test getting constraints for known hardware model"""
        constraints = validator.get_constraints("Nexus 93180YC-EX")
        assert constraints.min_vlan == 100
        assert constraints.max_vlan == 4094
        assert constraints.default_vlan_start == 100
        assert constraints.max_vlan_count == 100
        assert 1 in constraints.reserved_vlans
    
    def test_get_constraints_for_unknown_model(self, validator):
        """Test getting constraints for unknown model returns defaults"""
        constraints = validator.get_constraints("UnknownModel")
        assert constraints.min_vlan == 1
        assert constraints.max_vlan == 4094
        assert constraints.default_vlan_start == 10
        assert constraints.max_vlan_count == 1000
        assert len(constraints.reserved_vlans) == 0
    
    def test_constraint_caching(self, validator):
        """Test that constraints are cached"""
        constraints1 = validator.get_constraints("Nexus 93180YC-EX")
        constraints2 = validator.get_constraints("Nexus 93180YC-EX")
        assert constraints1 is constraints2
    
    def test_validate_vlan_assignment_valid(self, validator):
        """Test valid VLAN assignment"""
        valid, msg = validator.validate_vlan_assignment("Nexus 93180YC-EX", 150)
        assert valid is True
        assert msg == ""
    
    def test_validate_vlan_assignment_below_min(self, validator):
        """Test VLAN assignment below minimum"""
        valid, msg = validator.validate_vlan_assignment("Nexus 93180YC-EX", 50)
        assert valid is False
        assert "below minimum" in msg
    
    def test_validate_vlan_assignment_reserved(self, validator):
        """Test VLAN assignment to reserved VLAN"""
        # Use a VLAN that's within range but reserved
        valid, msg = validator.validate_vlan_assignment("Nexus 93180YC-EX", 997)
        assert valid is False
        assert "reserved" in msg
    
    def test_validate_vlan_range_valid(self, validator):
        """Test valid VLAN range"""
        valid, msg = validator.validate_vlan_range("Nexus 93180YC-EX", 100, 10)
        assert valid is True
        assert msg == ""
    
    def test_validate_vlan_range_exceeds_max(self, validator):
        """Test VLAN range exceeding maximum"""
        valid, msg = validator.validate_vlan_range("Nexus 93180YC-EX", 4000, 100)
        assert valid is False
        assert "exceeds maximum" in msg
    
    def test_validate_vlan_range_reserved_in_range(self, validator):
        """Test VLAN range containing reserved VLAN"""
        valid, msg = validator.validate_vlan_range("Nexus 93180YC-EX", 995, 10)
        assert valid is False
        assert "reserved" in msg
    
    def test_suggest_vlan_range_preferred_valid(self, validator):
        """Test suggesting VLAN range with valid preferred start"""
        start, end = validator.suggest_vlan_range("Nexus 93180YC-EX", 10, 150)
        assert start == 150
        assert end == 159
    
    def test_suggest_vlan_range_preferred_invalid(self, validator):
        """Test suggesting VLAN range with invalid preferred start"""
        start, end = validator.suggest_vlan_range("Nexus 93180YC-EX", 10, 50)
        assert start >= 100  # Should use default start
        assert end >= start
    
    def test_suggest_vlan_range_exceeds_max(self, validator):
        """Test suggesting VLAN range that would exceed max"""
        start, end = validator.suggest_vlan_range("Nexus 93180YC-EX", 4000, 100)
        assert end <= 4094
    
    def test_validate_multi_switch_vlan_consistency_no_conflicts(self, validator):
        """Test multi-switch VLAN consistency with no conflicts"""
        switches = [
            {"hostname": "LEAF1", "model": "Nexus 93180YC-EX", "base_access_vlan": 100, "access_vlan_count": 10},
            {"hostname": "LEAF2", "model": "Nexus 93180YC-EX", "base_access_vlan": 200, "access_vlan_count": 10},
        ]
        valid, errors = validator.validate_multi_switch_vlan_consistency(switches)
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_multi_switch_vlan_consistency_with_conflicts(self, validator):
        """Test multi-switch VLAN consistency with conflicts"""
        switches = [
            {"hostname": "LEAF1", "model": "Nexus 93180YC-EX", "base_access_vlan": 100, "access_vlan_count": 20},
            {"hostname": "LEAF2", "model": "Nexus 93180YC-EX", "base_access_vlan": 110, "access_vlan_count": 10},
        ]
        valid, errors = validator.validate_multi_switch_vlan_consistency(switches)
        assert valid is False
        assert len(errors) > 0
        assert "overlap" in errors[0].lower()
    
    def test_validate_multi_switch_vlan_consistency_invalid_ranges(self, validator):
        """Test multi-switch VLAN consistency with invalid ranges"""
        switches = [
            {"hostname": "LEAF1", "model": "Nexus 93180YC-EX", "base_access_vlan": 50, "access_vlan_count": 10},
            {"hostname": "LEAF2", "model": "Nexus 93180YC-EX", "base_access_vlan": 200, "access_vlan_count": 10},
        ]
        valid, errors = validator.validate_multi_switch_vlan_consistency(switches)
        assert valid is False
        assert len(errors) > 0
    
    def test_get_common_vlan_constraints(self, validator):
        """Test getting common constraints across multiple models"""
        models = ["Nexus 93180YC-EX", "Nexus 9336C-FX2"]
        common = validator.get_common_vlan_constraints(models)
        
        # Should use most restrictive constraints
        assert common.min_vlan == max(
            validator.get_constraints("Nexus 93180YC-EX").min_vlan,
            validator.get_constraints("Nexus 9336C-FX2").min_vlan
        )
        assert common.max_vlan == min(
            validator.get_constraints("Nexus 93180YC-EX").max_vlan,
            validator.get_constraints("Nexus 9336C-FX2").max_vlan
        )
    
    def test_get_common_vlan_constraints_empty_list(self, validator):
        """Test getting common constraints with empty model list"""
        common = validator.get_common_vlan_constraints([])
        assert common.min_vlan == 1
        assert common.max_vlan == 4094
    
    def test_ranges_overlap_helper(self, validator):
        """Test the internal range overlap detection"""
        range1 = {"start": 100, "end": 150}
        range2 = {"start": 120, "end": 170}
        assert validator._ranges_overlap(range1, range2) is True
        
        range3 = {"start": 200, "end": 250}
        assert validator._ranges_overlap(range1, range3) is False


class TestVLANPropagationIntegration:
    """Integration tests for VLAN propagation with IntentEngine"""
    
    @pytest.fixture
    def catalog(self):
        return CatalogLoader()
    
    def test_intent_engine_respects_vlan_constraints(self, catalog):
        """Test that IntentEngine respects VLAN constraints"""
        from core.intent_engine import IntentEngine
        from models.intent_model import BlueprintIntent, IntentOverrides
        
        engine = IntentEngine(catalog)
        
        # Request VLAN range that would be invalid for the model
        intent = BlueprintIntent(
            hostname="LEAF1",
            site_name="HQ",
            role="leaf",
            model="Nexus 93180YC-EX",
            mgmt_ip="10.10.10.1/24",
            mgmt_gw="10.10.10.1",
            redundancy_mode="standalone",
            security_tier="standard",
            uplink_ports=[],
            overrides=IntentOverrides(
                base_access_vlan=50,  # Below minimum for this model
                access_vlan_count=10,
            )
        )
        
        device, resolution = engine.resolve(intent)
        
        # Device should have VLANs, but they should be adjusted to valid range
        assert len(device.vlans) > 0
        # All VLANs should be >= 100 (model minimum)
        for vlan in device.vlans:
            assert vlan.id >= 100
    
    def test_intent_engine_skips_reserved_vlans(self, catalog):
        """Test that IntentEngine skips reserved VLANs"""
        from core.intent_engine import IntentEngine
        from models.intent_model import BlueprintIntent, IntentOverrides
        
        engine = IntentEngine(catalog)
        
        # Request VLAN range that includes reserved VLANs
        intent = BlueprintIntent(
            hostname="LEAF1",
            site_name="HQ",
            role="leaf",
            model="Nexus 93180YC-EX",
            mgmt_ip="10.10.10.1/24",
            mgmt_gw="10.10.10.1",
            redundancy_mode="standalone",
            security_tier="standard",
            uplink_ports=[],
            overrides=IntentOverrides(
                base_access_vlan=995,  # Range includes reserved VLANs
                access_vlan_count=10,
            )
        )
        
        device, resolution = engine.resolve(intent)
        
        # No VLANs should be in the reserved list
        reserved_vlans = catalog.get_hardware_profile("Nexus 93180YC-EX").get("vlan_constraints", {}).get("reserved_vlans", [])
        for vlan in device.vlans:
            assert vlan.id not in reserved_vlans


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
