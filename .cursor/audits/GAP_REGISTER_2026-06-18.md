# NST Zero-Trust Gap Register

- **Version:** 7.0.48 (read `VERSION`)
- **Date:** 2026-06-18
- **pytest:** 228 passed, 1 skipped
- **prebuild:** PASS
- **Council skills used:** nst-orchestrator, nst-network-operations, network-engineer, nst-product-architect, nst-python-backend, nst-security-ops, nst-release-engineer, nst-multi-advisor

## Executive summary

v7.0.44 is **production-viable for IOS, NX-OS, and Junos** on core paths: VLAN add/delete/rename (with Juniper rename blocked), VLAN validation pipeline, IM discover/deploy with vendor-specific parse/save/commit, MAC trace, topology/discovery, STP offline fixtures, and honest backup-only restore policy. P0/P1 council items from v7.0.43→7.0.44 are **verified in code and tests**. Remaining gaps are **P2/P3**: bulk IM, IM cancel mid-SSH, description-search ranking not in API layer, topology silent truncate, TXT-only IM reports, no live SSH CI, and hardening beyond localhost credential guard.

**Ship recommendation:** Yes for controlled change windows on the three primary vendors; document known P2 limits below.

---

## Verified strengths (code evidence)

| ID | Finding | Evidence |
|----|---------|----------|
| OK-01 | VLAN verification failure → honest status buckets | `modules/vlan_mgmt_production.py`, web summaries |
| OK-02 | No automated VLAN rollback; manual restore guide | `utils/restore_guide.py`, `_prebuild.py`, `test_vendor_matrix.py` |
| OK-03 | Credential API localhost + vault guard | `utils/api_security.py`, `_credential_api_guard()` |
| OK-04 | Cisco VLAN add blocked on ID+name collision | `vlan_mgmt_production.py`, `vlan_validate.py` |
| OK-05 | IM Junos dry-run commit check + display set | `interface_manager.py` `_deploy_configuration`, `_capture_current_config` |
| OK-06 | IM single-host scope banner in UI | `index.html` ~1211 |
| OK-07 | STP NX-OS/IOS fixture tests | `tests/test_vendor_matrix.py`, `tests/fixtures/stp/` |
| OK-08 | Topology/discovery supports `should_abort` between devices | `modules/adapters.py` ~1365–1368 |
| OK-09 | Unsupported VLAN platform fails validation | `utils/vlan_validate.py` L80–86, `test_validate_unsupported_platform_fails` |
| OK-10 | Vendor-specific IM parse/deploy/save paths | `interface_manager.py` `_determine_vendor`, `_parse_*`, `_deploy_configuration` |

---

## Vendor matrix (IOS | NX-OS | Junos | IOS-XR)

| Feature | IOS / IOS-XE | NX-OS | Junos | IOS-XR |
|---------|--------------|-------|-------|--------|
| VLAN add | ✅ | ✅ | ✅ | ✅ commit (`cisco_xr`) |
| VLAN rename | ✅ | ✅ | ❌ blocked | ✅ |
| VLAN delete | ✅ | ✅ | ✅ | ✅ |
| VLAN validate API | ✅ | ✅ | ✅ | ✅ |
| IM discover | ✅ | ✅ | ✅ | ❌ blocked (G-005) |
| IM deploy + save | ✅ wr mem | ✅ copy run start | ✅ commit | N/A |
| MAC trace | ✅ | ✅ | ✅ | ✅ |
| Topology | ✅ | ✅ | ✅ | ✅ |

---

## Gaps

### P0 — None open (v7.0.44)

All prior council P0 items addressed in 7.0.44. Re-verify on each release via pytest + `_prebuild.py`.

---

### P1 — Functional / parity (defer or next sprint)

| ID | Lens | Question | Evidence / Gap | Owner |
|----|------|----------|----------------|-------|
| G-001 | IM | Can operator cancel IM deploy mid-SSH? | **FIXED v7.0.46:** `_im_should_abort()` between backup, config lines, commit/save in `interface_manager.py` | nst-python-backend |
| G-002 | IM | Bulk interface deploy across inventory? | **GAP:** UI banner states single-host only (`index.html`); no batch IM in `/api/execute` | nst-network-operations |
| G-003 | Search | Description results ranked in API/run()? | **FIXED v7.0.45:** `match_score` + sort in `description_search.run()` | nst-python-backend |
| G-004 | Topology | >150 devices — operator informed in manifest? | **PARTIAL v7.0.46:** manifest + web status show `devices_truncated`, `failed_hosts`, `parallel_workers` | nst-product-architect |
| G-005 | Platform | Unknown device_type for IM defaults to IOS parse | **FIXED v7.0.47:** `_im_vendor_or_error` fail-closed; no silent IOS default | nst-network-operations |
| G-006 | VLAN | IOS-XR mentioned in save path but not first-class | **FIXED v7.0.48:** `_is_ios_xr()` unified detection; show/parse/validate/audit/commit paths for `cisco_xr`/`ios_xr` | nst-network-operations |
| G-007 | Junos | VLAN rename workflow | **By design blocked** — operators must delete+add; docs/UI must stay explicit | nst-product-architect |

---

### P2 — UX, outputs, performance

| ID | Lens | Question | Evidence / Gap | Owner |
|----|------|----------|----------------|-------|
| G-008 | IM | HTML report for interface operations? | **GAP:** `_format_interface_report` returns plain text only L2495+ | nst-product-architect |
| G-009 | Control plane | Progress `{devices_done, devices_total}` in task registry? | **GAP:** not in `utils/task_control_plane.py` public API | nst-python-backend |
| G-010 | Security | Credential API beyond localhost? | **GAP:** no session auth, HTTPS enforcement, or rate limit in `api_security.py` | nst-security-ops |
| G-011 | IM | Conflict checks — hard fail vs warning? | **PARTIAL:** many IM validation paths warn rather than block | nst-network-operations |
| G-012 | MAC | Short MAC patterns — ambiguity | **PARTIAL:** partial patterns allowed; ambiguous multi-match possible | nst-network-operations |
| G-013 | QA | enterprise_qa_gate markdown links | **FAIL:** gate fails on markdown link check; pytest + prebuild pass (2026-06-18 run) | nst-release-engineer |
| G-014 | GUI | Full GUI/web feature parity for all modules | **CLOSED (by design v7.0.47+):** Web-only product policy — Tk GUI (`vlan_checker_gui.py`) out of scope; control plane + Swiss Tools are web-only | nst-product-architect |

---

### P3 — Future / new scope

| ID | Lens | Question | Evidence / Gap | Owner |
|----|------|----------|----------------|-------|
| G-015 | Platform | Arista EOS first-class | **GAP:** `test_validate_unsupported_platform_fails` expects fail; IM may still default IOS | nst-network-operations |
| G-016 | CI | Live Netmiko / containerlab pytest | **GAP:** no live SSH tests under `tests/` | nst-release-engineer |
| G-017 | Platform | HP Comware in device type list | Listed in `vlan_checker_web.py` ~3004; support path unclear vs IOS/NXOS/Junos | nst-network-operations |
| G-018 | IM | Automated config rollback | **By design removed** — manual restore only per policy | — |

---

## Unverified this session

- Field CLI variants on every IOS-XE/NX-OS/Junos hardware generation
- Junos STP blocked-port parser vs live `show spanning-tree` output

---

## Recommended next step

Run **nst-gap-remediation-workflow** on this register. Suggested first batch: **G-001, G-003, G-004, G-008** (P1/P2 with clear code paths).
