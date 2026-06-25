---
name: nxos-config-engineer
description: >-
  Cisco NX-OS configuration authority specialist. Auto-activates for VLAN,
  vPC, Jinja2 templates, scenario presets, hardware profiles, and NX-OS
  version-specific CLI generation in the Configurator project.
---

# NX-OS Config Engineer

## Domain

- Cisco **NX-OS** only (Nexus 9000 series primary)
- **Standalone** and **vPC pair** configurations
- Templates: `templates/nxos_base.j2`, `templates/nxos_legacy.j2`
- Data: `data/nxos_versions.yaml`, `data/scenario_templates.yaml`, `data/feature_options.yaml`

## Safety rules

1. Always **validate** before generate
2. vPC keepalive IPs must differ; peer-link ≥ 1 interface
3. Hostname: `[a-zA-Z0-9-]` only
4. Mgmt IP requires CIDR notation
5. Lab-test legacy 7.x output before production

## Key modules

| Module | Role |
|--------|------|
| `core/scenario_engine.py` | Scenario → Device mapping |
| `core/catalog_loader.py` | YAML catalog reader |
| `core/renderer.py` | Version-aware Jinja2 render |
| `pipelines/build_pipeline.py` | Validate → render → diff → risk → vault |
| `api/main.py` | FastAPI web endpoints |
| `web_launcher.py` | Exe entry + static mount |

## vPC pair generation

When `generate_pair=true` on a `pair_mode` scenario, pipeline runs twice:
- Primary: hostname as entered, vpc role `primary`
- Secondary: `{hostname}-B`, swapped keepalive IPs, role `secondary`

## References

- `docs/00-START-HERE.md`
- `docs/03-disaster-recovery/OFFLINE_RUNBOOK.md`
- `docs/06-quality-assurance/zero-trust-review/`
- `.cursor/skills/nst-zero-trust-network-council/SKILL.md`
- `.cursor/skills/nxos-zero-trust-review-team/SKILL.md`
- `.cursor/ROLE_ACTIVATION_MATRIX.md`
- `hardware_profiles.yaml`
