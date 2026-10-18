# Release QA Gate

**Run before every VERSION bump and offline exe build.**

**Current Version: 6.14.0**

Manifest-driven gate: `data/release_qa_manifest.yaml`  
Council rationale: [MANDATORY_RELEASE_TESTS.md](MANDATORY_RELEASE_TESTS.md)

## Command

```powershell
python scripts/enterprise_qa_gate.py
```

Equivalent:

```powershell
python scripts/run_mandatory_qa.py --pre-exe
```

## Gate order (manifest `pre_exe` stages, fail-fast on blockers)

| # | Stage ID | What | On every commit? |
|---|----------|------|------------------|
| 1 | `manifest_integrity` | Manifest + path validation | Yes |
| 2 | `release_blockers` | Instance control / shutdown (port 9000) | No |
| 3 | `mandatory_ui_ux` | Text input stability (Interface Planner) | Yes |
| 4 | `mandatory_architecture` | Scenario catalog & matrix parity | Yes |
| 5 | `mandatory_field_vpc` | vPC 40G/10G/1G planner regression | No |
| 6 | `mandatory_api_contracts` | Operator API contracts | No |
| 7 | `mandatory_offline_bundle` | Offline exe bundle manifest | No |
| 8 | `mandatory_wizard_preflight` | Wizard payload & preflight hooks | Yes |
| 9 | `mandatory_generate_api` | `/scenario/generate` pair export | No |
| 10 | `mandatory_field_gaps` | P1/P2 field council regressions | Yes |
| 11 | `mandatory_api_expanded` | Full API surface — all 24 endpoints + auth | No |
| 12 | `mandatory_feature_render` | Every CLI feature renders in correct block | No |
| 13 | `mandatory_baseline_coverage` | All 14 institutional baseline options | No |
| 14 | `mandatory_hardware_coverage` | All 6 hardware profiles produce valid configs | No |
| 15 | `mandatory_intent_engine` | IntentEngine — all roles, vPC, hardened tier | No |
| 16 | `mandatory_v4_world_class` | Change package, port map, fabric, vault, S-HERO | Yes |
| 17 | `mandatory_vpc_link_planner` | Fabric links — downlinks, uplinks, fiber 49–54 | Yes |
| 18 | `full_pytest_suite` | Full `pytest tests/` (330 tests) | No |
| 19 | `prebuild` | `_prebuild.py` | No |
| 20 | `doc_links` | `validate_docs_links.py` | No |
| 21 | `frozen_bundle_sim` | Frozen PyInstaller simulation | No |

Steps 2–18 are **release blockers** for exe builds. Steps 1, 3–4, 8, 10, 16–17 run on every commit via pre-commit and CI.

## Automation

| Event | Command |
|-------|---------|
| Git commit | `pre-commit` → `run_mandatory_qa.py --on-change` |
| Push / PR | GitHub Actions `mandatory-qa.yml` (fast job) |
| VERSION bump | `run_mandatory_qa.py --pre-release` |
| Offline exe | `enterprise_qa_gate.py` (also invoked by `utils/build_exe.py`) |

## What instance control validates

- `POST /system/shutdown` works **without** session token on localhost
- Process exits after shutdown (no orphan listener on port 9000)
- PID file round-trip under `logs/nxos_configurator.pid`

## After gate passes

```powershell
python utils/build_exe.py
```

Artifact: `dist/NXOS_Configurator_Web_v{VERSION}_*.exe`

## Stop stuck instances (operator)

```powershell
.\scripts\stop_configurator.ps1
# or
.\dist\NXOS_Configurator_Web_vX.Y.Z_*.exe --stop
```

Upgrade in place:

```powershell
.\dist\NXOS_Configurator_Web_vX.Y.Z_*.exe --replace
```

See also: [OFFLINE_RUNBOOK](../03-disaster-recovery/OFFLINE_RUNBOOK.md)
