# NX-OS Configurator - Master Code Dictionary

**Generated:** 2026-07-09  
**Version:** 6.15.0  
**Purpose:** Complete codebase mapping for audit and remediation

---

## Project Structure Overview

```
Configurator - Copy/
├── api/                    # FastAPI backend endpoints
├── core/                   # Core business logic engines
├── data/                   # Configuration data & templates
├── static/                 # Frontend JavaScript & CSS
├── templates/              # Jinja2 templates for NX-OS configs
├── models/                 # Pydantic data models
├── utils/                  # Utility functions
├── gui/                    # Desktop GUI components
├── tests/                  # Test suite
├── docs/                   # Documentation
└── build/                  # Build artifacts
```

---

## Phase 1: File Inventory

### Python Files (41 total)

#### Entry Points
- `web_launcher.py` - Main web server launcher (uvicorn)
- `main.py` - Desktop GUI entry point
- `gui_main.py` - GUI application entry point

#### API Layer (api/)
- `api/main.py` - FastAPI application with all REST endpoints

#### Core Engines (core/)
- `core/engine.py` - Main configuration pipeline orchestrator
- `core/validator.py` - Device configuration validation
- `core/compliance.py` - NX-OS compliance checking
- `core/checkpoint_manager.py` - Configuration save/restore
- `core/intent_engine.py` - Intent-based configuration
- `core/catalog_loader.py` - Hardware/software catalog
- `core/scenario_engine.py` - Scenario template processing
- `core/renderer.py` - Jinja2 template rendering
- `core/import_wizard.py` - Config builder/paste functionality
- `core/config_remarks.py` - CLI comment generation
- `core/link_allocator.py` - Port allocation logic
- `core/po_map_store.py` - Port-channel mapping
- `core/cable_plan.py` - Physical cabling documentation
- `core/version_diff.py` - NX-OS version comparison
- `core/hostname_rules.py` - Hostname validation
- `core/device_enricher.py` - Device metadata enrichment
- `core/config_parser.py` - Running-config parsing
- `core/interface_customizer.py` - Interface customization
- `core/link_resolver.py` - Link resolution logic
- `core/manual_overrides.py` - Manual configuration overrides
- `core/vpc_topology.py` - vPC topology management
- `core/risk_analyzer.py` - Configuration risk analysis
- `core/cable_plan.py` - Cable plan generation
- `core/__init__.py` - Core module initialization

#### Models (models/)
- `models/device_model.py` - Device configuration models
- `models/vlan_model.py` - VLAN data models
- `models/interface_model.py` - Interface models
- `models/l3_models.py` - Layer 3 models (SVI, HSRP, routes)
- `models/intent_model.py` - Intent-based models

#### Utilities (utils/)
- `utils/web_logger.py` - Logging configuration
- `utils/version.py` - Version management
- `utils/change_package.py` - Build packaging
- `utils/app_dirs.py` - Cross-platform directory paths
- `utils/instance_control.py` - Port/PID management

#### GUI Components (gui/)
- `gui/main_app.py` - Main GUI application
- `gui/app_state.py` - GUI state management
- `gui/hardware_loader.py` - Hardware profile loading
- `gui/resource_path.py` - Resource path resolution
- `gui/views/` - View components (export, hardware, home, interface, vpc)
- `gui/widgets/` - Custom widgets (port badge, preview pane, sidebar button)

#### Modules (modules/)
- `modules/vpc_manager.py` - vPC management
- `modules/vlan_manager.py` - VLAN management
- `modules/__init__.py` - Module initialization

#### Build & Scripts
- `_prebuild.py` - Pre-build validation
- `build_exe.bat` - Windows executable build script

### JavaScript Files (12 total)

#### Frontend Logic (static/)
- `static/app.js` - Main application controller (3576 lines)
- `static/roadmap.js` - Wizard roadmap management
- `static/option-info.js` - Help text/option information
- `static/builder.js` - Config builder logic
- `static/config-studio.js` - Configuration studio
- `static/fabric-questionnaire.js` - Fabric wizard
- `static/interface-planner.js` - Interface planning
- `static/port-map-editor.js` - Port mapping UI
- `static/vpc-link-planner.js` - vPC link planning
- `static/wizard-enhancements.js` - Wizard enhancements
- `static/topology-view.js` - Topology visualization
- `static/admin-po-map.js` - Admin port-channel mapping

### Configuration Files (13 YAML)

#### Data Files (data/)
- `data/hardware_profiles.yaml` - Switch hardware specifications
- `data/nxos_versions.yaml` - NX-OS version catalog
- `data/feature_options.yaml` - Feature configuration options
- `data/config_matrix.yaml` - Configuration matrix
- `data/scenario_templates.yaml` - Scenario templates
- `data/interface_presets.yaml` - Interface presets
- `data/po_allocation_map.yaml` - Port-channel allocation
- `data/option_encyclopedia.yaml` - Option documentation
- `data/field_hints.yaml` - Field help text
- `data/placeholder_fields.yaml` - Placeholder field definitions
- `data/institutional_baseline.yaml` - Baseline configurations
- `data/release_qa_manifest.yaml` - QA manifest

#### Legacy
- `hardware_profiles.yaml` - Legacy hardware profiles (root level)

### Templates (2 Jinja2)

- `templates/nxos_base.j2` - Base NX-OS configuration template
- `templates/nxos_legacy.j2` - Legacy NX-OS template

### Web Templates (HTML)

- `templates/web/index.html` - Main web UI (779 lines)
- `templates/web/admin.html` - Admin interface

### Stylesheets (CSS)

- `static/styles.css` - Main application styles (2086 lines)
- `static/styles_backup.css` - Backup styles

---

## Phase 2: Variable & Function Dictionary

### Global Variables

#### api/main.py
```python
HISTORY_DIR = Path(get_history_dir())  # Configuration history directory
HOSTNAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$")  # Hostname validation regex
app = FastAPI(title="Configuration Authority System", version=get_app_version())
pipeline = ConfigurationPipeline()  # Main configuration pipeline
device_validator = DeviceValidator()  # Device validation instance
compliance = ComplianceEngine()  # Compliance checking engine
checkpoints = CheckpointManager()  # Checkpoint management
intent_engine = IntentEngine()  # Intent processing
catalog = CatalogLoader()  # Hardware/software catalog
scenario_engine = ScenarioEngine(catalog)  # Scenario processing
config_renderer = ConfigRenderer()  # Template rendering
config_builder = ConfigBuilderEngine(catalog)  # Config builder
remarks_engine = ConfigRemarksEngine(catalog)  # CLI remarks
```

#### static/app.js
```javascript
multiSwitchMode = false  // Multi-switch deployment flag
deployment = {  // Multi-switch deployment state
    switches: [],
    vpc_pairs: [],
    uplinks: []
}
DEPLOYMENT_TEMPLATES = {  // Predefined deployment templates
    "vpc_core_leaf": {...},
    "spine_leaf": {...}
}
currentStep = 1  // Current wizard step
```

### Key Functions

#### api/main.py - REST Endpoints
- `_auth_token()` - Get authentication token (removed for offline)
- `_enforce_privileged_access()` - Enforce loopback-only access
- `_is_loopback()` - Check if host is loopback address
- `POST /generate` - Generate NX-OS configuration
- `POST /generate-deployment` - Generate multi-switch deployment
- `GET /catalog` - Get hardware/software catalog
- `GET /catalog/hardware` - Get hardware profiles
- `POST /validate` - Validate configuration
- `POST /compliance` - Check compliance
- `POST /checkpoint/save` - Save configuration checkpoint
- `GET /checkpoints` - List checkpoints
- `POST /checkpoint/restore` - Restore checkpoint
- `POST /scenario/preview` - Preview scenario configuration
- `POST /intent/apply` - Apply intent-based configuration
- `POST /config-builder/parse` - Parse running-config
- `GET /version` - Get application version
- `POST /util/port-budget` - Calculate port budget
- `POST /util/expand-range` - Expand interface range

#### static/app.js - Frontend Logic
- `initDropdowns()` - Initialize header dropdown menus
- `setWizardMode()` - Set wizard mode (quick/architect)
- `showValidationPanel()` - Display validation errors
- `validateConfiguration()` - Validate form inputs
- `addVlanRow()` - Add VLAN row to form
- `applyVlanTemplate()` - Apply VLAN template (datacenter/campus/dmz/custom)
- `renderSwitchPortPanel()` - Render switch port visualization
- `editSwitch()` - Edit switch configuration modal
- `saveSwitchEdit()` - Save switch edits
- `toggleMultiSwitchMode()` - Toggle multi-switch deployment
- `renderTopologyDiagram()` - Render topology visualization

#### core/engine.py
- `ConfigurationPipeline` - Main pipeline orchestrator
- `build_configuration()` - Build complete configuration
- `validate_inputs()` - Validate all inputs
- `apply_intents()` - Apply intent-based rules

#### core/validator.py
- `DeviceValidator` - Device configuration validator
- `validate_device()` - Validate device configuration
- `validate_vpc()` - Validate vPC configuration
- `validate_vlan()` - Validate VLAN configuration

---

## Phase 3: Dependency Graph

### Core Data Flow

```
User Input (Web UI)
    ↓
static/app.js (Frontend validation)
    ↓
api/main.py (REST endpoints)
    ↓
core/engine.py (Pipeline orchestration)
    ↓
├── core/validator.py (Validation)
├── core/intent_engine.py (Intent processing)
├── core/scenario_engine.py (Scenario application)
├── core/renderer.py (Template rendering)
└── core/compliance.py (Compliance checking)
    ↓
templates/nxos_base.j2 (Jinja2 template)
    ↓
NX-OS Configuration Output
```

### Multi-Switch Deployment Flow

```
DEPLOYMENT_TEMPLATES (static/app.js)
    ↓
deployment state object
    ↓
api/main.py: /generate-deployment
    ↓
core/scenario_engine.py
    ↓
core/renderer.py (per-switch rendering)
    ↓
Multiple NX-OS configurations
```

### Import/Config Builder Flow

```
Paste running-config
    ↓
static/builder.js
    ↓
api/main.py: /config-builder/parse
    ↓
core/import_wizard.py
    ↓
core/config_parser.py
    ↓
Device model population
    ↓
Configuration generation
```

---

## Phase 4: Naming Conventions

### Python
- **Classes:** PascalCase (e.g., `DeviceValidator`, `ConfigurationPipeline`)
- **Functions:** snake_case (e.g., `validate_device`, `build_configuration`)
- **Variables:** snake_case (e.g., `hostname`, `mgmt_ip`, `vpc_domain`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `HISTORY_DIR`, `HOSTNAME_PATTERN`)
- **Private members:** Leading underscore (e.g., `_auth_token`, `_is_loopback`)

### JavaScript
- **Functions:** camelCase (e.g., `initDropdowns`, `validateConfiguration`)
- **Variables:** camelCase (e.g., `multiSwitchMode`, `currentStep`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `DEPLOYMENT_TEMPLATES`)
- **DOM IDs:** kebab-case (e.g., `vpc-domain`, `mgmt-ip`)

### Configuration (YAML)
- **Keys:** snake_case (e.g., `display_name`, `device_class`)
- **Sections:** lowercase with underscores (e.g., `port_groups`, `vpc_peer_link`)

---

## Phase 5: Detected Anti-Patterns & Issues

### Critical Issues
1. **Token Authentication Removed** - `_auth_token()` and `_enforce_privileged_access()` have authentication logic removed for offline use, creating potential security risk if deployed in networked environments
2. **Loopback Restriction Removed** - `_enforce_loopback_only()` is a no-op pass-through, removing network access controls

### High Priority Issues
1. **Global State Pollution** - `deployment` object in app.js is global, could cause state conflicts
2. **Magic Numbers** - Port numbers (9000), VLAN ranges (1-4094), vPC domain ranges hardcoded throughout
3. **Error Handling** - Some functions lack comprehensive error handling (e.g., `expandRange()` in app.js)
4. **Type Safety** - JavaScript lacks type checking, potential runtime errors from undefined variables

### Medium Priority Issues
1. **Code Duplication** - Similar validation logic in multiple places (api/main.py and static/app.js)
2. **Large File Size** - `static/app.js` is 3576 lines, should be modularized
3. **Inconsistent Naming** - Mix of `vpc_domain` vs `vpcDomain` across codebase
4. **Missing Documentation** - Many functions lack docstrings or comments

### Low Priority Issues
1. **Legacy Files** - Build artifacts and backup files should be cleaned
2. **Unused Imports** - Some imports may not be used in all files
3. **Hardcoded Paths** - Some file paths are hardcoded instead of using config

---

## Phase 6: External Dependencies

### Python (requirements.txt)
- fastapi - Web framework
- uvicorn - ASGI server
- pydantic - Data validation
- jinja2 - Template engine
- pyyaml - YAML parsing

### JavaScript (No package manager)
- Pure vanilla JavaScript
- No external libraries (offline-first design)

### System Dependencies
- Python 3.12+
- Modern web browser
- File system access for configs/history

---

## Phase 7: Configuration References

### File Paths
- `configs/history/` - Configuration history directory
- `configs/checkpoints/` - Checkpoint directory
- `logs/` - Application log directory
- `templates/` - Jinja2 templates
- `static/` - Static web assets
- `data/` - Configuration data files

### API Endpoints
- `GET /` - Main UI
- `GET /admin` - Admin interface
- `POST /generate` - Configuration generation
- `POST /generate-deployment` - Multi-switch generation
- `GET /catalog` - Catalog data
- `POST /validate` - Validation
- `POST /compliance` - Compliance check
- `GET /version` - Version info

### Environment Variables
- `NXOS_REPLACE_INSTANCE` - Replace running instance
- `NXOS_NO_BROWSER` - Disable browser auto-open
- `CONFIG_AUTH_TOKEN` - Authentication token (unused)

---

## Phase 8: Cross-Reference Map

### vPC Domain References
- `static/app.js`: `vpc_domain` variable
- `api/main.py`: `VPCInput.domain_id` field
- `templates/nxos_base.j2`: `{{ vpc.domain }}` template variable
- `data/hardware_profiles.yaml`: `vpc_peer_link` configuration

### Hardware Profile References
- `static/app.js`: `SWITCH_MODELS` object
- `core/catalog_loader.py`: Hardware profile loading
- `data/hardware_profiles.yaml`: Profile definitions
- `api/main.py`: `/catalog/hardware` endpoint

### Multi-Switch State
- `static/app.js`: `deployment` object, `multiSwitchMode` flag
- `api/main.py`: `/generate-deployment` endpoint
- `core/scenario_engine.py`: Deployment template processing

---

## Audit Status

**Phase 1:** ✅ Complete - File inventory and structure mapping  
**Phase 2:** ✅ Complete - Variable and function dictionary  
**Phase 3:** ✅ Complete - Dependency graph  
**Phase 4:** ✅ Complete - Naming conventions  
**Phase 5:** ✅ Complete - Anti-patterns detected  
**Phase 6:** ✅ Complete - External dependencies  
**Phase 7:** ✅ Complete - Configuration references  
**Phase 8:** ✅ Complete - Cross-reference map

**Next Phase:** Comprehensive audit checklist application per file
