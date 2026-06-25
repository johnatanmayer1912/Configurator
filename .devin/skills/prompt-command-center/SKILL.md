# SKILL: PROMPT COMMAND CENTER

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Status** | active |
| **Owner** | Prompt Governance Framework |
| **Registry ID** | G-CC |
| **last_updated** | 2026-06-16 |

---

## Purpose

All-in-one command center for role activation, batch operations, and mandatory documentation synchronization. This skill provides centralized orchestration for the entire prompt governance framework.

---

## Core Commands

### User Commands (Simple)

| User types | AI does |
|------------|---------|
| **check system for bugs** | `roles/CHECK_SYSTEM_FOR_BUGS.md` → `docs/14-bug-reports/` (all roles) |
| **fix bug [ID]** | fix-prompt + **mandatory doc/rebuild sync** |
| **code review** / **code review doc sync** | R-ARCH → R-ENG → R-QA → R-LIB (+ R-RECON) |
| **rebuild from docs** | `15-rebuild-roadmap/DISASTER_RECOVERY_COMMAND.md` (one batch at a time) |
| **prepare release** / **/release-vX.Y.Z** | R-REL chain + rebuild index version bump |
| **Any implementation task** | Auto: R-ENG + R-QA + **R-LIB + R-RECON doc sync** (no separate command needed) |

### Role Activation Commands

| Command | Description |
|---------|-------------|
| `/activate-role [role-name]` | Activate a specific council role |
| `/activate-roles [role1,role2,...]` | Activate multiple roles in dependency order |
| `/auto-activate` | Automatically activate all relevant roles based on task scope |
| `/list-roles` | List all available council and domain roles |
| `/role-info [role-name]` | Display detailed information about a specific role |

### Documentation Commands

| Command | Description |
|---------|-------------|
| `/full-docs-sync` | Execute full documentation synchronization (R-RECON + R-LIB) |
| `/doc-sync [module]` | Sync documentation for specific module |
| `/registry-update` | Update prompt registry with new changes |
| `/action-log [role]` | Create action log entry for role invocation |

### Batch Operations

| Command | Description |
|---------|-------------|
| `/batch-rebuild [batch-name]` | Execute batch rebuild from roadmap |
| `/batch-test [test-group]` | Run batch of tests |
| `/batch-review [review-type]` | Execute batch code review |

---

## Mandatory Doc Sync

**CRITICAL:** Every implementation role (R-ENG, R-ARCH, R-QA, R-REL, etc.) **MUST** treat documentation sync as part of **done**, not a follow-up task.

The `docs/15-rebuild-roadmap/` folder **MUST** stay current with code — R-RECON + R-LIB on every meaningful merge; disaster recovery is invalid if prompts drift.

---

## Dependency Chain Enforcement

When multiple roles are activated, they **MUST** be coordinated in dependency order:

```
RESYNC
→ Product Strategist (when scope/direction changes)
→ System Architect
→ Lead Developer
→ QA Engineer
→ Security Reviewer (if applicable)
→ Observability Engineer (if applicable)
→ Documentation Steward
→ Release Manager (if shipping)
→ Prompt Librarian (if prompts/registry changed)
```

**Team Meeting Council** overlays any step when conflicts exist.

---

## Auto-Activation

This command center **MUST** support automatic role activation based on task scope and system context, as defined in `PROMPT_ACTIVATION_POLICY.md` (G-13).

---

## Action Log Integration

Every meaningful command execution **MUST** create an action log entry using the template from `roles/_ACTION_LOG_SNIPPET.md`.

---

## Related Skills

- `INDEX_PROMPT` (G-00)
- `GLOBAL_MASTER_PROMPT_RULES` (G-18)
- `PROMPT_REGISTRY` (G-01)
- `PROMPT_ACTIVATION_POLICY` (G-13)
- `PROMPT_EXECUTION_RULES` (G-15)
- `FINAL_OPERATING_INSTRUCTION` (G-17)
- All council role skills (R-ARCH, R-ENG, R-QA, R-SEC, R-OBS, R-LIB, R-REL, R-PROD, R-COUNCIL)

---

## Auto-Activation

This skill **MUST** be automatically activated to provide centralized command orchestration for the entire prompt governance framework.
