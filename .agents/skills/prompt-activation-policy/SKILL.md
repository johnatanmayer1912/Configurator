# SKILL: PROMPT ACTIVATION POLICY

| Field | Value |
|-------|-------|
| **Version** | 4.0.0 |
| **Status** | active |
| **Owner** | Prompt Governance Framework |
| **Registry ID** | G-13 |
| **last_updated** | 2026-06-16 |

---

## Purpose

Define the automatic role activation policy that ensures all relevant roles are loaded and applied based on task scope and system context, without requiring explicit user invocation.

---

## Core Principle

The AI **MUST** automatically activate **ALL** relevant roles from task domain and system context. The AI **MUST NOT** rely only on roles explicitly named by the user. If a role's mission is relevant, it **MUST** be loaded, read, and applied. If role relevance is uncertain, the AI **MUST** err on the side of inclusion and escalation.

---

## Activation Rules

### 1. Domain-Based Activation

Roles are automatically activated based on task domain signals:

| Signal | Activate |
|--------|----------|
| `vpc`, `member interface`, `keepalive` | U-TOPO, U-QA, D-QA-VPC |
| `search_it`, `description` | U-ENG, D-SEARCH |
| `plugin` | U-ORCH, U-REG, plugin doc |
| `500`, `Jinja`, `template` | U-ENG, U-UI, U-QA |
| `EXE`, `PyInstaller`, `dist` | U-REL, U-QA |
| governance, registry, INDEX | U-GOV-LIB, G-00–G-15 |
| secrets, SSH, password | U-SEC |
| `VERSION`, release | U-REL, U-LIB |

### 2. Dependency Chain Activation

When multiple roles are relevant, coordinate in **dependency order**:

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

### 3. Council Role Activation

Council roles are activated based on their mission relevance:

| Role | Mission | Auto-Activation Triggers |
|------|---------|--------------------------|
| RESYNC | Reconstruct full project context | Before every significant action |
| Prompt Librarian | Maintain prompt ecosystem integrity | Governance, registry, INDEX tasks |
| System Architect | System coherence and scalability | Architecture, module boundaries, dependencies |
| Lead Developer | Implement approved changes safely | Code implementation, refactoring |
| QA Engineer | Verify correctness, no regression | Testing, validation, compatibility |
| Security Reviewer | Protect from unsafe behavior | Security, trust boundaries, secrets |
| Observability Engineer | Observable, diagnosable, operationally transparent | Diagnostics, monitoring, logging |
| Documentation Steward | Accurate docs aligned with code | Documentation changes, doc sync |
| Release Manager | Readiness, rollout discipline, rollback | Release preparation, deployment |
| Product Strategist | Mission and competitive advantage | Scope changes, strategic decisions |
| Team Meeting Council | Cross-functional review | Unresolved conflicts, escalations |

### 4. Domain Specialist Activation

Domain specialists are activated **in addition** to council roles when task signals match:

| Role | Mission | Auto-Activation Triggers |
|------|---------|--------------------------|
| TOPOLOGY | Network topology, VPC, and map intelligence | VPC, topology, network mapping |
| ORCHESTRATOR | Multi-device and plugin workflows | Plugin workflows, automation |
| UI DYNAMO | Web UI and template safety | UI, Flask, Jinja, templates |
| Plugin Registry | Plugin identity and registration | Plugin development, registry |

---

## Escalation Rules

1. **Unresolved conflicts** → Escalate to **Team Meeting Council** (`TEAM_MEETING.md`, G-11)
2. **Architecture boundary disputes** → U-ARCH + U-ENG → U-COUNCIL
3. **Breaking change without migration plan** → Block until documented or meeting decision
4. **Role relevance uncertain** → Err on the side of **inclusion and escalation**

---

## Action Log Requirements

Every meaningful role invocation MUST log:

| Field | Content |
|-------|---------|
| **structure reviewed** | Modules, files, diagrams, boundaries |
| **decisions made** | Approve / reject / defer with rationale |
| **tradeoffs noted** | Alternatives considered |
| **risks recorded** | Coupling, compatibility, performance, security |

Template: `roles/_ACTION_LOG_SNIPPET.md`

---

## Auto-Activation Enforcement

This policy **MUST** be enforced automatically by the AI:

1. **Before any work**: Identify all relevant roles based on task scope
2. **Load roles**: Read and apply all relevant role prompts
3. **Coordinate**: Ensure proper dependency ordering
4. **Escalate**: If conflicts or uncertainty exists, escalate to Team Meeting
5. **Log**: Create action log for every meaningful invocation

---

## Related Skills

- `INDEX_PROMPT` (G-00)
- `GLOBAL_MASTER_PROMPT_RULES` (G-18)
- `ROLE_MATRIX` (G-04)
- `PROMPT_EXECUTION_RULES` (G-15)
- `ROLE_USAGE_STANDARD` (G-14)
- All council role skills (R-ARCH, R-ENG, R-QA, R-SEC, R-OBS, R-LIB, R-REL, R-PROD, R-COUNCIL)
