# NST Zero-Trust Gap Register — Revalidation (Post Skill Import)

- **Product:** NX-OS Configuration Authority
- **Version:** 2.4.0 (`VERSION`)
- **Date:** 2026-06-21
- **pytest:** 3 passed / 0 failed
- **prebuild:** not run this session (manual: `python utils/build_exe.py`)
- **Council skills used:** nst-zero-trust-network-council, nxos-zero-trust-review-team, nxos-config-engineer, nst-network-operations, nst-python-backend, nst-release-engineer, nst-security-ops, nst-product-architect, network-engineer (devin)

## Executive summary

After importing **4335 files** from V6 `.cursor` (skills-sickn33, nst-*, rules, audits, SKILL_CATALOG.json, scripts/) and Configurator-specific governance adaptation, **revalidation confirms critical CLI bugs are fixed in source**. Stale artifacts in `dist/configs/history/` pre-date v2.4.0 fixes — **do not trust old vault files**; regenerate configs after upgrade.

**Ship recommendation:** Lab/staging with zero-trust checklist. Not production-unattended until Phase 2 roadmap complete.

## Verified strengths (code evidence)

| ID | Finding | Evidence |
|----|---------|----------|
| OK-001 | Feature lines render separately | `tests/test_scenario_engine.py` PASS; `templates/nxos_base.j2` block `{% if %}` form |
| OK-002 | vPC peer-link from hardware profile | `scenario_engine._apply_vpc_config()` + test `test_vpc_leaf_pair_uses_hardware_peer_link_ports` |
| OK-003 | UI overrides include peer_link_interfaces | `static/app.js` `buildScenarioPayload()` → `scenario_engine._parse_peer_links()` |
| OK-004 | vPC pair validation before dual generate | `api/main.py` `/scenario/generate` calls `validate_vpc_pair()` |
| OK-005 | History path exe-relative | `api/main.py` uses `get_history_dir()` |
| OK-006 | CLI preview on validate | `api/main.py` returns `config_preview` |
| OK-007 | Field hints + wizard tips | `data/field_hints.yaml` → `/catalog` |
| OK-008 | Skill library imported | `.cursor/` 4335 files; `scripts/resolve_skill.py` operational |
| OK-009 | Configurator role matrix | `.cursor/ROLE_ACTIVATION_MATRIX.md` adapted |
| OK-010 | Auth on `/validate` | `api/main.py` `_enforce_privileged_access` on validate endpoint |

## Open gaps

### P1

| ID | Lens | Question | Evidence / Gap | Owner |
|----|------|----------|----------------|-------|
| G-101 | Outputs | Are dist/ artifacts trustworthy? | Stale `dist/configs/history/*` still show concatenated features | nst-release-engineer — purge dist on release |
| G-102 | L3 | HSRP feature without HSRP blocks? | `intent_engine._build_svis()` no HSRP objects when feature enabled | nxos-config-engineer |
| G-103 | Security | Plaintext passwords in template? | `nxos_base.j2` L13-15 plaintext username password | nst-security-ops |
| G-104 | Docs | NST KNOWLEDGE_BASE still references vlan_checker? | Partially updated; `docs/ARCHITECTURE.md` still CTK-primary | documentation-and-adrs |
| G-105 | Catalog | nxos-* skills not in SKILL_CATALOG.json | `resolve_skill.py nxos-config-engineer` → No matches | nst-release-engineer |

### P2

| ID | Lens | Gap | Owner |
|----|------|-----|-------|
| G-201 | UX | Advanced manual VLAN/UI not wired to API | nst-product-architect |
| G-202 | Scenarios | No EVPN/VXLAN scenarios | nxos-config-engineer |
| G-203 | Tests | Only 3 pytest tests | nst-release-engineer |
| G-204 | Governance | Old `01-nst-network-engineering.mdc` still references modules/vlan | nxos-orchestrator — use `01-nxos-network-engineering.mdc` |

### P3

| ID | Lens | Gap |
|----|------|-----|
| G-301 | Catalog | skillss/ junction paths in SKILL_CATALOG.json point to NST layout |
| G-302 | Skills | 3889 sickn33 skills — use resolve_skill, don't load all |

## Vendor matrix (Configurator scope)

| Feature | NX-OS 9.3+ | NX-OS 7.0 | Notes |
|---------|------------|-----------|-------|
| Standalone access | YES | YES | `standalone_access` scenario |
| vPC leaf pair | YES | PARTIAL | Legacy template omits peer-gateway |
| Feature toggles | YES | YES | Checkbox-driven |
| Web wizard | YES | YES | Version selector |
| IOS/Junos | NO | NO | Out of scope — Configurator is NX-OS only |

## Unverified

- Offline exe post v2.4.0 (rebuild required)
- HSRP end-to-end on real switch
- skillss/ junction if catalog paths used without skills-sickn33 fallback

## Recommended next step

1. Run `docs/06-quality-assurance/zero-trust-review/NETWORK_TEAM_TEST_CHECKLIST.md`
2. Purge stale `dist/configs/history/`
3. Rebuild exe: `python utils/build_exe.py`
4. Execute Phase 2 of `REMEDIATION_ROADMAP.md`
5. Add nxos-* entries to skill catalog via `scripts/build_skill_catalog.py`

## Chaining

→ `nst-gap-remediation-workflow` for G-101 through G-105
