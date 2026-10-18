---
name: nst-python-backend
description: >-
  Python backend lead for Network Swiss Tool Pro. Auto-activates for vlan_checker_web,
  adapters, plugins, utils, Flask routes, threading, and netmiko device adapters.
---

# NST Python Backend Lead

## Conventions

- Match existing module style in `modules/` and `utils/`
- Minimize diff scope; reuse `adapters.py` and `vlan_mgmt_production.py`
- Thread entrypoints in `vlan_checker_web.py` → register `task_control_plane`
- Absolute imports in `utils/` (no broken relative imports in flat packages)

## Plugin pattern

- Metadata in plugin file AST block
- `run(device, user, pwd, enb_pwd, params, log_func)` signature
- Register in PyInstaller `hiddenimports`

## DBA / data note

NST is file-based (inventory txt, JSON manifests, HTML reports) — no production SQL.
For credential vault or future DB: apply `database-admin` / `postgresql` skills from catalog.

## References

- `.cursor/skills-devin/python-pro/SKILL.md`
- `.cursor/skills-devin/code-reviewer/SKILL.md`
- `.cursor/skills-devin/backend-architect/SKILL.md`
