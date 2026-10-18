"""Deployment State Unit Tests

Tests the in-memory deployment state management including:
- Switch state CRUD operations
- VPC pair state management
- Uplink state management
- Validation and consistency checks
"""

import pytest
from core.deployment_state import (
    SwitchState,
    VPCPairState,
    UplinkState,
    DeploymentStateManager
)


class TestSwitchState:
    """Test switch state dataclass and operations."""
    
    def test_switch_state_creation(self):
        """Test creating a switch state."""
        state = SwitchState(
            hostname="TEST-SW-01",
            model="Nexus 93180YC-EX",
            role="leaf",
            mgmt_ip="10.10.10.10/24",
            nxos_version="9.3"
        )
        
        assert state.hostname == "TEST-SW-01"
        assert state.model == "Nexus 93180YC-EX"
        assert state.role == "leaf"
        assert state.mgmt_ip == "10.10.10.10/24"
        assert state.nxos_version == "9.3"
    
    def test_switch_state_to_dict(self):
        """Test converting switch state to dictionary."""
        state = SwitchState(
            hostname="TEST-SW-01",
            model="Nexus 93180YC-EX",
            role="leaf",
            mgmt_ip="10.10.10.10/24",
            nxos_version="9.3"
        )
        
        state_dict = state.to_dict()
        
        assert isinstance(state_dict, dict)
        assert state_dict["hostname"] == "TEST-SW-01"
        assert state_dict["model"] == "Nexus 93180YC-EX"
    
    def test_switch_state_update(self):
        """Test updating switch state attributes."""
        state = SwitchState(
            hostname="TEST-SW-01",
            model="Nexus 93180YC-EX",
            role="leaf",
            mgmt_ip="10.10.10.10/24",
            nxos_version="9.3"
        )
        
        state.update({"mgmt_ip": "10.10.10.11/24"})
        
        assert state.mgmt_ip == "10.10.10.11/24"


class TestVPCPairState:
    """Test vPC pair state dataclass and operations."""
    
    def test_vpc_pair_state_creation(self):
        """Test creating a vPC pair state."""
        state = VPCPairState(
            domain=100,
            primary="LEAF1",
            secondary="LEAF2",
            peer_link_ports="Ethernet1/51-52",
            keepalive_ports="Ethernet1/49-50"
        )
        
        assert state.domain == 100
        assert state.primary == "LEAF1"
        assert state.secondary == "LEAF2"
        assert state.peer_link_ports == "Ethernet1/51-52"
        assert state.keepalive_ports == "Ethernet1/49-50"
    
    def test_vpc_pair_state_to_dict(self):
        """Test converting vPC pair state to dictionary."""
        state = VPCPairState(
            domain=100,
            primary="LEAF1",
            secondary="LEAF2",
            peer_link_ports="Ethernet1/51-52",
            keepalive_ports="Ethernet1/49-50"
        )
        
        state_dict = state.to_dict()
        
        assert isinstance(state_dict, dict)
        assert state_dict["domain"] == 100
        assert state_dict["primary"] == "LEAF1"


class TestUplinkState:
    """Test uplink state dataclass and operations."""
    
    def test_uplink_state_creation(self):
        """Test creating an uplink state."""
        state = UplinkState(
            source_switch="LEAF1",
            destination_switch="CORE1",
            source_ports="Ethernet1/53-54",
            destination_ports="Ethernet1/53-54",
            port_channel_id=10
        )
        
        assert state.source_switch == "LEAF1"
        assert state.destination_switch == "CORE1"
        assert state.port_channel_id == 10
    
    def test_uplink_state_to_dict(self):
        """Test converting uplink state to dictionary."""
        state = UplinkState(
            source_switch="LEAF1",
            destination_switch="CORE1",
            source_ports="Ethernet1/53-54",
            destination_ports="Ethernet1/53-54",
            port_channel_id=10
        )
        
        state_dict = state.to_dict()
        
        assert isinstance(state_dict, dict)
        assert state_dict["source_switch"] == "LEAF1"
        assert state_dict["destination_switch"] == "CORE1"


class TestDeploymentStateManager:
    """Test deployment state manager operations."""
    
    @pytest.fixture
    def state_manager(self):
        """Create deployment state manager instance."""
        return DeploymentStateManager()
    
    def test_manager_initialization(self, state_manager):
        """Test that state manager initializes correctly."""
        assert state_manager._switches == {}
        assert state_manager._vpc_pairs == {}
        assert state_manager._uplinks == {}
    
    def test_add_switch(self, state_manager):
        """Test adding a switch to state."""
        switch_data = {
            "hostname": "TEST-SW-01",
            "model": "Nexus 93180YC-EX",
            "role": "leaf",
            "mgmt_ip": "10.10.10.10/24",
            "nxos_version": "9.3"
        }
        
        result = state_manager.add_switch(switch_data)
        
        assert "TEST-SW-01" in state_manager._switches
        assert state_manager._switches["TEST-SW-01"].hostname == "TEST-SW-01"
    
    def test_get_switch(self, state_manager):
        """Test retrieving a switch from state."""
        switch_data = {
            "hostname": "TEST-SW-01",
            "model": "Nexus 93180YC-EX",
            "role": "leaf",
            "mgmt_ip": "10.10.10.10/24",
            "nxos_version": "9.3"
        }
        
        state_manager.add_switch(switch_data)
        
        retrieved = state_manager.get_switch("TEST-SW-01")
        
        assert retrieved is not None
        assert retrieved.hostname == "TEST-SW-01"
    
    def test_get_nonexistent_switch(self, state_manager):
        """Test retrieving a non-existent switch."""
        retrieved = state_manager.get_switch("NONEXISTENT")
        
        assert retrieved is None
    
    def test_remove_switch(self, state_manager):
        """Test removing a switch from state."""
        switch_data = {
            "hostname": "TEST-SW-01",
            "model": "Nexus 93180YC-EX",
            "role": "leaf",
            "mgmt_ip": "10.10.10.10/24",
            "nxos_version": "9.3"
        }
        
        state_manager.add_switch(switch_data)
        assert "TEST-SW-01" in state_manager._switches
        
        state_manager.delete_switch("TEST-SW-01")
        assert "TEST-SW-01" not in state_manager._switches
    
    def test_add_vpc_pair(self, state_manager):
        """Test adding a vPC pair to state."""
        # First add switches
        state_manager.add_switch({"hostname": "LEAF1", "mgmt_ip": "10.10.10.10/24"})
        state_manager.add_switch({"hostname": "LEAF2", "mgmt_ip": "10.10.10.11/24"})
        
        vpc_data = {
            "domain": 100,
            "primary": "LEAF1",
            "secondary": "LEAF2",
            "peer_link_ports": "Ethernet1/51-52",
            "keepalive_ports": "Ethernet1/49-50"
        }
        
        result = state_manager.add_vpc_pair(vpc_data)
        
        assert 100 in state_manager._vpc_pairs
        assert state_manager._vpc_pairs[100].domain == 100
    
    def test_get_vpc_pair(self, state_manager):
        """Test retrieving a vPC pair from state."""
        # First add switches
        state_manager.add_switch({"hostname": "LEAF1", "mgmt_ip": "10.10.10.10/24"})
        state_manager.add_switch({"hostname": "LEAF2", "mgmt_ip": "10.10.10.11/24"})
        
        vpc_data = {
            "domain": 100,
            "primary": "LEAF1",
            "secondary": "LEAF2",
            "peer_link_ports": "Ethernet1/51-52",
            "keepalive_ports": "Ethernet1/49-50"
        }
        
        state_manager.add_vpc_pair(vpc_data)
        
        retrieved = state_manager.get_vpc_pair(100)
        
        assert retrieved is not None
        assert retrieved.domain == 100
    
    def test_add_uplink(self, state_manager):
        """Test adding an uplink to state."""
        # First add switches
        state_manager.add_switch({"hostname": "LEAF1", "mgmt_ip": "10.10.10.10/24"})
        state_manager.add_switch({"hostname": "CORE1", "mgmt_ip": "10.10.10.11/24"})
        
        uplink_data = {
            "source_switch": "LEAF1",
            "destination_switch": "CORE1",
            "source_ports": "Ethernet1/53-54",
            "destination_ports": "Ethernet1/53-54",
            "port_channel_id": 10
        }
        
        result = state_manager.add_uplink(uplink_data)
        
        assert len(state_manager._uplinks) > 0
    
    def test_get_all_switches(self, state_manager):
        """Test retrieving all switches."""
        switch1_data = {"hostname": "SW1", "mgmt_ip": "10.10.10.10/24"}
        switch2_data = {"hostname": "SW2", "mgmt_ip": "10.10.10.11/24"}
        
        state_manager.add_switch(switch1_data)
        state_manager.add_switch(switch2_data)
        
        all_switches = state_manager.list_switches()
        
        assert len(all_switches) == 2
    
    def test_clear_state(self, state_manager):
        """Test clearing all state."""
        switch_data = {
            "hostname": "TEST-SW-01",
            "model": "Nexus 93180YC-EX",
            "role": "leaf",
            "mgmt_ip": "10.10.10.10/24",
            "nxos_version": "9.3"
        }
        
        state_manager.add_switch(switch_data)
        assert len(state_manager._switches) > 0
        
        state_manager.clear_all()
        
        assert len(state_manager._switches) == 0
        assert len(state_manager._vpc_pairs) == 0
        assert len(state_manager._uplinks) == 0
    
    def test_duplicate_switch_hostname(self, state_manager):
        """Test that duplicate switch hostnames raise error."""
        switch1_data = {
            "hostname": "TEST-SW-01",
            "model": "Nexus 93180YC-EX",
            "role": "leaf",
            "mgmt_ip": "10.10.10.10/24",
            "nxos_version": "9.3"
        }
        switch2_data = {
            "hostname": "TEST-SW-01",  # Duplicate hostname
            "model": "Nexus 93180YC-EX",
            "role": "leaf",
            "mgmt_ip": "10.10.10.11/24",
            "nxos_version": "9.3"
        }
        
        state_manager.add_switch(switch1_data)
        
        # Should raise ValueError for duplicate
        with pytest.raises(ValueError, match="already exists"):
            state_manager.add_switch(switch2_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
