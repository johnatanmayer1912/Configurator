---
name: nst-zero-trust-network-council
description: >-
  Zero-trust network engineer council for Network Swiss Tool Pro. Skeptical NOC
  team evaluates every feature with code-only evidence across functionality,
  performance, tech, UI, outputs, security, and IOS/NX-OS/Junos parity. Mandatory
  skill composition from nst-orchestrator and builder skills. Use when auditing
  gaps, production readiness, vendor support, or "network team review".
---

# NST Zero-Trust Network Engineer Council

## Mandate

Simulate a **skeptical network operations team** using Network Swiss Tool Pro in production. **Trust nothing** — every claim must be proven by reading the repository (code, tests, templates, formatters). No assumptions from docs, CHANGELOG, or prior chat unless verified in source.

**Output:** A structured **Gap Register** — not a feature list, not praise.

## When to invoke

- User asks for audit, gap analysis, production readiness, vendor parity review
- Before major release after large changes
- After council / team-meeting review
- When user says "zero trust", "network team", "what's broken", "360 review"

## Mandatory skill composition (every run)

Before asking or answering **any** council question, load and apply perspectives from:

| Order | Skill | Path | Role in council |
|-------|-------|------|-----------------|
| 1 | NST Orchestrator | `.cursor/skills/nst-orchestrator/SKILL.md` | Route domains, boards |
| 2 | Network operations | `.cursor/skills/nst-network-operations/SKILL.md` | Operator UX, platform matrix |
| 3 | Network engineer | `.cursor/skills-devin/network-engineer/SKILL.md` | CLI correctness, change order |
| 4 | Product architect | `.cursor/skills/nst-product-architect/SKILL.md` | Workflow effectiveness |
| 5 | Python backend | `.cursor/skills/nst-python-backend/SKILL.md` | API, adapters, plugins |
| 6 | Security ops | `.cursor/skills/nst-security-ops/SKILL.md` | Credentials, mutations |
| 7 | Release engineer | `.cursor/skills/nst-release-engineer/SKILL.md` | Tests, gates, vendor matrix |
| 8 | Multi-advisor | `.cursor/skills/nst-multi-advisor/SKILL.md` | Tradeoffs when findings conflict |

For each **360 lens** below, also pull **one** deep skill from `.cursor/SKILL_CATALOG.json` when relevant (e.g. `hybrid-cloud-networking`, `ui-ux-designer`, `python-testing-patterns`, `security-auditor`). Search catalog by keyword; read Overview + relevant section only.

## Zero-trust rules

1. **Code-only answers** — cite `file:line` or function name; if not found, mark **UNVERIFIED** or **GAP**
2. **No "should work"** — if no test or code path exists, it is a gap
3. **Per-vendor** — IOS, IOS-XE, NX-OS, Junos evaluated separately unless code explicitly unifies them
4. **GUI vs Web parity** — compare `vlan_checker_gui.py` and `vlan_checker_web.py` + `index.html`
5. **Outputs** — every feature must trace to `utils/output_paths.py` and a formatter
6. **Run gates when validating ship readiness:**
   ```bash
   python -m pytest tests/ -q
   python _prebuild.py
   python scripts/enterprise_qa_gate.py
   ```
7. Record pytest count and prebuild result in the gap register header

## 360° questionnaire (work through all lenses)

Use [QUESTIONNAIRE.md](QUESTIONNAIRE.md) as the checklist. For each item:

1. Formulate a **skeptical question** (as the NOC would ask at 2 AM)
2. **Search/read code** — Grep, Read, SemanticSearch; never skip
3. Record **Evidence** (path + symbol) or **GAP**
4. Assign **Severity**: P0 (data loss / false success / security) · P1 (broken feature / vendor gap) · P2 (UX / perf / polish) · P3 (nice-to-have)

### Lens summary

| Lens | Primary paths | Key questions |
|------|---------------|---------------|
| Functionality | `modules/`, `vlan_checker_web.py`, plugins | Does each advertised feature have a complete code path for all three vendors? |
| Vendor parity | `vlan_mgmt_production.py`, `interface_manager.py`, `adapters.py` | IOS vs NX-OS vs Junos — same validation, save, verify, rollback story? |
| Performance | adapters loops, topology, discovery | Timeouts, truncation, serial SSH, abort between devices? |
| Tech / architecture | `utils/task_control_plane.py`, plugins | Shared validation? Control plane vs sync routes? |
| UI / UX | `modules/web/templates/index.html`, GUI | Honest scope banners? Validation before execute? |
| Outputs / audit | `utils/output_paths.py`, `*formatter*.py` | manifest.json, HTML + TXT, run folders? |
| Security | `utils/api_security.py`, credential routes | Localhost, vault, audit log — gaps? |
| Effectiveness | End-to-end operator workflow | Can a team safely run VLAN + IM + discovery without surprises? |

## Gap register output format

Write to `.cursor/audits/GAP_REGISTER_<YYYY-MM-DD>.md` (create `audits/` if needed):

```markdown
# NST Zero-Trust Gap Register
- Version: (read VERSION file)
- Date: ...
- pytest: N passed / failed
- prebuild: PASS | FAIL
- Council skills used: (list)

## Executive summary
(3–5 sentences — honest ship/no-ship for production on IOS/NX-OS/Junos)

## Verified strengths (code evidence only)
- GAP-OK-01: ... (`path:line`)

## Gaps
### P0 — ...
| ID | Lens | Question | Evidence / Gap | Severity | Owner skill |
|----|------|----------|----------------|----------|-------------|
| G-001 | ... | ... | `file:line` or MISSING | P0 | nst-security-ops |

(repeat for P1, P2, P3)

## Vendor matrix (IOS | NX-OS | Junos)
| Feature | IOS | NX-OS | Junos | Notes |
|---------|-----|-------|-------|-------|

## Unverified (could not find in code)
- ...

## Recommended next step
Run **nst-gap-remediation-workflow** on this register.
```

## Council meeting flow

```
1. Resync: VERSION, CHANGELOG (last entry only), nst-orchestrator
2. Load mandatory skills (table above)
3. Run pytest + _prebuild → record in header
4. Walk QUESTIONNAIRE.md → fill gap register
5. Compose vendor matrix from code paths (not marketing)
6. Hand off to nst-gap-remediation-workflow
```

## Do not

- Close gaps during audit (audit only unless user explicitly asks to fix)
- Trust dist/ or build/ artifacts over source
- Mark vendor "supported" without a code branch for that `device_type`
- Skip mandatory skill composition

## References

- [QUESTIONNAIRE.md](QUESTIONNAIRE.md) — full 360 checklist
- `docs/12-master-prompts/roles/combined/ROLE_TEAM_MEETING_COUNCIL_USAGE_PROMPT.md` — issue schema for remediation
- `.cursor/ROLE_ACTIVATION_MATRIX.md`
