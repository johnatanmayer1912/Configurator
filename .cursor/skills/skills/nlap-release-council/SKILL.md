---
name: nlap-release-council
description: >-
  Multi-persona release council for Network Log Analysis Platform (NLAP). Network
  engineers, architect, software engineer, field operators, product simplicity
  (Steve Jobs lens), and UI/UX professional run an extensive code-backed
  questionnaire across every program aspect to find gaps before ship. Use for
  council QA, mandatory release gate review, gap registers, team-testing, or
  when the user asks for zero-trust validation from the whole team.
---

# NLAP Release Council — Code-Only Validation Team

## Mandate

Convene a **skeptical cross-functional council** that validates **every aspect** of NLAP. Answers come **only from this repository** (source, tests, templates, routes, specs). Documentation and CHANGELOG are hints until verified in code.

**Deliverable:** Gap register + mandatory test extensions when gaps are found.

## When to invoke

- Before any release or EXE build
- After feature work, bug fixes, or refactors
- User asks for council review, team QA, gap analysis, ship readiness
- Mandatory QA gate failed or manifest out of sync

## Council personas

Read [PERSONAS.md](PERSONAS.md) before each review. Each persona owns a lens:

| Persona | Lens | Primary question |
|---------|------|------------------|
| **Network council** | NOC/SOC/IR | Would this help at 2 AM during an outage? |
| **Architect** | Structure & contracts | Are boundaries, data flows, and offline paths sound? |
| **Software engineer** | Quality & maintainability | Are errors, types, tests, and APIs correct? |
| **Field operator** | Real workflows | Can a tier-1 engineer complete tasks without docs? |
| **Product simplicity** | Steve Jobs lens | What can we remove? Is the primary path obvious? |
| **UI/UX professional** | Operator experience | Clarity, contrast, progress honesty, accessibility |

## Zero-trust rules

1. **Code-only** — cite `path:line` or symbol; missing proof → **GAP**
2. **No "should work"** — no code path + no test → gap
3. **Per-vendor** — IOS, IOS-XE, NX-OS, Junos evaluated separately unless unified in code
4. **Offline EXE** — verify `sys._MEIPASS`, `_get_resource_path`, PyInstaller `datas`
5. **Extend tests** — every new gap → add `@pytest.mark.mandatory` test in `tests/mandatory/`
6. **Update manifest** — register new tests in `qa/mandatory/MANIFEST.yaml`

## Workflow

Follow [WORKFLOW.md](WORKFLOW.md). Use [QUESTIONNAIRE.md](QUESTIONNAIRE.md) as the master checklist (all sections, all IDs).

### Phase summary

1. **Resync** — `VERSION`, git status, `qa/mandatory/MANIFEST.yaml`
2. **Run mandatory gate (when executing)** — `python scripts/run_mandatory_qa.py`
3. **Questionnaire** — every section A–Z; record evidence or GAP
4. **Gap register** — `.cursor/audits/GAP_REGISTER_<YYYY-MM-DD>.md`
5. **Evolve tests** — add scenarios to `tests/mandatory/` per [EVOLUTION_POLICY](../../qa/mandatory/EVOLUTION_POLICY.md)
6. **Ship decision** — P0 open = no ship

## Gap register template

```markdown
# NLAP Release Council Gap Register
- Version: (read VERSION)
- Council: nlap-release-council
- Mandatory QA manifest: qa/mandatory/MANIFEST.yaml
- pytest mandatory: (count from run_mandatory_qa.py when executed)

## Executive summary
(ship / no-ship — 3–5 sentences)

## Persona summaries
### Network council | Architect | Software engineer | Field operator | Product | UI/UX

## Verified strengths (code evidence)
- GAP-OK-01: claim (`path:line`)

## Gaps (P0 → P3)
| ID | Persona | Question | Evidence / Gap | Mandatory test ID | Status |
```

## Mandatory automation (do not skip)

| Trigger | Mechanism |
|---------|-----------|
| Code change | `.cursor/hooks.json` → `afterFileEdit` |
| Release / EXE | `_prebuild.py` manifest check + `run_mandatory_qa.py` |
| CI | `.github/workflows/mandatory-qa.yml` |
| Agent rule | `.cursor/rules/05-nlap-mandatory-qa-gate.mdc` |

When adding features or fixing bugs: **extend** `tests/mandatory/` and `MANIFEST.yaml` in the same change.

## Related assets

| Asset | Path |
|-------|------|
| Network investigation team (subset) | `.cursor/skills/nlap-network-investigation-team/` |
| Mandatory manifest | `qa/mandatory/MANIFEST.yaml` |
| Evolution policy | `qa/mandatory/EVOLUTION_POLICY.md` |
| Release gate doc | `docs/06-quality-assurance/MANDATORY_RELEASE_GATE.md` |
| Runner | `scripts/run_mandatory_qa.py` |

## Primary code entry points

| Area | Path |
|------|------|
| Web shell | `vlan_checker_web.py` |
| Investigation routes | `modules/web/investigation_routes.py` |
| Incident pipeline | `modules/investigation/service.py` |
| Acquisition engine | `modules/investigation/acquisition/` |
| Security | `utils/api_security.py` |
| Credentials | `modules/credential_manager.py`, `modules/web/credential_routes.py` |
| UI | `modules/web/templates/index.html` |
| Offline build | `build_v5.*.spec`, `scripts/verify_offline_bundle.py` |
