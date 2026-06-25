---
name: nst-gap-remediation-workflow
description: >-
  Converts NST zero-trust gap register into prioritized P0/P1/P2 remediation plan
  with full council issue schema, then implements fixes using nst-orchestrator,
  network-ops, release-engineer, and security skills. Use after nst-zero-trust-network-council
  or when user asks to fix audit gaps, roadmap, or council P0/P1 items.
---

# NST Gap Remediation Workflow

## Input

- `.cursor/audits/GAP_REGISTER_*.md` from **nst-zero-trust-network-council**, OR
- User-supplied gap list / council roadmap

## Output

1. **Remediation plan** — `.cursor/audits/REMEDIATION_PLAN_<YYYY-MM-DD>.md`
2. **Implemented fixes** (when user approves execution phase)
3. **Validation evidence** — pytest, prebuild, version bump if shipped

## Phase 0 — Load context (mandatory skills)

Same composition as zero-trust council:

| Skill | Use |
|-------|-----|
| `nst-orchestrator` | Classify each gap, assign owner board |
| `nst-network-operations` | Operator impact, vendor CLI |
| `nst-python-backend` | Implementation location |
| `nst-security-ops` | P0 security gaps |
| `nst-release-engineer` | Tests, VERSION, EXE |
| `nst-product-architect` | UX gaps |
| `network-engineer` (devin) | CLI / change-order fixes |

Read `docs/12-master-prompts/roles/combined/ROLE_TEAM_MEETING_COUNCIL_USAGE_PROMPT.md` § **Required issue schema**.

## Phase 1 — Triage & prioritize

Map every gap ID to **P0 / P1 / P2 / P3**:

| Priority | Criteria | Examples |
|----------|----------|----------|
| **P0** | False success, data loss, credential exposure, broken safety | verification lies, auto-rollback, open cred API |
| **P1** | Feature broken or vendor parity hole on IOS/NX-OS/Junos | missing validate, Junos commit missing, GUI/web drift |
| **P2** | UX, perf, incomplete outputs, missing cancel/progress | ranking in API, topology truncate flag, IM HTML report |
| **P3** | Nice-to-have, new platforms, live lab CI | Arista first-class, containerlab pytest |

**Dependency order:** P0 → P1 → P2 → P3. Note blocks in plan.

## Phase 2 — Write remediation plan

Create `REMEDIATION_PLAN_<date>.md`:

```markdown
# NST Remediation Plan
- Source gap register: ...
- Target version: (current VERSION + patch unless user specifies)

## Executive summary

## Issue backlog

### P0
#### R-01: [title]
| Field | Value |
|-------|-------|
| Issue Description | ... |
| Severity | P0 |
| Root Cause | ... (code ref) |
| Impact | ... |
| Recommendation | ... |
| Owner | nst-security-ops / nst-python-backend / ... |
| Dependencies | R-XX or none |
| Priority | 1 |
| Estimated Complexity | S/M/L |
| Required Roles | ... |
| Implementation Strategy | ... |
| Exact AI IDE Prompt To Execute | (see below) |
| Expected Outcome | ... |
| Validation Procedure | pytest path, manual step |
| Rollback Procedure | git revert / doc only |
| Documentation Updates | CHANGELOG, AGENTS if skills |

(repeat for each issue)

### P1 ... ### P2 ...

## Action sequence
1. R-01 → R-02 → ...
2. Run pytest + _prebuild after each P0 batch
3. Ship gate after all requested priorities done

## Out of scope (explicit deferrals)
- ...
```

### Exact AI IDE Prompt template (per issue)

For each issue, generate a **copy-paste prompt** the user or agent can run standalone:

```markdown
**Prompt R-XX:**
Implement [one sentence fix] in Network Swiss Tool Pro v[VERSION].

Constraints:
- Minimize scope; match existing conventions in [primary file]
- IOS, NX-OS, Junos: [which vendors affected]
- Activate skills: [list]
- Do not reintroduce automated VLAN/IM rollback
- Outputs via utils/output_paths.py

Files likely touched: ...
Validation: python -m pytest tests/test_....py -q; python _prebuild.py
Done when: [measurable criteria]
```

## Phase 3 — Execute (only when user confirms)

Default: **plan only** unless user says "implement", "fix all P0", "ship", etc.

### Execution loop

```
FOR each issue in priority order (respect dependencies):
  1. Read owner skill + targeted code sections
  2. Implement minimal fix
  3. Add/adjust test if P0/P1
  4. Run: python -m pytest tests/ -q
  5. Run: python _prebuild.py
  6. Mark issue DONE in plan with commit refs / file list
END
```

### Ship sub-workflow (P0+P1 complete + user asks for release)

Activate **nst-release-engineer**:

1. Bump `VERSION`, `CHANGELOG.md`, `UPDATE_DATE` in `vlan_checker_web.py`
2. Copy/update `.spec` file
3. `python -m pytest tests/ -q` && `python _prebuild.py`
4. Build EXE per project convention
5. Update gap register → move fixed items to "Verified strengths"

## Skill routing table (gap type → implementer)

| Gap lens | Primary skill | Typical files |
|----------|---------------|---------------|
| VLAN / vendor CLI | nst-network-operations + network-engineer | `vlan_mgmt_production.py`, `vlan_validate.py` |
| IM / SSH deploy | nst-python-backend | `interface_manager.py`, `vlan_checker_web.py` |
| Web UI | nst-product-architect + ui-ux-designer | `index.html` |
| Security | nst-security-ops | `api_security.py`, cred routes |
| Outputs / HTML | nst-network-operations | `utils/*formatter*.py`, `output_paths.py` |
| Tests / release | nst-release-engineer | `tests/`, `_prebuild.py`, `.spec` |
| Architecture | nst-orchestrator + backend-architect | `adapters.py`, plugins |

## Governance

- Do **not** implement while council conflicts are open unless user overrides
- Every P0 fix needs a test or `_prebuild` guard where feasible
- Record outcomes in remediation plan; optional `TEAM_MEETING.md` entry for L2+

## Chaining

```
User request
  → nst-zero-trust-network-council (audit)
  → nst-gap-remediation-workflow Phase 1–2 (plan)
  → User approves scope
  → nst-gap-remediation-workflow Phase 3 (implement)
  → nst-release-engineer (ship)
```

## References

- `.cursor/skills/nst-zero-trust-network-council/SKILL.md`
- `ROLE_TEAM_MEETING_COUNCIL_USAGE_PROMPT.md` — issue schema
- `.cursor/ROLE_ACTIVATION_MATRIX.md`
