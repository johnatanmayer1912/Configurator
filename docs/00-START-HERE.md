# NX-OS Configuration Authority — Start Here

**Version:** 3.0.0 · **Platform:** Web (Configuration Studio) · **Offline:** Yes (single exe)

## What this program does

Generates validated Cisco NX-OS CLI configurations for:

- **Standalone** access, leaf, and spine switches
- **vPC pairs** (primary + secondary) with peer-link and keepalive
- Multiple **NX-OS versions** (9.3, 10.2, 10.3, legacy 7.0)

## Fastest path to a config

1. **Run the program**
   - From source: `python web_launcher.py`
   - From exe: double-click `NXOS_Configurator_Web_v*.exe`
2. Browser opens at `http://127.0.0.1:9000`
3. **Step 1** — Pick a scenario (e.g. *vPC Core Pair 40G*)
4. **Steps 2–4** — Configuration Studio cards; live preview updates on the right
5. **Action Required** — Fill Advanced fields (SNMP, location) until panel is clear
6. **Step 5** — Validate → Build Configuration

## Documentation map

| Folder | Purpose |
|--------|---------|
| [01-user-manual](01-user-manual/CONFIGURATION_STUDIO.md) | Configuration Studio guide |
| [02-quick-reference](02-quick-reference/CONFIG_MATRIX.md) | Scenario × model matrix |
| [03-disaster-recovery](03-disaster-recovery/OFFLINE_RUNBOOK.md) | When things break — recovery steps |
| [04-technical](04-technical/ARCHITECTURE.md) | Architecture & module map |
| [05-scenarios](05-scenarios/SCENARIO_GUIDE.md) | Scenario presets explained |
| [06-quality-assurance/zero-trust-review](06-quality-assurance/zero-trust-review/ZERO_TRUST_360_AUDIT_REPORT.md) | Zero-trust audit, gaps, roadmap |

## Skills & AI governance

Imported from Net Management Tool V6 (4335 files in `.cursor/`):

- `.cursor/ROLE_ACTIVATION_MATRIX.md` — when to activate each skill
- `.cursor/KNOWLEDGE_BASE_INDEX.md` — skill library index
- `.cursor/skills/nxos-orchestrator/` — Configurator project router
- `python scripts/resolve_skill.py <id>` — find deep skills

## Build the offline exe

```powershell
pip install -r requirements.txt
python utils/build_exe.py
```

Output: `dist/NXOS_Configurator_Web_v2.2.0_*.exe`

## Support files

- `data/` — NX-OS versions, scenarios, feature checkboxes
- `hardware_profiles.yaml` — Nexus port layouts & vPC suggestions
- `templates/nxos_base.j2` — Main Jinja2 template
- `.devin/` — AI skill framework (imported from Net Management Tool V6)
