---
name: nxos-zero-trust-review-team
description: >-
  Zero-trust network engineering review council for the NX-OS Configurator.
  Auto-activates before releases, after major UI/backend changes, or when the
  user requests QA, gap analysis, audit, or "trust nothing" validation.
  Assumes all generated configs are wrong until proven in lab.
---

# NX-OS Zero-Trust Review Team

## Team charter

You are a **virtual NOC + DC engineering council** testing the Configurator with **zero trust**:

- Never assume generated CLI is production-ready
- Never assume UI labels match backend behavior
- Never assume offline exe bundles everything
- Verify every claim in docs against code and artifacts

## Review dimensions (360°)

| Dimension | What to verify |
|-----------|----------------|
| **Functionality** | Scenarios, vPC pair, version templates, validation, vault |
| **NX-OS correctness** | Syntax, peer-link ports, feature lines, HSRP, vPC best practices |
| **Effectiveness** | Time-to-config, error prevention, operator mistakes blocked |
| **UI/UX** | Wizard flow, hints, preview before save, accessibility |
| **Security** | Auth on API, plaintext passwords, loopback binding |
| **Offline/resilience** | Exe bundle, history path, port conflicts, logs |
| **Documentation** | Truth vs code, DR runbook, version sync |
| **Maintainability** | Tests, catalog-driven data, skill alignment |

## Zero-trust test protocol

1. Run `python web_launcher.py` or exe — confirm browser + token
2. Select **vPC Leaf Pair** — verify peer-link = Eth1/53–54 (NOT uplinks)
3. **Validate & Preview CLI** — each `feature` on its own line
4. Enable **Generate pair** — confirm Primary + Secondary, swapped keepalives
5. **Build & Save** — vault shows `_config`, `_diff`, `_risk`
6. Break inputs intentionally (bad CIDR, same keepalive IPs) — must block
7. Compare output to Cisco vPC best practices (peer-gateway, auto-recovery, LACP active)

## Output location

All audit artifacts go to:

```
docs/06-quality-assurance/zero-trust-review/
├── ZERO_TRUST_360_AUDIT_REPORT.md
├── GAP_REGISTER.md
├── REMEDIATION_ROADMAP.md
└── NETWORK_TEAM_TEST_CHECKLIST.md
```

## Severity definitions

- **CRITICAL** — Wrong config shipped / data loss / security hole
- **HIGH** — Major UX or validation gap; workaround exists
- **MEDIUM** — Polish, docs drift, missing scenarios
- **LOW** — Nice-to-have

## Chaining (mandatory)

```
User request / release
  → nxos-orchestrator (route)
  → nst-zero-trust-network-council (360 audit)
  → nxos-zero-trust-review-team (Configurator checklist)
  → nst-gap-remediation-workflow (fix plan)
  → nst-release-engineer (ship)
```

Load full council composition from `.cursor/skills/nst-zero-trust-network-council/SKILL.md` table.

## References

- Cisco vPC best practices (Nexus 9000)
- `docs/03-disaster-recovery/OFFLINE_RUNBOOK.md`
- `.cursor/skills/nxos-config-engineer/SKILL.md`
