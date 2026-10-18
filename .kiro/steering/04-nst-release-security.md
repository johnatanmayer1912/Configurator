---
inclusion: fileMatch
fileMatchPattern: ['tests/**/*.py', 'utils/build_exe.py', '*.spec', 'api/main.py', 'web_launcher.py']
---

# Release & Security Context

Before shipping:

1. `python -m pytest tests/ -v` — all pass
2. `python utils/build_exe.py` — offline exe builds
3. Verify `/validate` and mutation endpoints require auth token
4. Server binds `127.0.0.1` only
5. Bump `VERSION`, `CHANGELOG.md`, sync `web_launcher.py` banner
6. Run zero-trust checklist: `docs/06-quality-assurance/zero-trust-review/NETWORK_TEAM_TEST_CHECKLIST.md`

Reference: `.cursor/skills/nst-release-engineer/SKILL.md`, `.cursor/skills/nst-security-ops/SKILL.md`
