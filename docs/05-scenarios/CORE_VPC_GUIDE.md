# vPC Core Pair — CORE1_VPC Template Guide

Production-aligned preset for dual 40G core switches.

## Template mapping

| CORE1_VPC element | Configurator field / default |
|-------------------|------------------------------|
| hostname CORE1_VPC | Step 2 hostname (use hyphens: CORE1-VPC) |
| vpc domain 100 | vPC Domain ID = 100 (editable in multi-switch mode) |
| peer-switch | Feature: vPC Peer-Switch |
| role priority 1000 / 2000 | Primary/secondary auto on pair build |
| system-priority 20000 | Scenario default |
| delay restore 150 | Feature: vPC Delay Restore |
| peer-keepalive vrf VPC_Keep_Alive | Keepalive VRF + baseline option |
| port-channel1 peer-link | Peer-Link Po ID = 1 |
| port-channel2 keepalive L3 | Keepalive Po ID = 2 |
| port-channel20 → 10G leaves | Downlink: 10G Leaf Pair (editable in **Fabric links**) |
| port-channel21 → 1G leaves | Downlink: 1G Leaf Pair (editable in **Fabric links**) |
| port-channel30 → spine (leaf) | Uplink: Fiber uplink pair — Eth1/49–50 default on 93180/9348 |
| port-channel10 → spine (core) | Uplink: Spine uplink pair — optional on 9336C |
| Eth1/33-36 (9336C) | Auto from hardware profile |
| Eth1/1-10 (9336C) | Downlink ports for 10GB leaf switches (v6.14.0+) |
| Eth1/11-20 (9336C) | Downlink ports for 1GB leaf switches (v6.14.0+) |
| CLI aliases wr/shint/shintd | Baseline: CLI Aliases |
| SNMP trap baseline | Baseline: SNMP Trap Baseline |
| cfs eth distribute | Baseline: CFS Ethernet Distribute |

## v6.14.0 Updates

### Multi-Switch Deployment
- **Domain ID Edit**: vPC domain ID can now be changed in multi-switch environments via the edit switch modal
- **Keepalive IP Options**: Added "Use default keepalive IP for vPC" checkbox for automatic IP generation
- **Keepalive Validation**: Enhanced validation ensures keepalive IPs are present and valid in all vPC scenarios

### Port Configuration Logic (v6.14.0+)

#### 1GB Leaf Switches (Nexus 9348GC-FXP)
- **Keepalive ports**: Ethernet1/47-48
- **Peer-link ports**: Ethernet1/49-50
- **Uplink ports**: Ethernet1/51-52 (to core switches)
  - Port 51 → Core1 port 1
  - Port 52 → Core2 port 1

#### 10GB Leaf Switches (Nexus 93180YC-EX)
- **Keepalive ports**: Ethernet1/49-50
- **Peer-link ports**: Ethernet1/51-52
- **Uplink ports**: Ethernet1/53-54 (to core switches)
  - Port 53 → Core1 port 1
  - Port 54 → Core2 port 1

#### Core Switch Downlinks (Nexus 9336C-FX2)
- **10GB leaf downlinks**: Ethernet1/1-10 (for 10GB leaf uplinks)
- **1GB leaf downlinks**: Ethernet1/11-20 (for 1GB leaf uplinks)
- **Mixed deployments**: Automatically separates 10GB and 1GB leaf connections to appropriate port ranges

## Before production paste

Use the **Action Required** panel to resolve:

1. Management IP and gateway (mgmt0)
2. Site / rack location
3. SNMP trap hosts and v3 username (Advanced card)
4. Confirm boot image matches `show boot`
5. Replace lab passwords with TACACS+ / AAA

## Pair build

Enable **Export primary + secondary files** on **Step 4 (Configure)**. Output folder contains primary + secondary with swapped keepalive IPs. Live preview always shows the current switch; export adds the `-B` secondary file.

## Related

- [CONFIGURATION_STUDIO](../01-user-manual/CONFIGURATION_STUDIO.md)
- [CONFIG_MATRIX](../02-quick-reference/CONFIG_MATRIX.md)
- [HARDWARE_PROFILES](../HARDWARE_PROFILES.md)
