# vPC Core Pair — CORE1_VPC Template Guide

Production-aligned preset for dual 40G core switches.

## Template mapping

| CORE1_VPC element | Configurator field / default |
|-------------------|------------------------------|
| hostname CORE1_VPC | Step 2 hostname (use hyphens: CORE1-VPC) |
| vpc domain 100 | vPC Domain ID = 100 |
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
| CLI aliases wr/shint/shintd | Baseline: CLI Aliases |
| SNMP trap baseline | Baseline: SNMP Trap Baseline |
| cfs eth distribute | Baseline: CFS Ethernet Distribute |

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
