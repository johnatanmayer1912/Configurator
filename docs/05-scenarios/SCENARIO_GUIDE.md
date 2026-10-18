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

## Multi-Switch Deployment (v6.14.0+)

### Port Configuration by Switch Type

#### 1GB Leaf Switches (Nexus 9348GC-FXP)
- **Keepalive**: Ethernet1/47-48
- **Peer-link**: Ethernet1/49-50
- **Uplinks**: Ethernet1/51-52
  - Port 51 → Core1 port 1
  - Port 52 → Core2 port 1

#### 10GB Leaf Switches (Nexus 93180YC-EX)
- **Keepalive**: Ethernet1/49-50
- **Peer-link**: Ethernet1/51-52
- **Uplinks**: Ethernet1/53-54
  - Port 53 → Core1 port 1
  - Port 54 → Core2 port 1

#### Core Switches (Nexus 9336C-FX2)
- **Keepalive**: Ethernet1/33-34
- **Peer-link**: Ethernet1/35-36
- **Downlinks for 10GB leaves**: Ethernet1/1-10
- **Downlinks for 1GB leaves**: Ethernet1/11-20

### Keepalive IP Configuration (v6.14.0+)

- **Manual Entry**: Specify local and remote keepalive IPs in the vPC wiring card
- **Auto-Generation**: Enable "Use default keepalive IP for vPC" checkbox for automatic IP generation based on vPC domain
- **Validation**: System validates keepalive IPs are present, valid IPv4 addresses, and unique within each vPC domain (IPs can be reused across different vPC domains per Cisco NX-OS behavior)

### Domain ID Management (v6.14.0+)

- vPC domain ID can be edited in multi-switch environments via the switch edit modal
- Domain ID must be between 1 and 4096
- Both switches in a vPC pair must have matching domain IDs

## Adding a custom scenario

1. Edit `data/scenario_templates.yaml`
2. Add block under `scenarios:` with unique `id`
3. Restart web server (or rebuild exe)
4. Document in this file
