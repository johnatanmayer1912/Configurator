# Implementation Tasks

## Overview
Implementation plan for the NX-OS Configuration Authority — CustomTkinter desktop application redesign. Tasks are ordered by dependency: foundation first, then GUI shell, then views, then integration, then packaging and docs.

---

## Task 1: Project Foundation — Dependencies, Structure, and Hardware Profiles YAML

- [x] 1.1 Install and pin dependencies: create `requirements.txt` with `customtkinter==5.2.2`, `jinja2==3.1.4`, `pyyaml==6.0.2`, `Pillow==10.3.0`, `darkdetect==0.8.0`, `packaging==24.0`
- [x] 1.2 Create the `gui/` package directory structure: `gui/__init__.py`, `gui/views/__init__.py`, `gui/widgets/__init__.py`
- [x] 1.3 Create `hardware_profiles.yaml` at the project root with full profiles for `Nexus 93180YC-EX`, `Nexus 9336C-FX2`, `Nexus 9348GC-FXP`, and `Generic` — each entry must include `name`, `total_ports`, `port_groups` (speed/start/end/type), `vpc_peer_link`, and `vpc_keepalive`
- [x] 1.4 Create `gui/hardware_loader.py` — `HardwareLoader` class with `load()` method that reads `hardware_profiles.yaml` via `resource_path()` helper; falls back to hardcoded `NexusModel` constants if YAML is missing; exposes `get_profile(name)`, `get_all_names()`, `get_port_speed(name, port_index)`, `get_vpc_ports(name)`
- [x] 1.5 Create `gui/resource_path.py` — `resource_path(relative: str) -> str` helper that checks `sys._MEIPASS` first, then falls back to the project root; used by all modules that load bundled assets

---

## Task 2: AppState — Shared Application State

- [x] 2.1 Create `gui/app_state.py` — `AppState` class holding all in-memory configuration: model, vpc_mode, generic port counts, standalone device fields (hostname/mgmt_ip/mgmt_gw/motd/admin_user/admin_password), vPC Switch-A fields, vPC Switch-B fields, vpc_domain_id, vpc_kpa_vrf, vpc_peer_link_id, vpc_peer_link_ports, vpc_keepalive_ports, vpc_override_ports, vlans list, interfaces list
- [x] 2.2 Add `validation_errors: dict` and `section_status: dict` fields to `AppState` — section_status keys: `hardware`, `vpc`, `interfaces`, `export`; values: `"ok"`, `"error"`, `"pending"`
- [x] 2.3 Implement `AppState.register_callback(fn)` and `AppState.notify()` — all registered callbacks are called on `notify()`; views register on construction to receive reactive updates
- [x] 2.4 Implement `AppState.build_device_a() -> Device` and `AppState.build_device_b() -> Device` — assembles `Device` and `VPCConfig` dataclasses from current state; raises `ValueError` with field name if required fields are empty
- [x] 2.5 Write unit tests in `scratch/test_app_state.py` — verify `notify()` fires callbacks, `build_device_a()` returns correct `Device`, `build_device_b()` returns correct `VPCConfig` with swapped keepalive IPs

---

## Task 3: Reusable Widget Library

- [x] 3.1 Create `gui/widgets/validated_entry.py` — `ValidatedEntry(CTkFrame)` wrapping a `CTkEntry` + error `CTkLabel`; accepts `validator: Callable[[str], tuple[bool, str]]`; on `<FocusOut>` runs validator, sets `border_color="#e74c3c"` on fail / default on pass, shows/hides error label, calls `on_change(field_key, is_valid)` callback
- [x] 3.2 Create `gui/widgets/sidebar_button.py` — `SidebarButton(CTkFrame)` with a `CTkButton` and a small status badge `CTkLabel`; `set_status(status: str)` accepts `"ok"` (green ✓), `"error"` (red ✗), `"pending"` (grey ○), `"disabled"` (dimmed, non-clickable)
- [x] 3.3 Create `gui/widgets/port_badge.py` — `PortBadge(CTkLabel)` displaying port speed string (e.g., `10/25G`, `40/100G`, `1G`) with color-coded background: blue for 100G, teal for 25G, grey for 1G
- [x] 3.4 Create `gui/widgets/preview_pane.py` — `PreviewPane(CTkFrame)` containing a read-only `CTkTextbox` with monospace font (`Consolas 11pt`); `update_text(text: str)` applies syntax tags: `!` comment lines → grey, `interface` lines → white bold, IP addresses → yellow, section headers → cyan; includes "Copy to Clipboard" `CTkButton`; shows line/char count `CTkLabel`
- [x] 3.5 Create `gui/widgets/vlan_table.py` — `VLANTable(CTkScrollableFrame)` displaying VLAN rows (ID + Name + Delete button); `add_vlan(vlan: VLAN)`, `remove_vlan(vlan_id: int)`, `get_vlans() -> list[VLAN]`; emits `on_change` callback on any mutation

---

## Task 4: GUI Shell — Main Application Window and Sidebar

- [x] 4.1 Create `gui/main_app.py` — `NXOSConfigApp(CTk)` class; sets `appearance_mode="dark"`, `color_theme="blue"`, window title `"NX-OS Configuration Authority vX.X.X"`, minimum size `1280x800`; reads version from `VERSION` file via `resource_path()`
- [x] 4.2 Build the two-column layout in `main_app.py`: left sidebar frame (fixed 220px wide, dark background) and right content frame (fills remaining space); sidebar contains app logo/title label at top and five `SidebarButton` instances: Home, Hardware Setup, VPC Config, Interface Config, Review & Export
- [x] 4.3 Implement `main_app.py` navigation controller — `show_view(name: str)` method that hides all view frames and packs the selected one; `SidebarButton` commands call `show_view()`; default view on launch is `"home"`
- [x] 4.4 Wire `AppState` callbacks in `main_app.py` — on `AppState.notify()`: update all `SidebarButton` badges from `app_state.section_status`; disable/enable VPC Config sidebar button based on `app_state.vpc_mode`
- [x] 4.5 Add a top header bar inside the content frame — `CTkFrame` with section title `CTkLabel` (left) and version badge `CTkLabel` (right); `main_app.py` updates the title label text when `show_view()` is called

---

## Task 5: Home View

- [x] 5.1 Create `gui/views/home_view.py` — `HomeView(CTkScrollableFrame)` accepting `app_state: AppState`; displays app name (`NX-OS Configuration Authority`), version, and one-line description
- [x] 5.2 Add "Quick Start" workflow steps panel to `HomeView` — five numbered `CTkLabel` rows: `1. Hardware Setup → 2. VPC Config (optional) → 3. Interface Config → 4. VLAN Management → 5. Review & Export`; each row has a "Go →" `CTkButton` that calls `main_app.show_view()`
- [x] 5.3 Add section status summary to `HomeView` — four `CTkFrame` status cards (Hardware, VPC, Interfaces, Export); each card shows section name + status badge; registers `AppState` callback to refresh badges on every `notify()`
- [x] 5.4 Add global readiness indicator to `HomeView` — `CTkLabel` showing `"✓ Ready to Generate"` in green when all `section_status` values are `"ok"`, or `"⚠ Configuration Incomplete (N issues)"` in amber otherwise; updates via `AppState` callback

---

## Task 6: Hardware Setup View

- [x] 6.1 Create `gui/views/hardware_view.py` — `HardwareView(CTkScrollableFrame)` accepting `app_state: AppState` and `hardware_loader: HardwareLoader`
- [x] 6.2 Add model selector row — `CTkLabel` + `CTkComboBox` populated from `hardware_loader.get_all_names()`; on selection change: update `app_state.model`, call `app_state.notify()`, refresh hardware summary panel and interface list
- [x] 6.3 Add vPC Pair Mode toggle — `CTkSwitch` labeled `"vPC Pair Mode"`; on toggle: update `app_state.vpc_mode`, call `app_state.notify()`, show/hide standalone vs. dual-device identity panels
- [x] 6.4 Build standalone device identity panel — `CTkFrame` with `ValidatedEntry` widgets for: Hostname (hostname validator: alphanumeric + hyphens), Management IP (CIDR validator), Management Gateway (IP validator), MOTD (`CTkEntry`); each `ValidatedEntry` updates `app_state` field and calls `app_state.notify()` on valid change
- [x] 6.5 Build dual-device identity panel (vPC mode) — two side-by-side `CTkFrame` panels (Switch-A / Switch-B), each with `ValidatedEntry` for Hostname, Management IP, Management Gateway, Keepalive Source IP; shown only when `app_state.vpc_mode == True`
- [x] 6.6 Add Admin Credentials row — `CTkEntry` for username (default `admin`) and masked `CTkEntry` (show=`"*"`) for password; both update `app_state` fields on change
- [x] 6.7 Add hardware summary panel — read-only `CTkTextbox` (or `CTkFrame` with labels) showing port groups from `hardware_loader.get_profile(app_state.model)`: speed, port range, type, total count; updates when model changes
- [x] 6.8 Add Generic mode port count fields — three `CTkEntry` widgets for 1G / 10G / 40G counts; shown only when `app_state.model == "Generic"`; hidden for named models; validate that values are non-negative integers
- [x] 6.9 Implement `HardwareView._update_section_status()` — sets `app_state.section_status["hardware"]` to `"ok"` when hostname + mgmt_ip + mgmt_gw + admin_user are all valid and non-empty, `"error"` if any validation_errors active, `"pending"` otherwise; calls `app_state.notify()`

---

## Task 7: VPC Config View

- [x] 7.1 Create `gui/views/vpc_view.py` — `VPCView(CTkScrollableFrame)` accepting `app_state: AppState` and `hardware_loader: HardwareLoader`; registers `AppState` callback to refresh all fields when state changes
- [x] 7.2 Add vPC domain parameters row — `ValidatedEntry` for Domain ID (integer 1–1000), `CTkEntry` for Peer-Keepalive VRF (default `management`), `ValidatedEntry` for Peer-Link Port-Channel ID (integer 1–4096); all update `app_state` fields on change
- [x] 7.3 Add peer-link port assignment panel — read-only `CTkTextbox` showing `app_state.vpc_peer_link_ports` (auto-populated from `hardware_loader.get_vpc_ports(model)["peer_link"]`); `CTkSwitch` labeled `"Override"`; when override enabled, replace with editable `CTkEntry` (comma-separated port names)
- [x] 7.4 Add keepalive port assignment panel — same pattern as 7.3 but for `app_state.vpc_keepalive_ports` and `hardware_loader.get_vpc_ports(model)["keepalive"]`
- [x] 7.5 Build vPC Intelligence Summary panel — `CTkFrame` with a grid of read-only labels: Switch-A Priority = 10, Switch-B Priority = 20, System Priority = 32667, Peer-Link PO = `app_state.vpc_peer_link_id`; updates via `AppState` callback
- [x] 7.6 Add keepalive cross-reference display — two `CTkLabel` rows showing `"Switch-A {kpa_a} → Switch-B (remote)"` and `"Switch-B {kpa_b} → Switch-A (remote)"`; shown only when both KPA IPs are non-empty; updates via `AppState` callback
- [x] 7.7 Add infrastructure note label — static `CTkLabel` reading `"vPC peer-link and keepalive ports are excluded from the Interface Config wizard automatically"`
- [x] 7.8 Implement `VPCView._update_section_status()` — sets `app_state.section_status["vpc"]` to `"ok"` when domain_id valid + both KPA IPs valid + peer_link_ports non-empty; `"pending"` when vpc_mode is False; calls `app_state.notify()`

---

## Task 8: Interface Config View and VLAN Management

- [x] 8.1 Create `gui/views/interface_view.py` — `InterfaceView(CTkFrame)` accepting `app_state: AppState` and `hardware_loader: HardwareLoader`; split into left panel (port list) and right panel (VLAN management)
- [x] 8.2 Build port list panel — `CTkScrollableFrame` populated with one row per available interface; each row: `CTkCheckBox` (select), `PortBadge` (speed), interface name `CTkLabel`; excludes vPC reserved ports when `app_state.vpc_mode == True`; regenerates when model or vpc_mode changes via `AppState` callback
- [x] 8.3 Add port range selector — `CTkEntry` for range input (e.g., `Eth1/1-24`) + `CTkButton` "Apply to Range"; on click: calls `expand_interface_range()` from `utils/range_parser.py`, selects matching checkboxes in port list
- [x] 8.4 Build per-interface config panel — shown when one or more ports are selected; `CTkSegmentedButton` for Mode (Access / Trunk / Routed); Access VLAN `CTkComboBox` (populated from `app_state.vlans`, shown when mode=Access); Trunk VLAN List `CTkEntry` (shown when mode=Trunk); Description `CTkEntry`; Shutdown `CTkSwitch`; vPC Member `CTkCheckBox` + vPC ID `CTkEntry` (shown when checked)
- [x] 8.5 Add "Apply to Selected" `CTkButton` — applies current per-interface config panel values to all selected interfaces in `app_state.interfaces`; calls `app_state.notify()`
- [x] 8.6 Add "Reset All Interfaces" `CTkButton` — resets all `app_state.interfaces` to default (mode=access, shutdown=True, vlan=None, description=None, vpc_id=None); calls `app_state.notify()`
- [x] 8.7 Add reserved port warning — when a selected port is in `hardware_loader.get_vpc_ports(model)["peer_link"]` or `["keepalive"]`, display a `CTkLabel` warning `"This port is reserved for vPC infrastructure"` in the config panel and disable the Apply button for that port
- [x] 8.8 Build VLAN management panel (right side) — `CTkFrame` with: `CTkEntry` for VLAN ID + `CTkEntry` for VLAN Name + `CTkButton` "Add VLAN"; `VLANTable` widget below; `CTkButton` "Import from File" (opens file dialog, parses `VLAN_ID VLAN_NAME` lines); all mutations update `app_state.vlans` and call `app_state.notify()`
- [x] 8.9 Implement VLAN validation in the add-VLAN flow — reject duplicates (show inline `CTkLabel` error), reject IDs in range 3968–4047 or equal to 4094 (show specific error message), reject IDs outside 1–4093
- [x] 8.10 Implement `InterfaceView._update_section_status()` — sets `app_state.section_status["interfaces"]` to `"ok"` when `app_state.interfaces` is non-empty; `"pending"` otherwise; calls `app_state.notify()`

---

## Task 9: Review and Export View

- [x] 9.1 Create `gui/views/export_view.py` — `ExportView(CTkFrame)` accepting `app_state: AppState`; two-column layout: left = preview pane + tabs, right = export controls + history + audit results
- [x] 9.2 Integrate `PreviewPane` widget — in Standalone mode: single `PreviewPane`; in vPC mode: `CTkTabview` with tabs `"Switch-A Config"` and `"Switch-B Config"`, each containing a `PreviewPane`
- [x] 9.3 Implement debounced preview refresh — register `AppState` callback that sets a dirty flag; use `root.after(500, _refresh_preview)` to debounce; `_refresh_preview()` calls `AppState.build_device_a()` → `ConfigRenderer.render_device_config()` → `PreviewPane.update_text()`; on missing required fields, display placeholder `"Complete required fields to preview configuration"`; catch all Jinja2 exceptions and display error text in pane
- [x] 9.4 Add "Generate & Export" `CTkButton` — disabled when `len(app_state.validation_errors) > 0`; on click: opens `CTkFileDialog` (directory picker); calls `_run_export(output_dir)`
- [x] 9.5 Implement `_run_export(output_dir)` — builds Device objects from AppState; calls `DeviceValidator.validate()` (and `validate_vpc_pair()` for vPC mode); on validation failure: shows `CTkMessagebox` listing all errors, aborts; on pass: calls `CheckpointManager.save_checkpoint()`, then `ConfigurationPipeline.execute(device, output_dir=output_dir)` for each device; displays success banner with artifact file paths
- [x] 9.6 Add post-export audit results panel — after successful export: display `RiskAnalyzer` overall risk level + finding counts by severity (CRITICAL/HIGH/MEDIUM/LOW) in color-coded `CTkLabel` widgets; display `ComplianceEngine` error + warning counts
- [x] 9.7 Build configuration history panel — `CTkScrollableFrame` listing files from `configs/history/` ordered by timestamp descending; each row: filename `CTkButton`; on click: reads file content and displays in a read-only `CTkTextbox` popup or side panel
- [x] 9.8 Add "Load Checkpoint" `CTkButton` — opens file picker filtered to `*.json` in `configs/checkpoints/`; calls `CheckpointManager.load_checkpoint(path)`; maps loaded dict back to `AppState` fields; navigates to Hardware Setup view; on malformed file: shows error dialog `"Checkpoint file is invalid or incompatible"`

---

## Task 10: Jinja2 Template Enhancement

- [x] 10.1 Update `templates/nxos_base.j2` — add `spanning-tree port type edge` and `storm-control` defaults to access-mode interfaces; add `no ip redirects` and `no ip proxy-arp` to all SVI interfaces; add explicit `no shutdown` to `mgmt0`; add `no ip redirects` to routed interfaces
- [x] 10.2 Add `switchport trunk allowed vlan` rendering to `nxos_base.j2` — when `intf.trunk_vlans` is set, render `switchport trunk allowed vlan {intf.trunk_vlans}`; update `Interface` dataclass in `models/interface_model.py` to add `trunk_vlans: Optional[str] = None`
- [x] 10.3 Verify `nxos_base.j2` renders `feature` block correctly — ensure `feature vpc` is only rendered when `device.vpc` is not None; `feature hsrp` only when `device.svis` contains HSRP config; `feature interface-vlan` always present
- [x] 10.4 Test template rendering end-to-end — run `scratch/test_templates.py` with a fully populated `Device` object (standalone + vPC) and verify output matches expected NX-OS CLI structure; check for no undefined variable errors

---

## Task 11: ConfigurationPipeline Export Directory Override

- [x] 11.1 Update `pipelines/build_pipeline.py` — modify `ConfigurationPipeline.__init__()` to accept optional `output_dir` parameter; modify `execute()` to accept optional `output_dir` override that takes precedence over `self.output_dir`; ensures GUI-selected export directory is used without breaking existing API usage
- [x] 11.2 Verify backward compatibility — existing `api/main.py` and `main.py` (legacy Tkinter) still work with no changes; run `scratch/test_pipeline.py` to confirm

---

## Task 12: GUI Entry Point and PyInstaller Packaging

- [x] 12.1 Create `gui_main.py` at project root — entry point for the CTK application; calls `customtkinter.set_appearance_mode("dark")`, `customtkinter.set_default_color_theme("blue")`; instantiates `NXOSConfigApp` and calls `mainloop()`; guards with `if __name__ == "__main__"`
- [x] 12.2 Create `requirements.txt` at project root with pinned versions: `customtkinter==5.2.2`, `jinja2==3.1.4`, `pyyaml==6.0.2`, `Pillow==10.3.0`, `darkdetect==0.8.0`, `packaging==24.0`
- [x] 12.3 Create `utils/build_ctk_exe.py` — script that runs the PyInstaller command programmatically: `pyinstaller --onefile --windowed --name NXOSConfigAuthority --collect-all customtkinter --collect-all jinja2 --add-data "templates;templates" --add-data "hardware_profiles.yaml;." --add-data "VERSION;." gui_main.py`; prints build output path on success
- [x] 12.4 Verify PyInstaller bundle — run `utils/build_ctk_exe.py`; confirm `dist/NXOSConfigAuthority.exe` launches, loads hardware profiles, renders preview, and exports artifacts without Python installed

---

## Task 13: Documentation

- [x] 13.1 Update `docs/MASTER_DOCUMENTATION.md` — replace web-centric content with CTK desktop app description; document all five views, AppState pattern, hardware YAML schema, and PyInstaller packaging; preserve existing web API section under "Legacy Web Interface"
- [x] 13.2 Create `docs/ARCHITECTURE.md` — module map table (file → responsibility), ASCII data-flow diagram (User Input → AppState → ConfigRenderer → Jinja2 → CLI → Pipeline → Artifacts), dependency graph (gui/ depends on core/ + models/ + pipelines/; api/ is independent)
- [x] 13.3 Create `docs/REBUILD_GUIDE.md` — step-by-step from zero: Python 3.11 install, `pip install -r requirements.txt`, directory structure creation order, module creation sequence, PyInstaller build command, verification checklist
- [x] 13.4 Create `docs/PROMPTS.md` — original feature request verbatim, plus decomposed sub-prompts for each major module: GUI shell, AppState, HardwareLoader, ValidatedEntry widget, each view, PreviewPane, export pipeline, PyInstaller packaging
- [x] 13.5 Create `docs/HARDWARE_PROFILES.md` — reference table for all supported Nexus models: model name, port groups (speed/range/type), vPC peer-link ports, vPC keepalive ports, recommended use case (access/leaf/spine/generic)
