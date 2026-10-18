# NLAP Zero-Trust Questionnaire

Answer every item with **code evidence** (`file:line`) or mark **GAP**.

---

## A — Security envelope

| ID | Skeptical question | Where to look |
|----|-------------------|---------------|
| A-01 | Can a remote host read plaintext passwords from the vault API? | `credential_routes.py`, `utils/api_security.py` |
| A-02 | Are SSH execution routes blocked from non-localhost? | `investigation_routes.py` `_require_local_ssh_api` |
| A-03 | Can anyone POST `/api/shutdown` from the LAN? | `vlan_checker_web.py` `api_shutdown` |
| A-04 | Can PCAP URL download hit internal IPs (SSRF)? | `validate_pcap_download_url`, `download-pcap-url` route |
| A-05 | Is vault unlock required before GET credential secrets? | `require_credential_vault_unlocked` on get route |
| A-06 | What is the default web bind address? | `config/app_config.yaml`, `utils/app_config.py` |

---

## B — Incident story pipeline

| ID | Skeptical question | Where to look |
|----|-------------------|---------------|
| B-01 | Does auto-collect checkbox reach `autonomous-run/start`? | `index.html`, `investigation_routes.py` |
| B-02 | Does tier-1 use counters errors (not plain show interface) for verdict? | `interface_counter_verdict.py` |
| B-03 | Does runbook dedupe avoid false "already collected" on counters? | `incident_runbook.py` |
| B-04 | Does cancel work after SSH during correlate/export? | `service.py` `_abort_if_cancelled`, `_job_stage` |
| B-05 | Does offline paste path skip SSH but still run brain? | `analyze_incident_story_from_logs` |
| B-06 | Does demo log load in frozen EXE? | `api_incident_story_demo`, `sys._MEIPASS` |

---

## C — Vendor parity

| ID | Skeptical question | Where to look |
|----|-------------------|---------------|
| C-01 | IOS-XE plan differs from legacy IOS? | `log_collectors.py` `cisco_ios_xe` |
| C-02 | NX-OS tier-1 commands all valid? | `log_collectors.py` `cisco_nxos` |
| C-03 | Gi0/1 matches GigabitEthernet0/1 in counters? | `interface_counter_verdict.py` `_iface_tokens` |
| C-04 | Gi0/1 anchors in syslog correlation? | `incident_correlation_engine.py` |
| C-05 | Action verifier gap text uses platform commands? | `incident_action_verifier.py` `_vendor_iface_cmds` |
| C-06 | IOS-XE alias `cisco_xe` resolves in collection plan? | `_DEVICE_TYPE_ALIASES` |

---

## D — Operator UX & control plane

| ID | Skeptical question | Where to look |
|----|-------------------|---------------|
| D-01 | Cancel shows amber "cancelled" not red "failed"? | `index.html` poll handler |
| D-02 | Control plane cancel returns honest `ok`? | `vlan_checker_web.py` |
| D-03 | Credential "Use" fills enable password field? | `useCredential()` in `index.html` |
| D-04 | Config translator readable (not grey-on-grey)? | `#tab-config-translator` styles |
| D-06 | Does readiness wizard reach `/api/health-check/run`? | `index.html` `healthCheckRun`, `tests/test_health_wizard_api.py` |

---

## E — Outputs & offline

| ID | Skeptical question | Where to look |
|----|-------------------|---------------|
| E-01 | Incident brain writes TXT export? | `incident_export_writer.py` |
| E-02 | Bundled PCAP demo works air-gapped? | `pcap_download.py` `offline_bundled` |
| E-03 | PyInstaller bundles demos/logs? | `build_v5*.spec` datas |
