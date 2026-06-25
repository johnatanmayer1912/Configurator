# SKILL: INDEX PROMPT

| Field | Value |
|-------|-------|
| **Version** | 4.0.0 |
| **Status** | active |
| **Owner** | Prompt Governance Framework |
| **Registry ID** | G-00 |
| **last_updated** | 2026-06-16 |

---

## Purpose

**MANDATORY** entry point for the master prompt system. **READ THIS FIRST** before any work. This skill orchestrates the entire prompt governance framework and ensures proper role activation and dependency ordering.

---

## Required Reading Order

The AI **MUST** read in this order (canonical paths only):

| Step | File |
|------|------|
| 1 | `GLOBAL_MASTER_PROMPT_RULES.md` (G-18) |
| 2 | `PROMPT_COMMAND_CENTER.md` (G-CC) — commands, all-in-one, mandatory doc sync |
| 3 | This file (`INDEX_PROMPT.md`) |
| 4 | `PROMPT_REGISTRY.md` (G-01) |
| 5 | `PROMPT_USAGE_MANUAL.md` (G-02) |
| 6 | `PROMPT_ACTIVATION_POLICY.md` (G-13) |
| 7 | `ROLE_USAGE_STANDARD.md` (G-14) |
| 8 | `PROMPT_EXECUTION_RULES.md` (G-15) |
| 9 | Policies G-03–G-11 (as applicable) |
| 10 | Council roles (as applicable) | `roles/combined/ROLE_*_USAGE_PROMPT.md` |
| 11 | Relevant **project documentation** | `docs/`, `LIBRARIAN_MANDATE.md`, `15-rebuild-roadmap/` if rebuilding |
| 12 | Latest **codebase changes** | Hot paths, diff, `VERSION` |
| 13 | Latest **release notes** | `CHANGELOG.md`, bug fixes |

**Then execute:** identify roles → dependency order → action logs → registry → documentation (G-15 Phase B).

**Extended:** `FINAL_OPERATING_INSTRUCTION.md` (G-17) · full `PLATFORM_PROMPTS/` for major RESYNC · `roles/CHECK_SYSTEM_FOR_BUGS.md` when user requests system bug check.

---

## Mandatory Rules

1. Read this file before any other prompt or action.
2. Read `PROMPT_REGISTRY.md` before any change.
3. Read original prompts in `docs/02-codebase/PLATFORM_PROMPTS/`.
4. **NEVER** delete original prompts.
5. Copy originals into `docs/13-master-prompts/` before enhancement.
6. **SYNC** forward, don't replace history.
7. Every council role has **role + usage** in one combined file (G-14); domain roles keep separate `*_USAGE.md`.
8. Create an **action log** for every meaningful role invocation.
9. Apply correct **policy prompts** before work.
10. Use dependency chain: **architect → developer → QA → security → observability → documentation → release** (RESYNC / Product Strategist precede architect when scope changes).
11. Escalate unresolved conflicts to `TEAM_MEETING.md` (G-11).
12. **RESYNC** before every significant action.
13. AI **MUST** automatically identify and activate **all** relevant roles from task scope, not just user-named roles.
14. **IF** role relevance uncertain, err on the side of **inclusion and escalation**.

**Authoritative superset:** `GLOBAL_MASTER_PROMPT_RULES.md` (G-18) — 20 absolute rules.

---

## Role Auto-Activation Rule (Critical)

The AI **MUST** infer all relevant roles from task domain and system context.  
The AI **MUST NOT** rely only on roles explicitly named by the user.  
If a role's mission is relevant, it **MUST** be loaded, read, and applied.  
If role relevance is uncertain, the AI **MUST** err on the side of inclusion and escalation.

Full matrix: `PROMPT_ACTIVATION_POLICY.md` (G-13).

---

## Simple Commands the User Can Type

**Authoritative tables:** **`PROMPT_COMMAND_CENTER.md` (G-CC)** · **`FINAL_OPERATING_INSTRUCTION.md` (G-17)**

| User types | AI does |
|------------|---------|
| **check system for bugs** | `roles/CHECK_SYSTEM_FOR_BUGS.md` → `docs/14-bug-reports/` (all roles) |
| **fix bug [ID]** | fix-prompt + **mandatory doc/rebuild sync** |
| **code review** / **code review doc sync** | R-ARCH → R-ENG → R-QA → R-LIB (+ R-RECON) |
| **rebuild from docs** | `15-rebuild-roadmap/DISASTER_RECOVERY_COMMAND.md` (one batch at a time) |
| **prepare release** / **/release-vX.Y.Z** | R-REL chain + rebuild index version bump |
| **Any implementation task** | Auto: R-ENG + R-QA + **R-LIB + R-RECON doc sync** (no separate command needed) |

---

## Project Mission

Build the most capable, maintainable, extensible, reliable, and professionally engineered **network management platform in the world**.

Mission, vision, and engineering principles (full text): `GLOBAL_MASTER_PROMPT_RULES.md` (G-18).

---

## Required Outputs Before Work

- Relevant prompts identified
- Relevant policies identified
- Relevant docs identified
- Risks identified
- Approval chain identified
- Next action defined

---

## Behavioral Standard

The prompt system must support enterprise-grade maintainability, safety, observability, compatibility, and strategic product growth while preserving **legacy prompt intent**.

---

## Local Paths

| Asset | Path |
|-------|------|
| Command center | `docs/13-master-prompts/PROMPT_COMMAND_CENTER.md` |
| Rebuild (disaster) | `docs/15-rebuild-roadmap/` |
| Master hub | `docs/13-master-prompts/` |
| Bug sweep output | `docs/14-bug-reports/` (prompt: `roles/CHECK_SYSTEM_FOR_BUGS.md`) |
| Bug scaffolds | `docs/14-bug-reports/_SCAFFOLD/` |
| Council roles (canonical) | `docs/13-master-prompts/roles/combined/` |
| Original prompts | `docs/02-codebase/PLATFORM_PROMPTS/` |
| Action logs | `docs/13-master-prompts/action-logs/` |
| Version / changelog | `/VERSION`, `/CHANGELOG.md` |

---

## Auto-Activation

This skill **MUST** be automatically activated at the start of every AI session to ensure proper governance and role activation.

---

## Related Skills

- `GLOBAL_MASTER_PROMPT_RULES` (G-18)
- `PROMPT_REGISTRY` (G-01)
- `PROMPT_COMMAND_CENTER` (G-CC)
- `FINAL_OPERATING_INSTRUCTION` (G-17)
- `PROMPT_EXECUTION_RULES` (G-15)
- All council role skills (R-ARCH, R-ENG, R-QA, R-SEC, R-OBS, R-LIB, R-REL, R-PROD, R-COUNCIL)
