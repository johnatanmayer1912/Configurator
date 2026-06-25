# Cisco Nexus Configurator - Advanced v5 Documentation (v2.0.0)

## 1. Overview
The **Cisco Nexus Configurator** is a production-grade automation system designed to unify and professionalize the generation of Cisco NX-OS configurations. It transitions from legacy script-based assembly to a modern, model-driven pipeline architecture.

---

## 2. Technical Stack
- **Language**: Python 3.x
- **GUI Framework**: `Tkinter` / `ttk`
- **Templating Engine**: **Jinja2** (Separates CLI syntax from business logic)
- **Data Modeling**: Python `dataclasses`
- **Logic Layers**:
  - `/core`: Engine, Validator, and Risk Analyzer.
  - `/models`: Structured data definitions.
  - `/pipelines`: Execution orchestration.
  - `/templates`: Jinja2 NX-OS blueprints.

---

## 3. Core Features

### 3.1 Model-Driven Configuration
Every user input is parsed into a structured `Device` model before processing, ensuring type-safety and logical consistency across all features.

### 3.2 Automated Validation Engine
The system intercepts the data model before rendering to check for:
- Duplicate VLAN IDs.
- Invalid IP address formats (using `ipaddress` library).
- Interface name collisions and invalid port modes.

### 3.3 Security & Risk Audit
The **Risk Analyzer** unit scans every generated configuration for high-impact commands:
- **Critical**: `vpc domain` changes, `reboot/reload`.
- **High**: `shutdown`, `spanning-tree` modifications.
- Produces a timestamped audit trail for every run.

### 3.4 Configuration Build Pipeline
A centralized execution flow that automates:
1. **Validation** → 2. **Rendering** → 3. **Diffing** → 4. **Risk Assessment** → 5. **Artifact Storage**.

### 3.5 Intent-to-Config Blueprint Engine
The system now includes an intent layer for institutional-scale provisioning:
- **Intent Inputs**: Site, role, redundancy, security tier, and controlled overrides.
- **Blueprint Profiles**: Access, Leaf, and Spine profile synthesis with deterministic defaults.
- **Intent Endpoints**:
  - `/intent/preview`: Pre-validation and compliance signal.
  - `/intent/generate`: Full artifact generation through the standard pipeline.
- **Intent Artifacts**: intent payload snapshot, blueprint summary, and policy flags archived with config outputs.

### 3.6 Dummy-Proof Operation Layer
- **Simple Wizard** enabled by default with preflight validation gates.
- **Advanced Mode** preserved for expert manual operations.
- **vPC Safety**: strict client preflight and backend guard checks prevent malformed vPC requests.
- **Execution Review**: payload preview panel displays the exact API request structure before validate/build.

### 3.7 UX Polish Layer
- **Stepper UX**: explicit stage visibility for guided operations.
- **Readiness Badges**: green/red status chips for global and section-level readiness.
- **Accessibility Upgrade**: larger controls and stronger visual hierarchy for rapid operator comprehension.

---

## 4. Supported Hardware Models

| Model | Port Density | vPC Peer-Link | vPC Keepalive |
| :--- | :--- | :--- | :--- |
| **N93180YC-EX** | 48x10/25G + 6x40/100G | Eth1/53-54 | Eth1/47-48 |
| **N9336C-FX2** | 36x40/100G QSFP28 | Eth1/35-36 | Eth1/33-34 |
| **N9348GC-FXP** | 48x1G + 4x10/25G + 2x40G | Eth1/53-54 | Eth1/47-48 |
| **Generic** | User Defined | Manual | Manual |

---

## 5. Artifacts & Storage

All generated data is organized into the `/dist` directory with unique timestamps:
- `[hostname]_config.txt`: The final executable CLI.
- `[hostname]_diff.txt`: Delta report showing the change baseline.
- `[hostname]_risk.txt`: Security and impact audit report.

---

## 6. Governance & Lifecycle
The project follows a strict engineering lifecycle:
- **Versioning**: Systematic semantic versioning (tracked in `VERSION`).
- **Auditability**: Comprehensive `CHANGELOG.md` for all architectural shifts.
- **Resilience**: Automated ZIP backups created before every major refactor.
- **Observability**: Centralized logging in `logs/system.log`.
- **Startup Forensics**: Bootstrap crash diagnostics in `logs/startup_bootstrap.log`.
