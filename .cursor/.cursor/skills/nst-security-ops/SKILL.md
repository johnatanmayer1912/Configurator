---
name: nst-security-ops
description: >-
  Security and change-control for Network Swiss Tool Pro. Auto-activates for
  credentials, SSH, enable passwords, config backup, VLAN/interface mutations,
  and audit features.
---

# NST Security Operations

## Trust boundaries

- Credentials flow through UI → API → netmiko; never log passwords
- Warn before destructive VLAN delete
- Dry-run and validation pipelines are **security controls**, not UX fluff

## Change control

1. Pre-change backup (`utils/config_backup_system.py`) when `auto_backup=True`
2. Validation before execute (`/api/vlan/validate`, `/api/interface/validate`)
3. Operator double-checkbox consent on production mutations
4. Artifacts retained under user data root for forensics

## Review triggers

- New API route accepting credentials
- New file write paths (must use `output_paths`)
- Plugin executing device commands
- Control plane cancel (cooperative, not kill -9 on SSH)

## References

- `.cursor/skills-devin/security-auditor/SKILL.md`
- `.cursor/skills-devin/security-and-hardening/SKILL.md`
- sickn33 `007` persona in `.cursor/skills-sickn33/` if deep threat modeling needed
