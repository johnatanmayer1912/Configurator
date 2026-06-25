# Cable Plan — DC-LEAF-01-A

**Site:** HQ_DC  
**Model:** Nexus 93180YC-EX  
**Scenario:** vPC Leaf Pair (Primary + Secondary)  
**Generated:** 2026-06-23T11:15:44Z  
**vPC peer:** DC-LEAF-01-B  

## Instructions

1. Label both ends of each cable before rack install.
2. Peer-link and keepalive connect only between the two vPC switches.
3. Uplinks go to the spine pair; downlinks to dual-homed leaf/access pairs.
4. Fill in **Remote port** on site copy when patched.

## Wiring table

| Local device | Local port | Port-channel | Role | Remote device | Remote port | Cable |
|--------------|------------|--------------|------|---------------|-------------|-------|
| DC-LEAF-01-A | Ethernet1/53 | port-channel1 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | SFP+/QSFP per model (fiber) |
| DC-LEAF-01-A | Ethernet1/54 | port-channel1 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | SFP+/QSFP per model (fiber) |
| DC-LEAF-01-A | Ethernet1/47 | port-channel2 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | DAC/AOC per site standard |
| DC-LEAF-01-A | Ethernet1/48 | port-channel2 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | DAC/AOC per site standard |
| DC-LEAF-01-A | Ethernet1/1 | port-channel22 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | DAC/AOC per site standard |
| DC-LEAF-01-A | Ethernet1/2 | port-channel22 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | DAC/AOC per site standard |
| DC-LEAF-01-A | Ethernet1/1 | port-channel22 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | DAC/AOC per site standard |
| DC-LEAF-01-A | Ethernet1/2 | port-channel22 | downlink | LEAF_PAIR (dual-homed) | — (label during install) | DAC/AOC per site standard |
| DC-LEAF-01-A | Ethernet1/49 | port-channel30 | uplink | SPINE_PAIR (both switches) | — (label during install) | SFP+/QSFP per model (fiber) |
| DC-LEAF-01-A | Ethernet1/50 | port-channel30 | uplink | SPINE_PAIR (both switches) | — (label during install) | SFP+/QSFP per model (fiber) |

## Post-patch verification

```
show interface status
show port-channel summary
show vpc brief
```