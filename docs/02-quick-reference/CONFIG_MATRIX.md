# Configuration Matrix

Scenario × model × speed tier reference. Source: `data/config_matrix.yaml` + `hardware_profiles.yaml`.

## Matrix

| Scenario | Speed | Class | Default Model | vPC Ports |
|----------|-------|-------|---------------|-----------|
| vPC Core Pair (40G) | 40G | core | Nexus 9336C-FX2 | Eth1/35-36 PL, Eth1/33-34 KA |
| vPC Leaf Pair | 10G | leaf_10g | Nexus 93180YC-EX | Eth1/53-54 PL, Eth1/47-48 KA |
| Standalone Access | 1G | leaf_1g | Nexus 9348GC-FXP | — |
| Standalone Leaf | 10G | leaf_10g | Nexus 93180YC-EX | — |
| Spine / Core | 40G | core | Nexus 9336C-FX2 | — |
| VXLAN/EVPN Leaf | 10G | leaf_10g | Nexus 93180YC-EX | Hardware profile |
| OOB Management | Multi | hybrid | Generic | — |

## vPC port reference by model

| Model | Peer-Link | Keepalive | Primary speed |
|-------|-----------|-----------|---------------|
| Nexus 9336C-FX2 | Ethernet1/35, Ethernet1/36 | Ethernet1/33, Ethernet1/34 | 40G |
| Nexus 93180YC-EX | Ethernet1/53, Ethernet1/54 | Ethernet1/47, Ethernet1/48 | 10G |
| Nexus 9348GC-FXP | Ethernet1/53, Ethernet1/54 | Ethernet1/47, Ethernet1/48 | 1G |
| Nexus 9364C-GX | Ethernet1/53, Ethernet1/54 | Ethernet1/47, Ethernet1/48 | 25G |
| Nexus 92348GC-X | Ethernet1/53, Ethernet1/54 | Ethernet1/47, Ethernet1/48 | 1G |

## Institutional baseline defaults

| Scenario | Default baseline options |
|----------|-------------------------|
| vPC Core Pair | CFS, CoPP, SNMP traps, STP, aliases, ICAM, keepalive VRF |
| vPC Leaf Pair | CFS, CoPP, aliases, SNMP traps |
| Standalone Access | CFS, aliases, SNMP traps |

API: `GET /catalog/matrix`
