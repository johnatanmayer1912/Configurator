# API Reference — NX-OS Configuration Authority

**Version:** 6.46.4  
**Date:** 2026-08-17  
**Purpose:** Complete REST API endpoint documentation for the NX-OS Configuration Authority web platform

---

## Overview

The NX-OS Configuration Authority exposes a FastAPI-based REST API for configuration generation, validation, and management. All endpoints run on `http://127.0.0.1:9000` by default and are designed for offline operation.

**Base URL:** `http://127.0.0.1:9000`  
**Authentication:** Loopback-only for offline use (no session token required)  
**Content-Type:** `application/json` for all POST/PUT requests

---

## Core Endpoints

### Configuration Generation

#### POST /generate-deployment

Generate configurations for multi-switch deployments with vPC pairs, uplinks, and custom topology.

**Request Body:**
```json
{
  "mode": "deployment",
  "deployment": {
    "site_name": "string",
    "switches": [
      {
        "hostname": "string",
        "role": "core|leaf|access|spine",
        "model": "string",
        "nxos_version": "string",
        "mgmt_ip": "string (CIDR)",
        "vlans": [{"id": int, "name": "string"}],
        "interfaces": [{"name": "string", "mode": "access|trunk"}],
        "vpc": {
          "domain_id": int,
          "peer_link_id": int,
          "local_keepalive_ip": "string",
          "remote_keepalive_ip": "string"
        }
      }
    ],
    "vpc_pairs": [
      {
        "domain": int,
        "primary": "string",
        "secondary": "string",
        "peer_link_ports": "string",
        "description": "string"
      }
    ],
    "uplinks": [
      {
        "from": "string",
        "to": "string",
        "ports": "string",
        "from_ports": "string",
        "to_ports": "string",
        "po_id": int,
        "description": "string"
      }
    ],
    "output_dir": "string (optional)"
  },
  "preview": false
}
```

**Response:**
```json
{
  "status": "success",
  "total_switches": int,
  "successful": int,
  "failed": int,
  "results": [
    {
      "hostname": "string",
      "status": "success|error",
      "export": {
        "cli": "string (NX-OS configuration)",
        "config": "string (NX-OS configuration)",
        "output_dir": "string (filesystem path)"
      },
      "device_config": {
        "port_map": {
          "ports": [
            {
              "port_number": "string",
              "port_name": "string",
              "type": "string",
              "description": "string",
              "port_channel": int
            }
          ]
        }
      }
    }
  ],
  "export": {
    "output_dir": "string (filesystem path)"
  }
}
```

**Validation Rules:**
- Hostname must match pattern `^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$`
- Management IP must include CIDR notation (e.g., `10.10.10.10/24`)
- vPC domain ID must be between 1 and 4095
- vPC primary and secondary must be different switches
- Uplink ports must be valid interface names or ranges

**File Output:**
- Configurations are written to `configs/history/{timestamp}/`
- Each switch generates `{hostname}_config.txt` and `{hostname}_device.json`
- vPC pairs share files when both switches succeed

---

#### POST /scenario/generate

Generate single-switch configuration from scenario presets.

**Request Body:**
```json
{
  "mode": "single",
  "device": {
    "hostname": "string",
    "role": "core|leaf|access",
    "model": "string",
    "nxos_version": "string",
    "mgmt_ip": "string (CIDR)",
    "vlans": [{"id": int, "name": "string"}],
    "interfaces": [{"name": "string", "mode": "access|trunk"}],
    "vpc": {
      "domain_id": int,
      "peer_link_id": int,
      "local_keepalive_ip": "string",
      "remote_keepalive_ip": "string"
    }
  },
  "scenario": "string (scenario slug)",
  "preview": false
}
```

**Response:**
```json
{
  "status": "success",
  "config": "string (NX-OS configuration)",
  "cli": "string (NX-OS configuration)",
  "hostname": "string",
  "output_dir": "string (filesystem path)"
}
```

---

### Validation Endpoints

#### POST /validate

Validate device configuration without generating output.

**Request Body:**
```json
{
  "device": {
    "hostname": "string",
    "mgmt_ip": "string (CIDR)",
    "vlans": [{"id": int, "name": "string"}],
    "interfaces": [{"name": "string", "mode": "access|trunk"}],
    "vpc": {
      "domain_id": int,
      "local_keepalive_ip": "string",
      "remote_keepalive_ip": "string"
    }
  }
}
```

**Response:**
```json
{
  "status": "pass|fail",
  "errors": [
    "string (error message)"
  ]
}
```

**Validation Checks:**
- IP address format validation
- VLAN ID uniqueness
- Interface name uniqueness
- Interface mode validity (access, trunk, routed, bare)
- vPC semantic checks (peer-link members, keepalive IP differences, domain ID range)
- vPC pair consistency (domain ID, peer-link ID, keepalive cross-check)

---

#### POST /validate/vpc-pair

Validate consistency between vPC peer switches.

**Request Body:**
```json
{
  "primary": {
    "hostname": "string",
    "vpc": {
      "domain_id": int,
      "peer_link_id": int,
      "local_keepalive_ip": "string",
      "remote_keepalive_ip": "string"
    },
    "vlans": [{"id": int, "name": "string"}]
  },
  "secondary": {
    "hostname": "string",
    "vpc": {
      "domain_id": int,
      "peer_link_id": int,
      "local_keepalive_ip": "string",
      "remote_keepalive_ip": "string"
    },
    "vlans": [{"id": int, "name": "string"}]
  }
}
```

**Response:**
```json
{
  "status": "pass|fail",
  "errors": [
    "string (error message)"
  ]
}
```

**Cross-Checks:**
- vPC domain ID must match between peers
- vPC peer-link ID must match between peers
- Primary local keepalive must equal secondary remote keepalive
- Primary remote keepalive must equal secondary local keepalive
- VLAN sets must be identical between peers

---

### Catalog and Scenario Endpoints

#### GET /catalog/scenarios

List available scenario presets.

**Response:**
```json
{
  "scenarios": [
    {
      "slug": "string",
      "name": "string",
      "description": "string",
      "category": "string"
    }
  ]
}
```

---

#### GET /catalog/hardware

List available hardware profiles.

**Response:**
```json
{
  "profiles": [
    {
      "model": "string",
      "ports": ["string"],
      "vpc_peer_link": ["string"],
      "vpc_keepalive": ["string"]
    }
  ]
}
```

---

#### GET /catalog/nxos-versions

List supported NX-OS versions.

**Response:**
```json
{
  "versions": [
    {
      "version": "string",
      "template": "string",
      "features": ["string"]
    }
  ]
}
```

---

### Vault and History Endpoints

#### GET /vault/history

List configuration history from the vault.

**Query Parameters:**
- `hostname` (optional): Filter by hostname
- `site` (optional): Filter by site name
- `scenario` (optional): Filter by scenario
- `type` (optional): Filter by artifact type (config, manifest, package, json)

**Response:**
```json
{
  "artifacts": [
    {
      "filename": "string",
      "hostname": "string",
      "site": "string",
      "scenario": "string",
      "timestamp": "string",
      "type": "string",
      "path": "string"
    }
  ]
}
```

---

#### GET /vault/checkpoints

List configuration checkpoints.

**Response:**
```json
{
  "checkpoints": [
    {
      "id": "string",
      "timestamp": "string",
      "description": "string",
      "hostname": "string"
    }
  ]
}
```

---

#### POST /vault/checkpoint

Create a configuration checkpoint.

**Request Body:**
```json
{
  "hostname": "string",
  "description": "string",
  "device": {
    "hostname": "string",
    "role": "string",
    "model": "string",
    "nxos_version": "string",
    "mgmt_ip": "string"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "checkpoint_id": "string"
}
```

---

### System Endpoints

#### POST /system/shutdown

Gracefully stop the configurator server.

**Access Control:** Loopback-only (localhost only)

**Response:**
```json
{
  "status": "shutdown_initiated"
}
```

---

#### GET /health

Health check endpoint with dependency status.

**Response:**
```json
{
  "status": "healthy|degraded",
  "version": "string",
  "timestamp": "string (ISO 8601)",
  "checks": {
    "catalog": "ok|failed: message",
    "pipeline": "ok|failed: message",
    "history_dir": "ok|failed: message"
  }
}
```

---

#### GET /metrics

Prometheus metrics endpoint for monitoring.

**Response:** Plain text Prometheus format (if prometheus_client is available)

---

### Audit and Logging Endpoints

#### POST /audit/log

Receive audit logs from frontend for persistent storage.

**Access Control:** Loopback-only (no session token required for offline use)

**Request Body:**
```json
{
  "action": "string",
  "timestamp": "string (ISO 8601)",
  "userAgent": "string",
  "url": "string",
  "method": "string",
  "status": "int",
  "duration": "int"
}
```

**Response:**
```json
{
  "status": "logged"
}
```

---

#### POST /open-folder

Open a folder in the system file explorer.

**Access Control:** Loopback-only (no session token required for offline use)

**Request Body:**
```json
{
  "path": "string (relative or absolute path)"
}
```

**Response:**
```json
{
  "status": "success",
  "path": "string (absolute path)"
}
```

**Behavior:**
- Resolves relative paths relative to the app directory
- Creates the folder if it doesn't exist
- Opens the folder in the system file explorer (Windows Explorer, macOS Finder, Linux file manager)

---

### Template Endpoints

#### GET /templates

List available deployment templates.

**Response:**
```json
{
  "templates": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "category": "string",
      "complexity": "simple|medium|complex",
      "switches": int,
      "vpc_domains": int,
      "vlans": int,
      "uplinks": int
    }
  ]
}
```

---

#### POST /templates

Save a custom template.

**Request Body:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "deployment": {
    "switches": [...],
    "vpc_pairs": [...],
    "uplinks": [...]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "template_id": "string"
}
```

---

#### GET /templates/{template_id}

Load a specific template.

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "deployment": {
    "switches": [...],
    "vpc_pairs": [...],
    "uplinks": [...]
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "string (error message)"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Successful request
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid authentication token
- `403 Forbidden`: Access denied (non-loopback request)
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Request ID Correlation

All API responses include an `X-Request-ID` header for request tracing and correlation. You can also provide your own request ID via the `X-Request-ID` header.

---

## CORS Configuration

CORS is configured for offline localhost access:

- **Allowed Origins:** `http://127.0.0.1:9000`, `http://localhost:9000`
- **Allowed Methods:** All methods
- **Allowed Headers:** All headers
- **Credentials:** Disabled (required when allow_origins=["*"])

---

## Rate Limiting and Performance

- No rate limiting is enforced for offline use
- Configuration generation typically completes within 1-5 seconds per switch
- Large multi-switch deployments (10+ switches) may take 10-30 seconds
- File I/O operations are synchronous for simplicity

---

## Security Considerations

### Loopback Restriction

Most system endpoints enforce loopback-only access for security:
- `/system/shutdown`
- `/audit/log`
- `/open-folder`

These endpoints can only be accessed from `127.0.0.1` or `localhost`.

### Input Validation

All inputs are validated using Pydantic models with the following rules:
- Hostname pattern: `^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$`
- IP address validation with CIDR support
- vPC domain ID range: 1-4095
- Port channel ID range: 1-4096
- VLAN ID range: 1-4094

### File System Access

- All file operations are restricted to the app directory and subdirectories
- `output_dir` parameters must be under the configuration vault
- Absolute paths outside the app directory are rejected

---

## Source of Truth

**Primary Implementation:** `api/main.py`  
**Input Contracts:** `api/input_contracts.py`  
**Validation Logic:** `core/validator.py`  
**Build Pipeline:** `pipelines/build_pipeline.py`  
**Deployment Builder:** `core/deployment_builder.py`

This documentation must be synchronized with code changes. Any API endpoint changes require immediate documentation updates.

---

## Related Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Multi-Switch User Flow](MULTI_SWITCH_USER_FLOW.md)
- [Configuration Studio Guide](01-user-manual/CONFIGURATION_STUDIO.md)
- [Validation Rules](VALIDATION_RULES.md)
