# NLAP Release Council — Master Questionnaire

Answer **every** item with code evidence (`file:line` or symbol) or mark **GAP**.  
Extend `tests/mandatory/` when a GAP is found.

---

## A — Security envelope

| ID | Question | Where to look |
|----|----------|---------------|
| A-01 | Can remote hosts read vault secrets? | `credential_routes.py`, `api_security.py` |
| A-02 | Are SSH routes localhost-guarded? | `investigation_routes.py` `_require_local_ssh_api` |
| A-03 | Is shutdown authenticated / local-only? | `vlan_checker_web.py` `api_shutdown` |
| A-04 | SSRF blocked for PCAP URL? | `validate_pcap_download_url`, pcap routes |
| A-05 | Vault unlock before secret reveal? | `require_credential_vault_unlocked` |
| A-06 | Default bind address safe? | `config/app_config.yaml`, `app_config.py` |
| A-07 | Command audit on success AND failure? | `service.py` `execute_command` |
| A-08 | Audit export per investigation? | `/audit/export`, `store.export_audit_events_csv` |
| A-09 | API execute route guarded? | `/api/execute`, security wrappers |
| A-10 | Credentials never logged in plaintext? | grep `password` in log paths |

---

## B — Incident story pipeline

| ID | Question | Where to look |
|----|----------|---------------|
| B-01 | Auto-collect reaches autonomous job? | `index.html`, `/autonomous-run/start` |
| B-02 | Forensic checkbox uses acquisition engine? | `incident-forensic-workflow`, `/acquisition/start` |
| B-03 | Tier-1 uses counter errors not plain show? | `interface_counter_verdict.py` |
| B-04 | Runbook dedupe correct for counters? | `incident_runbook.py` |
| B-05 | Cancel during SSH/correlate/export? | `service.py` `_abort_if_cancelled` |
| B-06 | Offline paste skips SSH, runs brain? | `analyze_incident_story_from_logs` |
| B-07 | Time window params reach correlation? | `window_minutes_before/after` in service + routes |
| B-08 | Multi-device secondary collection? | `_collect_secondary_device`, `multi_device_correlation` |
| B-09 | Incident story renders export path? | `incidentRenderStory`, `export_path` |
| B-10 | Demo logs work in frozen EXE? | `api_incident_story_demo`, `_MEIPASS` |
| B-11 | Brain applies health + verification? | `_apply_incident_brain` |
| B-12 | Collect-next runbook copy works? | `incidentRunbookCopy` in index.html |

---

## C — Vendor parity (per platform)

| ID | Question | Where to look |
|----|----------|---------------|
| C-01 | IOS vs IOS-XE command plans differ? | `log_collectors.py` |
| C-02 | NX-OS tier-1 commands valid? | `cisco_nxos` plan |
| C-03 | Junos ge/xe/et/ae iface tokens? | `incident_correlation_engine.py` |
| C-04 | Gi0/1 ↔ GigabitEthernet0/1 counters? | `interface_counter_verdict.py` |
| C-05 | Action verifier platform commands? | `incident_action_verifier.py` |
| C-06 | Alias `cisco_xe` resolves? | `_DEVICE_TYPE_ALIASES` |
| C-07 | Juniper parsing tests exist? | `tests/test_juniper_parsing.py` |
| C-08 | Vendor matrix integration tests? | `tests/test_vendor_matrix_integration.py` |
| C-09 | F5 TMSH parser covered? | `modules/f5/tmsh_parser.py` |
| C-10 | STP/vPC/BGP collectors conditional? | `workflow.py` interface step |

---

## D — Operator UX & control plane

| ID | Question | Where to look |
|----|----------|---------------|
| D-01 | Cancel shows cancelled not failed? | `index.html` poll handlers |
| D-02 | Control plane cancel honest `ok`? | `/api/control-plane/tasks/.../cancel` |
| D-03 | Credential Use fills enable password? | `useCredential()` |
| D-04 | Config translator readable contrast? | `#tab-config-translator` |
| D-05 | Health wizard hits `/api/health-check/run`? | `healthCheckRun` |
| D-06 | Acquisition progress percent accurate? | `updateAcquisitionProgress`, telemetry |
| D-07 | Error/warning counts in telemetry? | `InvestigationTelemetry.to_dict` |
| D-08 | Audit download links on results? | `incidentRenderStory` |
| D-09 | Config compare gap filters work? | `ctUpdateDiffFilterLabels` |
| D-10 | Multi-device textarea parsed? | `incidentParseAdditionalDevices` |

---

## E — Outputs & offline EXE

| ID | Question | Where to look |
|----|----------|---------------|
| E-01 | Incident brain writes TXT export? | `incident_export_writer.py` |
| E-02 | Bundled PCAP offline? | `pcap_download.py` `offline_bundled` |
| E-03 | PyInstaller bundles demos/logs/docs? | `build_v5.*.spec` datas |
| E-04 | VERSION file in EXE datas? | spec `('VERSION', '.')` |
| E-05 | verify_offline_bundle.py current? | scripts path to EXE name |
| E-06 | smoke_release.py health endpoints? | `scripts/smoke_release.py` |
| E-07 | Output paths not CWD-dependent? | `utils/output_paths.py` |
| E-08 | Resource path helper for frozen? | `_get_resource_path`, `resource_path.py` |

---

## H — Acquisition / forensic engine

| ID | Question | Where to look |
|----|----------|---------------|
| H-01 | 12 steps defined in enum? | `WorkflowStep` in events.py |
| H-02 | Background job stores result? | `acquisition_job.py` |
| H-03 | Incident story in workflow context? | `workflow.py` merge + generate step |
| H-04 | Finalize uses correct store APIs? | `_step_finalize` |
| H-05 | Telemetry per workflow_id? | `ProgressTracker` |
| H-06 | Cancel per workflow state? | `cancel_workflow` |
| H-07 | Result API merges cached + live? | `/acquisition/result/` |
| H-08 | Context passes time window? | `acquisition/start` context |
| H-09 | Parsers per vendor registered? | `acquisition/parsers/` |
| H-10 | Story generator fallback? | `story_generator.py` |

---

## I — PCAP & traffic analysis

| ID | Question | Where to look |
|----|----------|---------------|
| I-01 | PCAP upload analysis route? | `pcap_routes.py` |
| I-02 | Flow infographic generated? | `pcap_flow_infographic.py` |
| I-03 | Traffic-log correlation window? | `traffic_correlation.py` |
| I-04 | PCAP limits enforced? | `pcap_limits.py` |
| I-05 | Demo PCAP factory for offline? | `pcap_demo_factory.py` |
| I-06 | Stream stories in analysis? | `test_pcap_stream_story.py` |

---

## J — Runbooks & templates

| ID | Question | Where to look |
|----|----------|---------------|
| J-01 | Runbook template library API? | `/runbook-templates` |
| J-02 | STP/vPC/BGP/optics templates? | `runbook_templates.py` |
| J-03 | Collect-next integrated in story? | `incident_runbook.py` |
| J-04 | Execute runbook refreshes story? | `execute_runbook_commands` |

---

## K — Architecture & data model

| ID | Question | Where to look |
|----|----------|---------------|
| K-01 | Investigation store schema migrations? | `store.py` init |
| K-02 | Evidence types complete enum? | `models.py` `EvidenceType` |
| K-03 | Sessions vs investigations linked? | `sessions` table |
| K-04 | Timeline events recorded? | `add_timeline_event` |
| K-05 | JSON metadata merge safe? | `update_investigation_metadata` |
| K-06 | Sanitize before API JSON? | `sanitize_for_json` |
| K-07 | Job store separate from acquisition? | `incident_job.py` vs `acquisition_job.py` |
| K-08 | Plugin system removed cleanly? | no broken plugin imports in web |

---

## L — Module boundaries

| ID | Question | Where to look |
|----|----------|---------------|
| L-01 | Web routes thin — logic in service? | `investigation_routes.py` |
| L-02 | Device access isolated? | `modules/device_access/` |
| L-03 | Analysis pure from SSH? | `modules/analysis/` |
| L-04 | Config translator self-contained? | `modules/config_translator/` |
| L-05 | Capture separate from analysis? | `modules/capture/` |

---

## M — Concurrency & jobs

| ID | Question | Where to look |
|----|----------|---------------|
| M-01 | Task control plane abort? | `task_control_plane.py` |
| M-02 | Daemon threads for jobs? | `incident_job`, `acquisition_job` |
| M-03 | Progress tracker thread-safe? | `ProgressTracker._lock` |
| M-04 | Multiple workflows keyed by id? | `workflow._workflows` |

---

## N — API contracts

| ID | Question | Where to look |
|----|----------|---------------|
| N-01 | 400 on missing host? | acquisition start, autonomous start |
| N-02 | 404 on unknown investigation? | route handlers |
| N-03 | JSON error shape consistent? | `{'error': ...}` pattern |
| N-04 | Status poll returns percent/stage? | autonomous-run status |
| N-05 | Health endpoint for smoke? | `/health` |

---

## O — Test & regression discipline

| ID | Question | Where to look |
|----|----------|---------------|
| O-01 | Bug fix has regression test? | `tests/test_v538_bugfixes.py` pattern |
| O-02 | Mandatory suite exists? | `tests/mandatory/` |
| O-03 | Manifest synced with files? | `qa/mandatory/MANIFEST.yaml` |
| O-04 | Integration tests gated? | `NLAP_RUN_INTEGRATION` |
| O-05 | Prebuild runs core unittest subset? | `_prebuild.py` |

---

## P — Field operator scenarios

| ID | Scenario | Expected code path |
|----|----------|-------------------|
| P-01 | Paste logs only, no SSH | offline analyze API |
| P-02 | SSH auto-collect one interface | autonomous pipeline |
| P-03 | Forensic 12-step with progress | acquisition poll |
| P-04 | Cancel mid-collection | abort + cancelled UI |
| P-05 | Unlock vault, use cred, run | credential bridge |
| P-06 | Download audit CSV | audit export route |
| P-07 | Compare two configs | config translator compare |
| P-08 | Load demo incident logs | demo API / bundled file |
| P-09 | Health check before change window | health wizard |
| P-10 | Multi-device spine+leaf | additional_devices |

---

## Q — Discovery & inventory (if enabled)

| ID | Question | Where to look |
|----|----------|---------------|
| Q-01 | Discovery job async? | `/api/discovery/run` |
| Q-02 | Hostname from show version? | `network_base.py` |
| Q-03 | Inventory API? | `/api/inventory` |

---

## R — Product simplicity (Steve Jobs lens)

| ID | Question | Where to look |
|----|----------|---------------|
| R-01 | One clear CTA for "build story"? | `incidentStoryBuild` |
| R-02 | Forensic vs autonomous labeled distinctly? | checkbox labels |
| R-03 | Progress panel hidden when idle? | `hideAcquisitionProgress` |
| R-04 | Error messages actionable? | alert text in incident flow |
| R-05 | Duplicate credential fields avoided? | inv creds helper |
| R-06 | Release notes reachable in app? | `/api/release-notes` |

---

## S — UI visual & feedback

| ID | Question | Where to look |
|----|----------|---------------|
| S-01 | Verdict colors consistent? | `incidentVerdictColor` |
| S-02 | Complete badge on story? | incidentRenderStory COMPLETE |
| S-03 | Step indicators for 12-step? | acquisition-step-N |
| S-04 | sosEsc on user content? | XSS escape helper |
| S-05 | Loading state before poll? | "Building incident story…" |

---

## T — Accessibility & resilience

| ID | Question | Where to look |
|----|----------|---------------|
| T-01 | Labels on checkboxes? | `incident-auto-collect-label` |
| T-02 | Buttons have title/tooltip where needed? | `title=` attributes |
| T-03 | Graceful API failure in UI? | catch blocks in fetch handlers |
| T-04 | Long paths word-break? | `word-break:break-all` on export |

---

## Z — Release gate meta

| ID | Question | Where to look |
|----|----------|---------------|
| Z-01 | VERSION single source? | `VERSION` file |
| Z-02 | CHANGELOG entry for version? | `CHANGELOG.md` |
| Z-03 | RELEASE_NOTES for version? | `docs/11-release-management/` |
| Z-04 | Mandatory QA workflow in CI? | `.github/workflows/mandatory-qa.yml` |
| Z-05 | Cursor hook on code edit? | `.cursor/hooks.json` |
| Z-06 | Agent rule for gate? | `05-nlap-mandatory-qa-gate.mdc` |

---

## Extending this questionnaire

When adding a feature:

1. Add section row(s) here with unique ID
2. Add mandatory test(s) in `tests/mandatory/`
3. Register in `MANIFEST.yaml`
4. Reference ID in council gap register if GAP found
