"""
Expected Output Test Data for Full E2E Testing
===============================================

This module contains expected configuration outputs for multi-switch deployments,
including VLAN assignments, feature enablement, and interface configurations.
"""

# VLAN assignment expectations based on switch roles and VLAN templates
VLAN_ASSIGNMENT_RULES = {
    "campus": {
        "spine": ["TRANSIT"],
        "core": ["TRANSIT"],
        "leaf": ["FABRIC"],
        "access": ["FABRIC"]
    },
    "data_center": {
        "spine": ["TRANSIT"],
        "core": ["TRANSIT"],
        "leaf": ["FABRIC"],
        "access": ["FABRIC"]
    }
}

# Expected VLAN ranges for different templates
VLAN_TEMPLATE_RANGES = {
    "campus": {
        "TRANSIT": (10, 99),
        "FABRIC": (100, 999)
    },
    "data_center": {
        "TRANSIT": (10, 99),
        "FABRIC": (100, 999)
    }
}

# Expected feature enablement by switch role
FEATURE_EXPECTATIONS = {
    "spine": ["interface-vlan", "lacp", "lldp"],
    "core": ["interface-vlan", "lacp", "lldp", "vpc"],
    "leaf": ["interface-vlan", "lacp", "lldp", "hsrp", "vpc"],
    "access": ["interface-vlan", "lacp", "lldp", "storm-control"]
}

# Expected vPC configuration elements
VPC_EXPECTATIONS = {
    "domain": "vpc domain",
    "peer_link": "vpc peer-link",
    "peer_keepalive": "peer-keepalive",
    "peer_gateway": "peer-gateway",
    "auto_recovery": "auto-recovery"
}

# Expected interface configurations
INTERFACE_EXPECTATIONS = {
    "port_channel": "interface port-channel",
    "ethernet": "interface Ethernet",
    "svi": "interface Vlan",
    "mgmt": "interface mgmt0"
}

# Deployment template test cases
DEPLOYMENT_TEST_CASES = {
    "six_switch_fabric": {
        "name": "6-Switch Fabric (2 Spine + 4 Leaf)",
        "switch_count": 6,
        "spine_count": 2,
        "leaf_count": 4,
        "vpc_pairs": 2,
        "expected_vlans": {
            "SPINE1": ["TRANSIT"],
            "SPINE2": ["TRANSIT"],
            "LEAF1": ["FABRIC"],
            "LEAF2": ["FABRIC"],
            "LEAF3": ["FABRIC"],
            "LEAF4": ["FABRIC"]
        },
        "expected_features": {
            "SPINE1": ["interface-vlan", "lacp", "lldp"],
            "SPINE2": ["interface-vlan", "lacp", "lldp"],
            "LEAF1": ["interface-vlan", "lacp", "lldp", "hsrp", "vpc"],
            "LEAF2": ["interface-vlan", "lacp", "lldp", "hsrp", "vpc"],
            "LEAF3": ["interface-vlan", "lacp", "lldp", "hsrp", "vpc"],
            "LEAF4": ["interface-vlan", "lacp", "lldp", "hsrp", "vpc"]
        }
    },
    "spine_leaf": {
        "name": "Spine-Leaf Fabric",
        "switch_count": 4,
        "spine_count": 2,
        "leaf_count": 2,
        "vpc_pairs": 0,
        "expected_vlans": {
            "SPINE1": ["TRANSIT"],
            "SPINE2": ["TRANSIT"],
            "LEAF1": ["FABRIC"],
            "LEAF2": ["FABRIC"]
        },
        "expected_features": {
            "SPINE1": ["interface-vlan", "lacp", "lldp"],
            "SPINE2": ["interface-vlan", "lacp", "lldp"],
            "LEAF1": ["interface-vlan", "lacp", "lldp", "hsrp"],
            "LEAF2": ["interface-vlan", "lacp", "lldp", "hsrp"]
        }
    },
    "vpc_core_leaf": {
        "name": "vPC Core + Leaf Pairs",
        "switch_count": 4,
        "core_count": 2,
        "leaf_count": 2,
        "vpc_pairs": 2,
        "expected_vlans": {
            "CORE1": ["TRANSIT"],
            "CORE2": ["TRANSIT"],
            "LEAF10G-1": ["FABRIC"],
            "LEAF10G-2": ["FABRIC"]
        },
        "expected_features": {
            "CORE1": ["interface-vlan", "lacp", "lldp", "vpc"],
            "CORE2": ["interface-vlan", "lacp", "lldp", "vpc"],
            "LEAF10G-1": ["interface-vlan", "lacp", "lldp", "hsrp", "vpc"],
            "LEAF10G-2": ["interface-vlan", "lacp", "lldp", "hsrp", "vpc"]
        }
    }
}
