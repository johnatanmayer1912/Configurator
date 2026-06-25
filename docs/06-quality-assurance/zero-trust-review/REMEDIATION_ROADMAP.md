# Remediation Roadmap — Path to Best-in-Class NX-OS Configurator

**Target:** Trust score 9.5/10 · **Horizon:** 4 phases · **Updated:** 2026-06-21

---

## Vision

The world's best NX-OS configurator means:

1. **Zero-surprise CLI** — every line lab-verified against target NX-OS version
2. **Dummy-proof UX** — operators cannot submit invalid vPC/access configs
3. **Full offline confidence** — exe + docs + validation with no hidden dependencies
4. **Production-grade options** — AAA, NTP, logging, encrypted secrets (optional)
5. **Fabric-ready** — EVPN/VXLAN scenarios when team needs spine-leaf VXLAN

---

## Phase 1 — Trust foundation (1–2 weeks) ✅ mostly complete

| Task | Priority | Status |
|------|----------|--------|
| Fix feature line rendering | CRITICAL | ✅ Done v2.4.0 |
| Fix vPC peer-link from hardware profile | CRITICAL | ✅ Done v2.4.0 |
| Apply UI vPC overrides to backend | CRITICAL | ✅ Done v2.4.0 |
| vPC pair validation before dual generate | CRITICAL | ✅ Done v2.4.0 |
| Unify vault/history paths | CRITICAL | ✅ Done v2.4.0 |
| CLI preview on Validate | HIGH | ✅ Done v2.4.0 |
| Field hints + wizard tips | HIGH | ✅ Done v2.4.0 |
| Zero-trust audit docs + skill | HIGH | ✅ Done v2.4.0 |
| Sync stale docs to web-first | HIGH | 🔲 H-008 |
| Centralize version from `VERSION` file | MEDIUM | 🔲 M-006 |

**Exit criteria:** Network team signs off on vPC leaf pair lab test using checklist.

---

## Phase 2 — Production hardening (2–4 weeks)

| Task | Deliverable |
|------|-------------|
| pytest suite | `tests/test_scenario_engine.py`, `tests/test_templates.py`, `tests/test_api.py` |
| HSRP on SVIs when feature enabled | VIP/priority from scenario defaults |
| Management baseline template section | NTP, logging, optional SNMP — checkbox driven |
| Password handling | Lab plaintext vs `role network-operator` placeholder; document security |
| Hardened security tier in UI | Disable nxapi/bash by default; stricter storm-control |
| CI gate | Run tests on every change |
| Accessibility pass | focus-visible, step gating, aria labels |

**Exit criteria:** 80%+ test coverage on core pipeline; no CRITICAL/HIGH open gaps.

---

## Phase 3 — Operator excellence (4–6 weeks)

| Task | Deliverable |
|------|-------------|
| Expand hardware profiles | 9364C, 92348, C9232C, etc. |
| Wire advanced manual mode OR remove dead UI | Clear “reference only” or full `/generate-config` integration |
| Checkpoint restore in web vault | Load JSON snapshot → repopulate wizard |
| Alias injection | Selected aliases merge into interface/SVI blocks |
| Risk analyzer tuning | Context-aware severity; suppress known-safe patterns |
| Vault UX | Filter by type, hostname, date; download zip bundle |
| Post-build smoke test in `build_exe.py` | HTTP health + catalog load |

**Exit criteria:** NOC operators complete access + vPC builds in &lt;5 minutes without docs.

---

## Phase 4 — World-class differentiation (6–12 weeks)

| Task | Deliverable |
|------|-------------|
| EVPN/VXLAN leaf scenario | Based on Cisco VXLAN BGP EVPN design guide |
| Config import + diff | Paste running-config → highlight delta vs generated |
| Multi-switch rollout manifest | Single job → N config files + change checklist |
| Compliance packs | STIG-style optional blocks |
| Optional change-control export | Ticket ID in metadata header |
| PWA / enhanced offline | Service worker for static assets refresh |

**Exit criteria:** Team prefers this tool over manual CLI for standard DC leaf/access patterns.

---

## What else is needed (team consensus)

| Need | Why |
|------|-----|
| **Lab validation matrix** | NX-OS 7.0 / 9.3 / 10.2 on real or CML devices |
| **Golden config library** | Known-good outputs per scenario for diff regression |
| **Operator training deck** | 10-slide “first config in 5 minutes” |
| **Release checklist** | Zero-trust skill invoked every version bump |
| **Community scenario contributions** | YAML-only PRs for new deployment patterns |

---

## Success metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time to first valid config | ~8 min | &lt;3 min |
| Invalid config escape rate | Unknown | 0% (blocked at validate) |
| Critical open gaps | 0 | 0 sustained |
| Test coverage | ~0% | ≥80% core |
| Operator NPS (internal) | — | ≥8/10 |

---

See also: [NETWORK_TEAM_TEST_CHECKLIST.md](NETWORK_TEAM_TEST_CHECKLIST.md)
