"""Integration tests for multi-switch deployment generation."""

import pytest
from api.main import DeploymentInput, SwitchConfig
from core.validator import DeviceValidator
from core.compliance import ComplianceEngine


def test_multiswitch_deployment_generation():
    """Test multi-switch deployment generation with vPC pairs."""
    deployment_input = DeploymentInput(
        switches=[
            SwitchConfig(
                hostname="CORE1",
                mgmt_ip="10.0.0.1/24",
                mgmt_gw="10.0.0.254",
                model="Nexus 9336C-FX2",
                vpc_domain="10"
            ),
            SwitchConfig(
                hostname="CORE2",
                mgmt_ip="10.0.0.2/24",
                mgmt_gw="10.0.0.254",
                model="Nexus 9336C-FX2",
                vpc_domain="10"
            ),
            SwitchConfig(
                hostname="LEAF1",
                mgmt_ip="10.0.0.11/24",
                mgmt_gw="10.0.0.254",
                model="Nexus 93180YC-EX",
                vpc_domain="100"
            ),
            SwitchConfig(
                hostname="LEAF2",
                mgmt_ip="10.0.0.12/24",
                mgmt_gw="10.0.0.254",
                model="Nexus 93180YC-EX",
                vpc_domain="100"
            )
        ],
        vpc_pairs=[
            {"domain": "10", "primary": "CORE1", "secondary": "CORE2", "peer_link_ports": "E1/35-36"},
            {"domain": "100", "primary": "LEAF1", "secondary": "LEAF2", "peer_link_ports": "E1/51-52"}
        ],
        uplinks=[
            {"from": "LEAF1", "to": "CORE1", "ports": "E1/53", "to_ports": "E1/1", "po_id": "10"},
            {"from": "LEAF1", "to": "CORE2", "ports": "E1/54", "to_ports": "E1/1", "po_id": "10"}
        ]
    )
    
    # Validate deployment structure
    assert len(deployment_input.switches) == 4
    assert len(deployment_input.vpc_pairs) == 2
    assert len(deployment_input.uplinks) == 2
    
    # Validate hostnames are unique
    hostnames = [s.hostname for s in deployment_input.switches]
    assert len(hostnames) == len(set(hostnames)), "Hostnames must be unique"
    
    # Validate vPC domains are unique
    domains = [p["domain"] for p in deployment_input.vpc_pairs]
    assert len(domains) == len(set(domains)), "vPC domains must be unique"


def test_vpc_pair_validation():
    """Test vPC pair validation across switches."""
    from core.validator import DeviceValidator
    from models.device_model import Device, VPCConfig
    from models.vlan_model import VLAN
    
    validator = DeviceValidator()
    
    # Create primary device
    primary = Device(
        hostname="CORE1",
        mgmt_ip="10.0.0.1/24",
        mgmt_gw="10.0.0.254",
        model="Nexus 9336C-FX2",
        vlans=[VLAN(id=10, name="VLAN10")],
        vpc=VPCConfig(
            domain_id=10,
            role="primary",
            keepalive_vrf="management",
            local_keepalive_ip="10.255.255.1/24",
            remote_keepalive_ip="10.255.255.2/24",
            peer_link_id=1,
            peer_link_interfaces=["Ethernet1/35", "Ethernet1/36"]
        )
    )
    
    # Create secondary device
    secondary = Device(
        hostname="CORE2",
        mgmt_ip="10.0.0.2/24",
        mgmt_gw="10.0.0.254",
        model="Nexus 9336C-FX2",
        vlans=[VLAN(id=10, name="VLAN10")],
        vpc=VPCConfig(
            domain_id=10,
            role="secondary",
            keepalive_vrf="management",
            local_keepalive_ip="10.255.255.2/24",
            remote_keepalive_ip="10.255.255.1/24",
            peer_link_id=1,
            peer_link_interfaces=["Ethernet1/35", "Ethernet1/36"]
        )
    )
    
    # Validate vPC pair
    report = validator.validate_vpc_pair(primary, secondary)
    assert report["status"] == "pass", f"vPC pair validation failed: {report['errors']}"


def test_uplink_topology_validation():
    """Test uplink topology validation."""
    deployment_input = DeploymentInput(
        switches=[
            SwitchConfig(
                hostname="SPINE1",
                mgmt_ip="10.0.0.1/24",
                mgmt_gw="10.0.0.254",
                model="Nexus 9336C-FX2"
            ),
            SwitchConfig(
                hostname="LEAF1",
                mgmt_ip="10.0.0.11/24",
                mgmt_gw="10.0.0.254",
                model="Nexus 93180YC-EX"
            )
        ],
        uplinks=[
            {"from": "LEAF1", "to": "SPINE1", "ports": "E1/1-2", "to_ports": "E1/1-2", "po_id": "1"}
        ]
    )
    
    # Validate uplink references exist
    hostnames = [s.hostname for s in deployment_input.switches]
    for uplink in deployment_input.uplinks:
        assert uplink["from"] in hostnames, f"Source switch {uplink['from']} not found"
        assert uplink["to"] in hostnames, f"Destination switch {uplink['to']} not found"


def test_port_conflict_detection_complex():
    """Test port conflict detection in complex scenarios."""
    from core.link_allocator import build_reserved_inventory, validate_link_row
    
    # Build inventory with multiple port-channels
    inventory = build_reserved_inventory(
        model="Nexus 9336C-FX2",
        peer_link_interfaces=["Ethernet1/35", "Ethernet1/36"],
        keepalive_interfaces=["Ethernet1/33", "Ethernet1/34"],
        port_channels=[
            {"number": 10, "member_interfaces": ["Ethernet1/1", "Ethernet1/2"]},
            {"number": 20, "member_interfaces": ["Ethernet1/3", "Ethernet1/4"]}
        ],
        link_rows=[
            {"po_id": 30, "members": ["Ethernet1/5", "Ethernet1/6"]}
        ]
    )
    
    # Test conflict detection
    conflicting_row = {"po_id": 10, "members": ["Ethernet1/7"]}
    result = validate_link_row(conflicting_row, inventory, "Nexus 9336C-FX2")
    
    assert len(result["conflicts"]) > 0, "Should detect Po ID conflict"
    
    # Test member conflict
    member_conflict_row = {"po_id": 40, "members": ["Ethernet1/1"]}
    result = validate_link_row(member_conflict_row, inventory, "Nexus 9336C-FX2")
    
    assert len(result["conflicts"]) > 0, "Should detect member port conflict"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
