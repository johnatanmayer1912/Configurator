---
name: nxos-config-excellence
description: Generate correct NX-OS CLI with vPC keepalive, peer-link, hardware profiles, Jinja2 rendering, YAML catalogs
triggers: ["nxos", "cisco", "nexus", "vpc", "keepalive", "peer-link", "jinja2", "cli", "config"]
allowed-tools: read_file write_to_file edit bash
---

# NX-OS Configuration Excellence

1. Validate NX-OS CLI syntax. Use correct command structure. No typos.
2. vPC keepalive must be valid IP. Check subnet overlap. No conflicts.
3. vPC peer-link must be port-channel. Verify member ports.
4. vPC domain must be 1-4096. Check for conflicts.
5. Role priority: primary 4096, secondary 8192. Verify assignment.
6. Hardware profiles must match device model. Check port compatibility.
7. Jinja2 rendering must be version-aware. Handle NX-OS 7.x vs 9.x/10.x.
8. YAML catalogs must be valid. Check schema integrity.
9. VLAN ranges must be 1-4094. Validate all VLAN assignments.
10. If the current task needs deeper help in another area, immediately invoke the matching skill before continuing.
