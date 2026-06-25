# Configuration Studio — Operator Guide

**Version 4.1.0** · vPC at 40G / 10G / 1G

## Fabric links (v4.1)

On **Configure**, the **Fabric links** card lets you edit downlinks and uplinks without leaving the wizard:

| Section | When shown | Default |
|---------|------------|---------|
| **Downlinks** | Core vPC (`vpc_core_pair`) | Po20 (10G leaf) · Po21 (1G leaf) |
| **Uplinks** | vPC leaf/access, standalone leaf/access | Po30 on Eth1/49–50 (fiber pool) |

- Toggle each row **On/Off**, edit **Po**, **vPC**, **Members**, and **Description**
- **Expand** converts ranges like `Ethernet1/49-50` to explicit ports
- **+ Add downlink / uplink** for custom bundles
- Fiber defaults on 93180/9348 use ports **49–54**, excluding peer-link and keepalive

## Change package (v4)

Every **Build & Save** writes a change-window folder:

| Artifact | Purpose |
|----------|---------|
| `*_config.txt` | Paste-ready NX-OS CLI |
| `*_device.json` | Structured device model for automation |
| `manifest.json` | Site, scenario, hosts, lab_ready, file list |
| `CHANGE_PACKAGE.md` | Rollback notes, vPC pair paste order, checklist |

vPC pair builds use a timestamped subfolder with primary + secondary files.

## Custom port map

On **Configure**, open the **vPC wiring** card:

1. Enable **Customize port map** (auto-on for **Generic** model).
2. Enter peer-link / keepalive ports or ranges (e.g. `Ethernet1/53-54`).
3. Click **Expand** then **Apply port map**.

Hardware profiles still auto-fill ports when customize is off.

## Vault filters

Filter saved artifacts by **hostname**, **site**, **scenario**, or type (**config**, **manifest**, **package**, **json**).

## vPC by speed tier

| Roadmap path | Scenario | Model | vPC ports (auto) |
|--------------|----------|-------|------------------|
| Core · vPC Yes | `vpc_core_pair` | Nexus 9336C-FX2 | Peer Eth1/35–36 · KA Eth1/33–34 |
| Leaf · vPC Yes | `vpc_leaf_pair` | Nexus 93180YC-EX | Peer Eth1/53–54 · KA Eth1/47–48 |
| Access · vPC Yes | `vpc_access_pair` | Nexus 9348GC-FXP | Peer Eth1/53–54 · KA Eth1/47–48 |
| Access · vPC No | `standalone_access` | Nexus 9348GC-FXP | — (48 access ports by default) |

All vPC pair scenarios default to **infra only** (domain + peer-link + keepalive + uplinks). Use **Interface Planner** to add closet/server ports.

## Stop / upgrade

| Action | How |
|--------|-----|
| Stop from UI | Header **Stop** (localhost only) |
| Stop from console | **Ctrl+C** or close window |
| Kill stuck instance | `scripts\stop_configurator.ps1` or `exe --stop` |
| New version over old | `exe --replace` |

## Interface Planner

On **vPC pair** scenarios (40G core, 10G leaf, 1G access), access/trunk presets **default to vPC port-channel (Po ≥ 10)** — mirrored on secondary when you **Export primary + secondary files**. Storm control applies on access port-channels. Enter **VLAN ID** for access mode.

## HSRP gateway

When **HSRP** is enabled (feature grid), use the **Gateway SVI (HSRP)** card on Configure: VLAN ID + SVI IP (CIDR). Live preview adds standby VIP automatically.

## Expert / VXLAN

**VXLAN/EVPN Leaf** is under **Expert** on Step 1 — not on the guided roadmap. Use for overlay lab work; validate BGP EVPN underlay before production.

## Export vs preview

**Live preview** always shows the current switch. **Export primary + secondary files** (Configure step) adds the `-B` secondary config to the build folder.

See CHANGELOG v3.6–v3.7 for preset details.

## Workflow

1. **Mode** (Core / Leaf / Access / OOB)
2. **vPC** (Yes or No — shown for Core, Leaf, and Access)
3. **Speed** (auto for single-tier roles)
4. **Configure** → **Review** → **Build**

See also: [CORE_VPC_GUIDE](../05-scenarios/CORE_VPC_GUIDE.md) · [RELEASE_QA_GATE](../06-quality-assurance/RELEASE_QA_GATE.md)
