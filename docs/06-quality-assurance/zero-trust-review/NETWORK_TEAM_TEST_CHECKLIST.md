# Network Team Test Checklist — Zero Trust Protocol

**Use before every release or after template/API changes.**  
Sign off only when all **BLOCK** items pass.

---

## Pre-flight

- [ ] `VERSION` file matches UI banner and API `/version`
- [ ] `python web_launcher.py` starts without traceback
- [ ] Browser opens with token URL
- [ ] `/catalog` returns scenarios, versions, features, field_hints

---

## Scenario: Standalone Access

- [ ] Select **Standalone Access Switch**
- [ ] Hostname: `ACCESS-TEST-01`
- [ ] Mgmt: `10.99.1.10/24`, GW: `10.99.1.1`
- [ ] **Validate & Preview CLI** → status pass
- [ ] Output contains separate lines: `feature interface-vlan`, `feature lldp`, `feature lacp`
- [ ] Output does **NOT** contain concatenated `feature interface-vlanfeature`
- [ ] No vPC block in output
- [ ] **Build & Save** → vault shows `ACCESS-TEST-01_*_config.txt`

---

## Scenario: vPC Leaf Pair (BLOCK)

- [ ] Select **vPC Leaf Pair**
- [ ] Model: **Nexus 93180YC-EX**
- [ ] Enable **Generate vPC pair**
- [ ] Peer-link interfaces show **Ethernet1/53, Ethernet1/54** (NOT 49/50)
- [ ] Local KA: `10.255.255.1`, Remote KA: `10.255.255.2`
- [ ] **Validate & Preview CLI** → peer-link section uses Eth1/53–54
- [ ] Preview includes `peer-gateway`, `auto-recovery`, `ip arp synchronize` (9.3)
- [ ] Pair validation: no errors in preview
- [ ] Secondary preview hostname ends with `-B`
- [ ] **Build & Save** → two config files in vault (Primary + Secondary)
- [ ] Secondary keepalive IPs swapped vs primary
- [ ] **Fabric links** — Po30 uplink on Eth1/49–50; toggle off restores bare trunks

---

## Scenario: vPC Core 40G — Fabric links (BLOCK)

- [ ] Roadmap: Core · vPC Yes · 40G
- [ ] **Fabric links** downlinks Po20/Po21 enabled by default
- [ ] Change Po20 members (e.g. Eth1/5–6) → CLI reflects custom members
- [ ] Enable **Spine uplink** Po10 → `interface port-channel10` with `vpc 10`

---

## Negative tests (must block)

- [ ] Hostname `bad name` (space) → preflight error
- [ ] Mgmt IP `10.0.0.1` (no CIDR) → preflight error
- [ ] Same local and remote keepalive IP → validation error
- [ ] Empty peer-link interfaces on vPC scenario → preflight error

---

## NX-OS version matrix

| Version | Template | Spot-check |
|---------|----------|------------|
| 9.3 ★ | nxos_base | HSRP v2 if enabled |
| 10.2 | nxos_base | Same as 9.3 |
| 7.0 | nxos_legacy | No peer-gateway line |

---

## Offline exe (BLOCK for release)

- [ ] `python utils/build_exe.py` completes
- [ ] Run exe from `dist/` on clean machine (no Python installed)
- [ ] Browser opens; catalog loads
- [ ] Generate one config; files appear in `dist/configs/history/`
- [ ] `docs/` accessible next to exe (bundled)

---

## Security spot-check

- [ ] `/validate` requires auth token (401 without)
- [ ] Server binds 127.0.0.1 only
- [ ] Document plaintext password risk if admin password used

---

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| DC Engineer | | | |
| NOC Lead | | | |
| Release | | | |

**Notes:**

---

*Template version 1.0 · Zero-Trust Review Team*
