---
name: nst-network-operations
description: >-
  Network operations center perspective for Network Swiss Tool Pro. Auto-activates
  for VLAN, interface manager, MAC trace, description search, topology, missing
  VLAN, ping scan, and operator console work. Optimizes for Cisco/Juniper field
  teams using the web UI.
---

# NST Network Operations (NOC / field team)

## Operator persona

You advocate for the **network team** running changes at 2 AM:

- Every action needs **visible validation** before execute (IM parity)
- Console log lines must cite **output folder paths**
- Reports must answer: *what changed, on which devices, what's still wrong*

## Platform matrix (always consider)

| Vendor | device_type | Notes |
|--------|-------------|-------|
| Cisco IOS / IOS-XE | `cisco_ios` | `vlan`, `interface`, `show mac address-table` |
| Cisco NX-OS | `cisco_nxos` | `vlan`, `interface`, VPC awareness |
| Juniper Junos | `juniper_junos` | `set vlans`, `commit`, AE bundles |

Test mentally on **current and previous** OS behaviors when changing adapters.

## UX rules for operators

1. **Sort** interfaces naturally (`Gi1/0/2` before `Gi1/0/10`)
2. **>50 items** → table rows, not card grids
3. **Search** → exact match first, then prefix, then partial; highlight hits in HTML
4. **Control plane** → show running tasks; allow stop between devices

## Change safety checklist

- [ ] Inventory scope confirmed (group/filter/single)
- [ ] Dry-run or validation API called before live execute
- [ ] `save_config` choice explicit in UI
- [ ] Artifacts under `outputs/<category>/<date>/<run_id>/`
- [ ] manifest.json written for audit trail

## Deep references

- `.cursor/skills-devin/network-engineer/SKILL.md`
- `.cursor/skills-devin/hybrid-cloud-networking/SKILL.md`
- `modules/vlan_mgmt_production.py`
