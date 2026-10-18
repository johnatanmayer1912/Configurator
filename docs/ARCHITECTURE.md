# Architecture — NX-OS Configuration Authority (Web Platform)

**Version:** 6.46.4 · **Primary UI:** Web wizard + Multi-Switch Templates · **Delivery:** Offline exe

## Overview

The NX-OS Configuration Authority generates validated Cisco Nexus CLI configurations through a **dual-mode web interface**: a 5-step wizard for single-switch configurations and a template-based system for multi-switch deployments. It runs locally (browser + FastAPI) with no internet required when packaged as an exe.

## Module map

```
web_launcher.py          → FastAPI server, static mount, browser open
api/main.py              → REST API (catalog, scenario, vault, deployment, validation)
api/input_contracts.py   → Pydantic input contracts (hostname, IP, vPC, uplink)
static/app.js            → Wizard UI controller + Multi-Switch editor
static/ui-handlers.js    → UI event handlers (buttons, modals, actions)
static/audit_logger.js   → Frontend audit logging
templates/web/index.html → Wizard layout + Template gallery + Configuration editor

core/scenario_engine.py  → Scenario presets → Device model
core/device_enricher.py  → HSRP, security tier, NTP/logging post-processing
core/intent_engine.py    → Blueprint intent → VLANs/interfaces/SVIs
core/engine.py           → Validate + render orchestration
core/renderer.py         → Version-aware Jinja2
core/validator.py        → Device + vPC pair validation
core/risk_analyzer.py    → CLI risk report
core/checkpoint_manager.py → JSON snapshots
core/deployment_builder.py → Multi-switch deployment helpers (uplinks, export paths)
core/deployment_state.py  → Deployment state management
core.deployment_wiring.py → Topology validation (vPC pairs, uplinks)
core.template_store.py    → Template persistence (save/load)
core.vpc_topology.py     → vPC topology logic + keepalive generation

pipelines/build_pipeline.py → Validate → render → diff → risk → vault
templates/nxos_base.j2      → Primary NX-OS template (9.x/10.x)
templates/nxos_legacy.j2    → Legacy 7.x template

data/scenario_templates.yaml → Engineer presets
data/feature_options.yaml    → Feature checkboxes + CLI aliases
data/nxos_versions.yaml      → Version → template mapping
data/field_hints.yaml          → UI guidance
hardware_profiles.yaml       → Port layouts + vPC suggestions
```

## Data flow

###Single-Switch Wizard Flow

```
Wizard → POST /scenario/preview|generate
      → ScenarioEngine.apply_scenario()
      → IntentEngine.resolve()
      → device_enricher.enrich_device()  (HSRP, hardened tier, NTP)
      → DeviceValidator.validate()
      → ConfigRenderer → nxos_base.j2
      → ConfigurationPipeline → configs/history/
```

### Multi-Switch Deployment Flow

```
Template Gallery → Select Template
                → Apply Template to Deployment State
                → Configuration Editor (switches/vpc/VLANs/interfaces/uplinks)
                → POST /generate-deployment
                → Validate Deployment Topology
                → Validate vPC Pairs
                → Apply Custom Uplinks
                → Validate Each Switch
                → Generate Configurations
                → Write Files to Disk
                → Return Results with Port Maps
```

## vPC pair mode

When `generate_pair=true` on a `pair_mode` scenario:

1. Primary config with role priority 4096, keepalive A→B
2. `validate_vpc_pair()` cross-check
3. Secondary `{hostname}-B` with swapped keepalives, role priority 8192

### vPC Keepalive Auto-Generation

**Format:** `10.255.{domain/256}.{domain%256}` (local) and `+1` (remote)
**Example:** Domain 100 → Local `10.255.0.100`, Remote `10.255.0.101`

## Multi-Switch Architecture

### Deployment Data Model

```json
{
  "site_name": "string",
  "switches": [
    {
      "id": "UUID",
      "hostname": "string",
      "role": "spine|leaf|access|core",
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
      "peer_link_ports": "string"
    }
  ],
  "uplinks": [
    {
      "from": "string",
      "to": "string",
      "ports": "string",
      "po_id": int
    }
  ]
}
```

### Topology Validation

1. **Switch Existence**: All referenced switches must exist in deployment
2. **vPC Pair Validation**: Domain ID, peer link, keepalive cross-checks
3. **Uplink Validation**: Port specifications, port channel uniqueness
4. **Device Validation**: IP addresses, VLAN uniqueness, interface uniqueness

## File System Output

### Output Directory Structure

```
configs/history/
└── {timestamp}/
    ├── {hostname}_config.txt (for each switch)
    ├── {hostname}_device.json (for each switch)
    └── manifest.json
```

### vPC Pair File Sharing

- If both vPC peers succeed, one set of files is created
- File naming uses primary switch hostname
- Secondary switch configuration included in primary file

## AI governance

- `.cursor/ROLE_ACTIVATION_MATRIX.md` — skill activation
- `.cursor/skills/nxos-orchestrator/` — project router
- `.cursor/skills/nst-zero-trust-network-council/` — audit council
- `docs/06-quality-assurance/zero-trust-review/` — QA documentation

## Legacy components

| Component | Status |
|-----------|--------|
| `gui_main.py` (CustomTkinter) | Legacy — not primary |
| `main.py` (Tkinter) | Legacy |
| Web wizard | **Primary** |
| Multi-Switch Templates | **Primary** |

## Build

```powershell
pip install -r requirements.txt
pyinstaller NXOS_Configurator_Web_v{VERSION}.spec
python -m pytest tests/ -v
```

## Key API Endpoints

- `POST /generate-deployment` — Multi-switch configuration generation
- `POST /scenario/generate` — Single-switch configuration generation
- `POST /validate` — Device validation
- `POST /validate/vpc-pair` — vPC pair validation
- `POST /audit/log` — Frontend audit logging
- `POST /open-folder` — Open output folder in file explorer
- `GET /vault/history` — Configuration history listing
- `GET /templates` — Template listing

## Source of Truth

**Primary Implementation:** `api/main.py`  
**Input Contracts:** `api/input_contracts.py`  
**Validation:** `core/validator.py`  
**Multi-Switch Logic:** `core/deployment_builder.py`, `core/deployment_wiring.py`  
**File Generation:** `pipelines/build_pipeline.py`  
**UI Logic:** `static/app.js`, `static/ui-handlers.js`

See also: [API Reference](04-technical/API_REFERENCE.md), [File Generation Behavior](04-technical/FILE_GENERATION_BEHAVIOR.md), [Multi-Switch Architecture](04-technical/MULTI_SWITCH_ARCHITECTURE.md)
