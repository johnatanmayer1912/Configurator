# NX-OS Configuration Authority — Hardware Profiles Reference

**v3.0** — Each profile includes `device_class`, `primary_speed_label`, and `speed_badges` for Configuration Studio UI.

| Model | Class | Speed badge | Use |
|-------|-------|-------------|-----|
| Nexus 9336C-FX2 | core | 40G | Core/spine vPC |
| Nexus 93180YC-EX | leaf_10g | 10G | Leaf/ToR vPC |
| Nexus 9348GC-FXP | leaf_1g | 1G | Access |
| Nexus 9364C-GX | leaf_10g | 25G | High-speed leaf |
| Nexus 92348GC-X | leaf_1g | 1G | Legacy access |

See [CONFIG_MATRIX](02-quick-reference/CONFIG_MATRIX.md) for scenario × model matrix.

---

## Supported Models

### Nexus 93180YC-EX

| Attribute | Value |
|-----------|-------|
| **Total Ports** | 54 |
| **Form Factor** | 1RU |
| **Recommended Use** | Access layer, ToR (Top of Rack) leaf |

**Port Groups:**

| Port Range | Speed | Transceiver | Count |
|------------|-------|-------------|-------|
| Ethernet1/1–48 | 10/25G | SFP+ | 48 |
| Ethernet1/49–54 | 40/100G | QSFP28 | 6 |

**vPC Ports:**

| Role | Ports |
|------|-------|
| Peer-Link | Ethernet1/53, Ethernet1/54 |
| Keepalive | Ethernet1/47, Ethernet1/48 |

**Notes:** The 48 × 10/25G downlink ports are ideal for server connectivity. The 6 × 40/100G uplink ports connect to spine switches. Ports 53–54 are reserved for the vPC peer-link; ports 47–48 are reserved for the out-of-band keepalive link.

---

### Nexus 9336C-FX2

| Attribute | Value |
|-----------|-------|
| **Total Ports** | 36 |
| **Form Factor** | 1RU |
| **Recommended Use** | Spine layer, high-density 100G aggregation |

**Port Groups:**

| Port Range | Speed | Transceiver | Count |
|------------|-------|-------------|-------|
| Ethernet1/1–36 | 40/100G | QSFP28 | 36 |

**vPC Ports:**

| Role | Ports |
|------|-------|
| Peer-Link | Ethernet1/35, Ethernet1/36 |
| Keepalive | Ethernet1/33, Ethernet1/34 |

**Notes:** All 36 ports are 40/100G QSFP28, making this model ideal for spine-layer deployments with high-bandwidth leaf-to-spine links. Ports 35–36 are reserved for the vPC peer-link; ports 33–34 for keepalive.

---

### Nexus 9348GC-FXP

| Attribute | Value |
|-----------|-------|
| **Total Ports** | 54 |
| **Form Factor** | 1RU |
| **Recommended Use** | Access layer with 1G Base-T server connectivity |

**Port Groups:**

| Port Range | Speed | Transceiver | Count |
|------------|-------|-------------|-------|
| Ethernet1/1–48 | 1G | Base-T (RJ45) | 48 |
| Ethernet1/49–52 | 10/25G | SFP28 | 4 |
| Ethernet1/53–54 | 40/100G | QSFP28 | 2 |

**vPC Ports:**

| Role | Ports |
|------|-------|
| Peer-Link | Ethernet1/53, Ethernet1/54 |
| Keepalive | Ethernet1/47, Ethernet1/48 |

**Notes:** The 48 × 1G Base-T ports are ideal for legacy server connectivity or IoT/OT environments. The 4 × 10/25G SFP28 ports provide uplink flexibility. Ports 53–54 (40/100G) are reserved for the vPC peer-link.

---

### Generic

| Attribute | Value |
|-----------|-------|
| **Total Ports** | User-defined |
| **Form Factor** | N/A |
| **Recommended Use** | Lab environments, custom hardware, simulation |

**Port Groups:** Operator-specified via the Hardware Setup view:
- 1G port count
- 10G port count
- 40G port count

**vPC Ports:** None defined by default. Override manually in VPC Config view if needed.

**Notes:** The Generic profile generates a sequential interface list based on the specified port counts. Interfaces are named `Ethernet1/1` through `Ethernet1/N` for 1G, `Ethernet2/1` through `Ethernet2/N` for 10G, and `Ethernet3/1` through `Ethernet3/N` for 40G.

---

## YAML Schema Reference

Each profile in `hardware_profiles.yaml` follows this structure:

```yaml
profiles:
  - name: "Model Name"           # Display name (string)
    total_ports: 54               # Total physical port count (integer)
    port_groups:                  # List of port group definitions
      - speed: "10/25G"           # Speed string displayed in UI
        start: 1                  # First port index (1-based, inclusive)
        end: 48                   # Last port index (1-based, inclusive)
        type: "SFP+"              # Transceiver type string
    vpc_peer_link:                # List of peer-link port names
      - "Ethernet1/53"
      - "Ethernet1/54"
    vpc_keepalive:                # List of keepalive port names
      - "Ethernet1/47"
      - "Ethernet1/48"
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Model display name; must match `NexusModel` constants |
| `total_ports` | integer | Total physical port count |
| `port_groups[].speed` | string | Speed label shown in UI (e.g., "10/25G", "40/100G", "1G") |
| `port_groups[].start` | integer | First port index in this group (1-based) |
| `port_groups[].end` | integer | Last port index in this group (1-based, inclusive) |
| `port_groups[].type` | string | Transceiver type (e.g., "SFP+", "QSFP28", "Base-T") |
| `vpc_peer_link` | list[string] | Full interface names reserved for vPC peer-link |
| `vpc_keepalive` | list[string] | Full interface names reserved for vPC keepalive |

---

## Adding a New Hardware Profile

1. Add a new entry to `hardware_profiles.yaml` following the schema above
2. The `HardwareLoader` will automatically pick it up on next application launch
3. No Python code changes are required
4. If the YAML file is missing, the application falls back to the hardcoded `NexusModel` constants in `models/nexus_models.py`

---

## vPC Port Reservation

When **vPC Pair Mode** is enabled, the Interface Config view automatically excludes all ports listed in `vpc_peer_link` and `vpc_keepalive` from the available interface list. This prevents accidental configuration of infrastructure ports as access or trunk ports.

The VPC Config view displays these ports as read-only with an **Override** toggle for advanced use cases where the default port assignments need to be changed.
