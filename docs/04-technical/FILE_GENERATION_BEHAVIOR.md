# File Generation Behavior — NX-OS Configuration Authority

**Version:** 6.46.4  
**Date:** 2026-08-17  
**Purpose:** Complete documentation of file system output behavior, naming conventions, and artifact structure

---

## Overview

The NX-OS Configuration Authority writes configuration artifacts to the local file system during configuration generation. This document describes the exact file system behavior, output paths, naming conventions, and artifact structure for both single-switch and multi-switch deployments.

---

## Output Directory Structure

### Base Directory

All configuration artifacts are written to the **configuration vault** located at:

```
{app_dir}/configs/history/
```

Where `{app_dir}` is:
- **From EXE:** Directory containing the executable file
- **From Source:** Project root directory

The base directory is resolved by `utils/app_dirs.py:get_history_dir()`.

### Timestamped Batch Folders

Each configuration generation creates a timestamped subfolder:

```
configs/history/
└── {timestamp}/
    ├── {hostname}_config.txt
    ├── {hostname}_device.json
    ├── {hostname}_diff.txt
    ├── {hostname}_risk.txt
    └── manifest.json
```

**Timestamp Format:** `YYYYMMDD_HHMMSS` (e.g., `20260817_140530`)

---

## Single-Switch File Generation

### File Naming Convention

For single-switch configurations, files are named using the pattern:

```
{site}_{scenario}_{hostname}_{timestamp}_{suffix}.txt
```

**Components:**
- `site`: Site name (default: `DEFAULT_SITE`)
- `scenario`: Scenario slug (e.g., `vpc_core_pair`)
- `hostname`: Switch hostname (e.g., `CORE1`)
- `timestamp`: Generation timestamp
- `suffix`: Artifact type (`config`, `diff`, `risk`)

**Example:**
```
DEFAULT_SITE_vpc_core_pair_CORE1_20260817_140530_config.txt
DEFAULT_SITE_vpc_core_pair_CORE1_20260817_140530_device.json
DEFAULT_SITE_vpc_core_pair_CORE1_20260817_140530_diff.txt
DEFAULT_SITE_vpc_core_pair_CORE1_20260817_140530_risk.txt
```

### Artifact Types

| File | Purpose | Format |
|------|---------|--------|
| `*_config.txt` | Paste-ready NX-OS CLI configuration | Plain text |
| `*_device.json` | Structured device model for automation | JSON |
| `*_diff.txt` | Unified diff against baseline | Plain text |
| `*_risk.txt` | Risk analysis report | Plain text |
| `manifest.json` | Deployment metadata and file inventory | JSON |

### Device JSON Structure

```json
{
  "hostname": "CORE1",
  "role": "core",
  "model": "Nexus 9336C-FX2",
  "nxos_version": "10.2(1)",
  "mgmt_ip": "10.10.10.10/24",
  "vlans": [
    {
      "id": 10,
      "name": "Mgmt"
    }
  ],
  "interfaces": [
    {
      "name": "Ethernet1/1",
      "mode": "trunk",
      "description": "Uplink",
      "channel_group": 1,
      "channel_mode": "active"
    }
  ],
  "vpc": {
    "domain_id": 100,
    "peer_link_id": 1,
    "local_keepalive_ip": "10.255.255.1/32",
    "remote_keepalive_ip": "10.255.255.2/32",
    "role_priority": 4096
  },
  "port_channels": [
    {
      "id": 1,
      "mode": "active",
      "vpc_peer_link": true,
      "member_interfaces": ["Ethernet1/1", "Ethernet1/2"]
    }
  ]
}
```

---

## Multi-Switch File Generation

### Batch Folder Structure

For multi-switch deployments, all switches in the deployment share the same timestamped folder:

```
configs/history/
└── {timestamp}/
    ├── CORE1_config.txt
    ├── CORE1_device.json
    ├── CORE2_config.txt
    ├── CORE2_device.json
    ├── LEAF1_config.txt
    ├── LEAF1_device.json
    └── manifest.json
```

### vPC Pair File Sharing

When vPC pairs are generated, both switches in the pair share configuration files if both succeed:

```
configs/history/
└── {timestamp}/
    ├── CORE1_config.txt (contains both primary and secondary configs)
    ├── CORE1_device.json
    ├── manifest.json
```

**Behavior:**
- If both vPC peers succeed, only one set of files is created
- If one peer fails, the successful peer gets individual files
- File naming uses the primary switch hostname

### Manifest Structure

The `manifest.json` file provides deployment-level metadata:

```json
{
  "version": "6.46.4",
  "timestamp": "2026-08-17 14:05:30",
  "site_name": "DEFAULT_SITE",
  "scenario": "spine_leaf",
  "total_switches": 4,
  "successful": 4,
  "failed": 0,
  "files": [
    "CORE1_config.txt",
    "CORE1_device.json",
    "CORE2_config.txt",
    "CORE2_device.json",
    "LEAF1_config.txt",
    "LEAF1_device.json",
    "LEAF2_config.txt",
    "LEAF2_device.json",
    "manifest.json"
  ],
  "switches": [
    {
      "hostname": "CORE1",
      "role": "spine",
      "status": "success"
    },
    {
      "hostname": "CORE2",
      "role": "spine",
      "status": "success"
    },
    {
      "hostname": "LEAF1",
      "role": "leaf",
      "status": "success"
    },
    {
      "hostname": "LEAF2",
      "role": "leaf",
      "status": "success"
    }
  ],
  "vpc_pairs": [
    {
      "domain": 100,
      "primary": "LEAF1",
      "secondary": "LEAF2",
      "status": "success"
    }
  ]
}
```

---

## Custom Output Directory

### Override Behavior

Users can specify a custom output directory via the `output_dir` parameter in the `/generate-deployment` API:

```json
{
  "deployment": {
    "output_dir": "configs/custom_location"
  }
}
```

**Constraints:**
- Custom directory must be under the configuration vault (`configs/`)
- Absolute paths outside the app directory are rejected
- Directory is created automatically if it doesn't exist

**Resolution Logic:**
1. If `output_dir` is provided and non-empty:
   - Resolve to absolute path
   - Verify it's under the configuration vault
   - Create `{output_dir}/{timestamp}/` subfolder
2. If `output_dir` is not provided:
   - Use default `configs/history/{timestamp}/`

### Security Validation

```python
# From core/deployment_builder.py:resolve_deployment_export_base
if not str(candidate).startswith(str(history_root)):
    raise ValueError(
        f"output_dir must be under the configuration vault ({history_root})"
    )
```

---

## File Content Structure

### Configuration File Format

The `*_config.txt` files contain paste-ready NX-OS CLI configuration:

```
! NX-OS Configuration Authority v6.46.4
! Generated: 2026-08-17 14:05:30
! Scenario: vpc_core_pair
! Hostname: CORE1

hostname CORE1
feature lacp
feature vpc
vpc domain 100
  peer-keepalive destination 10.255.255.2 source 10.255.255.1
  peer-gateway
  auto-recovery
  delay restore 30
interface port-channel1
  switchport mode trunk
  vpc peer-link
interface Ethernet1/1
  switchport mode trunk
  channel-group 1 mode active
interface Ethernet1/2
  switchport mode trunk
  channel-group 1 mode active
interface mgmt0
  ip address 10.10.10.10/24
```

### Diff File Format

The `*_diff.txt` files contain unified diff format:

```
--- baseline
+++ proposed
@@ -1,3 +1,5 @@
 hostname SWITCH1
+feature vpc
+vpc domain 100
 interface mgmt0
  ip address 10.10.10.10/24
```

### Risk File Format

The `*_risk.txt` files contain risk analysis:

```
RISK ANALYSIS REPORT
Generated: 2026-08-17 14:05:30

HIGH RISK:
- No shutdown commands on critical interfaces
- Missing NTP configuration

MEDIUM RISK:
- Default passwords may be in use
- SNMP community strings not configured

LOW RISK:
- Logging configuration minimal
```

---

## File System Operations

### Write Behavior

**Implementation:** `pipelines/build_pipeline.py:ConfigurationPipeline.execute()`

**Process:**
1. Resolve output directory (custom or default)
2. Create timestamped subfolder
3. Generate configuration text
4. Write `*_config.txt`
5. Write `*_device.json`
6. Write `*_diff.txt`
7. Write `*_risk.txt`
8. Write `manifest.json` (for deployments)

**Atomicity:**
- Each file is written independently
- No transactional rollback on failure
- Partial writes may occur on interruption

### Error Handling

**Directory Creation Failures:**
- Raises `OSError` if directory cannot be created
- Returns error response to API caller

**File Write Failures:**
- Raises `IOError` if file cannot be written
- Returns error response to API caller
- Partial files may remain on disk

**Permission Issues:**
- Requires write access to app directory
- EXE runs with user permissions
- Source runs with Python interpreter permissions

---

## File Cleanup and Management

### No Automatic Cleanup

The system does **not** automatically delete old configuration files. Users must manually manage disk space.

### Recommended Cleanup Strategy

```powershell
# Remove configurations older than 30 days
Get-ChildItem configs\history\* | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-30)
} | Remove-Item -Recurse -Force
```

### Vault Filters

The UI provides filtering capabilities for the configuration vault:
- Filter by hostname
- Filter by site name
- Filter by scenario
- Filter by artifact type (config, manifest, package, json)

---

## E2E Test Validation

### File System Validation Tests

The E2E test suite validates file generation behavior:

**Test File:** `tests/e2e/test_file_system_validation.py`

**Validations:**
- Files are written to correct directory structure
- File naming follows conventions
- File content matches expected format
- vPC pair file sharing works correctly
- Custom output directories are respected

**Test File:** `tests/e2e/test_true_file_generation_and_ui_actions.py`

**Validations:**
- True file system output (not just API content)
- Multi-switch file generation
- Post-generation UI actions (Download All, Close)
- Configuration file content accuracy

---

## Port Map Device Config

### Port Map Structure

For each switch, the device config includes a port map:

```json
{
  "device_config": {
    "port_map": {
      "ports": [
        {
          "port_number": "Ethernet1/1",
          "port_name": "Uplink to CORE1",
          "type": "trunk",
          "description": "Fabric uplink",
          "port_channel": 1
        },
        {
          "port_number": "Ethernet1/2",
          "port_name": "Server Port 1",
          "type": "access",
          "description": "Server connection",
          "port_channel": null
        }
      ]
    }
  }
}
```

### Port Map Display

The UI displays port maps in the results panel:
- **View Config:** Shows CLI configuration
- **Port Map:** Shows table of ports with types and descriptions
- **Download:** Downloads individual configuration file

---

## Download and Open Folder Behavior

### Download All Configs

The "Download All Configs (ZIP)" button:
- Calls `downloadAllDeploymentConfigs()` function in `static/app.js`
- If export directory exists, opens folder instead of downloading
- Otherwise, downloads individual config files as text files

**Implementation:** `static/app.js:downloadAllDeploymentConfigs()`

### Open Output Folder

The "Open Output Folder" button:
- Calls `openVaultFolder()` function in `static/app.js`
- Makes POST request to `/open-folder` endpoint
- Opens folder in system file explorer

**Implementation:** `api/main.py:/open-folder`

### Close Button

The "Close" button in results panel:
- Calls `close-deployment-results` action handler
- Hides results panel
- Returns to configuration editor
- Clears results panel content

**Implementation:** `static/ui-handlers.js:close-deployment-results`

---

## Source of Truth

**Primary Implementation:** `pipelines/build_pipeline.py`  
**Directory Resolution:** `utils/app_dirs.py`  
**Export Base Resolution:** `core/deployment_builder.py`  
**File Writing:** `pipelines/build_pipeline.py:_write_file()`  
**Device JSON:** `utils/change_package.py:write_device_json()`  
**UI Handlers:** `static/app.js`, `static/ui-handlers.js`  
**API Endpoint:** `api/main.py:/generate-deployment`

This documentation must be synchronized with code changes. Any file generation behavior changes require immediate documentation updates.

---

## Related Documentation

- [API Reference](API_REFERENCE.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Multi-Switch User Flow](MULTI_SWITCH_USER_FLOW.md)
- [Validation Rules](VALIDATION_RULES.md)
