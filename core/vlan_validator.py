"""VLAN Validation and Propagation Module

This module provides model-aware VLAN validation, ensuring VLAN assignments
respect hardware constraints and maintain consistency across multi-switch deployments.

Architecture Principles:
- Hardware profile constraints are authoritative
- Reserved VLANs are never auto-assigned
- Multi-switch deployments enforce VLAN consistency
- Validation happens before configuration generation
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class VLANValidationError(Exception):
    """Exception raised for VLAN validation errors"""
    pass


@dataclass
class VLANConstraints:
    """VLAN constraints from hardware profile"""
    min_vlan: int = 1
    max_vlan: int = 4094
    default_vlan_start: int = 10
    max_vlan_count: int = 1000
    reserved_vlans: List[int] = None

    def __post_init__(self):
        if self.reserved_vlans is None:
            self.reserved_vlans = []
        # Validate constraint integrity
        if not (1 <= self.min_vlan <= 4094):
            raise ValueError(f"Invalid min_vlan: {self.min_vlan}")
        if not (1 <= self.max_vlan <= 4094):
            raise ValueError(f"Invalid max_vlan: {self.max_vlan}")
        if self.min_vlan > self.max_vlan:
            raise ValueError(f"min_vlan {self.min_vlan} > max_vlan {self.max_vlan}")
        if not (self.min_vlan <= self.default_vlan_start <= self.max_vlan):
            raise ValueError(f"default_vlan_start {self.default_vlan_start} outside range [{self.min_vlan}, {self.max_vlan}]")
        if self.max_vlan_count < 1:
            raise ValueError(f"max_vlan_count must be >= 1, got {self.max_vlan_count}")
        for vlan in self.reserved_vlans:
            if not (1 <= vlan <= 4094):
                raise ValueError(f"Invalid reserved VLAN: {vlan}")

    def is_vlan_reserved(self, vlan_id: int) -> bool:
        """Check if VLAN is in reserved list"""
        return vlan_id in self.reserved_vlans

    def is_vlan_valid(self, vlan_id: int) -> bool:
        """Check if VLAN ID is within valid range and not reserved"""
        return self.min_vlan <= vlan_id <= self.max_vlan and not self.is_vlan_reserved(vlan_id)

    def get_available_vlan_range(self) -> tuple[int, int]:
        """Get available VLAN range excluding reserved"""
        return (self.min_vlan, self.max_vlan)

    def clamp_vlan_count(self, requested_count: int) -> int:
        """Clamp requested VLAN count to maximum allowed"""
        return min(requested_count, self.max_vlan_count)


class VLANValidator:
    """Validates VLAN assignments against hardware constraints"""

    def __init__(self, catalog_loader):
        self.catalog = catalog_loader
        self._constraint_cache: Dict[str, VLANConstraints] = {}

    def get_constraints(self, model: str) -> VLANConstraints:
        """Get VLAN constraints for a hardware model"""
        if model in self._constraint_cache:
            return self._constraint_cache[model]

        hw_profile = self.catalog.get_hardware_profile(model)
        if not hw_profile:
            logger.warning(f"No hardware profile found for {model}, using default constraints")
            constraints = VLANConstraints()
        else:
            constraints_data = hw_profile.get("vlan_constraints", {})
            constraints = VLANConstraints(
                min_vlan=constraints_data.get("min_vlan", 1),
                max_vlan=constraints_data.get("max_vlan", 4094),
                default_vlan_start=constraints_data.get("default_vlan_start", 10),
                max_vlan_count=constraints_data.get("max_vlan_count", 1000),
                reserved_vlans=constraints_data.get("reserved_vlans", [])
            )

        self._constraint_cache[model] = constraints
        return constraints

    def validate_vlan_assignment(self, model: str, vlan_id: int) -> tuple[bool, str]:
        """Validate a single VLAN assignment against model constraints"""
        constraints = self.get_constraints(model)
        
        if not constraints.is_vlan_valid(vlan_id):
            if vlan_id < constraints.min_vlan:
                return False, f"VLAN {vlan_id} below minimum {constraints.min_vlan}"
            if vlan_id > constraints.max_vlan:
                return False, f"VLAN {vlan_id} above maximum {constraints.max_vlan}"
            if constraints.is_vlan_reserved(vlan_id):
                return False, f"VLAN {vlan_id} is reserved for this model"
        
        return True, ""

    def validate_vlan_range(self, model: str, start_vlan: int, vlan_count: int) -> tuple[bool, str]:
        """Validate a VLAN range assignment against model constraints"""
        constraints = self.get_constraints(model)
        
        # Clamp count to maximum
        actual_count = constraints.clamp_vlan_count(vlan_count)
        if actual_count != vlan_count:
            logger.warning(f"VLAN count clamped from {vlan_count} to {actual_count} for {model}")
        
        # Validate start VLAN
        if not constraints.is_vlan_valid(start_vlan):
            return False, f"Start VLAN {start_vlan} is invalid for {model}"
        
        # Validate end VLAN doesn't exceed maximum
        end_vlan = start_vlan + actual_count - 1
        if end_vlan > constraints.max_vlan:
            return False, f"VLAN range [{start_vlan}, {end_vlan}] exceeds maximum {constraints.max_vlan}"
        
        # Check for reserved VLANs in range
        for vlan_id in range(start_vlan, end_vlan + 1):
            if constraints.is_vlan_reserved(vlan_id):
                return False, f"VLAN {vlan_id} in range is reserved for {model}"
        
        return True, ""

    def suggest_vlan_range(self, model: str, requested_count: int, preferred_start: Optional[int] = None) -> tuple[int, int]:
        """Suggest a valid VLAN range for the model"""
        constraints = self.get_constraints(model)
        actual_count = constraints.clamp_vlan_count(requested_count)
        
        # Use preferred start if valid, otherwise use default
        if preferred_start and constraints.is_vlan_valid(preferred_start):
            start = preferred_start
        else:
            start = constraints.default_vlan_start
        
        # Ensure range doesn't exceed maximum or hit reserved VLANs
        end = start + actual_count - 1
        if end > constraints.max_vlan:
            end = constraints.max_vlan
            start = max(constraints.min_vlan, end - actual_count + 1)
        
        # Skip reserved VLANs
        while any(constraints.is_vlan_reserved(v) for v in range(start, min(start + actual_count, constraints.max_vlan + 1))):
            start += 1
            if start + actual_count - 1 > constraints.max_vlan:
                # Fallback to default if we can't find space
                start = constraints.default_vlan_start
                break
        
        return (start, min(start + actual_count - 1, constraints.max_vlan))

    def validate_multi_switch_vlan_consistency(self, switches: List[Dict]) -> tuple[bool, List[str]]:
        """Validate VLAN consistency across multi-switch deployment"""
        errors = []
        
        # Collect all VLAN ranges from switches
        vlan_ranges = []
        for switch in switches:
            model = switch.get("model", "Generic")
            base_vlan = switch.get("base_access_vlan", 10)
            vlan_count = switch.get("access_vlan_count", 4)
            
            constraints = self.get_constraints(model)
            valid, msg = self.validate_vlan_range(model, base_vlan, vlan_count)
            if not valid:
                errors.append(f"{switch.get('hostname', 'unknown')}: {msg}")
                continue
            
            vlan_ranges.append({
                "hostname": switch.get("hostname", "unknown"),
                "model": model,
                "start": base_vlan,
                "end": base_vlan + vlan_count - 1,
                "constraints": constraints
            })
        
        # Check for VLAN overlaps between switches
        for i, range1 in enumerate(vlan_ranges):
            for range2 in vlan_ranges[i + 1:]:
                if self._ranges_overlap(range1, range2):
                    errors.append(
                        f"VLAN overlap: {range1['hostname']} [{range1['start']}-{range1['end']}] "
                        f"conflicts with {range2['hostname']} [{range2['start']}-{range2['end']}]"
                    )
        
        return (len(errors) == 0, errors)

    def _ranges_overlap(self, range1: Dict, range2: Dict) -> bool:
        """Check if two VLAN ranges overlap"""
        return not (range1['end'] < range2['start'] or range2['end'] < range1['start'])

    def get_common_vlan_constraints(self, models: List[str]) -> VLANConstraints:
        """Get common VLAN constraints that work for all specified models"""
        if not models:
            return VLANConstraints()
        
        constraints_list = [self.get_constraints(model) for model in models]
        
        # Find most restrictive constraints
        common = VLANConstraints(
            min_vlan=max(c.min_vlan for c in constraints_list),
            max_vlan=min(c.max_vlan for c in constraints_list),
            default_vlan_start=max(c.default_vlan_start for c in constraints_list),
            max_vlan_count=min(c.max_vlan_count for c in constraints_list),
            reserved_vlans=list(set().union(*[set(c.reserved_vlans) for c in constraints_list]))
        )
        
        return common
