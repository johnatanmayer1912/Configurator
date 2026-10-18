# RESYNC Skill

**Role:** Synchronization and Context Reconstruction
**Registry ID:** U-RESYNC
**Version:** 5.3.1
**Status:** Active
**Owner:** Prompt Governance Framework
**Last Updated:** 2026-06-15

---

## Mission

Reconstruct full project context before any significant action, ensuring the AI has complete, current understanding of the NLAP platform state, documentation, code, policies, and changes.

---

## Automatic Activation

This skill should be **automatically activated** when:
- Any significant work is initiated
- Context appears stale or outdated
- Council role activation is needed
- New session begins or context reconstruction is needed
- User requests context refresh
- Before any major changes or decisions

---

## Core Responsibilities

- Reconstruct complete project context
- Ensure current understanding of platform state
- Validate documentation currency
- Check for recent changes and updates
- Identify context gaps or inconsistencies
- Provide current project status summary
- Establish risk list for proceeding actions
- Determine next appropriate actions

---

## Resync Procedure (Complete)

**Phase 1: Governance Foundation**
1. Read `docs/13-master-prompts/governance/INDEX_PROMPT.md` (G-00)
2. Read `docs/13-master-prompts/governance/PROMPT_REGISTRY.md` (G-01)
3. Read `docs/13-master-prompts/governance/GLOBAL_MASTER_PROMPT_RULES.md` (G-18)

**Phase 2: Platform Knowledge**
1. Read `docs/13-master-prompts/governance/PLATFORM_KNOWLEDGE_MODEL.md` (POS-02)
2. Read `docs/00-overview/project-overview.md`
3. Read `docs/README.md` - Documentation master hub

**Phase 3: Recent Changes**
1. Read `/CHANGELOG.md` - Latest changes and version history
2. Read `/VERSION` - Current platform version
3. Check recent git commits (if applicable)
4. Review recent bug reports in `docs/14-bug-reports/`

**Phase 4: Architecture and Codebase**
1. Read `docs/01-architecture/system-architecture.md`
2. Read `docs/02-codebase/repository-structure.md`
3. Review relevant feature documentation based on task

**Phase 5: Policies and Procedures**
1. Read relevant policies based on task context:
   - G-03: Prompt Governance Policy (for prompt work)
   - G-06: Documentation Policy (for doc work)
   - G-07: Quality Gate Policy (for quality work)
   - G-08: Change Management Policy (for code changes)
   - G-09: Release Management Policy (for releases)
   - G-10: Competitive Advantage Policy (for strategic work)

**Phase 6: Professional Standards**
1. Read `docs/13-master-prompts/standards/PROFESSIONALISM_STANDARDS.md` (G-22)
2. Read `docs/13-master-prompts/standards/OUTPUT_SPECIFICATIONS.md` (G-23)
3. Read `docs/13-master-prompts/standards/ONLINE_SEARCH_STRATEGIES.md` (G-21)

**Phase 7: Context Validation**
1. Validate VERSION consistency across files
2. Check for recent file modifications
3. Identify any documentation drift or inconsistencies
4. Verify registry accuracy against filesystem

**Phase 8: Risk Assessment**
1. Identify potential risks for proceeding actions
2. Check for outstanding issues or blockers
3. Assess current system state
4. Identify required role activations

---

## Context Output Format

**Platform Status Summary:**
```markdown
## Platform Status
- **Version:** [Current version from VERSION and PKM]
- **Status:** [Stable/In Transition/Issue Detected]
- **Last Updated:** [Date of most recent significant change]

## Current Context
- **Architecture:** [Brief architecture state summary]
- **Documentation:** [Documentation currency status]
- **Codebase:** [Codebase state summary]
- **Active Issues:** [Known issues or blockers]
- **Recent Changes:** [Summary of recent significant changes]

## Context Validation
- **VERSION Consistency:** [PASS/FAIL]
- **Documentation Currency:** [Current/Stale]
- **Registry Accuracy:** [Accurate/Inaccurate]
- **Known Risks:** [List of identified risks]

## Recommended Actions
1. [Specific action 1]
2. [Specific action 2]
3. [Specific action 3]

## Required Role Activations
- [Role 1]: [Reason for activation]
- [Role 2]: [Reason for activation]
```

---

## Risk Identification

**Context Risks:**
- Stale or outdated documentation
- VERSION inconsistencies across files
- Registry mismatch with filesystem
- Orphaned prompts or documentation
- Unclear recent changes

**Operational Risks:**
- Outstanding bug reports or issues
- Incomplete quality gates
- Pending documentation updates
- Unresolved role conflicts
- Missing dependencies or requirements

**Quality Risks:**
- Missing validation or testing
- Incomplete documentation for changes
- Unclear scope or requirements
- Undefined quality criteria
- Missing rollback procedures

---

## Success Criteria

- [ ] All governance documents read and understood
- [ ] Platform knowledge model validated
- [ ] Recent changes reviewed and contextualized
- [ ] Architecture and codebase context established
- [ ] Relevant policies identified for task
- [ ] Professional standards reviewed
- [ ] Context validation completed
- [ ] Risks identified and documented
- [ ] Required role activations determined
- [ ] Next steps clearly defined

---

## Professional Standards

**Context Accuracy:**
- Ensure all information is current and accurate
- Validate VERSION consistency across sources
- Check for recent file modifications
- Verify documentation currency

**Risk Awareness:**
- Identify potential risks proactively
- Assess impact of context gaps
- Consider dependencies and requirements
- Evaluate readiness for proceeding actions

**Clear Communication:**
- Provide clear context summary
- Document risks and recommendations
- Specify required role activations
- Define next steps explicitly

---

## Special RESYNC Functions

**Context Reconstruction:**
- Rebuild complete understanding after session break
- Re-establish governance framework context
- Re-validate platform state information
- Re-identify current operational status

**Context Refresh:**
- Update existing context with new information
- Validate currency of existing understanding
- Add new information to context
- Adjust recommendations based on new context

**Context Validation:**
- Verify accuracy of existing context
- Check for consistency across sources
- Identify gaps or inconsistencies
- Validate required information completeness

---

## Related Documentation

- `docs/13-master-prompts/governance/INDEX_PROMPT.md` - Master entry point
- `docs/13-master-prompts/governance/PROMPT_REGISTRY.md` - Prompt inventory
- `docs/13-master-prompts/governance/PLATFORM_KNOWLEDGE_MODEL.md` - Platform knowledge
- `docs/13-master-prompts/governance/GLOBAL_MASTER_PROMPT_RULES.md` - Absolute rules
- `docs/13-master-prompts/special/RESYNC.md` - Special RESYNC procedures

---

## Usage Notes

This skill is designed to be **automatically invoked** at the start of significant work sessions or when context reconstruction is needed. It provides the foundational context that ensures all subsequent work is based on current, accurate information about the NLAP platform.

When invoked, the RESYNC skill will:
- Systematically read all relevant governance and platform documents
- Validate VERSION consistency and documentation currency
- Identify risks and context gaps
- Provide clear context summary
- Recommend required role activations
- Define appropriate next steps

This skill is critical for maintaining accurate context across sessions and ensuring that all work is based on current platform state and governance requirements.