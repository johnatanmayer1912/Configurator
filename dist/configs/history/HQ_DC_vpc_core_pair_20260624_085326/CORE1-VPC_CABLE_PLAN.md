# Cable Plan — CORE1-VPC

**Site:** HQ_DC  
**Model:** Nexus 9336C-FX2  
**Scenario:** vPC Core Pair (40G)  
**Generated:** 2026-06-24T05:53:26Z  
**vPC peer:** CORE1-VPC-B  

## Instructions

1. Label both ends of each cable before rack install.
2. Peer-link and keepalive connect only between the two vPC switches.
3. Uplinks go to the spine pair; downlinks to dual-homed leaf/access pairs.
4. Fill in **Remote port** on site copy when patched.

## Wiring table

| Local device | Local port | Port-channel | Role | Remote device | Remote port | Cable |
|--------------|------------|--------------|------|---------------|-------------|-------|
| CORE1-VPC | Ethernet1/35 | port-channel1 | peer-link | CORE1-VPC-B | — (label during install) | QSFP28 DAC/AOC (40G) |
| CORE1-VPC | Ethernet1/36 | port-channel1 | peer-link | CORE1-VPC-B | — (label during install) | QSFP28 DAC/AOC (40G) |
| CORE1-VPC | Ethernet1/33 | port-channel2 | keepalive | CORE1-VPC-B | — (label during install) | QSFP28 DAC/AOC (40G) |
| CORE1-VPC | Ethernet1/34 | port-channel2 | keepalive | CORE1-VPC-B | — (label during install) | QSFP28 DAC/AOC (40G) |
| CORE1-VPC | Ethernet1/1 | port-channel20 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | QSFP28 DAC/AOC (40G) |
| CORE1-VPC | Ethernet1/2 | port-channel20 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | QSFP28 DAC/AOC (40G) |
| CORE1-VPC | Ethernet1/3 | port-channel21 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | QSFP28 DAC/AOC (40G) |
| CORE1-VPC | Ethernet1/4 | port-channel21 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | QSFP28 DAC/AOC (40G) |

## Post-patch verification

```
show interface status
show port-channel summary
show vpc brief
```