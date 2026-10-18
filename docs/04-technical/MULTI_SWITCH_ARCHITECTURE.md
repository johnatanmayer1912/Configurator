# Multi-Switch Architecture — NX-OS Configuration Authority

**Version:** 6.46.4  
**Date:** 2026-08-17  
**Purpose:** Complete documentation of multi-switch deployment architecture, data models, and generation pipeline

---

## Overview

The NX-OS Configuration Authority supports multi-switch topologies including spine-leaf, 3-tier, and custom deployments. This document describes the architecture for multi-switch configuration generation, including data models, topology validation, and the generation pipeline.

---

## Multi-Switch Data Model

### Deployment Structure

```json
{
  "site_name": "string",
  "switches": [
    {
      "id": "string (UUID)",
      "hostname": "string",
      "role": "spine|leaf|access|core",
      "model": "string",
      "nxos_version": "string",
      "mgmt_ip": "string (CIDR)",
      "vlans": [{"id": int, "name": "string"}],
      "interfaces": [
        {
          "name": "string",
          "mode": "access|trunk|routed",
          "description": "string",
          "channel_group": int,
          "channel_mode": "active"
        }
      ],
      "vpc": {
        "domain_id": int,
        "peer_link_id": int,
        "peer_link_interfaces": ["string"],
        "local_keepalive_ip": "string",
        "remote_keepalive_ip": "string",
        "role_priority": int
      },
      "port_channels": [
        {
          "id": int,
          "mode": "active",
          "vpc_peer_link": boolean,
          "member_interfaces": ["string"]
        }
      ],
      "svis": [
        {
          "vlan_id": int,
          "ip_address": "string (CIDR)",
          "hsrp": {
            "vip": "string",
            "priority": int,
            "preempt": boolean
          }
        }
      ]
    }
  ],
  "vpc_pairs": [
    {
      "domain": int,
      "primary": "string (hostname)",
      "secondary": "string (hostname)",
      "peer_link_ports": "string",
      "description": "string"
    }
  ],
  "uplinks": [
    {
      "uplink_id": "string (UUID)",
      "from": "string (hostname)",
      "to": "string (hostname)",
      "ports": "string",
      "from_ports": "string",
      "to_ports": "string",
      "po_id": int,
      "description": "string"
    }
  ]
}
```

---

## Switch Roles and Behavior

### Spine Switches

**Characteristics:**
- Layer 3 routing focus
- No vPC configuration
- Multiple uplink connections to leaf switches
- Typically use 40G/100G interfaces

**Configuration Profile:**
- OSPF/BGP underlay routing
- Loopback interfaces for routing
- No access VLANs
- No vPC domain

**Implementation:** `core/scenario_engine.py` - spine role presets

---

### Leaf Switches

**Characteristics:**
- Layer 2/Layer 3 boundary
- May have vPC configuration
- Uplinks to spine switches
- Downlinks to access switches or servers

**Configuration Profile:**
- vPC domain (if paired)
- VLAN trunking
- SVI for routing
- HSRP for gateway redundancy

**Implementation:** `core/scenario_engine.py` - leaf role presets

---

### Access Switches

**Characteristics:**
- Layer 2 focus
- May have vPC configuration
- Downlinks to servers/endpoints
- Uplinks to leaf switches

**Configuration Profile:**
- vPC domain (if paired)
- Access port configurations
- VLAN trunking
- Port security (optional)

**Implementation:** `core/scenario_engine.py` - access role presets

---

### Core Switches

**Characteristics:**
- Aggregation layer
- vPC configuration typical
- High port density
- Redundant design

**Configuration Profile:**
- vPC domain
- VLAN trunking
- SVI for routing
- HSRP for gateway redundancy

**Implementation:** `core/scenario_engine.py` - core role presets

---

## vPC Pair Architecture

### vPC Domain Model

```json
{
  "domain": int,
  "primary": "string (hostname)",
  "secondary": "string (hostname)",
  "peer_link_ports": "string",
  "description": "string"
}
```

### vPC Configuration Flow

```
1. User defines vPC pair in deployment
2. System validates domain ID (1-4095)
3. System validates peer link ports
4. System generates keepalive IPs (manual or auto)
5. System applies vPC configuration to both switches
6. System cross-validates vPC pair consistency
7. System generates configuration files
```

### vPC Keepalive IP Generation

**Manual Mode:**
- User specifies local and remote keepalive IPs
- System validates IP format and uniqueness

**Auto Mode:**
- System generates keepalive IPs based on domain ID
- Format: `10.255.{domain/256}.{domain%256}` (local)
- Remote IP: local IP + 1
- Example: Domain 100 → Local `10.255.0.100`, Remote `10.255.0.101`

**Implementation:** `core/vpc_topology.py` - keepalive generation logic

---

## Uplink Architecture

### Uplink Data Model

```json
{
  "uplink_id": "string (UUID)",
  "from": "string (hostname)",
  "to": "string (hostname)",
  "ports": "string",
  "from_ports": "string",
  "to_ports": "string",
  "po_id": int,
  "description": "string"
}
```

### Uplink Resolution

**Port Resolution Logic:**
1. If `ports` is specified, use for both ends
2. If `from_ports` and `to_ports` are specified, use respective ports
3. Parse port ranges (e.g., `Ethernet1/1-2`)
4. Normalize port names (e.g., `E1/1` → `Ethernet1/1`)
5. Apply port channel configuration if `po_id` specified

**Implementation:** `core/deployment_builder.py:apply_custom_uplinks_for_switch()`

### Uplink Validation

**Validation Rules:**
- Source and destination hostnames must exist
- Port specifications must be valid
- Port channel ID must be unique per switch
- No duplicate uplinks between same switch pair

---

## Topology Validation

### Switch Existence Validation

**Purpose:** Ensure all referenced switches exist in deployment

**Validation Points:**
- vPC pair primary and secondary hostnames
- Uplink source and destination hostnames
- Interface peer references

**Implementation:** `api/main.py:_validate_deployment_topology()`

---

### vPC Pair Validation

**Purpose:** Ensure vPC pairs are correctly configured

**Validation Checks:**
- Domain ID consistency between peers
- Peer link ID consistency between peers
- Keepalive IP cross-validation
- VLAN set consistency
- Peer link port count (minimum 2)

**Implementation:** `core/validator.py:validate_vpc_pair()`

---

### Uplink Topology Validation

**Purpose:** Ensure uplink topology is valid

**Validation Checks:**
- No circular dependencies
- No orphan switches
- Port availability
- Port channel ID uniqueness

**Implementation:** `core/deployment_wiring.py:validate_all_vpc_pairs()`

---

## Generation Pipeline

### Multi-Switch Generation Flow

```
POST /generate-deployment
    ↓
Validate deployment topology
    ↓
Validate vPC pairs
    ↓
Apply custom uplinks to switches
    ↓
Validate each switch device model
    ↓
Generate configuration for each switch
    ↓
Write configuration files to disk
    ↓
Generate deployment manifest
    ↓
Return results to UI
```

### Pipeline Stages

**Stage 1: Topology Validation**
- Validate switch existence
- Validate vPC pair references
- Validate uplink references
- Check for orphan references

**Stage 2: vPC Validation**
- Validate vPC domain IDs
- Validate peer link consistency
- Validate keepalive cross-checks
- Validate VLAN consistency

**Stage 3: Uplink Application**
- Apply uplink configurations to switches
- Resolve port specifications
- Configure port channels
- Set interface descriptions

**Stage 4: Device Validation**
- Validate each switch independently
- Check IP addresses
- Check VLAN uniqueness
- Check interface uniqueness
- Check vPC semantics

**Stage 5: Configuration Generation**
- Generate NX-OS CLI for each switch
- Apply role-specific configurations
- Apply vPC configurations
- Apply uplink configurations

**Stage 6: File Generation**
- Write configuration files to disk
- Write device JSON files
- Generate deployment manifest
- Handle vPC pair file sharing

**Implementation:** `api/main.py:generate_deployment()`

---

## File Generation Behavior

### Output Directory Structure

```
configs/history/
└── {timestamp}/
    ├── {hostname}_config.txt (for each switch)
    ├── {hostname}_device.json (for each switch)
    └── manifest.json
```

### vPC Pair File Sharing

**Behavior:**
- If both vPC peers succeed, one set of files is created
- File naming uses primary switch hostname
- Secondary switch configuration included in primary file
- If one peer fails, successful peer gets individual files

**Implementation:** `pipelines/build_pipeline.py:ConfigurationPipeline.execute()`

---

## Template System

### Deployment Templates

**Purpose:** Pre-configured multi-switch topologies

**Template Structure:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "complexity": "simple|medium|complex",
  "switches": [...],
  "vpc_pairs": [...],
  "uplinks": [...]
}
```

**Template Categories:**
- Production DC
- Cloud/VM
- Enterprise Campus
- Lab/Development

**Implementation:** `core/template_store.py`

---

## State Management

### Deployment State

**Purpose:** Track deployment configuration across UI interactions

**State Structure:**
```json
{
  "site_name": "string",
  "switches": [...],
  "vpc_pairs": [...],
  "uplinks": [...],
  "last_generated": "timestamp"
}
```

**State Persistence:**
- In-memory state during session
- No persistent state storage
- State reset on page refresh

**Implementation:** `core/deployment_state.py:get_state_manager()`

---

## Error Handling

### Generation Failures

**Partial Success Handling:**
- Continue generation for valid switches
- Skip switches with validation errors
- Return success/failure counts in response
- Generate error messages for failed switches

**Complete Failure Handling:**
- Return error response to UI
- No files written to disk
- Detailed error messages in response

**Implementation:** `api/main.py:generate_deployment()`

---

## Performance Considerations

### Generation Time

**Factors:**
- Number of switches
- Complexity of configurations
- vPC pair count
- Uplink count

**Typical Performance:**
- 2 switches: 1-2 seconds
- 4 switches: 3-5 seconds
- 8 switches: 8-15 seconds
- 16 switches: 20-40 seconds

### Optimization Strategies

**Implemented:**
- Parallel switch validation
- Cached hardware profiles
- Optimized template rendering
- Efficient file I/O

**Future Enhancements:**
- Async configuration generation
- Template caching
- Incremental generation

---

## Security Considerations

### Input Validation

**Validation Points:**
- Hostname format validation
- IP address validation
- vPC domain ID range validation
- Port specification validation

**Implementation:** `api/input_contracts.py`

### File System Security

**Constraints:**
- Output directory must be under app directory
- No absolute paths outside app directory
- No symbolic link following

**Implementation:** `core/deployment_builder.py:resolve_deployment_export_base()`

---

## E2E Test Coverage

### Multi-Switch Tests

**Test File:** `tests/e2e/test_multiswitch_deployments.py`

**Coverage:**
- Spine-leaf topology generation
- 3-tier topology generation
- vPC pair generation
- Uplink configuration
- File generation verification

**Test File:** `tests/e2e/test_multiswitch_editing_comprehensive.py`

**Coverage:**
- Switch editing in multi-switch deployments
- vPC domain editing
- Uplink modification
- Topology validation

**Test File:** `tests/e2e/test_true_file_generation_and_ui_actions.py`

**Coverage:**
- True file system output for multi-switch
- Post-generation UI actions
- Download All functionality
- Close button behavior

---

## Known Limitations

### Topology Constraints

**Not Currently Supported:**
- Multi-chassis EtherChannel (vPC+)
- FabricPath
- VXLAN BGP EVPN (limited support)
- Overlay routing protocols

**Scalability Limits:**
- Maximum switches per deployment: 64
- Maximum vPC pairs per deployment: 32
- Maximum uplinks per switch: 128

---

## Troubleshooting

### Common Multi-Switch Issues

**vPC Pair Failures:**
- Check domain ID consistency
- Verify keepalive IP cross-check
- Validate peer link port count
- Ensure VLAN sets match

**Uplink Failures:**
- Verify switch existence
- Check port specifications
- Validate port channel ID uniqueness
- Ensure no circular dependencies

**Generation Failures:**
- Check individual switch validation
- Verify hardware profile compatibility
- Ensure sufficient disk space
- Check file permissions

---

## Source of Truth

**Primary Implementation:** `api/main.py:generate_deployment()`  
**Data Models:** `models/device_model.py`  
**Validation:** `core/validator.py`  
**Topology Validation:** `core/deployment_wiring.py`  
**Uplink Application:** `core/deployment_builder.py`  
**State Management:** `core/deployment_state.py`  
**Template System:** `core/template_store.py`

This documentation must be synchronized with code changes. Any multi-switch architecture changes require immediate documentation updates.

---

## Related Documentation

- [API Reference](API_REFERENCE.md)
- [File Generation Behavior](FILE_GENERATION_BEHAVIOR.md)
- [Validation Rules](VALIDATION_RULES.md)
- [Multi-Switch User Flow](MULTI_SWITCH_USER_FLOW.md)
- [Architecture Overview](ARCHITECTURE.md)
