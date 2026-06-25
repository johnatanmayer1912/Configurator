# Requirements Document

## Introduction

This document defines the requirements for a complete architectural redesign and rebuild of the
Cisco NX-OS Configuration Authority System as a world-class, production-ready **offline desktop
application**. The new application replaces the existing Tkinter/web-based hybrid (v2.0.1) with a
pure **CustomTkinter** GUI (dark mode, Modern Windows aesthetic), retaining and elevating all
existing backend logic (Jinja2 rendering, model-driven validation, risk analysis, compliance
engine, vPC intelligence, and the full build pipeline) while delivering a dramatically superior
operator experience.

The application targets **Principal Network Automation Engineers** and **Senior Network
Operators** who provision Cisco Nexus 9000-series switches (9300/9500 families) in enterprise
and data-center environments. It must operate **100% offline** — no internet connectivity, no
external API calls, no browser dependency.

---

## Glossary

- **Application**: The CustomTkinter desktop application being built (the subject of these requirements).
- **CTK**: CustomTkinter — the Python GUI framework used for the dark-mode desktop UI.
- **ConfigEngine**: The existing `core/engine.py` orchestrator that validates and renders device configurations.
- **ConfigRenderer**: The existing `core/renderer.py` Jinja2-based template renderer.
- **DeviceValidator**: The existing `core/validator.py` validation engine.
- **RiskAnalyzer**: The existing `core/risk_analyzer.py` risk-scoring engine.
- **ComplianceEngine**: The existing `core/compliance.py` institutional compliance auditor.
- **BuildPipeline**: The existing `pipelines/build_pipeline.py` end-to-end orchestration pipeline.
- **Device**: The `models/device_model.py` dataclass representing a single switch's full configuration state.
- **VPCConfig**: The `models/device_model.py` dataclass representing vPC domain parameters.
- **Interface**: The `models/interface_model.py` dataclass representing a single switchport.
- **VLAN**: The `models/vlan_model.py` dataclass representing a VLAN definition.
- **SVI**: The `models/l3_models.py` dataclass representing a Layer 3 Switch Virtual Interface.
- **NexusModel**: The `models/nexus_models.py` constants defining supported hardware profiles.
- **Hardware_Profile**: A YAML-defined data structure encoding port counts, speeds, and vPC port assignments per Nexus model.
- **Sidebar**: The left-side navigation panel in the CTK application.
- **Preview_Pane**: The real-time scrolling text widget displaying the rendered NX-OS CLI configuration.
- **Wizard**: The guided, multi-step configuration workflow presented in the main content area.
- **vPC_Pair**: A redundant pair of Nexus switches configured with Cisco Virtual Port Channel.
- **Peer_Link**: The inter-switch link carrying vPC traffic, typically a port-channel.
- **Peer_Keepalive**: The out-of-band management-plane link used for vPC heartbeat.
- **CIDR**: Classless Inter-Domain Routing notation (e.g., `192.168.1.1/24`).
- **Artifact**: A generated output file (config `.txt`, diff `.txt`, risk `.txt`).
- **PyInstaller**: The tool used to bundle the application into a single `.exe` for offline distribution.
- **MEIPASS**: The PyInstaller runtime extraction path used to locate bundled templates.
- **Jinja2**: The Python templating engine used to render NX-OS CLI from structured data.
- **YAML**: The data serialization format used for Hardware_Profile definitions.
- **Trunk_VLAN_List**: A comma-separated or range-notation list of VLANs allowed on a trunk port.
- **Access_VLAN**: The single VLAN assigned to an access-mode switchport.
- **Port_Range**: A contiguous or non-contiguous set of interface identifiers (e.g., `Eth1/1-24, Eth1/49`).
- **Validation_Error**: A structured error produced by DeviceValidator when input data violates rules.
- **Risk_Finding**: A structured finding produced by RiskAnalyzer categorized as CRITICAL, HIGH, MEDIUM, or LOW.
- **Compliance_Finding**: A structured finding produced by ComplianceEngine categorized as error or warning.
- **Checkpoint**: A JSON snapshot of a Device model saved before a build, enabling rollback.
- **Export**: The act of writing one or more Artifact files to a user-selected directory.

---

## Requirements

### Requirement 1: Application Framework and Visual Identity

**User Story:** As a network engineer, I want a professional dark-mode desktop application, so
that I can work comfortably in data-center environments and present a credible tool to my team.

#### Acceptance Criteria

1. THE Application SHALL use CustomTkinter as its sole GUI framework, with no Tkinter `ttk` or
   legacy `tk` widgets visible in the primary interface.
2. THE Application SHALL launch in dark mode by default, using CustomTkinter's `"dark"` appearance
   mode and the `"blue"` color theme.
3. THE Application SHALL display a minimum window size of 1280×800 pixels and SHALL be resizable.
4. THE Application SHALL display the title `"NX-OS Configuration Authority"` and the current
   version string (read from the `VERSION` file) in the window title bar.
5. THE Application SHALL render a persistent left-side Sidebar containing navigation entries for:
   Home, Hardware Setup, VPC Config, Interface Config, Review & Export.
6. WHEN a Sidebar navigation entry is selected, THE Application SHALL display the corresponding
   content panel in the main area without restarting or re-initializing the application state.
7. THE Application SHALL display a header bar at the top of the main content area showing the
   active section name and a build/version badge.
8. THE Application SHALL use consistent typography: `"Segoe UI"` or `"Roboto"` font family,
   minimum 13pt for body text, minimum 16pt for section headings.
9. THE Application SHALL be fully functional without any internet connection, browser, or
   external server process.

---

### Requirement 2: YAML-Based Hardware Profile System

**User Story:** As a network engineer, I want the application to know the exact port layout of
my Nexus hardware model, so that I cannot accidentally configure a port that does not exist on
my switch.

#### Acceptance Criteria

1. THE Application SHALL load hardware profiles from a `hardware_profiles.yaml` file at startup,
   defining for each supported model: model name, total port count, port groups (speed, start
   index, end index), vPC peer-link port list, and vPC keepalive port list.
2. THE Hardware_Profile YAML SHALL define profiles for at minimum: `Nexus 93180YC-EX`,
   `Nexus 9336C-FX2`, `Nexus 9348GC-FXP`, and `Generic`.
3. WHEN the `Nexus 93180YC-EX` profile is loaded, THE Application SHALL recognize ports
   `Ethernet1/1–48` as 10/25G SFP+, ports `Ethernet1/49–54` as 40/100G QSFP28, vPC peer-link
   ports as `Ethernet1/53–54`, and vPC keepalive ports as `Ethernet1/47–48`.
4. WHEN the `Nexus 9336C-FX2` profile is loaded, THE Application SHALL recognize all 36 ports
   (`Ethernet1/1–36`) as 40/100G QSFP28, vPC peer-link ports as `Ethernet1/35–36`, and vPC
   keepalive ports as `Ethernet1/33–34`.
5. WHEN the `Nexus 9348GC-FXP` profile is loaded, THE Application SHALL recognize ports
   `Ethernet1/1–48` as 1G Base-T, ports `Ethernet1/49–52` as 10/25G SFP28, ports
   `Ethernet1/53–54` as 40/100G QSFP28, vPC peer-link ports as `Ethernet1/53–54`, and vPC
   keepalive ports as `Ethernet1/47–48`.
6. WHEN the `Generic` profile is selected, THE Application SHALL allow the operator to manually
   specify the count of 1G, 10G, and 40G ports via numeric input fields.
7. IF the `hardware_profiles.yaml` file is not found at startup, THEN THE Application SHALL fall
   back to the hardcoded `NexusModel` constants in `models/nexus_models.py` and SHALL display a
   non-blocking warning banner indicating the YAML file was not found.
8. WHERE PyInstaller bundling is used, THE Application SHALL locate `hardware_profiles.yaml`
   using `sys._MEIPASS` when running as a frozen executable, and SHALL fall back to the
   source-relative path when running from source.

---

### Requirement 3: Home Screen

**User Story:** As a network engineer, I want a clear home screen that orients me to the
application's capabilities and current state, so that I can quickly understand what to do next.

#### Acceptance Criteria

1. THE Application SHALL display a Home screen as the default view on launch.
2. THE Home screen SHALL display the application name, version, and a one-line description of
   the application's purpose.
3. THE Home screen SHALL display a "Quick Start" section listing the five workflow steps in
   order: Hardware Setup → VPC Config → Interface Config → Review & Export.
4. THE Home screen SHALL display a status summary showing whether each section has been
   configured (complete / pending), updated in real time as the operator fills in data.
5. WHEN all required fields across all sections are populated and valid, THE Home screen SHALL
   display a global "Ready to Generate" indicator in green.
6. WHEN one or more required fields are missing or invalid, THE Home screen SHALL display a
   "Configuration Incomplete" indicator in amber/yellow with a count of outstanding issues.

---

### Requirement 4: Hardware Setup Section

**User Story:** As a network engineer, I want to select my switch model and deployment mode in
one place, so that all subsequent sections automatically adapt to my hardware.

#### Acceptance Criteria

1. THE Hardware_Setup section SHALL provide a dropdown (CTK `CTkComboBox`) for selecting the
   switch model, populated from the loaded Hardware_Profile YAML.
2. THE Hardware_Setup section SHALL provide a toggle switch (CTK `CTkSwitch`) labeled
   `"vPC Pair Mode"` to switch between Standalone and vPC Pair deployment.
3. WHEN `"vPC Pair Mode"` is disabled, THE Application SHALL display a single set of device
   identity fields: Hostname, Management IP (CIDR), Management Gateway, MOTD.
4. WHEN `"vPC Pair Mode"` is enabled, THE Application SHALL display two parallel sets of device
   identity fields: one for Switch-A (Primary) and one for Switch-B (Secondary), each containing
   Hostname, Management IP (CIDR), Management Gateway, and Keepalive Source IP.
5. THE Hardware_Setup section SHALL display a read-only hardware summary panel showing the
   selected model's port groups, speeds, and total port count, sourced from the Hardware_Profile.
6. WHEN the `Generic` model is selected, THE Hardware_Setup section SHALL display editable
   numeric fields for 1G port count, 10G port count, and 40G port count.
7. WHEN a non-Generic model is selected, THE Hardware_Setup section SHALL hide the manual port
   count fields and display the model's fixed port layout from the Hardware_Profile.
8. THE Hardware_Setup section SHALL provide a field for Admin Username and a masked field for
   Admin Password, both required before generation is permitted.

---

### Requirement 5: Input Validation with Visual Feedback

**User Story:** As a network engineer, I want the application to immediately flag invalid inputs
with visual cues, so that I catch mistakes before generating a configuration.

#### Acceptance Criteria

1. WHEN an IP address field loses focus and the entered value does not conform to CIDR notation
   (e.g., `x.x.x.x/prefix`), THE Application SHALL highlight the field border in red and display
   an inline error label beneath the field stating `"Invalid IP — use CIDR format (e.g., 10.0.0.1/24)"`.
2. WHEN an IP address field loses focus and the entered value is a valid CIDR address, THE
   Application SHALL display the field border in the default theme color and remove any error label.
3. WHEN a Hostname field loses focus and the entered value contains characters other than letters,
   digits, and hyphens, THE Application SHALL highlight the field border in red and display an
   inline error label stating `"Invalid hostname — letters, digits, and hyphens only"`.
4. WHEN a VLAN ID field contains a value outside the range 1–4093 or within the NX-OS reserved
   range 3968–4047, THE Application SHALL highlight the field border in red and display an inline
   error label stating the specific violation.
5. WHEN a port number is entered manually (Generic mode) and the value is zero or negative, THE
   Application SHALL highlight the field border in red and display an inline error label.
6. THE Application SHALL prevent the "Generate Configuration" action from executing if any
   validation error indicators are currently active on any section.
7. WHEN all fields on a section are valid and complete, THE Application SHALL display a green
   checkmark badge on the corresponding Sidebar navigation entry.
8. WHEN a section contains one or more validation errors, THE Application SHALL display a red
   warning badge on the corresponding Sidebar navigation entry.

---

### Requirement 6: VPC Config Section

**User Story:** As a network engineer, I want a dedicated vPC configuration section that
auto-populates intelligent defaults and hides complexity I don't need, so that I can configure
a vPC pair correctly without memorizing every parameter.

#### Acceptance Criteria

1. THE VPC_Config section SHALL be accessible from the Sidebar only when `"vPC Pair Mode"` is
   enabled in Hardware Setup; WHEN `"vPC Pair Mode"` is disabled, THE Sidebar SHALL display the
   VPC Config entry as dimmed/disabled.
2. THE VPC_Config section SHALL provide fields for: vPC Domain ID (integer 1–1000), Peer-Keepalive
   VRF (default: `management`), and Peer-Link Port-Channel ID (default: `1`).
3. WHEN a hardware model with known vPC ports is selected, THE VPC_Config section SHALL
   auto-populate the Peer-Link member interfaces and Keepalive member interfaces from the
   Hardware_Profile, displaying them as read-only with an "Override" toggle.
4. WHEN the "Override" toggle is enabled for vPC port assignments, THE VPC_Config section SHALL
   display editable text fields for Peer-Link interfaces and Keepalive interfaces.
5. THE VPC_Config section SHALL display a "vPC Intelligence Summary" panel showing: computed
   Switch-A priority (10), computed Switch-B priority (20), system-priority value (32667),
   peer-keepalive source/destination cross-mapping, and peer-link port-channel ID.
6. WHEN the Keepalive Source IP for Switch-A and the Keepalive Source IP for Switch-B are both
   populated, THE VPC_Config section SHALL display a visual cross-reference confirming:
   Switch-A local → Switch-B remote, Switch-B local → Switch-A remote.
7. IF the vPC Domain ID field contains a value outside the range 1–1000, THEN THE Application
   SHALL display an inline validation error on that field.
8. THE VPC_Config section SHALL display a note: `"vPC peer-link and keepalive ports are excluded
   from the Interface Config wizard automatically"`.

---

### Requirement 7: Interface Config Section

**User Story:** As a network engineer, I want a dynamic interface wizard that shows me only the
ports available on my hardware and lets me configure them in bulk, so that I can set up dozens
of ports quickly without errors.

#### Acceptance Criteria

1. THE Interface_Config section SHALL display a scrollable list of all available interfaces for
   the selected hardware model, excluding ports reserved for vPC peer-link and keepalive when
   vPC Pair Mode is enabled.
2. WHEN the `Generic` model is selected, THE Interface_Config section SHALL generate the
   interface list based on the 1G/10G/40G counts entered in Hardware Setup.
3. THE Interface_Config section SHALL allow the operator to select individual interfaces or
   define a Port_Range (e.g., `Eth1/1-24`) using a range input field with an "Apply to Range"
   button.
4. THE Interface_Config section SHALL provide per-interface (or per-range) configuration options:
   Mode (Access / Trunk / Routed), Access VLAN (shown when Mode = Access), Trunk VLAN List
   (shown when Mode = Trunk), Description, and Shutdown state toggle.
5. WHEN Mode is set to `"Trunk"`, THE Interface_Config section SHALL display a Trunk_VLAN_List
   field accepting comma-separated values and ranges (e.g., `10,20,30-50`).
6. WHEN Mode is set to `"Access"`, THE Interface_Config section SHALL display an Access_VLAN
   dropdown or numeric field populated from the VLANs defined in the VLAN configuration.
7. THE Interface_Config section SHALL provide a "vPC Member" checkbox per interface; WHEN
   checked, THE Application SHALL display a vPC ID numeric field for that interface.
8. WHEN a port number is selected that falls within the vPC peer-link or keepalive reserved
   range for the current model, THE Application SHALL display a warning label stating
   `"This port is reserved for vPC infrastructure"` and SHALL prevent assignment.
9. THE Interface_Config section SHALL display a port-speed badge next to each interface name,
   sourced from the Hardware_Profile (e.g., `10/25G`, `40/100G`, `1G`).
10. THE Interface_Config section SHALL provide a "Reset All Interfaces" button that restores all
    interfaces to their default state (mode: access, shutdown: true, no VLAN, no description).

---

### Requirement 8: VLAN Management

**User Story:** As a network engineer, I want to define VLANs in a structured way and have them
available throughout the interface wizard, so that I don't have to type VLAN IDs repeatedly.

#### Acceptance Criteria

1. THE Application SHALL provide a VLAN management panel (accessible from the Interface Config
   section or as a sub-panel) where the operator can add, edit, and remove VLAN entries.
2. EACH VLAN entry SHALL contain: VLAN ID (integer 1–4093, excluding reserved range 3968–4047)
   and VLAN Name (alphanumeric with underscores, UPPER_CASE recommended).
3. THE Application SHALL allow bulk VLAN import from a plain-text file where each line contains
   `VLAN_ID VLAN_NAME` (space-separated).
4. WHEN a VLAN ID is entered that duplicates an existing entry, THE Application SHALL display an
   inline error and SHALL prevent the duplicate from being added.
5. WHEN a VLAN ID falls within the NX-OS reserved range 3968–4047 or equals 4094, THE
   Application SHALL display an inline error and SHALL prevent the entry from being added.
6. THE Application SHALL display the current VLAN list in a scrollable table showing ID and Name.
7. WHEN VLANs are defined, THE Application SHALL make the VLAN ID list available as selectable
   options in the Interface Config Access VLAN field.

---

### Requirement 9: Real-Time Preview Pane

**User Story:** As a network engineer, I want to see the exact NX-OS CLI that will be generated
as I fill in the form, so that I can catch logical errors before exporting.

#### Acceptance Criteria

1. THE Application SHALL display a Preview_Pane as a scrollable, read-only text widget in the
   Review & Export section showing the rendered NX-OS CLI configuration.
2. THE Preview_Pane SHALL update its content within 500 milliseconds of any change to device
   identity, VLAN, interface, or vPC configuration fields.
3. THE Preview_Pane SHALL use monospace font (`"Courier New"` or `"Consolas"`, minimum 11pt)
   with syntax-appropriate coloring: comments (`!` lines) in grey, section headers in cyan,
   interface names in white, IP addresses in yellow.
4. WHEN vPC Pair Mode is enabled, THE Preview_Pane SHALL provide two tabs: `"Switch-A Config"`
   and `"Switch-B Config"`, each showing the full rendered configuration for the respective device.
5. THE Preview_Pane SHALL display a character count and line count for the current configuration.
6. THE Preview_Pane SHALL provide a "Copy to Clipboard" button that copies the currently
   displayed configuration text to the system clipboard.
7. WHEN the configuration cannot be rendered due to missing required fields, THE Preview_Pane
   SHALL display a placeholder message: `"Complete required fields to preview configuration"`.
8. THE Preview_Pane SHALL render configurations using the existing `ConfigRenderer` and
   `nxos_base.j2` Jinja2 template, preserving all existing CLI standards.

---

### Requirement 10: Configuration Generation and Export

**User Story:** As a network engineer, I want to generate and save the final configuration files
with a single action, so that I have production-ready artifacts ready for deployment.

#### Acceptance Criteria

1. THE Review_Export section SHALL provide a "Generate & Export" button that executes the full
   BuildPipeline (validate → render → diff → risk → artifacts).
2. WHEN the "Generate & Export" button is clicked, THE Application SHALL open a native OS
   directory picker dialog allowing the operator to choose the export destination folder.
3. WHEN the BuildPipeline executes successfully, THE Application SHALL write the following
   Artifact files to the selected directory: `[hostname]_config.txt`, `[hostname]_diff.txt`,
   `[hostname]_risk.txt`.
4. WHEN vPC Pair Mode is enabled, THE Application SHALL generate and export separate Artifact
   sets for Switch-A and Switch-B in the same export directory.
5. WHEN the BuildPipeline completes successfully, THE Application SHALL display a success
   notification (CTK `CTkMessagebox` or inline banner) listing the exported file paths.
6. WHEN the BuildPipeline raises a Validation_Error, THE Application SHALL display a modal
   dialog listing all validation errors with clear field-level descriptions, and SHALL NOT write
   any Artifact files.
7. WHEN the BuildPipeline raises a Validation_Error for a vPC pair consistency check (domain ID
   mismatch, keepalive cross-check failure, VLAN mismatch), THE Application SHALL display the
   specific vPC consistency error in the modal dialog.
8. THE Review_Export section SHALL display the Risk_Finding summary (overall risk level and
   finding count by severity) after each successful generation, sourced from the RiskAnalyzer.
9. THE Review_Export section SHALL display the Compliance_Finding summary (error and warning
   counts) after each successful generation, sourced from the ComplianceEngine.
10. THE Application SHALL save a Checkpoint (JSON snapshot of the Device model) to
    `configs/checkpoints/` before each BuildPipeline execution.

---

### Requirement 11: Configuration History and Checkpoints

**User Story:** As a network engineer, I want to review previously generated configurations and
restore a prior state, so that I can recover from mistakes or reuse a known-good baseline.

#### Acceptance Criteria

1. THE Review_Export section SHALL display a scrollable history list showing previously generated
   Artifact sets, sourced from the `configs/history/` directory, ordered by timestamp descending.
2. WHEN a history entry is selected, THE Application SHALL display the contents of the
   corresponding `_config.txt` Artifact in a read-only text panel.
3. THE Application SHALL provide a "Load Checkpoint" button in the Review_Export section that
   opens a file picker filtered to `*.json` files in `configs/checkpoints/`.
4. WHEN a Checkpoint file is loaded, THE Application SHALL restore all Device model fields
   (hostname, IPs, VLANs, interfaces, vPC config) to the values stored in the Checkpoint.
5. WHEN a Checkpoint is loaded successfully, THE Application SHALL navigate to the Hardware
   Setup section and refresh all form fields to reflect the restored state.
6. IF a Checkpoint file is malformed or missing required fields, THEN THE Application SHALL
   display an error dialog stating `"Checkpoint file is invalid or incompatible"` and SHALL
   leave the current application state unchanged.

---

### Requirement 12: Jinja2 Template Engine Integration

**User Story:** As a network engineer and developer, I want the CLI generation to be driven by
Jinja2 templates so that CLI syntax is fully separated from application logic and templates can
be updated without modifying Python code.

#### Acceptance Criteria

1. THE Application SHALL use the existing `ConfigRenderer` class (`core/renderer.py`) for all
   configuration rendering, with no inline string concatenation of CLI commands in the GUI layer.
2. THE Application SHALL locate Jinja2 templates using `sys._MEIPASS` when running as a
   PyInstaller frozen executable, and SHALL fall back to the source-relative `templates/`
   directory when running from source.
3. THE `nxos_base.j2` template SHALL render the following NX-OS CLI sections in order:
   banner/header comment block, hostname, MOTD banner, admin credentials, feature declarations
   (`feature interface-vlan`, `feature hsrp`, `feature lacp`, `feature vpc`, `feature lldp`),
   VLAN block, vPC domain block (conditional), SVI block (conditional), interface block,
   management interface and VRF, static routes (conditional).
4. THE `nxos_base.j2` template SHALL use professional Cisco CLI standards: `spanning-tree port
   type edge` on access ports, `spanning-tree port type network` on peer-link port-channels,
   `no ip redirects` on routed SVIs, `ip arp synchronize` in the vPC domain block.
5. THE Application SHALL support rendering separate Jinja2 templates for modular CLI sections
   (e.g., `vpc_domain.j2`, `interfaces.j2`) if the template directory contains them, falling
   back to `nxos_base.j2` if modular templates are absent.
6. WHEN a template rendering error occurs (e.g., undefined variable, syntax error), THE
   Application SHALL catch the Jinja2 exception and display a descriptive error message in the
   Preview_Pane and in a modal dialog, without crashing the application.

---

### Requirement 13: Offline Portability and PyInstaller Packaging

**User Story:** As a network engineer, I want a single `.exe` file that runs on any Windows
machine without installing Python or any dependencies, so that I can use the tool on air-gapped
lab and production networks.

#### Acceptance Criteria

1. THE Application SHALL be packageable into a single-file Windows executable using PyInstaller
   with the `--onefile` flag.
2. THE PyInstaller build SHALL embed the `templates/` directory using `--add-data
   "templates;templates"` so that Jinja2 templates are available at runtime inside the bundle.
3. THE PyInstaller build SHALL embed the `hardware_profiles.yaml` file using `--add-data
   "hardware_profiles.yaml;."` so that hardware profiles are available at runtime.
4. THE PyInstaller build SHALL include `--collect-all customtkinter` to ensure all CTK theme
   assets and fonts are bundled.
5. THE PyInstaller build SHALL include `--collect-all jinja2` and `--collect-all yaml` to
   ensure all templating and YAML parsing dependencies are bundled.
6. THE Application SHALL write all runtime output files (configs, logs, checkpoints) to paths
   relative to the executable's directory (not to `sys._MEIPASS`), ensuring output persists
   after the process exits.
7. THE Application SHALL read the `VERSION` file at startup; WHERE PyInstaller bundling is used,
   THE Application SHALL locate `VERSION` using `sys._MEIPASS` first, then fall back to the
   source-relative path.
8. THE `requirements.txt` SHALL specify pinned versions for: `customtkinter`, `jinja2`,
   `pyyaml`, and all transitive dependencies required for offline installation.

---

### Requirement 14: Modular Code Architecture

**User Story:** As a senior developer maintaining this codebase, I want the application split
into clearly separated modules so that GUI, business logic, and templates can be modified
independently.

#### Acceptance Criteria

1. THE Application SHALL be structured with the following top-level modules: `gui/main_app.py`
   (CTK application shell and Sidebar), `gui/views/` (one file per Sidebar section),
   `gui/widgets/` (reusable CTK widget components), `engine.py` (re-exported facade over
   existing `core/` modules), `templates/` (Jinja2 `.j2` files), `hardware_profiles.yaml`
   (YAML hardware definitions).
2. THE GUI layer SHALL NOT import from `api/` or `web_launcher.py`; the web interface and
   desktop interface SHALL remain independently executable.
3. THE Application SHALL preserve all existing `core/`, `models/`, `modules/`, `pipelines/`,
   and `utils/` modules without breaking changes, so that the web API and legacy Tkinter GUI
   remain functional.
4. EACH view module in `gui/views/` SHALL expose a single CTK frame class that accepts the
   shared application state object as a constructor argument.
5. THE Application SHALL use a shared `AppState` object (plain Python dataclass or class) to
   hold all in-memory configuration data, passed by reference to all view frames, so that
   changes in one view are immediately visible to all other views.
6. THE Application SHALL use Python's `logging` module via the existing `utils/logger.py` for
   all diagnostic output, with log level configurable via an environment variable
   `NXOS_LOG_LEVEL` (default: `INFO`).

---

### Requirement 15: Documentation and Rebuild Guide

**User Story:** As a librarian-minded engineer, I want comprehensive documentation that allows
any qualified engineer to rebuild the application from scratch, so that the project is not
dependent on any single person's knowledge.

#### Acceptance Criteria

1. THE Application SHALL include a `docs/` directory containing at minimum: `MASTER_DOCUMENTATION.md`
   (updated for the CTK redesign), `ARCHITECTURE.md` (module map, data flow diagram in ASCII,
   dependency graph), `REBUILD_GUIDE.md` (step-by-step instructions to recreate the application
   from zero), `PROMPTS.md` (master prompts and sub-prompts used to generate each module, for
   AI-assisted reconstruction), and `HARDWARE_PROFILES.md` (reference for all supported Nexus
   models, port layouts, and vPC assignments).
2. THE `REBUILD_GUIDE.md` SHALL include: environment setup (Python version, pip install
   commands), directory structure listing, module creation order, PyInstaller build command,
   and verification steps.
3. THE `ARCHITECTURE.md` SHALL include an ASCII data-flow diagram showing: User Input → AppState
   → ConfigEngine → ConfigRenderer → Jinja2 Template → CLI Output → BuildPipeline → Artifacts.
4. THE `PROMPTS.md` SHALL contain the original feature request verbatim, plus decomposed
   sub-prompts for each major module (GUI shell, Hardware Profile loader, vPC Intelligence,
   Interface Wizard, Preview Pane, Export pipeline).
5. THE `HARDWARE_PROFILES.md` SHALL contain a table for each supported model listing: model
   name, port groups with speed and index range, vPC peer-link ports, vPC keepalive ports, and
   recommended use case.
6. ALL documentation files SHALL be written in Markdown and SHALL be renderable by standard
   Markdown viewers without custom plugins.
