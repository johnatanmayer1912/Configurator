# Gap Register — NX-OS Configurator

**Last updated:** 2026-06-23 · **Version:** 5.0.3  
**Maintainer:** Zero-Trust Review Team + Field Engineer Council

Status legend: `OPEN` | `IN_PROGRESS` | `FIXED` | `WONTFIX` | `DEFERRED`

---

## Critical

| ID | Status | Title | File(s) | Notes |
|----|--------|-------|---------|-------|
| C-001 | FIXED | Feature lines concatenated in CLI output | `templates/nxos_base.j2` | v2.4.0 |
| C-002 | FIXED | vPC peer-link used uplink ports | `core/scenario_engine.py`, `core/intent_engine.py` | v2.4.0 |
| C-003 | FIXED | UI vPC overrides ignored | `static/app.js`, `core/scenario_engine.py` | v2.4.0 |
| C-004 | FIXED | No vPC pair cross-validation on generate | `api/main.py` | v2.4.0 |
| C-005 | FIXED | Vault history path mismatch | `api/main.py`, `utils/app_dirs.py` | v2.4.0 |
| C-006 | FIXED | Missing BlueprintIntent import broke scenario engine | `core/scenario_engine.py` | v2.5.0 |

---

## High

| ID | Status | Title | File(s) | Target phase |
|----|--------|-------|---------|--------------|
| H-001 | FIXED | No automated pytest regression suite | `tests/` | v2.6.0 |
| H-002 | FIXED | Plaintext password in generated config | `templates/nxos_base.j2` | Lab-only when explicitly set |
| H-003 | FIXED | HSRP feature without HSRP config blocks | `core/device_enricher.py` | v2.5.0 |
| H-004 | FIXED | Advanced manual UI not connected to API | `core/manual_overrides.py`, `static/app.js` | v2.6.0 |
| H-005 | FIXED | No NTP/SNMP/AAA/logging baseline section | `templates/`, `data/feature_options.yaml` | v2.5.0 |
| H-006 | FIXED | Limited hardware profile catalog | `hardware_profiles.yaml` | 6 profiles v3.9.0; custom port map v4.0.0 |
| H-007 | FIXED | Risk analyzer noisy false positives | `core/risk_analyzer.py` | v2.5.0 |
| H-008 | FIXED | Stale documentation (CTK-primary narrative) | `docs/ARCHITECTURE.md` | v2.5.0 |
| H-009 | FIXED | No change-window export package | `utils/change_package.py`, `api/main.py` | v4.0.0 |
| H-010 | FIXED | Intent API missing vPC topology | `core/scenario_engine.py` | v4.0.0 |

---

## Medium

| ID | Status | Title | Target phase |
|----|--------|-------|--------------|
| M-001 | FIXED | No EVPN/VXLAN fabric scenarios | Foundation v2.6.0; BGP/NVE skeleton v4.0.0 |
| M-002 | FIXED | CLI aliases not rendered into config | v2.6.0 |
| M-003 | FIXED | Checkpoint restore missing from web UI | v2.6.0; full vPC restore v4.0.0 |
| M-004 | FIXED | Hardened security tier not in wizard | v2.5.0 |
| M-005 | FIXED | No import/diff against existing config | v2.6.0; parse-running-config-diff v4.0.0 |
| M-006 | FIXED | Version string drift in templates | v2.6.0 |
| M-007 | FIXED | Accessibility: reduced motion, focus-visible | v4.0.0 |
| M-008 | FIXED | Wizard step gating optional | v2.6.0 |
| M-009 | FIXED | Vault search limited to hostname | Site/scenario/type filters v4.0.0 |
| M-010 | FIXED | No JSON device export for automation | `_device.json` per build v4.0.0 |

---

## Low

| ID | Status | Title |
|----|--------|-------|
| L-001 | FIXED | Favicon / PWA |
| L-002 | FIXED | Hostname pair suffix edge cases |
| L-003 | DEFERRED | i18n |
| L-004 | FIXED | Exe size optimization | PyInstaller excludes v4.0.0; verified v4.1.0 build |
| L-005 | IN_PROGRESS | Browser E2E (Playwright) wizard walk-through | v5 DOM/JS contracts + optional e2e folder; full Playwright gate when `tests/e2e/` added |

---

## Change log

| Date | Change |
|------|--------|
| 2026-06-23 | v5.0.3: Offline-integrity audit + automated guards (no external refs, relative fetch, no outbound calls, system fonts); header wrap; 370-test QA gate (no new exe) |
| 2026-06-23 | v5.0.2: UI visibility fixes — topology SVG styling, semantic CSS tokens, .btn-ghost; "Steve Jobs" polish; 365-test QA gate (no new exe) |
| 2026-06-23 | v5.0.1: Correctness audit — preset-id persistence, admin token flow, read-only topology/capacity, meter ordering; 361-test QA gate (no new exe) |
| 2026-06-23 | v5.0.0: Po collision guard, cable plan export, admin Po map, Quick/Architect modes, topology, readiness meter, 350-test QA gate |
| 2026-06-23 | v4.1.0: Fabric Link Planner — editable downlinks/uplinks, fiber uplink defaults 49–54, 330-test QA gate |
| 2026-06-23 | v4.0.0: Change package, port map editor, VXLAN fabric skeleton, intent topology parity, vault filters, 321-test QA gate |
| 2026-06-22 | v3.9.0: Full API/feature/baseline/hardware/intent mandatory coverage (295 tests) |
| 2026-06-22 | v3.8.0: Field council P1/P2 UI + storm + generate API |
| 2026-06-21 | v2.9.0: Dual QA pass — peer-link parser, vPC validate-before-export |
| 2026-06-21 | Initial register; C-001–C-005 marked FIXED in v2.4.0 |
