# Quality Assurance — Documentation Index

This folder contains **verification and trust** documentation — not generated configs.

## Related documents

- **[MANDATORY_RELEASE_TESTS.md](MANDATORY_RELEASE_TESTS.md)** — living council test list (`data/release_qa_manifest.yaml`)
- **[RELEASE_QA_GATE.md](RELEASE_QA_GATE.md)** — mandatory pre-release gate (`enterprise_qa_gate.py`)
- [REVALIDATION_POST_SKILL_IMPORT_2026-06-21.md](zero-trust-review/REVALIDATION_POST_SKILL_IMPORT_2026-06-21.md) — Latest council revalidation
- [ZERO_TRUST_360_AUDIT_REPORT.md](zero-trust-review/ZERO_TRUST_360_AUDIT_REPORT.md) — Full 360° audit
- [GAP_REGISTER.md](zero-trust-review/GAP_REGISTER.md) — Tracked issues by severity (OPEN/FIXED)
- [REMEDIATION_ROADMAP.md](zero-trust-review/REMEDIATION_ROADMAP.md) — 4-phase plan to world-class
- [NETWORK_TEAM_TEST_CHECKLIST.md](zero-trust-review/NETWORK_TEAM_TEST_CHECKLIST.md) — Repeatable sign-off protocol

## When to run zero-trust review

- Before every release (VERSION bump)
- After template or API changes
- After adding scenarios or hardware profiles

## Pre-ship (mandatory)

```powershell
python scripts/run_mandatory_qa.py --pre-release   # before VERSION bump
python scripts/enterprise_qa_gate.py             # before exe (auto-runs from build_exe)
python utils/build_exe.py
```

## On every code change

```powershell
pip install pre-commit && pre-commit install      # once per clone
python scripts/run_mandatory_qa.py --on-change    # manual fast gate
```

## Skills

- `.cursor/skills/nxos-zero-trust-review-team/SKILL.md` — activates review council
- `.cursor/skills/nxos-config-engineer/SKILL.md` — domain engineering
- `.cursor/skills/nst-release-engineer/SKILL.md` — VERSION, CHANGELOG, exe
