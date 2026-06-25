# Architecture — NX-OS Configuration Authority (Web Platform)

**Version:** 2.5.0 · **Primary UI:** Web wizard · **Delivery:** Offline exe

## Overview

The NX-OS Configuration Authority generates validated Cisco Nexus CLI configurations through a **5-step web wizard**, backed by YAML catalogs and Jinja2 templates. It runs locally (browser + FastAPI) with no internet required when packaged as an exe.

## Module map

```
web_launcher.py          → FastAPI server, static mount, browser open
api/main.py              → REST API (catalog, scenario, vault, checkpoints)
static/app.js            → Wizard UI controller
templates/web/index.html → Wizard layout

core/scenario_engine.py  → Scenario presets → Device model
core/device_enricher.py  → HSRP, security tier, NTP/logging post-processing
core/intent_engine.py    → Blueprint intent → VLANs/interfaces/SVIs
core/engine.py           → Validate + render orchestration
core/renderer.py         → Version-aware Jinja2
core/validator.py        → Device + vPC pair validation
core/risk_analyzer.py    → CLI risk report
core/checkpoint_manager.py → JSON snapshots

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

```
Wizard → POST /scenario/preview|generate
      → ScenarioEngine.apply_scenario()
      → IntentEngine.resolve()
      → device_enricher.enrich_device()  (HSRP, hardened tier, NTP)
      → DeviceValidator.validate()
      → ConfigRenderer → nxos_base.j2
      → ConfigurationPipeline → configs/history/
```

## vPC pair mode

When `generate_pair=true` on a `pair_mode` scenario:

1. Primary config with role priority 4096, keepalive A→B
2. `validate_vpc_pair()` cross-check
3. Secondary `{hostname}-B` with swapped keepalives, role priority 8192

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

## Build

```powershell
pip install -r requirements.txt
python web_launcher.py
python utils/build_exe.py
python -m pytest tests/ -v
```
