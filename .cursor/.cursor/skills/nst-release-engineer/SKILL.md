---
name: nst-release-engineer
description: >-
  Release, QA, and PyInstaller discipline for Network Swiss Tool Pro. Auto-activates
  for VERSION bumps, CHANGELOG, _prebuild, enterprise_qa_gate, spec files, EXE builds,
  and vendor compatibility testing matrices.
---

# NST Release Engineer

## Pre-ship gate (mandatory)

```bash
python -m pytest tests/ -q
python _prebuild.py
python scripts/enterprise_qa_gate.py
```

## Version sync checklist

- [ ] `VERSION`
- [ ] `CHANGELOG.md` entry
- [ ] `vlan_checker_web.py` → `UPDATE_DATE`
- [ ] `NetworkSwissToolPro_vX.Y.Z.spec` (copy from prior, bump name)
- [ ] `build_scripts/build_vX.Y.Z.bat` (optional)
- [ ] `dist/NetworkSwissToolPro_vX.Y.Z_OFFLINE.exe`

## Vendor QA matrix (offline + field)

| Area | Cisco IOS/XE | NX-OS | Juniper Junos |
|------|--------------|-------|---------------|
| VLAN add/rename/delete | ✓ | ✓ | ✓ |
| Interface discover | ✓ | ✓ | ✓ |
| MAC trace | ✓ | ✓ | ✓ |
| Description search | ✓ | ✓ | ✓ |
| Topology | ✓ | ✓ | ✓ |

Unit tests prove plumbing; field inventory proves CLI variants.

## PyInstaller notes

- Add new modules to `hiddenimports` in spec
- Add syntax-checked paths in `_prebuild.py`
- Never write runtime data to install directory — `NST_DATA_DIR` / Documents root

## References

- `.cursor/skills-devin/python-testing-patterns/SKILL.md`
- `.cursor/skills-devin/test-driven-development/SKILL.md`
- `.cursor/skills-devin/deployment-engineer/SKILL.md`
