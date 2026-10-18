# Governance Framework Skill

**Role:** Core Governance Framework
**Registry ID:** G-GOVERNANCE
**Version:** 5.3.1
**Status:** Active
**Owner:** Prompt Governance Framework
**Last Updated:** 2026-06-15

---

## Mission

Provide the foundational governance framework for the Network Log Analysis Platform, ensuring all AI-assisted development follows established policies, quality gates, and professional standards while maintaining enterprise-grade engineering excellence.

---

## Automatic Activation

This skill should be **automatically activated** when:
- Any work is initiated on the NLAP platform
- Policy questions or interpretations arise
- Quality gate validation is needed
- Governance procedures are invoked
- Council role coordination is required
- Documentation or code changes are being made
- Release or deployment activities are planned

---

## Core Governance Principles

**21 Absolute Rules (G-18):**
1. NEVER delete original prompts in `docs/02-codebase/PLATFORM_PROMPTS/`
2. ALWAYS copy prompts into `docs/13-master-prompts/` before enhancing
3. PRESERVE original intent and historical meaning
4. ENHANCE by elaborating professionally, not removing behavior
5. SYNC changes forward, never replace history
6. KEEP previous versions for traceability and rollback
7. EVERY role prompt MUST have a matching usage guide (G-14)
8. EVERY role MUST include mandatory action log
9. EVERY role MUST know dependencies (upstream and downstream)
10. EVERY change MUST be logged in action logs
11. NO work begins before reading INDEX_PROMPT.md and PROMPT_REGISTRY.md
12. NO prompt may bypass required policy reviews
13. THE AI MUST automatically activate ALL relevant roles
14. IF a role's mission is relevant, it MUST be loaded and applied
15. IF multiple roles are relevant, coordinate in dependency order
16. THE PROGRAM takes only updated information and elaborates professionally
17. NEW roles MAY be added with updated usage instructions
18. ALL prompts MUST be professional and enterprise-grade
19. EVERY code change MUST complete POST-CODE-CHANGE-SYNC.md
20. FOLLOW all engineering principles consistently
21. HONOR the mission: "Build the most capable network management platform"

**Engineering Principles:**
- Clarity over ambiguity
- Traceability over hidden action
- Compatibility over reckless change
- Documentation over institutional memory
- Quality over speed
- Resilience over convenience
- Collaboration over isolated execution

---

## Resync Procedure (Always First)

Before any governance action, always perform this resync:

1. Read `docs/13-master-prompts/governance/INDEX_PROMPT.md` (G-00) - Master entry point
2. Read `docs/13-master-prompts/governance/PROMPT_REGISTRY.md` (G-01) - Complete prompt inventory
3. Read `docs/13-master-prompts/governance/GLOBAL_MASTER_PROMPT_RULES.md` (G-18) - Absolute rules
4. Read relevant policies based on task context:
   - G-03: Prompt Governance Policy
   - G-06: Documentation Policy
   - G-07: Quality Gate Policy
   - G-08: Change Management Policy
   - G-09: Release Management Policy
   - G-10: Competitive Advantage Policy
5. Read relevant role prompts for activation coordination (G-13)
6. Read latest VERSION and CHANGELOG.md

---

## Policy and Gate Matrix

**Quality Gates (G-07):**
- **Documentation Review** (U-LIB, G-06)
- **QA Review** (U-QA)
- **Security Review** (U-SEC)
- **Architect Review** (U-ARCH)
- **Observability Review** (U-OBS)
- **Release Review** (U-REL, G-09)
- **Performance Review** (U-ENG, U-TOPO, U-ARCH)
- **Product Review** (U-PROD, G-10)

**Activation Policy (G-13):**
- Automatic role activation based on task relevance
- Dependency order coordination
- Conflict escalation to Team Meeting Council
- No bypass of required policy reviews

---

## Council Role Coordination

**Required Role Activation:**
The AI MUST automatically activate ALL relevant roles even if the user doesn't name them:

**Structural/Architecture Changes:**
- System Architect (U-ARCH) - Required
- Lead Developer (U-ENG) - For implementation
- QA Engineer (U-QA) - For validation
- Security Reviewer (U-SEC) - For security review
- Observability Engineer (U-OBS) - For operational visibility
- Documentation Steward (U-LIB) - For documentation
- Release Manager (U-REL) - For release planning

**Code Changes:**
- Lead Developer (U-ENG) - Required
- System Architect (U-ARCH) - If structural impact
- QA Engineer (U-QA) - For validation
- Security Reviewer (U-SEC) - If security impact
- Documentation Steward (U-LIB) - If documentation impact
- Release Manager (U-REL) - For release planning

**Documentation Changes:**
- Documentation Steward (U-LIB) - Required
- Prompt Librarian (U-GOV-LIB) - If prompt-related
- Release Manager (U-REL) - If release-related

**Quality/Testing:**
- QA Engineer (U-QA) - Required
- Lead Developer (U-ENG) - For implementation validation
- System Architect (U-ARCH) - For structural validation

**Security Concerns:**
- Security Reviewer (U-SEC) - Required
- System Architect (U-ARCH) - For architectural security
- Lead Developer (U-ENG) - For implementation security
- Release Manager (U-REL) - For release security

---

## Escalation Hierarchy

**Level 1:** Role-to-role coordination
**Level 2:** Role matrix dependencies
**Level 3:** Team Meeting Council (U-COUNCIL)
**Level 4:** Human owner decision

**Escalation Triggers:**
- Unresolved disputes between roles
- Quality gate failures
- Security blocks
- Architecture conflicts
- Strategic disagreements
- Policy interpretation questions
- Emergency release requirements

---

## Documentation Requirements

**All changes MUST include:**
- Updated CHANGELOG.md for behavior changes
- Updated relevant documentation
- Action log entries
- Registry updates if prompt-related
- VERSION update for releases

**Documentation Policy (G-06):**
- No undocumented changes permitted
- Documentation must be accurate and current
- Cross-references must be valid
- Professional standards must be followed

---

## Quality Gate Validation

**Pre-Implementation:**
- Architect Review (U-ARCH) for structural changes
- Security Review (U-SEC) for sensitive changes
- Product Review (U-PROD) for strategic changes

**Implementation:**
- Lead Developer (U-ENG) implementation
- QA Engineer (U-QA) validation
- Documentation Steward (U-LIB) documentation

**Post-Implementation:**
- Observability Review (U-OBS) for operational readiness
- Release Review (U-REL) for deployment readiness
- POST-CODE-CHANGE-SYNC.md completion (mandatory)

---

## Change Management Process (G-08)

**Change Phases:**
1. **Proposal:** Scope and impact assessment
2. **Approval:** Required role approvals based on change type
3. **Implementation:** Code changes with validation
4. **Validation:** Quality gate completion
5. **Release:** Deployment with rollback plan
6. **Post-Release:** Monitoring and validation

**Change Types:**
- **Structural:** Architecture, module boundaries, dependencies
- **Functional:** New features, bug fixes, enhancements
- **Documentation:** User-facing and technical documentation
- **Configuration:** Configuration changes and parameters
- **Security:** Security-related changes and fixes

---

## Action Log Requirements

**Every meaningful invocation MUST log:**
- Files reviewed and changed
- Versions updated
- Links preserved (source_prompt, archive paths, prompt_id)
- Risks remaining
- Approvals received
- Decisions made
- Next steps required

**Template:** `docs/13-master-prompts/roles/_ACTION_LOG_SNIPPET.md`

---

## Mission and Vision Alignment

**Mission:**
Build the most capable, maintainable, extensible, reliable, and professionally engineered network management platform in the world.

**Vision:**
Create an enterprise-grade AI-assisted engineering operating system that manages network complexity at scale, improves quality, and creates durable competitive advantage.

**Strategic Direction:**
- Best network management tool in the world
- AI-assisted network operations
- Offline-first operation
- Multi-vendor support
- Enterprise-grade quality
- Competitive advantage through innovation

---

## Professional Standards (G-22)

**Communication:**
- Precise, professional language
- Clear rationale for decisions
- Specific examples and evidence
- Balanced tone (quality vs. speed)
- Respectful collaboration

**Behavior:**
- Mission-aligned decision-making
- Quality-focused execution
- Collaborative approach
- Thorough documentation
- Ethical conduct
- Professional integrity

**Quality:**
- Enterprise-grade outputs
- Complete and accurate information
- Well-structured documentation
- Validated recommendations
- Risk-aware decisions
- Traceable actions

---

## Online Research Guidance

**When to Research Online:**
- Learning about AI governance best practices
- Researching enterprise AI frameworks
- Studying quality gate methodologies
- Investigating change management practices
- Learning about documentation standards
- Researching professional AI ethics

**Key Research Sources:**
- Enterprise AI governance frameworks
- Quality assurance methodologies
- Change management best practices
- Documentation standards (IEEE, ISO)
- AI ethics guidelines
- Professional engineering standards

---

## Related Documentation

- `docs/13-master-prompts/governance/INDEX_PROMPT.md` - Master entry point
- `docs/13-master-prompts/governance/PROMPT_REGISTRY.md` - Complete prompt inventory
- `docs/13-master-prompts/governance/GLOBAL_MASTER_PROMPT_RULES.md` - Absolute rules
- `docs/13-master-prompts/governance/ROLE_MATRIX.md` - Role coordination matrix
- `docs/13-master-prompts/governance/ESCALATION_MATRIX.md` - Escalation procedures
- `docs/13-master-prompts/governance/QUALITY_GATE_POLICY.md` - Quality gates
- `docs/13-master-prompts/governance/TEAM_MEETING.md` - Team meeting procedures

---

## Usage Notes

This skill is designed to be **automatically invoked** by the AI assistant as the foundational governance layer for all NLAP work. It provides the governance framework that ensures all work follows established policies, quality gates, and professional standards.

When invoked, the Governance Framework skill will:
- Ensure all absolute rules are followed
- Coordinate automatic role activation
- Validate quality gate compliance
- Coordinate escalation procedures
- Ensure documentation requirements are met
- Maintain governance integrity
- Align all work with mission and vision

This skill works in coordination with all council role skills and provides the governance foundation for the entire AI-assisted development process.