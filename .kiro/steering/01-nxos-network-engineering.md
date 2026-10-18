---
inclusion: fileMatch
fileMatchPattern: ['core/**/*.py', 'templates/**/*.j2', 'data/**/*.yaml', 'hardware_profiles.yaml', 'models/**/*.py']
---

# NX-OS Configuration Authority — Network Engineering Context

When editing templates, scenarios, or core engine:

- **Primary platform:** Cisco NX-OS (Nexus 9000). Legacy 7.x uses `nxos_legacy.j2`.
- **vPC best practices:** Peer-link on dedicated ports (from `hardware_profiles.yaml`), not uplinks. LACP active. peer-gateway + auto-recovery on 9.x+.
- **Validate before generate:** `/scenario/preview` and `DeviceValidator` must pass before vault write.
- **vPC pair:** `validate_vpc_pair()` required before secondary `pipeline.execute()`.
- **Feature lines:** Each `feature` command on its own line in Jinja2 (block form, not inline trim).
- **Outputs:** `configs/history/` via `utils/app_dirs.get_history_dir()` — never CWD-relative.

Reference skills:
- `.cursor/skills/nxos-config-engineer/SKILL.md`
- `.cursor/skills/nst-network-operations/SKILL.md`
- `.devin/skills/network-engineer/SKILL.md`
