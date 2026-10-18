# NX-OS Configuration Authority — Start Here

**Version:** 6.46.4 · **Platform:** Web (Configuration Studio) · **Offline:** Yes (single exe)

## What this program does

Generates validated Cisco NX-OS CLI configurations for:

- **Standalone** access, leaf, spine, and core switches
- **vPC pairs** (primary + secondary) with peer-link and keepalive
- **Multi-switch topologies** (spine-leaf, 3-tier, custom deployments)
- **Template-based deployments** with one-click configuration
- Multiple **NX-OS versions** (9.3, 10.2, 10.3, legacy 7.0)

## Fastest path to a config

### Single-Switch Mode (Quick)

1. **Run the program**
   - From source: `python web_launcher.py`
   - From exe: double-click `NXOS_Configurator_Web_v*.exe`
2. Browser opens at `http://127.0.0.1:9000`
3. **Step 1** — Pick a scenario (e.g. *vPC Core Pair 40G*)
4. **Steps 2–4** — Configuration Studio cards; live preview updates on the right
5. **Action Required** — Fill Advanced fields (SNMP, location) until panel is clear
6. **Step 5** — Validate → Build Configuration

### Multi-Switch Mode (Templates)

1. **Run the program**
2. Click **Mode: Quick** → Select **Multi-Switch**
3. **Template Gallery** — Select a deployment template
4. **Customize Network** — Edit switches, vPC domains, VLANs, uplinks
5. **Generate Config** — Generate all switch configurations
6. **Open Output Folder** — Access generated configuration files

## Documentation map

| Folder | Purpose |
|--------|---------|
| [01-user-manual](01-user-manual/CONFIGURATION_STUDIO.md) | Configuration Studio guide |
| [01-user-manual](01-user-manual/QUICK_START.md) | Quick start guide |
| [02-quick-reference](02-quick-reference/CONFIG_MATRIX.md) | Scenario × model matrix |
| [03-disaster-recovery](03-disaster-recovery/OFFLINE_RUNBOOK.md) | When things break — recovery steps |
| [04-technical](04-technical/ARCHITECTURE.md) | Architecture & module map |
| [04-technical](04-technical/API_REFERENCE.md) | Complete REST API documentation |
| [04-technical](04-technical/FILE_GENERATION_BEHAVIOR.md) | File system output behavior |
| [04-technical](04-technical/VALIDATION_RULES.md) | All validation rules and error conditions |
| [04-technical](04-technical/MULTI_SWITCH_ARCHITECTURE.md) | Multi-switch deployment architecture |
| [05-scenarios](05-scenarios/SCENARIO_GUIDE.md) | Scenario presets explained |
| [MULTI_SWITCH_USER_FLOW](MULTI_SWITCH_USER_FLOW.md) | Multi-switch user flow documentation |
| [TEMPLATE_UX_IMPROVEMENT_PLAN](TEMPLATE_UX_IMPROVEMENT_PLAN.md) | Template UX improvements |
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
pyinstaller NXOS_Configurator_Web_v{VERSION}.spec
```

Output: `dist/NXOS_Configurator_Web_v{VERSION}.exe`

## Support files

- `data/` — NX-OS versions, scenarios, feature checkboxes
- `hardware_profiles.yaml` — Nexus port layouts & vPC suggestions
- `templates/nxos_base.j2` — Main Jinja2 template
- `.devin/` — AI skill framework (imported from Net Management Tool V6)

## Key Features (v6.46.4)

- **Multi-Switch Deployments**: Generate configurations for entire topologies
- **Template System**: Pre-configured deployment templates for common patterns
- **vPC Keepalive Auto-Generation**: Automatic keepalive IP assignment based on domain ID
- **File System Output**: True file generation with configurable output directories
- **Open Folder Integration**: Direct access to generated configuration files
- **Audit Logging**: Comprehensive frontend audit logging for troubleshooting
- **Validation Engine**: Multi-layer validation for configurations and topologies
