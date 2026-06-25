# NX-OS Configuration Authority — Rebuild Guide

This guide walks through recreating the application from scratch on a clean machine.

---

## Prerequisites

### 1. Install Python 3.11

Download from https://www.python.org/downloads/release/python-3110/

- Select **Windows installer (64-bit)**
- Check **"Add Python to PATH"** during installation
- Verify: `python --version` → `Python 3.11.x`

### 2. Install Git (optional, for version control)

Download from https://git-scm.com/

---

## Step 1: Create Project Directory

```
mkdir NXOSConfigAuthority
cd NXOSConfigAuthority
```

---

## Step 2: Create Directory Structure

Create these directories in order:

```
mkdir core
mkdir models
mkdir modules
mkdir pipelines
mkdir templates
mkdir templates\web
mkdir utils
mkdir gui
mkdir gui\views
mkdir gui\widgets
mkdir configs
mkdir configs\history
mkdir configs\checkpoints
mkdir docs
mkdir scratch
```

---

## Step 3: Install Dependencies

Create `requirements.txt`:

```
customtkinter==5.2.2
jinja2==3.1.4
pyyaml==6.0.2
Pillow==10.3.0
darkdetect==0.8.0
packaging==24.0
```

Install:

```bash
pip install -r requirements.txt
```

---

## Step 4: Create Root Files

| File | Content |
|------|---------|
| `VERSION` | `2.0.1` |
| `hardware_profiles.yaml` | See `docs/HARDWARE_PROFILES.md` for full schema |

---

## Step 5: Create Model Dataclasses (models/)

Create in this order (each depends on the previous):

1. `models/__init__.py` — empty
2. `models/vlan_model.py` — `VLAN(id, name)` dataclass with validation
3. `models/l3_models.py` — `HSRPConfig`, `SVI`, `StaticRoute` dataclasses
4. `models/interface_model.py` — `Interface(name, mode, vlan, description, shutdown, vpc_id, trunk_vlans)` dataclass
5. `models/device_model.py` — `VPCConfig`, `Device` dataclasses (imports VLAN, Interface, SVI, StaticRoute)
6. `models/nexus_models.py` — `NexusModel` string constants

---

## Step 6: Create Core Backend (core/)

Create in this order:

1. `core/__init__.py` — empty
2. `core/renderer.py` — `ConfigRenderer` using Jinja2 `FileSystemLoader`
3. `core/validator.py` — `DeviceValidator` with IP, VLAN, interface, and vPC pair validation
4. `core/risk_analyzer.py` — `RiskAnalyzer` with pattern-based risk scoring
5. `core/compliance.py` — `ComplianceEngine` with VLAN naming and IP format checks
6. `core/checkpoint_manager.py` — `CheckpointManager` for JSON snapshot save/load
7. `core/engine.py` — `ConfigEngine` orchestrating renderer + validator

---

## Step 7: Create Utilities (utils/)

1. `utils/__init__.py` — empty
2. `utils/logger.py` — `get_logger(name)` using Python `logging` module
3. `utils/range_parser.py` — `expand_interface_range(range_str)` for NX-OS range notation

---

## Step 8: Create Pipeline (pipelines/)

1. `pipelines/__init__.py` — empty
2. `pipelines/build_pipeline.py` — `ConfigurationPipeline` with `execute(device, output_dir=None)`

---

## Step 9: Create Jinja2 Template (templates/)

1. `templates/nxos_base.j2` — Full NX-OS CLI template

Key sections in order:
- Header comment block
- `hostname`, `banner motd`, admin credentials
- Feature declarations (conditional: `feature vpc` only when `device.vpc is not none`)
- VLAN block
- vPC domain block (conditional)
- SVI block with `no ip redirects`, `no ip proxy-arp`
- Interface block with `spanning-tree port type edge` + storm-control for access ports
- Management interface with `no shutdown`
- Static routes

---

## Step 10: Create GUI Foundation (gui/)

Create in this order (dependencies must exist first):

1. `gui/__init__.py`
2. `gui/resource_path.py` — `resource_path(relative)` checking `sys._MEIPASS`
3. `gui/hardware_loader.py` — `HardwareLoader` loading YAML profiles
4. `gui/app_state.py` — `AppState` with all fields, callbacks, and `build_device_a/b()`

---

## Step 11: Create Widget Library (gui/widgets/)

1. `gui/widgets/__init__.py`
2. `gui/widgets/validated_entry.py` — `ValidatedEntry(CTkFrame)`
3. `gui/widgets/sidebar_button.py` — `SidebarButton(CTkFrame)`
4. `gui/widgets/port_badge.py` — `PortBadge(CTkLabel)`
5. `gui/widgets/preview_pane.py` — `PreviewPane(CTkFrame)`
6. `gui/widgets/vlan_table.py` — `VLANTable(CTkScrollableFrame)`

---

## Step 12: Create Views (gui/views/)

1. `gui/views/__init__.py`
2. `gui/views/home_view.py` — `HomeView(CTkScrollableFrame)`
3. `gui/views/hardware_view.py` — `HardwareView(CTkScrollableFrame)`
4. `gui/views/vpc_view.py` — `VPCView(CTkScrollableFrame)`
5. `gui/views/interface_view.py` — `InterfaceView(CTkFrame)`
6. `gui/views/export_view.py` — `ExportView(CTkFrame)`

---

## Step 13: Create Main App Shell (gui/)

1. `gui/main_app.py` — `NXOSConfigApp(CTk)` with sidebar, navigation, header bar

---

## Step 14: Create Entry Point

1. `gui_main.py` — instantiates AppState, HardwareLoader, NXOSConfigApp, all views; calls `mainloop()`

---

## Step 15: Verify from Source

```bash
python gui_main.py
```

Verification checklist:
- [ ] Application launches in dark mode at 1400×900
- [ ] Sidebar shows all five navigation entries
- [ ] Home view displays Quick Start steps and status cards
- [ ] Hardware Setup: model selector populates from YAML
- [ ] Hardware Setup: vPC toggle shows/hides dual-device panels
- [ ] VPC Config: disabled when vPC mode is off
- [ ] Interface Config: port list populates for selected model
- [ ] Interface Config: VLAN add/delete works with validation
- [ ] Review & Export: preview pane shows placeholder text
- [ ] Review & Export: preview updates after filling required fields
- [ ] Generate & Export: runs pipeline and writes artifacts

---

## Step 16: Build Standalone Executable

Install PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
python utils/build_ctk_exe.py
```

Output: `dist/NXOSConfigAuthority.exe`

Verification checklist:
- [ ] Executable launches without Python installed
- [ ] Hardware profiles load from bundled YAML
- [ ] Templates render correctly
- [ ] Export writes artifacts to selected directory
- [ ] Checkpoints save and load correctly

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'customtkinter'`**  
Run `pip install -r requirements.txt`

**`FileNotFoundError: hardware_profiles.yaml`**  
Ensure `hardware_profiles.yaml` is in the project root. The app will fall back to hardcoded profiles and show a warning.

**`Jinja2 TemplateNotFound: nxos_base.j2`**  
Ensure `templates/nxos_base.j2` exists. When running from source, the renderer looks in `templates/` relative to the project root.

**PyInstaller build fails with missing modules**  
Add `--hidden-import <module>` to the PyInstaller command in `utils/build_ctk_exe.py`.
