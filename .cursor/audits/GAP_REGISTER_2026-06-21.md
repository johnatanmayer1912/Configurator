# NLAP Zero-Trust Gap Register

- **Version:** 5.3.10
- **Date:** 2026-06-21
- **Council:** nlap-release-council
- **pytest:** 519 passed / 149 mandatory passed / 2 skipped

## Executive summary

v5.3.10 closes **G-04**, **G-24**, **G-27**, and **G-29–G-32** (integration QA, UI consolidation, component split, accessibility, mobile, unified status, design tokens). **Approved** for skilled-operator offline deployment.

---

## Fixed in v5.3.10

| ID | Item | Evidence |
|----|------|----------|
| G-04 | Acquisition integration tests | `tests/test_acquisition_integration.py` — 19 pass with `NLAP_RUN_INTEGRATION=1`; CI step in `mandatory-qa.yml` |
| G-24 | Advanced entry paths consolidated | `partials/incident_story_tab.html` — `#incident-advanced-options` |
| G-27 | Component split | `nlap-design-system.css`, partial include, index ~6030 lines |
| G-29 | Accessibility | skip link, ARIA, `:focus-visible` in `nlap-a11y-mobile.css` |
| G-30 | Mobile/tablet layout | `@media` rules in `nlap-a11y-mobile.css` |
| G-31 | Unified status styling | `static/js/nlap-ui-status.js`, `.nlap-status-banner` |
| G-32 | Design tokens | `--nlap-status-*` tokens in a11y CSS + base tokens in design system |

Mandatory tests: `tests/mandatory/test_lens_gap_closure.py` (MQA-gap04 through MQA-gap32)

---

## Fixed in v5.3.9 (P0 + P1)

| ID | Item |
|----|------|
| FIX-01–21 | See prior register — forensic brain, mandatory QA harness, workflow locks, UI CTA |

---

## Open — deferred by user request

| ID | Item |
|----|------|
| G-06 | Junos counter/correlation parity behind Cisco |
| G-07 | Per-host credentials for multi-device |
| G-10 | One-click closure ZIP |
| G-23 | Compare two incidents |

---

## Open — remaining for public / enterprise release

| ID | Sev | Item |
|----|-----|------|
| G-14 | P2 | Streaming correlation for 100k+ log lines |
| G-20 | P2 | First-run guided tour (beyond help text) |
| G-22 | P2 | PCAP demo manifest optional in some environments |
| G-28 | P2 | In-app “what’s new” on version bump |
| G-33 | P3 | ITSM webhooks (ServiceNow/Jira) |
| G-34 | P3 | Role-based UI |
| G-35 | P3 | Signed EXE / update channel |
| G-36 | P3 | SNMP/trap ingest |
| G-37 | P3 | Plugin SDK |
| G-38 | P3 | i18n |

---

## Council verdict

**Approved** for skilled-operator offline use on v5.3.10. Enterprise mass release still blocked on G-33–G-35 until ITSM/RBAC/signed installer land.
