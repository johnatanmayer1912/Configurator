# Zero-Trust 360° Questionnaire

Each row is a **skeptical question**. Answer only from code. Mark ✅ verified, ⚠️ partial, ❌ gap.

## A — VLAN management

| ID | Question | Where to look |
|----|----------|---------------|
| A1 | Add VLAN: dry-run, live, verify, idempotency for IOS/NX-OS/Junos? | `modules/vlan_mgmt_production.py`, `utils/vlan_validate.py` |
| A2 | Rename: blocked on Juniper with clear error? Cisco name collision blocked? | `vlan_mgmt_production.py`, `adapters.py`, `vlan_validate.py` |
| A3 | Delete: member ports / dependencies checked per vendor? | `vlan_mgmt_production.py` |
| A4 | `verification_failed` vs `success` — honest UI buckets? | `vlan_checker_web.py`, `index.html`, summaries |
| A5 | GUI parity with web validate + save_config? | `vlan_checker_gui.py` vs web API |
| A6 | No automated rollback — manual restore guide only? | `utils/restore_guide.py`, `_prebuild.py` |
| A7 | Unsupported platforms fail validation (not silent IOS default)? | `utils/vlan_validate.py`, `test_vendor_matrix.py` |

## B — Interface Manager

| ID | Question | Where to look |
|----|----------|---------------|
| B1 | Discover/parse: separate paths NX-OS / IOS / Junos? | `interface_manager.py` `_parse_*`, `_determine_vendor` |
| B2 | Deploy: Junos commit check on dry-run? Cisco save (wr mem / copy run start)? | `_deploy_configuration` |
| B3 | Junos `display set` for config capture? | `_capture_current_config`, `_junos_display_set_config_cmd` |
| B4 | Bulk deploy — honest banner or batch support? | `index.html`, `/api/execute` IM routes |
| B5 | Cancel mid-deploy via `should_abort`? | `interface_manager.py` (grep should_abort) |
| B6 | Post-verify and rediscovery after change? | `_perform_post_verification`, `_rediscover_interfaces` |
| B7 | Manual restore API + UI? | `/api/interface/restore-guide`, `restore_guide.py` |
| B8 | IM report: TXT only or HTML too? | `_format_interface_report` |

## C — MAC trace & description search

| ID | Question | Where to look |
|----|----------|---------------|
| C1 | MAC trace: vendor-specific show commands? | `modules/mac_trace*.py`, adapters |
| C2 | Short MAC patterns — ambiguity handled? | MAC validation in web + plugin |
| C3 | Description search: ranking in API or only HTML formatter? | `modules/description_search.py`, `description_search_formatter.py` |
| C4 | Search highlight / sort (exact > prefix > partial)? | formatter vs run() return order |

## D — Topology & discovery

| ID | Question | Where to look |
|----|----------|---------------|
| D1 | CDP vs LLDP vs Juniper LLDP parsers? | `network_discovery.py` |
| D2 | 150-device truncate — logged and in manifest? | `adapters.py` ~1360 |
| D3 | Control plane cancel between devices? | `should_abort` in adapters, discovery |
| D4 | VPC placeholder edges when no LLDP edges? | `adapters.py` map pipeline |
| D5 | Discovery outputs split per device + manifest? | `output_paths.py`, discovery plugin |

## E — STP, standards, interfaces report

| ID | Question | Where to look |
|----|----------|---------------|
| E1 | STP blocked-port parsers: IOS + NX-OS fixtures? | `stp_swiss_runner.py`, `tests/fixtures/stp/` |
| E2 | DEMO vs LIVE banner in STP HTML? | STP formatter / template |
| E3 | Standards consolidated HTML report? | standards plugin, formatters |
| E4 | Node interfaces report — HTML path exists? | `adapters.py` `node_interfaces.html` |

## F — Security & credentials

| ID | Question | Where to look |
|----|----------|---------------|
| F1 | Credential API: localhost + vault unlock? | `utils/api_security.py` |
| F2 | Audit log on secret access? | api_security, web routes |
| F3 | HTTPS / session auth / rate limit? | grep credential routes |
| F4 | Secrets never written to reports? | formatters, log redaction |

## G — Performance & reliability

| ID | Question | Where to look |
|----|----------|---------------|
| G1 | SSH timeouts and retry policy consistent? | `network_base.py`, plugins |
| G2 | Serial device iteration — progress in task registry? | `task_control_plane.py` |
| G3 | Large inventory (>100) — UI and memory behavior? | web JS, adapters |
| G4 | Offline EXE: hiddenimports for new modules? | `.spec`, `_prebuild.py` |

## H — UI / operator effectiveness

| ID | Question | Where to look |
|----|----------|---------------|
| H1 | Console log cites output folder paths? | web JS log handlers |
| H2 | Validation before execute for risky ops? | VLAN validate, IM validate routes |
| H3 | Natural interface sort (Gi1/0/2 before Gi1/0/10)? | interface_manager sort |
| H4 | >50 rows → table not cards? | formatters, index.html |

## I — Testing & release

| ID | Question | Where to look |
|----|----------|---------------|
| I1 | pytest covers vendor matrix offline? | `tests/test_vendor_matrix.py` |
| I2 | Live SSH / containerlab tests? | tests/ grep netmiko live |
| I3 | enterprise_qa_gate passes? | run script |
| I4 | No `rollback_vlan_change` in production code? | `_prebuild.py`, grep |

## J — Out-of-scope / explicit non-support

| ID | Question | Where to look |
|----|----------|---------------|
| J1 | Arista / IOS-XR — fail closed or IOS fallback? | `interface_manager._determine_vendor`, vlan_validate |
| J2 | HP Comware in device list — actually supported? | `vlan_checker_web.py` device types |
