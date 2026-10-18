# Quick Start — NX-OS Configurator (Web)

## Prerequisites

- Windows 10/11 (primary target)
- Python 3.11+ for development; **no Python needed** for the exe

## Launch

### Option A — Executable (recommended for field / offline)

1. Run `dist/NXOS_Configurator_Web_v*.exe`
2. Wait for console: `Starting Production Server at http://127.0.0.1:9000`
3. Browser opens automatically with session token

### Option B — From source

```powershell
cd Configurator
pip install -r requirements.txt
python web_launcher.py
```

## Wizard steps

### 1. Scenario

Choose the closest match:

| Scenario | When to use |
|----------|-------------|
| Standalone Access | IDF, closet switch, no vPC |
| Standalone Leaf | DC leaf without vPC (lab/staging) |
| vPC Leaf Pair | Production dual-homed leaf |
| Spine / Core | Spine layer, routed uplinks |
| OOB Management | Minimal bootstrap config |

### 2. Identity

- **Hostname** — alphanumeric + hyphens only
- **Mgmt IP** — must include CIDR (`10.1.1.1/24`)
- **NX-OS Version** — pick target train; ★ = recommended baseline
- **Generate vPC pair** — check for dual-switch output

### 3. Features

Checkboxes map directly to `feature` commands and vPC options. Hover for descriptions.

### 4. vPC / Network

Peer-link ports auto-fill from hardware profile. Override only if your cabling differs.

**v6.14.0+ Features:**
- **Keepalive IP Options**: Choose manual entry or auto-generation based on vPC domain
- **Domain ID Edit**: Modify vPC domain ID in multi-switch environments
- **Enhanced Validation**: Automatic validation of keepalive IPs and domain IDs

### 5. Review

- **Validate Scenario** — dry-run, no files written
- **Build Configuration** — writes config, diff, and risk report to vault

## Output artifacts

Each build creates:

- `{hostname}_{timestamp}_config.txt` — paste-ready NX-OS CLI
- `{hostname}_{timestamp}_diff.txt` — diff vs empty baseline
- `{hostname}_{timestamp}_risk.txt` — command risk assessment

## Stop the program

Click **Stop Program** in the UI or close the console window.

## v6.14.0 New Features

### Multi-Switch Deployment
- **Automatic Port Configuration**: Leaf switches automatically configure uplink ports based on model type
  - 1GB leaf (Nexus 9348GC-FXP): Uplinks on ports 51-52
  - 10GB leaf (Nexus 93180YC-EX): Uplinks on ports 53-54
- **Core Downlink Logic**: Core switches automatically configure downlinks for mixed 10GB/1GB deployments
  - 10GB leaf downlinks: Ports 1-10
  - 1GB leaf downlinks: Ports 11-20

### Keepalive IP Management
- **Auto-Generation**: "Use default keepalive IP for vPC" checkbox generates IPs based on domain ID
- **Validation**: Ensures keepalive IPs are present, valid, and unique within each vPC domain (IPs can be reused across different vPC domains per Cisco NX-OS behavior)
- **Manual Override**: Option to specify custom keepalive IPs when needed
