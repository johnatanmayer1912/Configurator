# Validation Rules — NX-OS Configuration Authority

**Version:** 6.46.4  
**Date:** 2026-08-17  
**Purpose:** Complete documentation of all validation rules, error conditions, and compliance checks

---

## Overview

The NX-OS Configuration Authority implements comprehensive validation at multiple stages: input validation, device model validation, vPC pair validation, and deployment topology validation. This document describes all validation rules, error conditions, and their enforcement points.

---

## Validation Architecture

### Validation Layers

```
User Input → Pydantic Contract Validation → Device Model Validation → vPC Pair Validation → Deployment Validation
```

**Implementation Layers:**
1. **API Layer:** Pydantic input contracts (`api/input_contracts.py`)
2. **Device Layer:** Device validator (`core/validator.py`)
3. **Pair Layer:** vPC pair validator (`core/validator.py`)
4. **Deployment Layer:** Topology validation (`core/deployment_wiring.py`)

---

## Input Contract Validation

### Hostname Validation

**Pattern:** `^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$`

**Rules:**
- Must start with letter or number
- Can contain letters, numbers, and hyphens
- Maximum length: 63 characters
- Cannot end with hyphen
- Case-sensitive

**Error Messages:**
- `"Hostname is required."`
- `"Hostname must use letters, numbers, and hyphens only."`

**Implementation:** `api/input_contracts.py:validate_hostname_value()`

---

### Management IP Validation

**Format:** CIDR notation required (e.g., `10.10.10.10/24`)

**Rules:**
- Must include CIDR prefix (e.g., `/24`)
- IPv4 address must be valid (4 octets, 0-255 each)
- CIDR prefix must be between 0 and 32

**Error Messages:**
- `"Management IP must include CIDR notation (e.g. 10.10.10.10/24)."`
- `"Invalid IPv4 address: {value}"`

**Implementation:** `api/input_contracts.py:validate_mgmt_ip_cidr()`

---

### IPv4 Address Validation (Loose)

**Format:** CIDR optional (e.g., `10.10.10.10` or `10.10.10.10/24`)

**Rules:**
- IPv4 address must be valid (4 octets, 0-255 each)
- CIDR prefix optional for gateways and keepalives

**Error Messages:**
- `"IP address cannot be empty."`
- `"Invalid IPv4 address: {value}"`

**Implementation:** `api/input_contracts.py:validate_ipv4_loose()`

---

### vPC Pair Input Validation

**Required Fields:**
- `domain`: Integer between 1 and 4095
- `primary`: Hostname string
- `secondary`: Hostname string
- `peer_link_ports`: Interface string (e.g., `Ethernet1/1-2`)

**Rules:**
- Domain ID must be between 1 and 4095
- Primary and secondary hostnames must be different
- Peer link ports must be specified
- Both hostnames must pass hostname validation

**Error Messages:**
- `"vPC domain ID must be between 1 and 4095"`
- `"vPC primary and secondary must be different switches."`
- `"vPC peer_link_ports (or vpc_pl_ints) is required."`

**Implementation:** `api/input_contracts.py:VPCPairInput`

---

### Uplink Input Validation

**Required Fields:**
- `from`: Source hostname
- `to`: Destination hostname
- `ports`: Interface string OR `from_ports` + `to_ports`

**Rules:**
- Source and destination hostnames must be different
- At least one port specification must be provided
- Port channel ID must be between 1 and 4096 (if specified)
- Both hostnames must pass hostname validation

**Error Messages:**
- `"Uplink requires ports, from_ports, or to_ports."`

**Implementation:** `api/input_contracts.py:UplinkInput`

---

## Device Model Validation

### IP Address Validation

**Validated Fields:**
- `device.mgmt_ip`
- `device.vpc.local_keepalive_ip`
- `device.vpc.remote_keepalive_ip`
- `device.svis[].ip_address`
- `device.svis[].hsrp.vip`

**Rules:**
- IP address must be valid IPv4 format
- CIDR prefix required for management IP
- CIDR prefix optional for keepalive IPs and SVI IPs

**Error Messages:**
- `"{label} is missing"`
- `"Invalid {label} format: {value}"`

**Implementation:** `core/validator.py:DeviceValidator._validate_ip()`

---

### VLAN Uniqueness Validation

**Validated Fields:**
- `device.vlans[].id`

**Rules:**
- VLAN IDs must be unique within a device
- VLAN ID range: 1-4094

**Error Messages:**
- `"Duplicate VLAN IDs detected: {duplicates}"`

**Implementation:** `core/validator.py:DeviceValidator.validate()`

---

### Interface Uniqueness Validation

**Validated Fields:**
- `device.interfaces[].name`

**Rules:**
- Interface names must be unique within a device
- Interface names must follow NX-OS naming conventions

**Error Messages:**
- `"Duplicate Interface names detected: {duplicates}"`

**Implementation:** `core/validator.py:DeviceValidator.validate()`

---

### Interface Mode Validation

**Validated Fields:**
- `device.interfaces[].mode`

**Valid Modes:**
- `access`: Access port (single VLAN)
- `trunk`: Trunk port (multiple VLANs)
- `routed`: Layer 3 routed port
- `bare`: No configuration

**Error Messages:**
- `"Interface {name} has invalid mode: {mode}. Expected: {valid_modes}"`

**Implementation:** `core/validator.py:DeviceValidator.validate()`

---

### vPC Semantic Validation

**Validated Fields:**
- `device.vpc.domain_id`
- `device.vpc.peer_link_id`
- `device.vpc.local_keepalive_ip`
- `device.vpc.remote_keepalive_ip`
- `device.vpc.peer_link_interfaces`
- `device.port_channels[].vpc_peer_link`

**Rules:**
- vPC domain ID must be between 1 and 4095
- Peer link must have at least 2 member interfaces
- Local and remote keepalive IPs must be different
- Peer link port channel must exist if specified

**Error Messages:**
- `"vPC domain {domain_id}: peer-link requires at least two member interfaces"`
- `"vPC domain {domain_id}: local and remote keepalive IPs must differ ({local_host})"`
- `"vPC domain ID must be 1-4095, got {domain_id}"`

**Implementation:** `core/validator.py:DeviceValidator._validate_vpc_semantics()`

---

## vPC Pair Validation

### Domain ID Consistency

**Validated Fields:**
- `primary.vpc.domain_id`
- `secondary.vpc.domain_id`

**Rules:**
- Both switches must have the same vPC domain ID

**Error Messages:**
- `"vPC Domain ID mismatch: {primary_domain} vs {secondary_domain}"`

**Implementation:** `core/validator.py:DeviceValidator.validate_vpc_pair()`

---

### Peer Link Consistency

**Validated Fields:**
- `primary.vpc.peer_link_id`
- `secondary.vpc.peer_link_id`

**Rules:**
- Both switches must have the same peer link port channel ID

**Error Messages:**
- `"vPC Peer-Link PO ID mismatch: {primary_po} vs {secondary_po}"`

**Implementation:** `core/validator.py:DeviceValidator.validate_vpc_pair()`

---

### Keepalive Cross-Validation

**Validated Fields:**
- `primary.vpc.local_keepalive_ip`
- `primary.vpc.remote_keepalive_ip`
- `secondary.vpc.local_keepalive_ip`
- `secondary.vpc.remote_keepalive_ip`

**Rules:**
- Primary local keepalive must equal secondary remote keepalive
- Primary remote keepalive must equal secondary local keepalive

**Error Messages:**
- `"vPC Keepalive Cross-Check Failed: Primary Local does not match Secondary Remote"`
- `"vPC Keepalive Cross-Check Failed: Primary Remote does not match Secondary Local"`

**Implementation:** `core/validator.py:DeviceValidator.validate_vpc_pair()`

---

### VLAN Consistency

**Validated Fields:**
- `primary.vlans[].id`
- `secondary.vlans[].id`

**Rules:**
- Both switches must have identical VLAN sets
- VLAN names should match (recommended, not enforced)

**Error Messages:**
- `"vPC VLAN Mismatch detected in IDs: {diff}"`

**Implementation:** `core/validator.py:DeviceValidator.validate_vpc_pair()`

---

## Deployment Topology Validation

### Switch Existence Validation

**Validated Fields:**
- `vpc_pairs[].primary`
- `vpc_pairs[].secondary`
- `uplinks[].from`
- `uplinks[].to`

**Rules:**
- All referenced hostnames must exist in `deployment.switches`
- No orphan references in vPC pairs or uplinks

**Error Messages:**
- `"Switch {hostname} referenced in vPC pair but not found in deployment"`
- `"Switch {hostname} referenced in uplink but not found in deployment"`

**Implementation:** `api/main.py:_validate_deployment_topology()`

---

### vPC Pair Blocking

**Validated Fields:**
- `vpc_pairs[].domain`
- `deployment.vpc_errors`

**Rules:**
- If vPC pair validation fails, both switches are blocked from export
- Switches with failed vPC pairs are excluded from file generation

**Implementation:** `core/deployment_builder.py:switches_blocked_by_vpc_errors()`

---

### Uplink Port Validation

**Validated Fields:**
- `uplinks[].ports`
- `uplinks[].from_ports`
- `uplinks[].to_ports`

**Rules:**
- Port specifications must be valid interface names or ranges
- Port ranges must be parseable (e.g., `Ethernet1/1-2`)
- Port channel IDs must be between 1 and 4096

**Error Messages:**
- `"Invalid port specification: {ports}"`

**Implementation:** `core/deployment_builder.py:parse_port_list()`

---

## Compliance Validation

### NX-OS Compliance Checks

**Validated Areas:**
- Feature enablement consistency
- Interface configuration completeness
- vPC best practices
- Security hardening (if enabled)

**Rules:**
- vPC requires `feature lacp` and `feature vpc` enabled
- vPC peer-link requires consistent configuration
- HSRP requires consistent VIP configuration

**Implementation:** `core/compliance.py:ComplianceEngine`

---

### Security Tier Validation

**Validated Areas:**
- Password strength (if configured)
- SNMP community strings (if configured)
- AAA configuration (if enabled)

**Rules:**
- Passwords must meet minimum length requirements
- SNMP communities must not use default values
- AAA must have at least one authentication method

**Implementation:** `core/device_enricher.py`

---

## Error Response Format

### Validation Error Structure

```json
{
  "status": "fail",
  "errors": [
    "Hostname is required.",
    "Invalid IPv4 address: 10.10.10"
  ]
}
```

### API Error Response

```json
{
  "detail": "Validation failed: Hostname is required."
}
```

---

## Validation Enforcement Points

### API Layer Enforcement

**Endpoints:**
- `POST /generate-deployment`
- `POST /scenario/generate`
- `POST /validate`
- `POST /validate/vpc-pair`

**Behavior:**
- Pydantic validation runs before business logic
- Returns 422 Unprocessable Entity on validation failure
- Detailed error messages in response body

---

### UI Layer Enforcement

**Validation Points:**
- Real-time field validation in forms
- Pre-submission validation checks
- Visual error indicators
- Toast notifications for validation failures

**Implementation:** `static/validation-ui.js`, `static/app.js`

---

### Generation Pipeline Enforcement

**Validation Points:**
- Pre-generation validation in `ConfigurationPipeline.execute()`
- Device model validation before rendering
- vPC pair validation before file generation
- Deployment topology validation before export

**Implementation:** `pipelines/build_pipeline.py`, `core/validator.py`

---

## Validation Configuration

### Customizable Rules

Some validation rules can be configured via:

**Hardware Profiles:** `hardware_profiles.yaml`
- Port layout validation
- vPC port suggestions
- Interface type restrictions

**Feature Options:** `data/feature_options.yaml`
- Feature enablement requirements
- CLI command validation
- Version-specific constraints

---

## E2E Test Coverage

### Validation Tests

**Test File:** `tests/e2e/test_comprehensive_validation_scenarios.py`

**Coverage:**
- Hostname validation (valid and invalid)
- Management IP validation (with and without CIDR)
- vPC domain ID validation (range and type)
- vPC keepalive IP validation (format and cross-check)
- VLAN uniqueness validation
- Interface uniqueness validation
- Interface mode validation
- vPC pair consistency validation

**Test File:** `tests/e2e/test_vpc_keepalive_validation.py`

**Coverage:**
- Keepalive IP presence validation
- Keepalive IP format validation
- Keepalive IP uniqueness validation
- Domain-based keepalive generation
- vPC pair keepalive cross-validation

---

## Known Limitations

### Validation Scope

**Not Currently Validated:**
- Physical port existence on specific hardware
- Bandwidth capacity constraints
- Power budget considerations
- Cable length limitations
- Environmental constraints

**Future Enhancements:**
- Hardware-specific port validation
- Bandwidth capacity planning
- Physical topology validation
- Cable plan validation

---

## Troubleshooting Validation Errors

### Common Validation Failures

**Hostname Issues:**
- Ensure hostname starts with letter or number
- Check for special characters (only hyphens allowed)
- Verify length is under 64 characters

**IP Address Issues:**
- Include CIDR prefix for management IP
- Use valid IPv4 octets (0-255)
- Check for typos in IP addresses

**vPC Issues:**
- Ensure domain ID is between 1 and 4095
- Verify peer link has at least 2 ports
- Check keepalive IPs are different
- Validate keepalive cross-check between peers

**VLAN Issues:**
- Ensure VLAN IDs are unique
- Check VLAN ID range (1-4094)
- Verify VLAN names are consistent in vPC pairs

---

## Source of Truth

**Primary Implementation:** `core/validator.py`  
**Input Contracts:** `api/input_contracts.py`  
**Compliance Engine:** `core/compliance.py`  
**Device Enricher:** `core/deployment_builder.py`  
**Validation UI:** `static/validation-ui.js`  
**E2E Tests:** `tests/e2e/test_comprehensive_validation_scenarios.py`

This documentation must be synchronized with code changes. Any validation rule changes require immediate documentation updates.

---

## Related Documentation

- [API Reference](API_REFERENCE.md)
- [File Generation Behavior](FILE_GENERATION_BEHAVIOR.md)
- [Multi-Switch User Flow](MULTI_SWITCH_USER_FLOW.md)
- [Architecture Overview](ARCHITECTURE.md)
