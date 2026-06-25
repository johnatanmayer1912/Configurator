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
