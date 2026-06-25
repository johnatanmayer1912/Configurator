# Scenario Guide — Network Engineer Presets

Scenarios live in `data/scenario_templates.yaml`. Each encodes role, redundancy, defaults, and help text.

## Standalone Access Switch

- **Role:** access
- **Use:** IDF, user port aggregation
- **Default model:** Nexus 9348GC-FXP (48x1G)
- **Features:** interface-vlan, LLDP, LACP, storm-control

## Standalone Leaf

- **Role:** leaf without vPC
- **Use:** lab racks, staging, single-homed designs
- **Features:** + HSRP for SVI redundancy (single switch)

## vPC Leaf Pair ★ (most common DC pattern)

- **Role:** leaf + vPC
- **Pair mode:** generates **two** configs (Primary `-A`, Secondary `-B`)
- **Check:** Generate vPC pair on Step 2
- **Defaults:** domain 100, peer-link Po100, ports from hardware profile
- **Features:** vPC, peer-gateway, auto-recovery, ARP sync

### vPC checklist before paste

- [ ] Keepalive on dedicated link or mgmt VRF — IPs reachable
- [ ] Peer-link ports match physical cabling
- [ ] Domain ID matches on both peers
- [ ] Primary role on intended switch

## Spine / Core

- Minimal VLAN footprint; routed uplinks focus
- Model default: Nexus 9336C-FX2

## OOB Management

- Bare minimum for initial provisioning
- Expand later via Advanced section or new scenario run

## Adding a custom scenario

1. Edit `data/scenario_templates.yaml`
2. Add block under `scenarios:` with unique `id`
3. Restart web server (or rebuild exe)
4. Document in this file
