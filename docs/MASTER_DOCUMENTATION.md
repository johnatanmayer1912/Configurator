# NX-OS Configuration Authority — Master Documentation

**Version:** 3.0.0 (Configuration Studio Web)  
**Application:** NX-OS Configuration Authority  
**Platform:** Web UI + offline PyInstaller exe (`web_launcher.py`)

---

## v3.0 Documentation Index

| Document | Purpose |
|----------|---------|
| [00-START-HERE](00-START-HERE.md) | Quick start |
| [CONFIGURATION_STUDIO](01-user-manual/CONFIGURATION_STUDIO.md) | Split-screen wizard guide |
| [CONFIG_MATRIX](02-quick-reference/CONFIG_MATRIX.md) | Scenario × model matrix |
| [CORE_VPC_GUIDE](05-scenarios/CORE_VPC_GUIDE.md) | CORE1_VPC template mapping |
| [HARDWARE_PROFILES](HARDWARE_PROFILES.md) | Port layouts and speed tiers |

---

## Overview

The NX-OS Configuration Authority is a professional, offline desktop application for generating production-ready Cisco NX-OS CLI configurations for Nexus 9000-series switches. It targets Principal Network Automation Engineers and Senior Network Operators who provision Nexus 9300/9500 switches in enterprise and data-center environments.

The application operates **100% offline** — no internet connectivity, no browser, no external server process required.

---

## Architecture

### Module Structure

```
project_root/
├── gui_main.py                  # CTK application entry point
├── hardware_profiles.yaml       # YAML hardware profile definitions
├── requirements.txt             # Pinned Python dependencies
├── VERSION                      # Application version string
│
├── gui/                         # CTK GUI package
│   ├── main_app.py              # NXOSConfigApp — main window + sidebar + navigation
│   ├── app_state.py             # AppState — shared reactive application state
│   ├── hardware_loader.py       # HardwareLoader — YAML profile loader
│   ├── resource_path.py         # resource_path() — PyInstaller-aware asset resolver
│   ├── views/
│   │   ├── home_view.py         # HomeView — landing page
│   │   ├── hardware_view.py     # HardwareView — model selection + device identity
│   │   ├── vpc_view.py          # VPCView — vPC domain configuration
│   │   ├── interface_view.py    # InterfaceView — port config + VLAN management
│   │   └── export_view.py       # ExportView — preview + generate + history
│   └── widgets/
│       ├── validated_entry.py   # ValidatedEntry — entry with inline validation
│       ├── sidebar_button.py    # SidebarButton — nav button with status badge
│       ├── port_badge.py        # PortBadge — color-coded speed label
│       ├── preview_pane.py      # PreviewPane — read-only config display
│       └── vlan_table.py        # VLANTable — scrollable VLAN management table
│
├── core/                        # Backend business logic
│   ├── engine.py                # ConfigEngine — orchestrator
│   ├── renderer.py              # ConfigRenderer — Jinja2 template renderer
│   ├── validator.py             # DeviceValidator — validation engine
│   ├── risk_analyzer.py         # RiskAnalyzer — risk scoring
│   ├── compliance.py            # ComplianceEngine — compliance auditor
│   └── checkpoint_manager.py   # CheckpointManager — JSON snapshot manager
│
├── models/                      # Data model dataclasses
│   ├── device_model.py          # Device, VPCConfig
│   ├── interface_model.py       # Interface
│   ├── vlan_model.py            # VLAN
│   ├── l3_models.py             # SVI, StaticRoute, HSRPConfig
│   └── nexus_models.py          # NexusModel constants
│
├── pipelines/
│   └── build_pipeline.py        # ConfigurationPipeline — end-to-end export
│
├── templates/
│   └── nxos_base.j2             # Jinja2 NX-OS CLI template
│
└── utils/
    ├── range_parser.py          # expand_interface_range() utility
    ├── logger.py                # Logging setup
    └── build_ctk_exe.py         # PyInstaller build script
```

---

## Application Views

### 1. Home View (`gui/views/home_view.py`)

The default landing page displayed on launch. Shows:
- Application name, version, and description
- **Quick Start** panel with five numbered workflow steps and "Go →" navigation buttons
- **Configuration Status** cards for each section (Hardware, VPC, Interfaces, Export)
- **Global Readiness Indicator** — green "✓ Ready to Generate" or amber "⚠ Configuration Incomplete (N issues)"

All status indicators update reactively via `AppState.notify()`.

### 2. Hardware Setup View (`gui/views/hardware_view.py`)

Configures the switch model and device identity:
- **Model Selector** — CTkComboBox populated from `hardware_profiles.yaml`
- **vPC Pair Mode Toggle** — switches between standalone and dual-device identity panels
- **Standalone Identity Panel** — Hostname, Management IP (CIDR), Management Gateway, MOTD
- **Dual-Device Identity Panel** — Switch-A and Switch-B fields including Keepalive Source IPs
- **Admin Credentials** — Username and masked password fields
- **Hardware Summary** — Read-only display of port groups, speeds, and counts
- **Generic Mode Fields** — Manual 1G/10G/40G port count inputs (shown only for Generic model)

### 3. VPC Config View (`gui/views/vpc_view.py`)

Accessible only when vPC Pair Mode is enabled:
- **Domain Parameters** — Domain ID (1-1000), Peer-Keepalive VRF, Peer-Link Port-Channel ID
- **Port Assignments** — Auto-populated from hardware profile with Override toggle
- **vPC Intelligence Summary** — Switch-A priority (10), Switch-B priority (20), System priority (32667)
- **Keepalive Cross-Reference** — Visual confirmation of A→B and B→A keepalive mapping
- **Infrastructure Note** — Reminder that vPC ports are excluded from Interface Config

### 4. Interface Config View (`gui/views/interface_view.py`)

Two-panel layout for port configuration and VLAN management:

**Left Panel — Port Configuration:**
- **Port Range Selector** — Range input (e.g., `Eth1/1-24`) with "Apply to Range" button
- **Port List** — Scrollable list with checkboxes, speed badges, and interface names; excludes vPC reserved ports in vPC mode
- **Per-Interface Config Panel** — Mode (Access/Trunk/Routed), Access VLAN, Trunk VLAN List, Description, Shutdown toggle, vPC Member checkbox + ID
- **Apply to Selected** — Applies config panel values to all checked interfaces
- **Reset All Interfaces** — Restores all interfaces to defaults

**Right Panel — VLAN Management:**
- Add VLAN form with ID + Name inputs and inline validation
- Import from File (space-separated `VLAN_ID VLAN_NAME` format)
- Scrollable VLAN table with Delete buttons

### 5. Review & Export View (`gui/views/export_view.py`)

Two-column layout for preview and export:

**Left Column — Configuration Preview:**
- Single `PreviewPane` in standalone mode
- `CTkTabview` with "Switch-A Config" and "Switch-B Config" tabs in vPC mode
- Debounced 500ms refresh on any AppState change
- Syntax highlighting: comments (grey), interface lines (white bold), IPs (yellow), headers (cyan)
- Copy to Clipboard button and line/char count

**Right Column — Controls:**
- **Generate & Export** button — opens directory picker, runs full pipeline
- **Load Checkpoint** button — restores a prior Device snapshot
- **Audit Results** — Risk level + finding counts by severity, compliance error/warning counts
- **Configuration History** — Scrollable list of past exports; click to view in popup

---

## AppState Pattern

`AppState` (`gui/app_state.py`) is the single source of truth for all in-memory configuration. All views receive a reference to the same `AppState` instance.

### Reactive Updates

```python
# Register a callback (called in view __init__)
app_state.register_callback(self._on_state_change)

# Trigger all callbacks after any mutation
app_state.notify()
```

### Building Device Objects

```python
# Standalone mode
device = app_state.build_device_a()

# vPC mode
device_a = app_state.build_device_a()  # role="primary"
device_b = app_state.build_device_b()  # role="secondary", swapped KPA IPs
```

Both methods raise `ValueError(field_name)` if a required field is empty.

### Section Status

```python
app_state.section_status = {
    "hardware": "ok" | "error" | "pending",
    "vpc":      "ok" | "error" | "pending",
    "interfaces": "ok" | "error" | "pending",
    "export":   "ok" | "error" | "pending",
}
```

---

## Hardware Profile YAML Schema

`hardware_profiles.yaml` defines port layouts and vPC port assignments per model:

```yaml
profiles:
  - name: "Nexus 93180YC-EX"
    total_ports: 54
    port_groups:
      - speed: "10/25G"
        start: 1
        end: 48
        type: "SFP+"
      - speed: "40/100G"
        start: 49
        end: 54
        type: "QSFP28"
    vpc_peer_link:
      - "Ethernet1/53"
      - "Ethernet1/54"
    vpc_keepalive:
      - "Ethernet1/47"
      - "Ethernet1/48"
```

If the YAML file is missing at startup, `HardwareLoader` falls back to hardcoded `NexusModel` constants and displays a warning.

---

## PyInstaller Packaging

Build a single-file Windows executable:

```bash
python utils/build_ctk_exe.py
```

This runs:
```
pyinstaller --onefile --windowed --name NXOSConfigAuthority
  --collect-all customtkinter
  --collect-all jinja2
  --add-data "templates;templates"
  --add-data "hardware_profiles.yaml;."
  --add-data "VERSION;."
  gui_main.py
```

Output: `dist/NXOSConfigAuthority.exe`

The application uses `resource_path()` (`gui/resource_path.py`) to locate bundled assets at runtime, checking `sys._MEIPASS` first (frozen) then falling back to the project root (source).

Runtime output files (configs, logs, checkpoints) are written relative to the executable's directory, not `sys._MEIPASS`, so they persist after the process exits.

---

## Running from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the CTK desktop application
python gui_main.py

# Launch the legacy web interface (unchanged)
python web_launcher.py
```

---

## Legacy Web Interface

The web-based interface (`web_launcher.py`, `api/main.py`) remains fully functional and independent of the CTK desktop application. The GUI layer does not import from `api/` or `web_launcher.py`.

The web interface provides the same configuration generation capabilities via a browser-based UI using Flask/FastAPI. Refer to the original web documentation for usage details.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| customtkinter | 5.2.2 | Dark-mode CTK GUI framework |
| jinja2 | 3.1.4 | NX-OS CLI template rendering |
| pyyaml | 6.0.2 | Hardware profile YAML parsing |
| Pillow | 10.3.0 | Image support for CTK |
| darkdetect | 0.8.0 | OS dark mode detection |
| packaging | 24.0 | Version string utilities |
