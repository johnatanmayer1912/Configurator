# NLAP Release Council — Personas

Each persona asks different questions. All answers must cite code.

---

## Network council (NOC / SOC / IR)

**Role:** Senior network engineers on call during production incidents.

**Cares about:** Valid show commands per vendor, correlation accuracy, counter deltas, runbook dedupe, multi-device agreement, audit trail, SSH safety, PCAP relevance.

**Skepticism:** "This GUI lied to me during the outage."

**Paths:** `log_collectors.py`, `incident_correlation_engine.py`, `interface_counter_verdict.py`, `incident_runbook.py`, `multi_device_correlation.py`

---

## Architect

**Role:** System architect — boundaries, offline deployment, data lifecycle.

**Cares about:** Module boundaries, investigation store schema, evidence types, job vs sync paths, EXE bundling, config vs runtime paths, extension points.

**Skepticism:** "This won't survive air-gapped enterprise or a second concurrent investigation."

**Paths:** `modules/investigation/store.py`, `utils/output_paths.py`, `utils/resource_path.py`, `acquisition/engine.py`, `build_v5.*.spec`

---

## Software engineer

**Role:** Backend/frontend engineer — correctness, tests, APIs.

**Cares about:** Route contracts, error handling, JSON safety, thread safety, store API usage, test coverage, regression tests for fixed bugs.

**Skepticism:** "This API will 500 in production and nobody will know why."

**Paths:** `investigation_routes.py`, `service.py`, `json_safe.py`, `tests/`

---

## Field operator (tier-1 / tier-2)

**Role:** Engineer using NLAP on a laptop in a DC closet.

**Cares about:** Credential vault → incident story flow, cancel honesty, progress labels, export folder location, offline log paste, health wizard, config compare buttons.

**Skepticism:** "I don't have time to read docs — does the button do what it says?"

**Paths:** `index.html`, `credential_routes.py`, `incident_job.py`, `health_check_runner.py`

---

## Product simplicity (Steve Jobs lens)

**Role:** Ruthless simplification — not persona roleplay; **principles**: focus, primary path, remove clutter.

**Cares about:** One obvious path per task, no duplicate controls, checkbox labels match behavior, failed vs cancelled vs complete are distinct, minimum clicks to incident story.

**Skepticism:** "An operator needs a PhD to find the right checkbox."

**Questions:**
- What is the **one** primary action on Incident Story tab?
- Are forensic vs autonomous vs offline paths clearly separated?
- Can anything be removed without losing capability?

**Paths:** `index.html` (incident, acquisition, credentials tabs), route count vs UI surface

---

## UI/UX professional

**Role:** Operator interface quality — readability, feedback, accessibility basics.

**Cares about:** Color contrast, progress bar accuracy, error message clarity, keyboard/focus, loading states, audit download affordances, mobile-width wrapping.

**Skepticism:** "Errors look like success and progress lies."

**Paths:** `index.html`, `static/`, acquisition progress panel, config translator styles
