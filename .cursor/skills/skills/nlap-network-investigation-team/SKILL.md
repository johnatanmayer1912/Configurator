---
name: nlap-network-investigation-team
description: >-
  Zero-trust network engineer investigation council for Network Log Analysis Platform (NLAP).
  Skeptical NOC/SOC team audits every feature with code-only evidence across incident story,
  log extraction, PCAP, credentials, SSH collection, vendor parity (IOS/IOS-XE/NX-OS/Junos),
  security, and offline EXE behavior. Use for team QA, gap analysis, production readiness,
  or "network team review" of this program.
---

# NLAP Network Investigation Team — Zero Trust Council

## Mandate

Simulate a **skeptical network operations / incident response team** using NLAP during a live outage or post-mortem. **Trust nothing** — every claim must be proven by reading this repository (code, tests, templates, formatters). Docs and CHANGELOG are hints only until verified in source.

**Output:** A structured **Gap Register** — not marketing, not assumptions.

## When to invoke

- User asks for team QA, zero-trust audit, gap analysis, production readiness
- Before shipping a major version (incident brain, credentials, EXE)
- After integrating features from Net_mngmnt_tool V6
- User says "network engineer review", "what's broken", "360 review", "0 trust"

## Zero-trust rules

1. **Code-only answers** — cite `path:line` or symbol; if not found → **GAP** or **UNVERIFIED**
2. **No "should work"** — no test + no code path = gap
3. **Per-vendor** — IOS, IOS-XE, NX-OS, Junos evaluated separately unless code unifies them
4. **Security first** — credential vault, SSH routes, shutdown, PCAP URL fetch, bind address
5. **Offline EXE** — verify PyInstaller paths (`sys._MEIPASS`, `_get_resource_path`)
6. **Run gates when validating ship readiness:**
   ```bash
   python -m pytest tests/ -q
   python _prebuild.py
   ```
7. Record pytest count in gap register header

## Council workflow

Follow [WORKFLOW.md](WORKFLOW.md) step-by-step. Use [QUESTIONNAIRE.md](QUESTIONNAIRE.md) as the checklist.

### Lens summary

| Lens | Primary paths | Key questions |
|------|---------------|---------------|
| Incident story | `modules/investigation/service.py`, `modules/analysis/*` | Does autonomous → correlate → brain → export work for all vendors? |
| Collection | `log_collectors.py`, `incident_runbook.py` | Are show commands valid per platform? Collect-next dedupe correct? |
| Security | `utils/api_security.py`, `credential_routes.py`, `investigation_routes.py` | Localhost-only SSH/creds? Vault unlock before secret reveal? SSRF blocked? |
| Credentials | `modules/credential_manager.py`, `#tab-credentials` | Encrypted at rest? UI bridge populates enable password? |
| Control plane | `utils/task_control_plane.py`, `incident_job.py` | Cancel during SSH + post-collect phases? Honest `ok` responses? |
| PCAP | `modules/capture/pcap_download.py`, investigation PCAP routes | Bundled offline samples? URL validation? |
| UI / UX | `modules/web/templates/index.html` | Checkbox visibility, contrast, cancelled vs error states? |
| Outputs | `incident_export_writer.py`, `utils/output_paths.py` | TXT/HTML export, manifest, run folders? |

## Gap register output

Write to `.cursor/audits/GAP_REGISTER_<YYYY-MM-DD>.md`:

```markdown
# NLAP Zero-Trust Gap Register
- Version: (read VERSION)
- pytest: N passed / failed
- Council: nlap-network-investigation-team

## Executive summary
(3–5 sentences — ship/no-ship for production)

## Verified strengths (code evidence)
- GAP-OK-01: ... (`path:line`)

## Gaps (P0 → P3)
| ID | Lens | Question | Evidence / Gap | Status |
```

After register: fix P0/P1 where feasible, update `docs/02-testing/ZERO_TRUST_QA_*.md`, extend `docs/00-overview/WORLD_CLASS_ROADMAP.md`.

## Related skills

- **Release council (full team + mandatory QA):** `.cursor/skills/nlap-release-council/`
- When auditing cross-cutting concerns, also read perspectives from:
- `.cursor/.cursor/skills/nst-zero-trust-network-council/SKILL.md` (pattern reference)
- `.cursor/skills/nst-security-ops/SKILL.md` if present under nested `.cursor` copy

## Primary entry points (always grep these first)

| Area | Path |
|------|------|
| Autonomous pipeline | `modules/investigation/service.py` — `run_autonomous_incident_story`, `_apply_incident_brain` |
| Jobs / cancel | `modules/investigation/incident_job.py` |
| Runbook | `modules/analysis/incident_runbook.py` |
| Counter verdict | `modules/analysis/interface_counter_verdict.py` |
| Correlation | `modules/analysis/incident_correlation_engine.py` |
| Web routes | `modules/web/investigation_routes.py`, `vlan_checker_web.py` |
| Security | `utils/api_security.py` |
