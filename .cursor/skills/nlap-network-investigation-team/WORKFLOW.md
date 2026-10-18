# NLAP Investigation Team — Zero-Trust Workflow

## Phase 0 — Resync (5 min)

1. Read `VERSION` and last CHANGELOG entry (unverified until code matches)
2. `git status` — note uncommitted work
3. Load this skill + [QUESTIONNAIRE.md](QUESTIONNAIRE.md)

## Phase 1 — Security envelope (P0)

Work through questionnaire **Section A**. For each item:

1. Ask the skeptical question (as NOC at 2 AM)
2. Grep/Read until you find the guard or prove absence
3. Record evidence or GAP

**Stop-the-line if:** plaintext creds over LAN, unauthenticated SSH, SSRF, unauthenticated shutdown.

## Phase 2 — Incident pipeline (P0/P1)

Work **Section B** end-to-end:

```
UI checkbox → autonomous-run/start → SSH tier1/2 → correlate → _apply_incident_brain → export → UI render
```

Verify cancel at: SSH loop, correlate, brain stages.

## Phase 3 — Vendor matrix (P1)

Work **Section C** for IOS, IOS-XE, NX-OS, Junos separately:

- `log_collectors.py` command validity
- `incident_runbook.py` collect-next
- `interface_counter_verdict.py` interface token matching (Gi, Eth, Ethernet1/1)
- `incident_correlation_engine.py` anchor matching

## Phase 4 — Operator UX (P2)

Work **Section D**: credentials tab, control plane, cancelled vs error UI, config translator contrast.

## Phase 5 — Gates

```bash
python -m pytest tests/ -q
python _prebuild.py
```

Record counts in gap register.

## Phase 6 — Deliverables

1. `.cursor/audits/GAP_REGISTER_<date>.md`
2. Fix P0/P1 gaps in code (minimal diff)
3. `docs/02-testing/ZERO_TRUST_QA_<version>.md` — summary of run + fixes
4. Update `docs/00-overview/WORLD_CLASS_ROADMAP.md` — next milestones

## Severity guide

| Level | Meaning | Examples |
|-------|---------|----------|
| P0 | Security / false success / data loss | LAN cred leak, SSRF, wrong counter source |
| P1 | Broken feature / vendor gap | Invalid NX-OS command, cancel ignored post-SSH |
| P2 | UX / polish | Grey-on-grey, cancelled shown as error |
| P3 | Nice-to-have | 12-step acquisition UI unwired |

## Council meeting script (optional live review)

1. **Lead NOC:** "Prove autonomous collection works on IOS-XE Gi0/1."
2. **Security:** "What happens if I curl credentials from another host?"
3. **Vendor SME:** "Is `show interface Eth1/1 status err-disabled` valid on NX-OS?"
4. **Release:** "What's pytest count and did prebuild pass?"

Each answer must cite code before moving on.
