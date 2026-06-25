# Field Engineer Council — Real-Life NX-OS Scenarios

Use these as **acceptance tests** when evaluating Configuration Authority. Each scenario lists operator intent, wizard path, and CLI must-haves.

---

## S1 — 40G Core vPC Pair (institutional)

**Use case:** New dual 9336C core — peer-link, keepalive, leaf downlinks Po20/Po21.

| Field | Value |
|-------|-------|
| Mode | Core / Spine |
| vPC | Yes |
| Speed | 40G |
| Hostname | CORE1-VPC |
| Model | Nexus 9336C-FX2 |

**Must appear in CLI:**

- `vpc domain`, `peer-link`, `peer-keepalive`, `peer-gateway`, `peer-switch`
- `Ethernet1/35-36` peer-link, `Ethernet1/33-34` keepalive (9336C profile)
- `port-channel20` / `port-channel21` downlinks when toggled
- Unused ports: `interface Ethernet1/x` + `no shutdown` only (no SPARE description, no `no switchport`)
- `cfs eth distribute`, `copp profile strict`, baseline aliases

**Lab ready:** mgmt IP/CIDR + gateway filled.  
**Production later:** SNMP trap hosts, rack location in Production details.

---

## S2 — 10G vPC Leaf Pair

**Use case:** Dual-homed ToR for server racks.

| Field | Value |
|-------|-------|
| Mode | Leaf / ToR |
| vPC | Yes |
| Speed | 10G |
| Hostname | DC-LEAF-01-A |
| Generate pair | Yes |

**Must appear:** `feature vpc`, HSRP optional on SVIs, storm control on access, uplink trunks.

---

## S3 — Standalone Leaf (staging)

**Use case:** Single leaf in lab — no vPC domain.

| Mode | Leaf | vPC | No |
| Hostname | DC-LEAF-STAGE-01 |

**Must NOT appear:** `vpc domain`, keepalive VRF.

---

## S4 — 1G Access Closet

**Use case:** IDF switch, access ports + dual uplinks.

| Mode | Access | vPC | No |

**Must appear:** access VLANs, storm control, `Ethernet1/49-50` uplink trunks.

---

## S5 — OOB Bootstrap

**Use case:** Console-first mgmt-only config.

| Mode | Out-of-Band |

**Must appear:** hostname, mgmt0, minimal features.  
**Must NOT:** vPC step noise, large feature grid.

---

## S6 — Hardened production preset

**Use case:** Security review before DC cutover.

1. Complete S1 through Configure
2. Click **Hardened** preset
3. Fill Production details (SNMP, location)

**Must appear:** CoPP, no DNS lookup, no NX-API/bash, TACACS+ comment block, syslog source mgmt0.

---

## S7 — Paste running-config (Config Builder)

**Use case:** Engineer pastes existing `show run` to pre-fill wizard.

**Must detect:** hostname, mgmt IP, vPC domain, peer-link ports if present in paste.

---

## S8 — vPC pair build output

**Use case:** Change window — two files, one folder.

**Must:** Primary + Secondary in timestamped subfolder; secondary hostname `-B` suffix; swapped keepalive IPs.

---

## S9 — Spine / Core standalone (roadmap)

**Use case:** Single 40G spine without vPC — routed fabric role.

| Mode | Core / Spine | vPC | No |

**Must NOT appear:** `vpc domain`, keepalive VRF.

---

## Council sign-off (v4.0.0 — 2026-06-23)

| Scenario | Lab ready | CLI correct | UX clear | pytest | Date |
|----------|-----------|-------------|----------|--------|------|
| S1 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S2 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S3 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S4 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S4b | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S5 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S6 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S7 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S8 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| S9 | ✅ | ✅ | ✅ | ✅ | 2026-06-22 |
| VXLAN | ✅ (expert) | ✅ | ✅ | ✅ | 2026-06-22 |

Automated: `tests/test_field_council_scenarios.py`, `tests/mandatory/test_scenario_generate_api.py`, `tests/mandatory/test_field_gap_contracts.py`, `tests/mandatory/test_hardware_profiles_coverage.py`, `tests/mandatory/test_feature_render_coverage.py`, `tests/mandatory/test_baseline_options_coverage.py`, `tests/mandatory/test_intent_engine_coverage.py`, `tests/mandatory/test_api_expanded_contracts.py`.

## Council sign-off (v3.5.0 — 2026-06-22)

| Scenario | Lab ready | CLI correct | UX clear | Date |
|----------|-----------|-------------|----------|------|
| S1 | ✅ | ✅ | ✅ | 2026-06-22 |
| S2 | ✅ | ✅ | ✅ | 2026-06-22 |
| S3 | ✅ | ✅ | ✅ | 2026-06-22 |
| S4 | ✅ | ✅ | ✅ | 2026-06-22 |
| S5 | ✅ | ✅ | ✅ | 2026-06-22 |
| S6 | ✅ | ✅ | ✅ | 2026-06-22 |
| S7 | ✅ | ✅ | ✅ | 2026-06-22 |
| S8 | ✅ | ✅ | ✅ | 2026-06-22 |
| S9 | ✅ | ✅ | ✅ | 2026-06-22 |

## Council sign-off (template)
