# NLAP Release Council — Workflow

## Phase 0 — Resync (mandatory)

1. Read `VERSION`
2. `git status` — note scope of change
3. Load `qa/mandatory/MANIFEST.yaml` — confirm lens list current
4. Load [QUESTIONNAIRE.md](QUESTIONNAIRE.md) + [PERSONAS.md](PERSONAS.md)

## Phase 1 — Mandatory automation check

When **executing** (release or explicit council run):

```bash
python scripts/run_mandatory_qa.py --manifest-check
python scripts/run_mandatory_qa.py
python -m pytest tests/ -q
python _prebuild.py
```

When **adding tests only** (user requested no run): update manifest + test files; skip execution.

## Phase 2 — Persona rounds

For each persona in PERSONAS.md:

1. Assign questionnaire sections (see mapping below)
2. Grep/read until evidence or GAP
3. Log finding with severity P0–P3

| Persona | Questionnaire sections |
|---------|------------------------|
| Network council | A, B, C, H, I, J |
| Architect | K, L, M, E |
| Software engineer | N, O, B (API contracts) |
| Field operator | D, P, Q |
| Product simplicity | R, D (primary paths) |
| UI/UX | D, S, T |

## Phase 3 — Gap → test evolution

For each GAP:

1. Add ID `MQA-<lens>-<nnn>` to gap register
2. Add `@pytest.mark.mandatory` test in `tests/mandatory/test_lens_<lens>.py`
3. Register in `qa/mandatory/MANIFEST.yaml` under correct lens
4. Link test name in gap register row

See `qa/mandatory/EVOLUTION_POLICY.md`.

## Phase 4 — Deliverables

1. `.cursor/audits/GAP_REGISTER_<date>.md`
2. Updated `tests/mandatory/` + `MANIFEST.yaml` if gaps found
3. `docs/06-quality-assurance/MANDATORY_RELEASE_GATE.md` — bump "last council run" if executed
4. Ship decision: **no P0**, P1 documented or fixed

## Severity

| Level | Meaning | Examples |
|-------|---------|----------|
| P0 | Security / data loss / ship blocker | LAN cred leak, wrong store API, SSRF |
| P1 | Core workflow broken | Story not saved, cancel ignored |
| P2 | Vendor parity / UX deception | Wrong show command, progress lies |
| P3 | Polish | Copy, contrast, docs drift |

## Stop-the-line (P0)

- Plaintext credentials exposed off localhost
- SSH/credential routes without local guard
- Unauthenticated shutdown from LAN
- SSRF in PCAP URL fetch
- Forensic workflow loses incident story (no code path to UI)
