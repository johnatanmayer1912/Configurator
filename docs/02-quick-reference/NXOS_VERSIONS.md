# NX-OS Version Quick Reference

| Version | Template | vPC Peer-Gateway | vPC Auto-Recovery | HSRP | Notes |
|---------|----------|------------------|-------------------|------|-------|
| 9.3.x ★ | nxos_base.j2 | Yes | Yes | v2 | Recommended baseline |
| 10.2.x | nxos_base.j2 | Yes | Yes | v2 | Current generation |
| 10.3.x | nxos_base.j2 | Yes | Yes | v2 | Lab validate first |
| 7.0.x | nxos_legacy.j2 | No | No | v1 | Legacy switches |

## Editing versions

File: `data/nxos_versions.yaml`

Add a new block under `versions:` with `id`, `label`, `template`, `notes`, and `features`.

## Feature checkbox mapping

File: `data/feature_options.yaml`

Each checkbox `id` must match what the Jinja2 template expects in `core/renderer.py` `_feature_flags()`.
