# Configuration Studio — Operator Guide

**Version 6.46.4** · vPC at 40G / 10G / 1G · Multi-Switch Deployments

## Overview

The Configuration Studio provides two primary modes for generating NX-OS configurations:

1. **Single-Switch Wizard** (Quick Mode): Step-by-step configuration for individual switches
2. **Multi-Switch Templates** (Multi-Switch Mode): Template-based deployment generation for entire topologies

---

## Single-Switch Wizard (Quick Mode)

### Fabric links (v4.1+)

On **Configure**, the **Fabric links** card lets you edit downlinks and uplinks without leaving the wizard:

| Section | When shown | Default |
|---------|------------|---------|
| **Downlinks** | Core vPC (`vpc_core_pair`) | Po20 (10G leaf) · Po21 (1G leaf) |
| **Uplinks** | vPC leaf/access, standalone leaf/access | Po30 on Eth1/49–50 (fiber pool) |

- Toggle each row **On/Off**, edit **Po**, **vPC**, **Members**, and **Description**
- **Expand** converts ranges like `Ethernet1/49-50` to explicit ports
- **+ Add downlink / uplink** for custom bundles
- Fiber defaults on 93180/9348 use ports **49–54**, excluding peer-link and keepalive

### vPC Keepalive Configuration (v6.14.0+)

#### Keepalive IP Options

On the **vPC wiring** card (Step 7), two options are available for keepalive IP configuration:

1. **Manual Entry**: Specify local and remote keepalive IPs directly
   - Local keepalive IP: e.g., `10.255.255.1`
   - Remote keepalive IP: e.g., `10.255.255.2`

2. **Auto-Generation**: Enable "Use default keepalive IP for vPC" checkbox
   - Automatically generates keepalive IPs based on vPC domain ID
   - Format: `10.255.{domain/256}.{domain%256}` (local) and `+1` (remote)
   - Example: Domain 100 → Local `10.255.0.100`, Remote `10.255.0.101`

#### Keepalive Validation

The system validates keepalive IPs in all vPC scenarios:

- **Presence**: Keepalive IPs are required when vPC domain is configured
- **Format**: Must be valid IPv4 addresses (e.g., `10.255.255.1`)
- **Uniqueness**: Local and remote keepalive IPs must be different
- **Domain-based**: When using auto-generation, IPs are derived from vPC domain

#### Domain ID Management (v6.14.0+)

In multi-switch environments, vPC domain ID can be edited via the switch edit modal:

- **Access**: Click "Edit" on a switch in the deployment list
- **Validation**: Domain ID must be between 1 and 4096
- **Consistency**: Both switches in a vPC pair must have matching domain IDs

### Change package (v4)

Every **Build & Save** writes a change-window folder:

| Artifact | Purpose |
|----------|---------|
| `*_config.txt` | Paste-ready NX-OS CLI |
| `*_device.json` | Structured device model for automation |
| `manifest.json` | Site, scenario, hosts, lab_ready, file list |
| `CHANGE_PACKAGE.md` | Rollback notes, vPC pair paste order, checklist |

vPC pair builds use a timestamped subfolder with primary + secondary files.

### Custom port map

On **Configure**, open the **vPC wiring** card:

1. Enable **Customize port map** (auto-on for **Generic** model).
2. Enter peer-link / keepalive ports or ranges (e.g. `Ethernet1/53-54`).
3. Click **Expand** then **Apply port map**.

Hardware profiles still auto-fill ports when customize is off.

### Vault filters

Filter saved artifacts by **hostname**, **site**, **scenario**, or type (**config**, **manifest**, **package**, **json**).

### vPC by speed tier

| Roadmap path | Scenario | Model | vPC ports (auto) |
|--------------|----------|-------|------------------|
| Core · vPC Yes | `vpc_core_pair` | Nexus 9336C-FX2 | Peer Eth1/35–36 · KA Eth1/33–34 |
| Leaf · vPC Yes | `vpc_leaf_pair` | Nexus 93180YC-EX | Peer Eth1/53–54 · KA Eth1/47–48 |
| Access · vPC Yes | `vpc_access_pair` | Nexus 9348GC-FXP | Peer Eth1/53–54 · KA Eth1/47–48 |
| Access · vPC No | `standalone_access` | Nexus 9348GC-FXP | — (48 access ports by default) |

All vPC pair scenarios default to **infra only** (domain + peer-link + keepalive + uplinks). Use **Interface Planner** to add closet/server ports.

### Interface Planner

On **vPC pair** scenarios (40G core, 10G leaf, 1G access), access/trunk presets **default to vPC port-channel (Po ≥ 10)** — mirrored on secondary when you **Export primary + secondary files**. Storm control applies on access port-channels. Enter **VLAN ID** for access mode.

### HSRP gateway

When **HSRP** is enabled (feature grid), use the **Gateway SVI (HSRP)** card on Configure: VLAN ID + SVI IP (CIDR). Live preview adds standby VIP automatically.

### Expert / VXLAN

**VXLAN/EVPN Leaf** is under **Expert** on Step 1 — not on the guided roadmap. Use for overlay lab work; validate BGP EVPN underlay before production.

### Export vs preview

**Live preview** always shows the current switch. **Export primary + secondary files** (Configure step) adds the `-B` secondary config to the build folder.

### Single-Switch Workflow

1. **Mode** (Core / Leaf / Access / OOB)
2. **vPC** (Yes or No — shown for Core, Leaf, and Access)
3. **Speed** (auto for single-tier roles)
4. **Configure** → **Review** → **Build**

---

## Multi-Switch Templates (Multi-Switch Mode)

### Access Multi-Switch Mode

1. Click **Mode: Quick** in the header
2. Select **Multi-Switch** from the dropdown
3. Template Gallery appears with deployment templates

### Template Gallery

**Template Categories:**
- All
- Production DC
- Cloud/VM
- Enterprise Campus

**Template Information:**
- Switch count
- vPC domain count
- VLAN count
- Uplink count
- Complexity badge (simple/medium/complex)
- Hardware compatibility indicators
- Best practice badges

### Template Application

1. **Select Template**: Click on a template card to view details
2. **Apply Template**: Click "Apply Template" to load the deployment
3. **Success Screen**: Visual topology preview with switch counts and configuration summary
4. **Action Buttons**:
   - **Customize Network**: Edit switches, vPC domains, VLANs, uplinks
   - **Generate Config**: Generate all switch configurations
   - **Change Template**: Select a different template
   - **Save as Template**: Save current configuration as custom template

### Configuration Editor

**Tabs:**
- **Switches**: Add, edit, remove switches with role, model, and basic settings
- **vPC Domains**: Add, edit, remove vPC pairs with domain ID and peer links
- **VLANs**: Add, edit, remove VLANs with IDs and names
- **Interfaces**: Configure interface templates (Server Port, IP Phone, AP, iSCSI, Management, LACP)
- **Uplinks**: Add, edit, remove uplinks between switches

**Topology Canvas:**
- Live visualization of switch topology
- Role-based switch colors
- vPC connection indicators
- Uplink visualization

**Interface Templates:**
- Server Port: Access mode with VLAN
- IP Phone: Trunk mode with voice VLAN
- AP: Trunk mode with multiple VLANs
- iSCSI: Access mode with jumbo frames
- Management: Access mode with OOB VLAN
- LACP: Port-channel configuration

**Quick Actions:**
- **Validate**: Validate deployment topology
- **Reset**: Reset to template defaults
- **Save as Template**: Save current configuration as custom template
- **Generate Config**: Generate all switch configurations

### Configuration Generation

**Generation Process:**
1. Validate deployment topology
2. Validate vPC pairs
3. Apply custom uplinks
4. Validate each switch
5. Generate NX-OS configurations
6. Write files to disk
7. Display results panel

**Results Panel:**
- Success/failure count
- Per-switch status
- **View Config**: View CLI configuration for each switch
- **Port Map**: View port assignment table
- **Download**: Download individual configuration file
- **Download All Configs (ZIP)**: Download all configurations (opens folder instead)
- **Open Output Folder**: Open folder in file explorer
- **Close**: Return to configuration editor

### File Output

**Output Directory:** `configs/history/{timestamp}/`

**Files Generated:**
- `{hostname}_config.txt`: NX-OS CLI configuration
- `{hostname}_device.json`: Structured device model
- `manifest.json`: Deployment metadata

**vPC Pair File Sharing:**
- If both vPC peers succeed, one set of files is created
- File naming uses primary switch hostname
- Secondary switch configuration included in primary file

### Custom Templates

**Save Custom Template:**
1. Configure deployment in editor
2. Click "Save as Template"
3. Enter template name and description
4. Template saved to localStorage

**Load Custom Template:**
1. Custom templates are loaded automatically on page load
2. Appear in template gallery with custom badge
3. Can be applied like built-in templates

---

## Common Operations

### Stop / Upgrade

| Action | How |
|--------|-----|
| Stop from UI | Header **Stop** (localhost only) |
| Stop from console | **Ctrl+C** or close window |
| Kill stuck instance | `scripts\stop_configurator.ps1` or `exe --stop` |
| New version over old | `exe --replace` |

### Open Output Folder

After configuration generation, click **Open Output Folder** to access generated files in the system file explorer.

### Download Configurations

The **Download All Configs (ZIP)** button opensthe output folder instead of downloading, providing direct access to all generated files.

---

## See Also

- [API Reference](../04-technical/API_REFERENCE.md)
- [File Generation Behavior](../04-technical/FILE_GENERATION_BEHAVIOR.md)
- [Multi-Switch Architecture](../04-technical/MULTI_SWITCH_ARCHITECTURE.md)
- [Validation Rules](../04-technical/VALIDATION_RULES.md)
- [Multi-Switch User Flow](../MULTI_SWITCH_USER_FLOW.md)
- [CORE_VPC_GUIDE](../05-scenarios/CORE_VPC_GUIDE.md)
