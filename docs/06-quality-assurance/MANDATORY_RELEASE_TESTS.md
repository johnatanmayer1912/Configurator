# Mandatory Release Tests

**Single source of truth:** `data/release_qa_manifest.yaml`

This document explains *why* each gate exists. The manifest defines *what* runs and *when*. Update the manifest when you add scenarios, UI surfaces, API routes, or release blockers — `tests/mandatory/test_release_manifest.py` enforces that every referenced path exists.

## Council ownership

| Stakeholder | Lens | Mandatory coverage |
|-------------|------|-------------------|
| **Product architect** | Catalog coherence, pair_mode matrix, infra-only vPC defaults | `test_scenario_catalog_architecture.py` |
| **Software engineer** | API contracts, auth boundaries, pytest discipline | `test_operator_api_contracts.py`, full `tests/` |
| **Field engineer / NOC** | vPC 40G / 10G / 1G, Po mirror, reserved ports | `test_vpc_planner_mandatory.py`, `test_instance_control.py` |
| **Operator UX** | Wizard preflight, payload shape, stop/upgrade | `test_wizard_preflight_contract.py` |
| **UI/UX professional** | No focus-loss re-render on text inputs | `test_ui_text_input_stability.py` |
| **Steve Jobs (simplicity)** | One path to stop; no hidden toggles for vPC Po on pairs | Instance control + `isVpcPairScenario()` contracts |
| **Release engineer** | VERSION semver, offline bundle, frozen sim | `test_offline_bundle_manifest.py`, `_prebuild.py`, frozen audit |

## Triggers

| Trigger | When | Runner |
|---------|------|--------|
| `on_change` | Every commit (pre-commit), every push/PR (CI fast job) | `python scripts/run_mandatory_qa.py --on-change` |
| `pre_release` | Before `VERSION` bump, tag builds, manual dispatch | `python scripts/run_mandatory_qa.py --pre-release` |
| `pre_exe` | Immediately before `utils/build_exe.py` | `python scripts/enterprise_qa_gate.py` |

## Stage catalog (living list)

### 1. Manifest integrity
- **File:** `tests/mandatory/test_release_manifest.py`
- **Triggers:** all
- Ensures manifest loads, stages have labels/triggers, and every referenced file exists.

### 2. Instance control / shutdown (release blocker)
- **File:** `tests/test_instance_control.py`
- **Triggers:** pre_release, pre_exe
- Stop without session token; PID file; port 9000 cleanup. Prevents the autostart loop.

### 3. UI/UX — text input stability
- **File:** `tests/mandatory/test_ui_text_input_stability.py`
- **Triggers:** all
- Regression guard for v3.7.4: description fields must not trigger full `renderInterfacePlanner()` on every keystroke. Requires `STRUCTURAL_PLAN_FIELDS`, `data-field` delegation, no inline `oninput="updateInterfacePlan"`.

### 4. Product architect — scenario catalog
- **File:** `tests/mandatory/test_scenario_catalog_architecture.py`
- **Triggers:** all
- Config matrix ↔ scenario catalog parity; all vPC tier scenarios declared; infra-only defaults; interface preset catalog.

### 5. Field engineer — vPC planner regression
- **File:** `tests/mandatory/test_vpc_planner_mandatory.py`
- **Triggers:** pre_release, pre_exe
- Implicit/explicit vPC Po on 40G core, 10G leaf, 1G access; secondary mirror; reserved downlink ports; missing VLAN warnings.

### 6. Software engineer — API contracts
- **File:** `tests/mandatory/test_operator_api_contracts.py`
- **Triggers:** pre_release, pre_exe
- `/version`, `/catalog`, `/scenario/preview` with interface plans, hostname validation, shutdown loopback contract.

### 7. Release engineer — offline bundle
- **File:** `tests/mandatory/test_offline_bundle_manifest.py`
- **Triggers:** pre_release, pre_exe
- VERSION semver; PyInstaller `datas` includes templates/static/data/hardware; `--replace` / `--stop`; tier hardware vPC ports.

### 8. Operator UX — wizard preflight
- **File:** `tests/mandatory/test_wizard_preflight_contract.py`
- **Triggers:** all
- `interfacePlanPreflightErrors`, `collectInterfacePlans`, roadmap `generate_pair`, planner markup in `index.html`.

### 9. Full pytest suite
- **Path:** `tests/`
- **Triggers:** pre_release, pre_exe

### 9a. Generate API (F-002)
- **File:** `tests/mandatory/test_scenario_generate_api.py`
- **Triggers:** pre_release, pre_exe

### 9b. Field gap regressions (P1/P2)
- **File:** `tests/mandatory/test_field_gap_contracts.py`
- **Triggers:** on_change, pre_release, pre_exe

### 9c. v4 world-class (change package, port map, fabric, S-HERO)
- **File:** `tests/mandatory/test_v4_world_class_contracts.py`
- **Triggers:** on_change, pre_release, pre_exe
- Change package `manifest.json` + `CHANGE_PACKAGE.md`, device JSON, Config Builder flow, checkpoint restore, port map DOM, vault filters, VXLAN NVE/BGP, intent topology parity, all 8 scenarios smoke

### 10–12. Scripts
- `_prebuild.py` — syntax + bundle paths
- `scripts/validate_docs_links.py` — doc link integrity
- `scripts/audit_frozen_plugin_sim.py` — frozen PyInstaller asset simulation

## How to extend (as the product evolves)

1. Add or update tests under `tests/mandatory/` (or existing `tests/`).
2. Register the file in `data/release_qa_manifest.yaml` with the correct `triggers` and `blocker: true`.
3. Run `python scripts/run_mandatory_qa.py --on-change` locally (fast) before pushing.
4. `test_release_manifest.py` fails if the manifest references a missing path — keeps the list honest.

## Operator commands

```powershell
# Fast check after edits
python scripts/run_mandatory_qa.py --on-change

# Before VERSION bump
python scripts/run_mandatory_qa.py --pre-release

# Before offline exe (also auto-runs from build_exe.py)
python scripts/enterprise_qa_gate.py
python utils/build_exe.py
```

## Pre-commit setup

```powershell
pip install pre-commit
pre-commit install
```

Every commit runs the `on_change` stages automatically.
