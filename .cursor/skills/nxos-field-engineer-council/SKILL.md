---
name: nxos-field-engineer-council
description: >-
  Team of practicing NX-OS network engineers evaluates the Configuration
  Authority wizard end-to-end with real-life scenarios. Finds usage gaps,
  validates CLI against production cutovers, and drives simplicity fixes. Use
  when user asks for field review, real-life configurator audit, network team
  evaluation, gap analysis from operator perspective, or "does this meet
  professional needs".
---

# NX-OS Field Engineer Council

## Mandate

Simulate a **multi-disciplinary network engineering team** that uses NX-OS Configuration Authority the way a real NOC / DC team would — not as developers reading code, but as engineers pasting configs on Nexus 9336C, 93180, and 9348 switches during change windows.

**Goal:** Reassure (with evidence) that every wizard step, toggle, and generated CLI block meets **actual professional needs** — simple, effective, lab-ready first, production-complete when asked.

**Output:** A **Field Gap Register** with prioritized fixes (P0 lab blocker → P2 polish).

## When to invoke

- User asks for field engineer review, real-life scenarios, professional usability audit
- Before shipping a major VERSION bump after UI or scenario changes
- After Action Required, wizard, or template complaints
- User says: "network team review", "field council", "real-life configurator"

## Council roster (every run)

| Role | Lens | Skills to load |
|------|------|----------------|
| **DC Core Lead** | 40G vPC pair, peer-link/keepalive, downlinks Po20/Po21 | `nxos-config-engineer`, `nst-network-operations` |
| **Leaf / ToR Engineer** | 10G vPC leaf, HSRP, access VLANs | `nxos-config-engineer`, `nst-network-operations` |
| **Access / IDF Engineer** | 1G standalone, storm control, uplinks | `nst-network-operations` |
| **Security / Hardening** | CoPP, TACACS+, SNMPv3, no NX-API in prod | `nst-security-ops` |
| **NOC UX Lead** | Wizard steps, Action Required noise, info popups | `nst-product-architect`, `02-nst-ui-ux` rule |
| **Release QA** | pytest, exe bundle, offline assets | `nst-release-engineer` |

Also read: [SCENARIOS.md](SCENARIOS.md) — execute **every** scenario in a session when doing a full audit.

## Execution sequence

### 1. Run the product (mandatory)

```bash
python -m pytest tests/ -q
python web_launcher.py
# or: dist/NXOS_Configurator_Web_v*.exe
```

Walk the wizard: **Mode → vPC → Speed → Configure → Review**. For each scenario in SCENARIOS.md:

1. Complete the roadmap without using Expert scenario picker (primary path)
2. Confirm **Lab ready** in Action Required (not 20+ false items)
3. Copy live CLI preview — spot-check against `docs/05-scenarios/CORE_VPC_GUIDE.md` or production template
4. Build & Save — verify vault output and vPC pair folder layout

### 2. Per-step checklist

| Step | Pass when |
|------|-----------|
| **Mode** | One clear choice; info (i) explains role; no scenario wall |
| **vPC** | Yes/No obvious; skipped for Access/OOB |
| **Speed** | Maps to correct model (9336C / 93180 / 9348) |
| **Configure** | Option B cards; Standard/Hardened presets; toggles match CLI |
| **Review** | Validate before Build; preflight matches lab rules |

### 3. CLI fidelity (code + output)

Verify in `templates/nxos_base.j2`, `core/vpc_topology.py`, `core/scenario_engine.py`:

- vPC domain, peer-link, keepalive match hardware profile
- Unused Ethernet ports: **`no shutdown` only** — no `description SPARE`, no `no switchport` on bare ports
- Institutional baseline (CFS, CoPP, aliases) present when toggled
- No placeholder tokens in lab path unless Production details empty by design
- MOTD and mgmt0 use real wizard values, not `NETWORK_NAME` literals

### 4. Gap register format

```markdown
## Field Gap Register — YYYY-MM-DD

**Version:** (read VERSION)
**pytest:** N passed
**Auditor:** Field Engineer Council

| ID | P | Scenario | Step/Area | Gap | Evidence | Fix direction |
|----|---|----------|-----------|-----|----------|---------------|
| F-001 | P0 | vpc_core_pair | Configure | ... | CLI line / UI | ... |
```

**Priority:**

- **P0** — Wrong or dangerous CLI; lab paste fails; wizard blocked
- **P1** — Missing real-life option; confusing UX; production gap
- **P2** — Polish, docs, info text

### 5. Remediation

For each P0/P1 gap:

1. Propose **minimal** fix (operator-first, not feature sprawl)
2. Implement with `nxos-config-engineer` + `nst-python-backend` + UI rule `02-nst-ui-ux`
3. Add or extend test in `tests/test_*` proving the scenario
4. Update `CHANGELOG.md` and `docs/01-user-manual/CONFIGURATION_STUDIO.md`

## Principles (non-negotiable)

1. **Lab ready ≠ production complete** — Action Required must separate the two
2. **Three clicks to CLI** — Mode + vPC + Speed → Configure shows preview
3. **No false validation** — only explicit placeholders from `data/placeholder_fields.yaml`
4. **Defaults match institutional templates** — CORE1-VPC style: ports up, vPC wiring auto
5. **Every toggle maps to visible CLI** — if it doesn't change output, delete or fix it

## References

- Scenarios: [SCENARIOS.md](SCENARIOS.md)
- CORE template: `docs/05-scenarios/CORE_VPC_GUIDE.md`
- Zero-trust code audit (complementary): `nst-zero-trust-network-council`
- UI audit: `docs/12-master-prompts/roles/UI_UX_AUDIT.md`
