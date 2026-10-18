# Changelog

All notable changes to this project will be documented in this file.

## [6.43.0] - 2026-08-13

### P0/P1 architecture & Cisco cutover order

#### Unified API & typed deployment contracts
- **`POST /api/v1/config/generate`** — single entry for `single`, `preview`, `wizard`, and `deployment` modes
- **`VPCPairInput` / `UplinkInput`** — shared Pydantic validators; `from_ports` / `to_ports` for asymmetric cabling
- **`DeploymentInput.normalize_topology()`** — authoritative vPC/uplink validation at API boundary
- **`baseline_options`** — preserved through deployment `DeviceInput` construction
- **`output_dir`** — honored via `resolve_deployment_export_base()` (vault-relative paths only)
- **vPC export blocking** — pass 3 skips switches in failed vPC pairs (`switches_blocked_by_vpc_errors`)

#### Deployment builder extraction
- **`core/deployment_builder.py`** — export path resolver, custom uplink wiring (`apply_custom_uplinks_for_switch`)
- Replaced ~230-line inline uplink loop in `generate_deployment` with shared helper

#### NX-OS 9.x template cutover order
- **`nxos_base.j2`** — `vpc domain` / `peer-keepalive` moved **after** port-channel block (matches legacy 7.x order)
- Routed keepalive interfaces render `vrf member` + `ip address` on dedicated Ethernet (no LACP PO)

#### Routed keepalive (Cisco best practice)
- **`baseline_keepalive_routed`** baseline option — dedicated routed link instead of L3 port-channel
- `core/vpc_topology.py` — `_append_keepalive_topology()` + `_inject_routed_keepalive_interface()`

### P2 Product / UX

#### Config template API (live)
- **`GET/POST /config/templates`** + **`GET /config/templates/{id}`** — disk-backed saved templates (`core/template_store.py`)
- Web UI **Save as Template** posts to server API with localStorage fallback; gallery loads saved templates on startup

#### Accessibility & responsive layout
- Removed **`min-width: 1024px`** body constraint — supports tablet/narrow viewports (320px+)
- Skip navigation, skeleton loaders, and reduced-motion support retained from prior releases

#### Desktop GUI parity note
- CTK **Home** view banner directs operators to `web_launcher.py` for multi-switch fabric deployments

#### Tests
- `tests/mandatory/test_remediation_v643.py` (6 regressions)

## [6.42.0] - 2026-08-13

### Legacy 7.x keepalive + two-pass deployment refactor

#### NX-OS 7.x legacy template (`nxos_legacy.j2`)
- Full **port-channels** block (peer-link trunk + allowed VLANs, L3 keepalive with `no switchport`)
- **vPC domain** moved after keepalive/port-channel interfaces (correct cutover order)
- Ethernet stanza newline fixes; uses `device.vpc.role_priority` for role election

#### Two-pass multi-switch deployment
- **Pass 1:** build all `Device` models (scenario + vPC + custom uplinks)
- **Pass 2:** `wire_core_leaf_downlinks()` — order-independent core/spine → leaf wiring
- **Pass 3:** pipeline render/export per switch
- Post-build **`validate_all_vpc_pairs()`** for every vPC domain
- New module: `core/deployment_wiring.py`

#### Tests
- `tests/mandatory/test_legacy_and_twopass.py` (4 regressions)

## [6.41.1] - 2026-08-13

### Multi-disciplinary audit — P0 remediation

#### Correctness & Cisco NX-OS output
- **vPC keepalive symmetry** — `_build_deployment_vpc_config()` role-aware local/remote IP mapping with partner cross-check (fixes secondary peer validation failures)
- **Peer-link trunk allowed VLANs** — explicit `switchport trunk allowed vlan` on vPC peer-links from device VLAN set (type-2 consistency)
- **L3 keepalive port-channel** — `no switchport` on L3 PO and routed LAG members in `nxos_base.j2`
- **`DeviceValidator` vPC semantics** — peer-link member count, keepalive IP inequality, domain range

#### API & safety
- **`/config/upload` basic path** — fixed `ValidationSeverity` / `ConfigValidationError` construction (was HTTP 500)
- **`/generate-config`** — pre-flight `device_validator.validate()` before pipeline execute
- **`/api/generate-config`** — preview mode (no vault write); rejects empty CLI output
- **`DeploymentInput`** — rejects empty switch list at schema level

#### Tests
- New `tests/mandatory/test_audit_remediation_p0.py` (5 regressions)

## [6.41.0] - 2026-08-13

### Multi-switch deployment route hardening, vPC fixes, offline EXE

#### Multi-switch route (distinct from VPC wizard)
- **Route separation** — `CONFIG_ROUTE_VPC` (`/scenario/generate`) vs `CONFIG_ROUTE_MULTISWITCH` (`/generate-deployment`); wizard preflight skipped when multi-switch deployment is active
- **`preflightDeploymentErrors()`** — validates deployment switches, mgmt IPs, vPC pairs, and peer-link ports instead of wizard steps 1–8
- **`updateBadges()`** — shows deployment-specific badges (switch count, vPC count) in multi-switch mode

#### Backend fixes
- **`_build_deployment_vpc_config()`** — full `VPCConfig` population from deployment vPC pair data (fixes HTTP 500 on `/generate-deployment`)
- **Secondary vPC role** — always overwrites scenario vPC config; secondary peers get `role priority 8192`
- **`channel_group`** — peer-link interfaces use correct `iface.channel_group` field for Jinja rendering
- **`validate_vpc_pair()`** — called when both vPC peers are processed
- **`_switch_is_spine_or_core()`** — spine/core uplink auto-wiring for spine-leaf topologies
- **`/api/generate-config`** — delegates to real deployment pipeline via `_dict_to_switch_config()` (PA-005)
- **CORS** — localhost-specific origins with `allow_credentials=False`

#### Tests
- 52 multiswitch mandatory + E2E tests passing (including PA-005 server-side config generation)

## [6.39.0] - 2026-08-02

### Multi-switch results display, Cancel modal fix, API VLAN fix, EXE build

#### Fixes
- **Results container visible** — `displayDeploymentResults` now navigates wizard to step-8, activates `portMapTab`, and removes hidden state so deployment results are always visible after generation
- **Success modal** — `showMultiSwitchSuccessModal` uses correct `.modal` class pattern instead of `modal-backdrop`
- **view-config / view-port-map buttons** — Added missing click handlers in `ui-handlers.js` for result item action buttons
- **Cancel Add Switch** — Moved `close-modal` and `confirm-add-switch` from `change` event handler to `click` handler; Cancel now correctly removes the modal overlay
- **API preview Renderer** — Fixed `from core.renderer import Renderer` (class is `ConfigRenderer`) in `/generate-deployment?preview=true` path
- **API VLAN str** — Fixed `str(v.id)` → `str(v)` in `user_vlan_str` when `user_vlan_ids` contains raw ints from `global_vlans`
- **Template flow** — Removed premature `hideTemplateGallery()` call from `applyTemplate`; editor only appears after "Customize Network" click
- **ui-handlers event routing** — Moved `filter-templates`, `show-template-comparison`, `render-template-gallery` from `change` to `click` handler

## [6.28.9] - 2026-07-20

### JavaScript ReferenceError fix

Fixed the ReferenceError in topology-view.js that was causing console errors during multi-switch deployment.

#### Fixes
- **ReferenceError fix** - Renamed `multiSwitchMode` variable to `isMultiSwitchMode` in topology-view.js:562 to avoid temporal dead zone issue
- **Console error resolution** - Eliminated repeated "Cannot access 'multiSwitchMode' before initialization" errors

## [6.28.8] - 2026-07-19

### Interface ordering fix

Fixed interface ordering in CLI output to ensure interfaces appear in natural numeric order.

#### Fixes
- **Interface sorting** - Added automatic interface sorting by name in Device class __post_init__ method
- **Natural order** - Interfaces now sort as Ethernet1/1, 1/2, 1/3, 1/4 before 1/35-36, etc.
- **CSS display fix** - Removed max-height constraint from .cli-block to show full configuration

## [6.28.7] - 2026-07-19

### Post-build popup mandatory for all scenarios

Made the build success popup mandatory across all configuration scenarios.

#### Features
- **Universal build success popup** - Post-build popup now appears for all scenarios (vPC, multi-switch, standalone) showing created files and next actions
- **Multi-switch export summary** - Added export information to multi-switch deployment response to enable popup display
- **Consistent user experience** - Users always see file creation summary and action options (open folder, restart, etc.) after successful builds

## [6.28.6] - 2026-07-19

### User VLAN choice override fix

Fixed scenario defaults overriding user's explicit VLAN choices in multi-switch deployments.

#### Fixes
- **Override application logic** - Modified scenario_engine to only apply override values when explicitly provided (not None), ensuring user's VLAN choices are respected over scenario defaults
- **VLAN parameter preservation** - User-selected base_access_vlan and access_vlan_count now take precedence over scenario template defaults

## [6.28.5] - 2026-07-19

### VLAN naming consistency fix

Fixed inconsistent VLAN naming across different device roles in multi-switch deployments.

#### Fixes
- **Consistent VLAN naming** - Updated VLAN naming logic to use consistent "TRANSIT" prefix across all device roles (spine, leaf, access) instead of role-specific prefixes (TRANSIT for spine, FABRIC for leaf, USER for access)
- **Multi-switch VLAN consistency** - Ensures all devices in a multi-switch deployment have matching VLAN names when the same VLAN range is selected

## [6.28.4] - 2026-07-19

### Core switch scenario selection fix

Fixed campus network configuration generation for core switches in vPC pairs.

#### Fixes
- **Core role scenario selection** - Updated scenario selection logic to include `role: "core"` switches in vPC deployments, ensuring they use `vpc_core_pair` scenario for proper VLANs, SVIs, and institutional baseline
- **vPC pair variable scope** - Fixed UnboundLocalError by initializing `vpc_pair` variable before use in scenario selection

## [6.28.3] - 2026-07-19

### Multi-switch configuration completeness fix

Fixed spine/core switch configuration generation in multi-switch deployments to include VLANs, SVIs, and institutional baseline configurations matching the VPC scenario output.

#### Fixes
- **Scenario-based configuration enrichment** - Applied scenario templates to enrich device configurations with proper VLANs, SVIs, features, and baseline options during multi-switch deployment generation
- **Spine scenario selection** - Updated spine switches in multi-switch deployments with vPC leaf pairs to use `vpc_core_pair` scenario for complete institutional baseline
- **Default vPC parameters** - Added default vPC parameter values for spine switches that don't have explicit vPC configuration to prevent TypeError during scenario application

## [6.28.2] - 2026-07-19

### Multi-switch deployment fixes

Fixed critical issues preventing leaf switch configuration generation in multi-switch deployments.

#### Fixes
- **ImportError in catalog_loader** - Fixed incorrect import of non-existent `load_hardware_profiles` function; replaced with correct `CatalogLoader().list_hardware_profiles()` method call
- **Variable scope error** - Fixed local variable shadowing of global `catalog` variable that caused "cannot access local variable 'catalog' where it is not associated with a value" error
- **VPCConfig instantiation** - Previously fixed VPCConfig() being called without required arguments by implementing `_build_deployment_vpc_config` helper function
- **Topology rendering** - Fixed multi-switch topology diagram to correctly render full spine-leaf topology instead of only vPC core pair
- **Port map display** - Fixed port maps and configuration maps not displaying in deployment results
- **Spine-leaf classification** - Fixed device class matching to correctly identify spine switches with `device_class` "core" and role "spine"

#### Testing
- Verified all 6 switches (2 spines + 4 leaves) now generate configurations successfully
- Confirmed topology diagram renders correctly for multi-switch deployments
- Port maps and configuration maps display properly for all switches

## [5.0.3] - 2026-06-23

### Offline-integrity hardening + UI polish — no new exe

Full air-gap audit of every UI asset and code path, with automated guards so offline
support can never silently regress. CSS/JS/test/script changes only — no exe rebuilt.

#### Offline verification (audited clean, now enforced by tests)
- No CDNs, web fonts, `@font-face`, or external stylesheets/scripts anywhere in the UI
- All `fetch()` calls are relative paths to the local FastAPI server (127.0.0.1)
- App packages (`api`/`core`/`utils`/`pipelines`/`models`) make **no** outbound network
  calls — only a local socket bind for the port check
- Font stacks fall back to system fonts (`-apple-system`, `Segoe UI`, monospace)

#### New automated guards (mandatory)
- `test_all_referenced_static_assets_exist` — every `/static` + icon reference resolves to a real file
- `test_no_external_resource_references_for_offline` — bans CDN/font/preconnect tokens
- `test_js_fetches_are_relative_only` — no absolute/`//` fetch URLs
- `test_app_code_has_no_outbound_network_calls` — bans `requests`/`httpx`/`urllib`/`smtplib` in app code
- `test_fonts_use_system_fallbacks_only` — every font stack ends in a generic family
- Frozen-bundle sim (`audit_frozen_plugin_sim.py`) now verifies all v5 assets
  (`vpc-link-planner.js`, `fabric-questionnaire.js`, `topology-view.js`,
  `wizard-enhancements.js`, `admin-po-map.js`, `favicon.svg`, `admin.html`,
  `po_allocation_map.yaml`)

#### UI polish
- `.header-actions` now wraps and right-aligns so the toolbar never overflows on narrow widths

#### QA
- **370 tests** total (was 365), 1 skipped; full suite + enterprise `pre_release` gate PASS

## [5.0.2] - 2026-06-23

### UI/UX visibility + "Steve Jobs" polish pass — no new exe

Fixes the unreadable topology diagram reported on v5.0.0 (invisible black boxes) and a
systemic CSS-token defect that left several panels with invisible text/borders. Adds a
cohesive, premium visual polish across the wizard. CSS/JS only — no exe rebuilt.

#### Fixes (visibility — the "I don't see anything" defect)
- **Topology diagram had zero CSS** — `.topo-node`/`.topo-label`/`.topo-link`/`.topo-legend`
  rendered as default-black on a dark background. Added full SVG styling with per-role
  colors (core/leaf/spine/peer/access), readable labels, and links; rewrote
  `topology-view.js` into a clean, balanced, legible diagram that only re-renders on change
  (`static/styles.css`, `static/topology-view.js`)
- **Undefined CSS tokens** — many rules referenced `--text`, `--muted`, `--border`,
  `--surface`, `--warn` which were never defined, so the Fabric links table headers/borders,
  readiness panel, capacity hint, and version-diff text were invisible. Added a semantic
  token layer aliasing the real palette (`static/styles.css`)
- **`.btn-ghost` was never defined** — Undo button, row-remove "×", and "Details" toggle
  rendered unstyled; added `.btn-ghost` + `.full-width`/`.questionnaire-nav`/`.undo-control`

#### "Steve Jobs" polish (cohesive, calm, enterprise-grade)
- Refined palette + design tokens: radius scale, soft/pop shadows, focus ring, easing
- Premium panels (softer elevation), tactile buttons, confident input focus states
- Segmented-control wizard mode toggle; clearer active/done step rail
- Lift on choice/scenario cards; at-a-glance readiness status card
- Cleaner fabric links table (uppercase headers, hover rows, conflict highlight)
- Native-feeling thin scrollbars; antialiased typography with tightened headings

#### QA
- **5 new mandatory regression tests** — topology styling present + per-role fills,
  topology renderer uses styled classes (read-only), semantic tokens defined,
  `.btn-ghost`/utilities defined (`tests/mandatory/test_v5_professional_ux.py`)
- **365 tests** total (was 361); full suite + enterprise `pre_release` gate PASS

## [5.0.1] - 2026-06-23

### Enterprise correctness hardening (multi-model code audit) — no new exe

Strict re-audit of the v5.0.0 frontend↔backend integration. No exe rebuilt; v5.0.0
offline binary remains the shipping artifact (these are source/QA correctness fixes).

#### Fixes
- **Link planner lost stable preset ids** — `renderLinkSection` now writes `tr.dataset.id`,
  so `syncLinkPlannerFromDom` keeps real preset ids (`uplink_fiber_pair`, `downlink_10g_leaf`)
  instead of regenerating `*_custom_N`. Prevents corrupted `downlink_options`/`uplink_options`
  maps and incorrect re-enabling of disabled rows (`static/vpc-link-planner.js`)
- **Admin Po map 401 under session auth** — wizard `Admin` link and admin `Back to wizard`
  link now carry the session token; admin page degrades gracefully on 401/403 with a clear
  message (`static/app.js`, `static/admin-po-map.js`, `templates/web/index.html`, `admin.html`)
- **Topology diagram mutated planner state** — `renderTopologyDiagram` now reads
  `linkPlannerRows` read-only instead of calling `getLinkPlannerPayload()` on a timer,
  eliminating a path that could wipe rows from stale DOM (`static/topology-view.js`)
- **Capacity hint mutation** — `refreshCapacityHint` builds the port-budget request from
  `linkPlannerRows` directly (read-only) and tolerates non-200 responses (`static/wizard-enhancements.js`)
- **Readiness meter skipped on clean configs** — meter + capacity hint now update on every
  `renderActionRequired` path, including the lab-ready/no-blockers early return (`static/config-studio.js`)
- **Deprecation** — `core/cable_plan.py` uses timezone-aware UTC (`datetime.now(timezone.utc)`)

#### QA
- **11 new regression/edge-case tests** in `tests/mandatory/test_v5_professional_ux.py`
  (preset-id persistence, read-only topology, admin token propagation, meter ordering,
  self-exclusion in Po validation, Po range exhaustion fallback, zero-free port budget,
  empty cable plan, unknown version diff, hostname underscore hint, core/access pools)
- **361 tests** total (was 350); enterprise QA gate `pre_release` PASS

## [5.0.0] - 2026-06-23

### Professional operator release — wizard UX, fabric intelligence, installer cable plans

#### Operator features (A/B/C/D/H/I)
- **Po collision guard (A1)** — live validation on fabric link rows; modal offers next free Po or custom ID
- **Fabric links questionnaire (A2)** — Architect mode wizard asks downlink/uplink counts before table edit
- **Port suggestion engine (A3)** — hardware-aware member suggestions from fiber/core/access pools
- **Quick vs Architect modes (B1)** — toggle hides/shows questionnaire and topology for fast lab builds
- **Live topology diagram (B2)** — SVG peer/spine/leaf sketch updates with scenario
- **Why-this-default tooltips (B4)** — `data-why-default` hints from catalog option help
- **Undo stack (B5)** — restore last link planner / hostname snapshot
- **Keyboard-first link table (B6)** — Enter expands row; tab-friendly inputs
- **Empty-state copy (B8)** — guided hints when no fabric links enabled
- **Lab vs production readiness meter (B9)** — sidebar badge from action-required panel
- **Expert collapse (B10)** — compact fabric links table for senior operators
- **Institutional Po map admin (C2)** — `/admin` page edits per-model Po ranges (exe-relative `configs/`)
- **NX-OS train diff (C8)** — inline change list when version dropdown changes
- **Hostname / site validation (C10)** — multi-site hints and pair naming suggestions
- **Cable plan export (D5)** — `{hostname}_CABLE_PLAN.md` installer wiring sheet on every generate
- **Capacity planner (I3)** — port budget hint on Configure step
- **Training mode (I8)** — optional tips overlay for onboarding
- **Release notes modal (H8)** — first-run excerpt from CHANGELOG

#### UI polish (screenshot fixes)
- Equal-width management IP / gateway grid; full-width version & model selects
- Configure-path banner shortened with expandable Details
- Platform badge shows tier + port count (dropdown is canonical model picker)
- Live CLI preview title alignment via `panel-title-row`

#### Backend
- `core/link_allocator.py`, `core/po_map_store.py`, `core/cable_plan.py`, `core/version_diff.py`, `core/hostname_rules.py`
- API: `/admin/po-map`, `/util/validate-link`, `/util/suggest-members`, `/util/port-budget`, `/util/cable-plan`, `/util/version-diff`, `/util/hostname-hints`, `/release/notes`

#### QA
- **22 new mandatory tests** — `tests/mandatory/test_v5_professional_ux.py` (350 total)
- L-005: DOM + static JS contracts; Playwright gate when `tests/e2e/` suite is added

## [4.1.0] - 2026-06-23

### Fabric Link Planner — vPC downlink & uplink configurability (40G / 10G / 1G)

#### Operator features
- **Fabric links card** — replaces simple downlink toggles with editable table: enable, Po ID, vPC ID, members, description (`static/vpc-link-planner.js`)
- **Custom downlinks** — core vPC Po20/Po21 members editable (e.g. move 10G/1G leaf downlinks off Eth1/1–4)
- **Uplink port-channels** — fiber uplink Po30/Po31 on Nexus 93180YC-EX and Nexus 9348GC-FXP (Eth1/49–54 pool, peer-link/keepalive auto-reserved)
- **40G spine uplinks** — optional Po10 toward spine on Nexus 9336C-FX2 (`uplink_core_spine` preset)
- **Standalone tiers** — uplink presets resolve to bare trunk ports (no vPC Po) on non-pair scenarios

#### Backend
- `core/link_resolver.py` — hardware-aware member resolution (`fiber_pool`, `core_pool`)
- `data/institutional_baseline.yaml` — `uplink_presets` catalog
- `data/config_matrix.yaml` — per-scenario `uplink_presets` matrix rows
- `core/vpc_topology.py` — spine/uplink port-channel bundles on vPC builds

#### QA
- **9 new mandatory tests** — `tests/mandatory/test_vpc_link_planner.py`
- **330 tests** total, new stage `mandatory_vpc_link_planner`
- L-005 progress: DOM contracts for Fabric links card (full Playwright gate still deferred)

## [4.0.0] - 2026-06-23

### World-class operator release — P0/P1/P2 council gaps closed

#### P0 — Change-window confidence
- **Change package export** — every build writes `manifest.json` + `CHANGE_PACKAGE.md` (rollback notes, vPC pair paste order, post-paste checklist) alongside config artifacts
- **Device JSON export** — `{prefix}_device.json` per switch for automation pipelines
- **Config Builder E2E** — parse → recommend flow mandatory; checkpoint restore repopulates vPC ports and lands on Configure step
- **26 new v4 mandatory tests** — `test_v4_world_class_contracts.py` (S-HERO all 8 scenarios, change package, builder, checkpoint)

#### P1 — Production & fabric depth
- **VXLAN/EVPN fabric foundation** — BGP, NVE, VNI skeleton in `nxos_base.j2` (lab-extendable)
- **Intent + Scenario topology parity** — `enrich_intent_topology()` applies hardware peer-link/keepalive for vPC intent API
- **TACACS+ live block** — renders real `aaa group server tacacs+` when Production details filled
- **Vault filters** — hostname, site, scenario, artifact type (`config`, `manifest`, `package`, `json`)

#### P2 — UX & accessibility
- **Custom port map editor** — toggle on vPC card; editable peer-link/keepalive for Generic or custom cabling; range expand; port chips (`static/port-map-editor.js`)
- **Accessibility** — `:focus-visible` rings, `prefers-reduced-motion` support (M-007 progress)
- **Parse + diff API** — `/util/parse-running-config-diff` for read-only validation against pasted running-config
- **Exe build** — excludes `tkinter`, `matplotlib`, `pytest` modules for smaller offline bundle

#### QA gate
- **20 mandatory stages**, **321 tests** (was 295)
- New stage: `mandatory_v4_world_class` (on_change + pre_release + pre_exe blocker)

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v4.0.0_2026-06-23_110905.exe`

## [3.9.0] - 2026-06-22

### QA automation — full surface coverage (second pass)

Complete second-pass mandatory test expansion: every previously untested API endpoint, CLI feature, baseline option, hardware profile, and the entire IntentEngine are now covered with dedicated assertion tests. Zero gaps remain against the audit inventory.

#### 5 new mandatory test files (144 new tests)

- **`tests/mandatory/test_api_expanded_contracts.py`** (41 tests) — Complete API surface coverage: `/validate`, `/generate-config`, `/intent/preview`, `/intent/generate`, `/history`, `/history/{filename}`, `/system/paths`, `/builder/parse`, `/builder/questions`, `/builder/recommend`, `/checkpoints`, `/checkpoints/{filename}/restore-preview`, `/util/expand-range`, `/util/diff-config`, `/catalog/versions`, `/catalog/scenarios`, `/catalog/hardware`, `/catalog/features`. Plus auth enforcement: 403 on non-loopback for privileged endpoints, 401 on bad `x-config-auth-token`, 200 on correct token. Confirms catalog routes are intentionally public.
- **`tests/mandatory/test_feature_render_coverage.py`** (21 tests) — Every CLI feature renders in the correct config section: `bfd`, `vpc_orphan_suspend`, `vpc_auto_recovery`, `vpc_peer_gateway`, `vpc_peer_switch`, `vpc_delay_restore`, `vpc_arp_sync`, `nxapi`, `bash`, `aaa_tacacs`, `vxlan`. Asserts absence when not enabled. Confirms hardened tier strips `nxapi`/`bash`.
- **`tests/mandatory/test_baseline_options_coverage.py`** (22 tests) — All 14 institutional baseline options render (`baseline_cfs`, `baseline_copp`, `baseline_no_pwd_check`, `baseline_snmp_traps`, `baseline_spanning_tree`, `baseline_cli_aliases`, `baseline_icam`, `baseline_vrf_keepalive`, `baseline_errdisable_recovery`, `baseline_icmp_redirects`, `baseline_vpc_delay_restore_vlan`, `baseline_no_dns_lookup`, `baseline_exec_timeout`, `baseline_logging_source`). Asserts absent when not enabled. Coexistence test with all 14 active simultaneously.
- **`tests/mandatory/test_hardware_profiles_coverage.py`** (22 tests) — All 6 hardware profiles smoke-tested: Nexus 9364C-GX and Nexus 92348GC-X (previously untested) produce valid vPC configs, verify device_class, speed_badges, peer-link port counts. Parametrized render test across all profiles.
- **`tests/mandatory/test_intent_engine_coverage.py`** (38 tests) — IntentEngine (previously zero coverage): all 3 roles (`access`, `leaf`, `spine`), vPC leaf mode, hardened/standard MOTD, custom admin creds, uplink port assignment, resolution profile name/summary/policy_flags, invalid role rejection, API `/intent/preview` contracts.

#### Manifest updated

- 5 new `pre_release`/`pre_exe` blocker stages: `mandatory_api_expanded`, `mandatory_feature_render`, `mandatory_baseline_coverage`, `mandatory_hardware_coverage`, `mandatory_intent_engine`
- Gate now runs **19 stages** (was 14); full test count: **295 tests** (was 151)

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.9.0_2026-06-22_175839.exe`

## [3.8.0] - 2026-06-22

### Field council P1/P2 — gaps closed
- **Storm control on vPC access port-channels** — access-mode Po10+ now get storm-control when feature enabled (matches S2 field requirement)
- **`/scenario/generate` integration tests** — pair export writes two configs, batch folder, vault files (mandatory pre-release)
- **VXLAN/EVPN** — expert callout on Step 1 (guided path unchanged; fabric scenario via expert picker)
- **Gateway SVI (HSRP) card** — visible on Configure when HSRP feature enabled (VLAN + SVI CIDR)
- **Export toggle clarity** — renamed to “Export primary + secondary files” with preview vs export note
- **Hardened secrets modal** — confirms lab-only before Build when TACACS key or local password present
- **Expert scenario grid** — shows default hardware model per scenario + full hardware profile list
- **Layout** — `min-width: 1024px` for engineer desktop displays
- **Config Builder** — full peer-link paste detection test (S7 extended)
- **Legacy NX-OS 7.0** — mandatory render regression on vPC leaf scenario

### Tests
- `tests/mandatory/test_scenario_generate_api.py` — generate pair export (F-002)
- `tests/mandatory/test_field_gap_contracts.py` — storm, HSRP, UI contracts, layout, legacy (P1/P2)
- Manifest stages: `mandatory_generate_api`, `mandatory_field_gaps`

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.8.0_2026-06-22_174146.exe`

## [3.7.4] - 2026-06-22

### Fixed — Interface Planner typing (1 letter at a time)
- **Description**, port, VLAN name, trunk list, and custom CLI fields no longer trigger a full card re-render on every keystroke (focus was lost after each character)
- Text fields update the in-memory plan + live preview only; full re-render runs for structural changes (preset, vPC Po toggle, access/trunk mode)
- `syncInterfacePlansFromDom()` before build/preview as a safety net
- Audited other UI text inputs — main wizard uses native fields + delegated listeners (no re-render-on-input pattern)

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.7.4_2026-06-22_132915.exe`

## [3.7.3] - 2026-06-22

### Fixed — Interface Planner vPC port-channels (40G / 10G / 1G)
- **Root cause**: UI only sent `vpc_port_channel` when **Generate pair** was checked; VLAN/port values were lost until blur (`onchange` only)
- **Interface Planner** now keys off **vPC scenario** (`pair_mode`), not the export toggle — Po ≥ 10 builds in preview even when only exporting primary
- **Default**: vPC port-channel **on** for access/trunk presets on pair scenarios
- **Backend**: auto-applies vPC Po when `access_vlan` / `trunk_*` on pair scenarios (flag optional)
- **Reserved ports**: all port-channel members (incl. core downlinks Eth1/1–4) blocked from planner override
- **Validation**: `planner_warnings` in preview when VLAN missing or port reserved; preflight blocks build

### Tests
- `tests/test_vpc_planner_all_tiers.py` — 24 cases across 40G core, 10G leaf, 1G access (explicit/implicit Po, trunk, API, downlink reserve)

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.7.3_2026-06-22_124730.exe`

## [3.7.2] - 2026-06-22

### Added — mandatory release QA
- **`enterprise_qa_gate.py`** runs `tests/test_instance_control.py` first as **RELEASE BLOCKER** (fail-fast before exe build)
- `docs/06-quality-assurance/RELEASE_QA_GATE.md` — pre-ship checklist and stop/upgrade commands
- Shutdown integration test marked `@pytest.mark.release_blocker`

### Docs
- OFFLINE_RUNBOOK — stop / `--replace` / `--stop` procedures
- CONFIGURATION_STUDIO — Stop / upgrade table

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.7.2_2026-06-22_115434.exe`

## [3.7.1] - 2026-06-22

### Fixed — stop / single-instance loop
- **Stop button** works without session token in the URL (localhost only) — fixes false "stopped" UI while old exe kept running
- **Shutdown** verifies the server actually exited; shows clear error if still listening
- **Hard exit fallback** after Stop (Windows console no longer left orphaned on port 9000)
- **Ctrl+C** in console triggers graceful shutdown
- **`--replace`** flag (or `NXOS_REPLACE_INSTANCE=1`) stops prior listener before starting a new version
- **`--stop`** flag / `scripts/stop_configurator.ps1` — kill stuck instance on port 9000
- PID file: `logs/nxos_configurator.pid`

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.7.1_2026-06-22_115125.exe`

## [3.7.0] - 2026-06-22

### Added — vPC at every speed tier
- **`vpc_access_pair` (1G)** — Nexus 9348GC-FXP dual-switch closet vPC; peer-link Eth1/53–54, keepalive Eth1/47–48, uplinks Eth1/49–50; infra-only by default
- **Roadmap** — Access mode now shows **vPC Yes/No** (was hidden); resolves `vpc_access_pair` vs `standalone_access`
- **40G** `vpc_core_pair` validated across tier tests (hardware ports, pair mirror, no bulk access)

### Fixed
- Config Builder recommends `vpc_access_pair` when role=access and redundancy=vpc
- Encyclopedia copy updated for 1G standalone vs vPC pair

### Tests
- `tests/test_vpc_tier_pairs.py` — 40G/1G vPC, standalone 1G, planner Po mirror, reserved port edge cases
- Field council S4b, hardware profile 9348 vPC ports

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.7.0_2026-06-22_114421.exe`

## [3.6.0] - 2026-06-22

### Changed — infrastructure-only vPC/leaf templates
- **vPC leaf, standalone leaf, VXLAN leaf, spine, and vPC core** now use `interface_count: 0` and `bring_up_spare_ports: false` by default — output is **vPC domain, peer-link, keepalive, and uplinks** only (no bulk `Access_Port_*` stanzas)
- **Standalone access** still generates closet access ports (by design)

### Added — Interface Planner (Configure step)
- **Preset dropdown** per port: bring up, access VLAN, trunk (all/custom), routed, custom CLI
- **vPC port-channel wizard** on pair builds: access or trunk → VLAN name/ID (autocomplete from scenario VLANs) → Po **10+** with `vpc N` and `channel-group N mode active`
- **Mirrored on secondary** switch — same interface, Po number, and vPC config on both A/B configs
- `data/interface_presets.yaml`, `core/interface_customizer.py`, `static/interface-planner.js`
- `tests/test_interface_customizer.py` — 11 tests (pair mirroring, Po allocation, reserved ports, custom CLI, edge cases)

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.6.0_2026-06-22_112418.exe`

## [3.5.2] - 2026-06-22

### Fixed — wizard state & vPC port mapping
- **Restart configuration** — header **Restart** clears roadmap, scenario, form fields, live preview, and cached build state without stopping the program
- **Post-build prompt** — after Build & Save, modal offers **Start new configuration** or stay on current build
- **vPC ports per model** — peer-link and keepalive fields refresh when hardware model, roadmap role, or scenario changes (fixes stale Eth1/35–36 after switching Core → Leaf)
- **Leaf port clarity** — ports 1–46 are server access by design; 47–48 are keepalive LAG members; 53–54 peer-link (not bare `no shutdown` when engine runs correctly)

### Added
- `tests/test_hardware_vpc_ports.py` — hardware profile vPC port matrix + leaf keepalive CLI regression

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.5.2_2026-06-22_105608.exe`

## [3.5.1] - 2026-06-22

### Fixed — CLI formatting (sectioned output)
- **Interface indentation** — port-channel L3 (keepalive), trunk MTU/vpc, and SVI sub-commands now render with correct 2-space indent (Jinja `lstrip_blocks` fix)
- **Section headers** — labeled blocks: Hostname & Global Services, Features, SNMP, VLANs, vPC Domain, Port-Channels, Ethernet Interfaces, Management & Routing, NTP, Logging, CLI Aliases, AAA, Boot System, POST-PASTE CHECKLIST
- **Spacing** — blank line between interface/port-channel stanzas for readable paste

### Added
- `tests/test_template_formatting.py` — indentation + section header regression across all scenarios

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.5.1_2026-06-22_104701.exe`

## [3.5.0] - 2026-06-22

### UX / UI (Field Engineer Council re-audit)
- **Speed tier clarity** — 40G / 10G / 1G cards show model (9336C / 93180 / 9348), descriptions, and (i) encyclopedia popups
- **Auto-speed note** — when Access/OOB/Core auto-select speed, step 3 explains model mapping
- **Configure path banner** — scenario name + one-line operator guidance at top of Configure step
- **Mode cards** — show target Nexus model under each role
- **OOB simplified Configure** — hides baseline grid, presets, and feature toggles (platform-only)
- **Roadmap summary** — includes hardware model in the breadcrumb trail
- **Wizard tips** — rewritten for simplicity (lab ready vs production, speed → model map)

### QA
- Field council speed-tier audit: S1/S9 (40G), S2/S3 (10G), S4 (1G), S5 (OOB) — all CLI checks pass
- Added tests: S9 spine, speed-tier model mapping
- `enterprise_qa_gate` PASS (50 tests)

### Build
- Offline exe: `dist/NXOS_Configurator_Web_v3.5.0_2026-06-22_103540.exe`
- Run locally — browser opens at `http://127.0.0.1:9000` (fully offline)

## [3.4.0] - 2026-06-22

### Fixed (Field Engineer Council — zero-gap release)
- **vPC leaf pair (S2)** — core downlink presets no longer steal Eth1/1–4; access ports and storm-control restored via `apply_vpc_leaf_topology`
- **Access / leaf uplinks (S4)** — `Ethernet1/49–50` (and other uplinks above `interface_count`) now generated as trunks
- **Downlink resolution** — respects `config_matrix.yaml` per scenario; leaf scenarios default off for core Po20/Po21
- **CLI descriptions** — replaced `INTENT_*` placeholders with `Access_Port_N`, `Uplink_N`, `SVI_*`
- **VXLAN/EVPN leaf** — vPC peer-link/keepalive topology applied without core downlinks; baseline options preserved
- **Leaf vPC peer-link** — default port-channel ID aligned to Po1 (was Po100)
- **Release QA** — restored `_prebuild.py`; Configurator-scoped frozen bundle check; doc link scan excludes legacy NST archives
- **TACACS+** — Production details fields render live AAA config when server is filled (comment block when empty)

### Added
- **Site code** field visible on Configure step (was hidden `HQ_DC`)
- **`tests/test_field_council_scenarios.py`** — acceptance tests for council scenarios S1–S8
- Council scenario **S9** — Core standalone (`spine_core`) documented in `SCENARIOS.md`

## [3.3.1] - 2026-06-22

### Added
- **nxos-field-engineer-council** skill — field engineer team audits real-life scenarios (`.cursor/skills/nxos-field-engineer-council/`)

### Fixed
- Unused Ethernet ports (vPC pair): **`no shutdown` only** — removed `description SPARE` and `no switchport` on bare ports
- Duplicate "Bring up unused ports" toggle removed from Configure step

## [3.3.0] - 2026-06-22

### Fixed
- **Action Required false positives** — removed uppercase-word heuristic that flagged FATAL, ACCESS, BPDU, POST-PASTE checklist text, etc.
- Action Required split into **Lab ready** vs **Before production paste** (optional for lab)
- SNMP placeholder lines removed from generated CLI until Production details are filled
- Site/location defaults from Site Name (HQ_DC) — no more NET_DEVICE_LOCATION in lab configs

### Added
- **Bring up unused Ethernet ports** toggle (default ON) — all spare Eth ports get `no shutdown` per hardware profile
- `bring_up_spare_ports` on all scenario defaults

## [3.2.0] - 2026-06-22

### Added
- **Option encyclopedia** (`data/option_encyclopedia.yaml`) — rich help for modes, vPC, baseline, features, downlinks
- **Info popups** — tap **i** on any choice or toggle for what/why/when/CLI effect
- **Quick presets** on Configure — Standard vs Hardened (CoPP, DNS lookup off, TACACS placeholder, no NX-API/bash)
- Baseline: Disable DNS lookup, idle session timeout, syslog source-interface mgmt0
- Feature: AAA / TACACS+ commented placeholder block for production handoff

### Changed
- Wizard tips updated for Mode → vPC → Speed → Configure flow
- Hardened preset aligns with Cisco NX-OS hardening guidance (CoPP, NTP, syslog, ICMP redirects)

## [3.1.0] - 2026-06-22

### Added
- **Guided roadmap wizard** — Mode → vPC → Speed → Configure → Review (replaces 7-card scenario wall)
- **Option B configure screen** — 2×2 card grid: Platform, Baseline, vPC wiring, Downlinks with toggle switches
- `static/roadmap.js` — maps role/vPC/speed choices to scenario templates automatically
- Hostname auto-sanitization (underscores → hyphens) and human-readable preview errors

### Changed
- Expert scenario picker moved behind collapsible on step 1
- NX-OS features and production SNMP/syslog fields collapsed under Advanced on Configure step
- Default core vPC hostname `CORE1-VPC` (hyphen) — fixes live preview validation error
- CONFIGURATION_STUDIO operator guide updated for v3.1 workflow

## [3.0.0] - 2026-06-22

### Added
- **Configuration Studio** — card-grid wizard with persistent split-screen live preview
- Action Required panel — detects placeholders (SNMP, location, boot image) until Advanced fields filled
- Per-option CLI expansion — click features/baseline/downlinks to see exact CLI blocks
- Speed-tier badges on scenarios and models (40G / 10G / 1G / Multi)
- `data/config_matrix.yaml` — scenario × model matrix for UI and documentation
- `data/placeholder_fields.yaml` — placeholder registry with severity and wizard step hints
- `GET /catalog/matrix` — configuration matrix API
- Extended `POST /scenario/preview` — returns `action_required`, `cli_blocks`, `model_meta`
- `core/config_remarks.py` — Action Required engine
- vPC Core Pair (40G) scenario aligned to CORE1_VPC production template
- Institutional baseline checkboxes (CFS, CoPP, SNMP traps, aliases, ICAM, keepalive VRF)
- Leaf downlink toggles (10G / 1G / extra Po3) with model-aware vPC ports
- Advanced card: SNMPv3 user, trap hosts, boot image, site location, spectrum lab user
- Boot image per NX-OS version in `data/nxos_versions.yaml`
- Enterprise docs: CONFIGURATION_STUDIO, CONFIG_MATRIX, CORE_VPC_GUIDE

### Changed
- Web UI v3.0 — Concept B card layout + live debounced preview (400ms)
- Hardware profiles include `device_class`, `primary_speed_label`, `speed_badges`
- Leaf/access scenarios default institutional baseline options
- Template emits `! ATTENTION:` comments for unresolved placeholders

## [2.5.0] - 2026-06-21

### Added
- HSRP auto-configuration on SVIs when feature enabled (`core/device_enricher.py`)
- Management baseline: NTP, syslog, SNMP location in template and wizard
- Security tier (standard/hardened) with automatic feature hardening
- vPC orphan-port suspend, corrected role priority (4096/8192)
- Hardware profiles: Nexus 9364C-GX, 92348GC-X
- Checkpoint list API (`GET /checkpoints`) and UI panel
- Expanded tests (`tests/test_enricher_and_risk.py`)
- Updated `docs/ARCHITECTURE.md` for web-first platform

### Fixed
- Plaintext password only emitted when explicitly set (lab warning in CLI)
- Risk analyzer false positives on `no shutdown` and benign vlan lines
- Static route VRF block structure in template

### Changed
- Trust score target improvements per zero-trust Phase 2 remediation

## [2.4.0] - 2026-06-21

### Added
- Full V6 `.cursor` import (4335 files): skills-sickn33, nst council, SKILL_CATALOG.json, scripts/
- `nxos-orchestrator` skill; Configurator-adapted ROLE_ACTIVATION_MATRIX and governance rules
- Revalidation audit: `.cursor/audits/GAP_REGISTER_2026-06-21_REVALIDATION.md`
- `docs/06-quality-assurance/zero-trust-review/REVALIDATION_POST_SKILL_IMPORT_2026-06-21.md`
- `.cursor/CONFIGURATOR_SKILLS.json` — native skill index supplement
- Zero-trust review skill (`.cursor/skills/nxos-zero-trust-review-team/`)
- QA documentation: `docs/06-quality-assurance/zero-trust-review/` (360 audit, gap register, roadmap, test checklist)
- Field hints catalog (`data/field_hints.yaml`) with wizard tips and inline UI guidance
- CLI preview in Validate response; secondary vPC preview; config in Build response
- Toast notifications, preflight checklist, vault artifact type labels
- Regression tests (`tests/test_scenario_engine.py`)

### Fixed
- vPC peer-link now uses hardware profile ports (not uplinks)
- UI vPC overrides (domain, keepalive, peer-link) applied to backend
- Feature CLI lines render on separate lines (valid NX-OS syntax)
- vPC pair cross-validation before dual generate
- Vault history path unified via `get_history_dir()`
- `/validate` requires auth token

## [2.3.0] - 2026-06-21
### Added
- Web-first wizard UI with scenario cards, feature checkboxes, and NX-OS version selector
- Data catalogs in `data/` (versions, scenarios, feature options)
- Scenario API endpoints: `/catalog`, `/scenario/preview`, `/scenario/generate` with vPC pair support
- Legacy NX-OS 7.x template (`templates/nxos_legacy.j2`)
- Hardened offline exe build (`utils/build_exe.py`)
- Organized docs library with disaster recovery runbook
- Imported `.devin` skill framework and `.cursor` skills from Net Management Tool V6

### Changed
- Primary delivery is web platform (browser UI, not Tkinter)
- Version-aware Jinja2 rendering in `core/renderer.py`
- `requirements.txt` includes FastAPI, Uvicorn, Pydantic, PyInstaller

## [2.0.0] - 2026-04-13
### Added
- Added a visual wizard stepper with active/completed states for first-time operator guidance.
- Added global and section readiness badges (green/red) tied to live preflight validation.
- Added wizard next/previous controls to simplify end-to-end navigation.

### Changed
- Increased control sizes, spacing, and text hierarchy for faster readability and safer operation under pressure.
- Improved UI action clarity for Validate/Build readiness and review flow.
- Finalized UX-polish release packaging with updated versioning and EXE metadata.

## [2.0.1] - 2026-04-14
### Changed
- Made **Simple Config (Intent)** the default first-screen workflow; moved manual configuration tabs under **Advanced Mode** to reduce cognitive load.
- Added vPC peer-link/keepalive **port suggestions** based on selected Nexus switch model (auto-filled when empty, still operator-overridable).
- Aligned UI model strings with backend model identifiers to prevent mismatched defaults.

## [1.9.0] - 2026-04-13
### Fixed
- Resolved vPC Validate flow instability by adding strict client preflight checks and vPC payload sanitization before API submission.
- Eliminated generic `ENGINE ERROR: Failed to fetch` user experience for incomplete vPC inputs through deterministic preflight blocking and clearer guidance.

### Added
- Added dual-mode UX controls: **Simple Wizard** (default) and **Advanced Mode**.
- Added one-click **Apply Safe Defaults** helper for management and vPC critical fields.
- Added **Preflight Review** panel that shows final payload before API execution.
- Added backend defensive vPC model validation for malformed peer-link/keepalive combinations.

### Changed
- Validate/Build actions now remain disabled until minimum required inputs are structurally valid.
- Improved client-side operator guidance for junior engineers via inline preflight messaging.

## [1.8.0] - 2026-04-13
### Added
- Implemented a full **Intent-to-Config Blueprint** engine for Access, Leaf, and Spine workflows.
- Added secure intent endpoints: `/intent/preview` and `/intent/generate`.
- Added guided Intent Blueprint mode in the web UI with role/security/redundancy profiles and preview-first workflow.
- Added intent artifact outputs (`intent`, `blueprint_summary`, `blueprint_policy`) into the historical artifact vault.

### Changed
- Upgraded startup diagnostics with runtime metadata logging in bootstrap logs.
- Extended pipeline artifact writer to support structured, release-grade extra artifacts.
- Aligned web/API/UI/build metadata for the 1.8.0 institutional release.

## [1.7.0] - 2026-04-13
### Added
- Enforced privileged endpoint access controls with per-session auth token support for offline browser sessions.
- Added role-based profile presets and interface normalization workflows to reduce operator input time.
- Added safer artifact access protections to block path traversal in vault history endpoints.

### Changed
- Upgraded web UI styling to a MacOS-inspired institutional dashboard aesthetic with clearer hierarchy.
- Reworked shutdown flow to request graceful server lifecycle termination instead of forceful process exit.
- Improved compliance findings with remediation-focused guidance text for network operators.
- Hardened logger configuration with rotating file handling and duplicate-handler protection.
- Sanitized generated artifact filename prefixes to prevent invalid path/filename usage.

## [1.6.0] - 2026-04-12
### Added
- **Institutional Release**: Transformed system into the "Configuration Authority System".
- **Phase 6-7**: Implemented Authority Metadata Headers and `/configs/history/` management.
- **Phase 8-9**: Added Strategic Interface Profiles (ACCESS_SERVER, TRUNK_UPLINK) and Layer 3 features (SVI, HSRP v2, Static Routes).
- **Phase 10**: Enabled vPC Consistency Validation for multi-device parity.
- **Phase 11**: Launched FastAPI Backend and Web-based Provisioning Dashboard.
- **Phase 12-13**: Rebranded UI and automated Institutional EXE Build system.
- **Phase 14-16**: Completed Master Documentation, Full QA Audit, and Disaster Recovery Backup system.

## [1.5.1] - 2026-04-12
### Added
- Implemented PyInstaller distribution layer for offline standalone EXE creation.
- Added support for internal resource path handling using `sys._MEIPASS` for bundled templates.

## [1.5.0] - 2026-04-12
### Added
- Implemented full configuration build pipeline (`pipelines/build_pipeline.py`).
- Automated generation of `config.txt`, `diff.txt`, and `risk.txt`.
- Integrated `RiskAnalyzer` for automated CLI security auditing.

## [1.4.0] - 2026-04-12
### Added
- Integrated a comprehensive validation engine (`core/validator.py`).
- Pre-rendering checks for: Duplicate VLANs, IP address syntax, interface conflicts, and mode validity.
- Structured validation reporting in the GUI.

## [1.3.0] - 2026-04-12
### Added
- Migrated configuration generation to Jinja2 templates (`templates/nxos_base.j2`).
- Introduced modular `ConfigRenderer` for decoupled template handling.
- Optimized vPC logic for template-driven assembly.

## [1.2.0] - 2026-04-12
### Added
- Introduced structured data models using Python dataclasses (`Device`, `VLAN`, `Interface`, `VPCConfig`).
- Migrated Engine and UI to use structured objects for configuration generation.
- Enhanced internal data validation via model-based structures.

## [1.1.0] - 2026-04-12
### Changed
- Refactored project structure into layered architecture:
  - Created `/core`, `/modules`, `/models`, `/templates`, `/pipelines`.
  - Moved logic into modular components in `/modules/`.
  - Introduced `core/engine.py` as the orchestration layer.
  - Isolated models into `models/`.

## [1.0.0] - 2026-04-12
### Added
- Initial project structure.
- Governance system: Versioning, Changelog, Logging, and Backup utility.
