# AGENTS.MD - World-Class Skills & Rules

## 1. Core Engineering & Quality Standards
- **Token & Output Efficiency**: Never produce redundant conversational text or long status chatter. Deliver concise, high-density responses and production-grade implementations.
- **Zero-Trust Verification**: Verify code state and test execution directly via tools; never make assumptions about API signatures or UI states.
- **Robust Offline Operation**: Ensure all frontend dependencies, stylesheets, fonts, and assets compile cleanly for offline single-exe deployment via PyInstaller.

## 2. UI/UX & Frontend Excellence
- **Intuitive Workflows & Modals**: Every complex operation (e.g. multi-switch generation, switch deletion, template selection) must provide clear feedback, confirmation, and step-by-step guidance (modals, action buttons, tabbed interfaces).
- **Dynamic State Refresh**: UI controls and panels (e.g. port maps, vPC domain lists, VLAN selections) must auto-refresh immediately upon model mutation.
- **Preventative UX Constraints**: Validate interface formats, duplicate hostnames, VLAN ranges (1-4094), and vPC pair dependencies in UI input handlers prior to submission.

## 3. Network Architecture & NX-OS CLI Engineering
- **VLAN & Interface Synchronization**: Custom VLAN definitions across all device models must strictly propagate to both global VLAN definitions and specific interface access/trunk configuration lines (`switchport access vlan X`, `switchport trunk allowed vlan Y`).
- **Topology & Uplink Integration**: Custom deployment uplinks and vPC definitions must be parsed, validated, and directly reflected in device port mapping and rendered CLI outputs without falling back to default hardcoded topologies.
- **Domain & Subnet Integrity**: Rigorously check keepalive IP subnets, vPC domain ranges (1-4096), management IP subnets, and interface compatibility.

## 4. API & Python Backend Patterns
- **Unified Schema & Error Standard**: All API endpoints must adhere to consistent request/response schemas and standardized structured JSON error objects.
- **Strict Data Validation**: Validate all incoming payload fields (IP addresses using `ipaddress`, port-channel unique IDs, hostnames) prior to execution.


# Project Rules
- Whenever an external terminal command, network request, or API call fails due to a network or connection timeout, wait 60 seconds and automatically execute the retry command up to 5 times before asking the user for help.
