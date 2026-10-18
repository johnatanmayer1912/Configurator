# Skill Activation Configuration

**Platform:** Network Log Analysis Platform (NLAP)
**Version:** 5.3.1
**Status:** Active
**Purpose:** Define automatic skill activation rules for AI-assisted development

---

## Activation Philosophy

**Automatic Activation:**
- The AI MUST automatically activate ALL relevant skills based on task context
- Skills should not require manual activation by the user
- Activation follows dependency order and coordination rules
- Conflicts are escalated to Team Meeting Council skill

**Priority Order:**
1. RESYNC - Always first for context reconstruction
2. Governance Framework - Foundation for all work
3. Council Roles - Based on task relevance
4. Domain Specialists - Based on domain-specific needs
5. Team Meeting Council - For disputes and escalation

---

## Universal Activation Rules

**Always Activate (Base Layer):**
- **RESYNC** - At start of every significant work session
- **Governance Framework** - For all work to ensure compliance

---

## Council Role Activation Rules

### System Architect (U-ARCH)

**Automatic Activation When:**
- Architecture, module boundaries, or dependencies may change
- A new subsystem is proposed
- A change touches core design or long-term maintainability
- Structural changes to the codebase are proposed
- Module boundaries are being redefined
- New dependencies are being introduced
- Performance or scalability implications are discussed
- Migration strategies are needed

**Dependency Coordination:**
- Activates before: Lead Developer (U-ENG)
- Coordinates with: QA Engineer (U-QA), Security Reviewer (U-SEC), Observability Engineer (U-OBS)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### Lead Developer (U-ENG)

**Automatic Activation When:**
- Code needs to be written or changed
- A fix must be implemented
- A refactor must be executed
- Approved design needs translation into code
- Implementation tasks are being discussed
- Code changes are being made to the codebase
- Bug fixes or feature implementation is required

**Dependency Coordination:**
- Activates after: System Architect (U-ARCH) for structural work
- Coordinates with: QA Engineer (U-QA), Security Reviewer (U-SEC), Observability Engineer (U-OBS), Documentation Steward (U-LIB)
- Escalates to: System Architect (U-ARCH) or Team Meeting Council (U-COUNCIL)

---

### QA Engineer (U-QA)

**Automatic Activation When:**
- A feature, fix, refactor, or prompt-driven behavior changes
- Regression risk exists
- Release readiness must be validated
- Code changes are being made that affect functionality
- Testing is being discussed or planned
- Validation of changes is needed
- Quality assurance questions arise

**Dependency Coordination:**
- Activates after: Lead Developer (U-ENG) implementation
- Coordinates with: Lead Developer (U-ENG), System Architect (U-ARCH), Security Reviewer (U-SEC)
- Escalates to: Release Manager (U-REL) or Team Meeting Council (U-COUNCIL)

---

### Documentation Steward (U-LIB)

**Automatic Activation When:**
- Documentation is being created, updated, or reviewed
- Code changes affect user-facing documentation
- New features require documentation
- API changes require doc updates
- Policies or procedures are being modified
- Architecture changes require doc updates
- Documentation quality or accuracy is discussed
- User guides or operational procedures are needed

**Dependency Coordination:**
- Coordinates with: Prompt Librarian (U-GOV-LIB), System Architect (U-ARCH), Lead Developer (U-ENG)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### Security Reviewer (U-SEC)

**Automatic Activation When:**
- Code changes affect security boundaries or data handling
- Authentication or authorization logic is modified
- Network communication protocols are changed
- File system operations are being modified
- Encryption or security algorithms are involved
- User input validation is being changed
- Security vulnerabilities or concerns are raised
- Configuration or credential handling is affected

**Dependency Coordination:**
- Coordinates with: System Architect (U-ARCH), Lead Developer (U-ENG), QA Engineer (U-QA)
- Escalates to: Release Manager (U-REL) or Team Meeting Council (U-COUNCIL)

---

### Observability Engineer (U-OBS)

**Automatic Activation When:**
- Logging or monitoring capabilities are being added or modified
- Diagnostics or troubleshooting features are discussed
- Performance monitoring or metrics are being implemented
- Error handling or alerting is being designed
- Operational visibility needs are identified
- System instrumentation is being planned
- Telemetry or observability gaps are discovered

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), QA Engineer (U-QA), Security Reviewer (U-SEC)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### Release Manager (U-REL)

**Automatic Activation When:**
- Release planning or preparation is discussed
- Version changes or deployment is being planned
- Release readiness is being assessed
- Rollback procedures are needed
- Change management processes are invoked
- Hotfix or emergency releases are considered
- Deployment strategies are being designed
- Quality gate results are being coordinated

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Security Reviewer (U-SEC), Observability Engineer (U-OBS), Documentation Steward (U-LIB), System Architect (U-ARCH)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### Product Strategist (U-PROD)

**Automatic Activation When:**
- Product strategy or roadmap is being discussed
- New features or capabilities are being proposed
- Competitive analysis or market positioning is needed
- Prioritization decisions are being made
- Strategic investments or deprecations are considered
- Product vision or mission alignment is questioned
- User value or business impact is assessed
- Platform direction or evolution is discussed

**Dependency Coordination:**
- Coordinates with: System Architect (U-ARCH), Release Manager (U-REL), Prompt Librarian (U-GOV-LIB)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### Prompt Librarian (U-GOV-LIB)

**Automatic Activation When:**
- Prompts are created, copied, renamed, synced, deprecated, or retired
- Prompt structure or governance changes are discussed
- Prompt registry updates are needed
- Prompt usage guides must be created or updated
- Prompt ecosystem integrity is being reviewed
- Command manual or command library changes are needed
- Prompt governance or lifecycle management is invoked

**Dependency Coordination:**
- Coordinates with: Documentation Steward (U-LIB), Release Manager (U-REL), System Architect (U-ARCH)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### Team Meeting Council (U-COUNCIL)

**Automatic Activation When:**
- Unresolved disputes exist between council roles
- Quality gate failures require escalation
- Security blocks need resolution
- Architecture conflicts cannot be resolved
- Strategic disputes or mission alignment questions arise
- Emergency release decisions are needed
- Policy interpretation questions exist
- Multiple roles disagree on approach or priority

**Dependency Coordination:**
- Coordinates with: ALL council roles based on dispute context
- Final escalation point within AI governance
- Escalates to: Human owner for L3/L4 issues

---

## Domain Specialist Activation Rules

### Network Topology (U-TOPO)

**Automatic Activation When:**
- Network topology or mapping features are discussed
- VPC/VLAN configuration is being analyzed
- Device relationships and neighbors are being determined
- Network map visualization is needed
- Connectivity analysis is required
- Network discovery features are implemented
- MAC address tables or ARP tables are being processed

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), QA Engineer (U-QA), System Architect (U-ARCH)
- Escalates to: System Architect (U-ARCH) or Team Meeting Council (U-COUNCIL)

---

### Automation Orchestrator (U-ORCH)

**Automatic Activation When:**
- Multi-device workflows are being designed or executed
- Plugin orchestration and coordination is needed
- Batch operations across devices are planned
- Workflow automation features are discussed
- Plugin execution order or dependencies are being managed
- Complex multi-step operations are being designed
- Error handling in automated workflows is discussed

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), QA Engineer (U-QA), System Architect (U-ARCH), Plugin Registry (U-REG)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### UI Dynamo (U-UI)

**Automatic Activation When:**
- Web UI templates or HTML are being created or modified
- Jinja2 templates are being designed or updated
- User interface changes are being made
- Frontend code (HTML, CSS, JavaScript) is modified
- XSS vulnerabilities or security concerns in UI are discussed
- User experience or interface design is being improved
- Template rendering or validation issues arise

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), QA Engineer (U-QA), Security Reviewer (U-SEC)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

### Plugin Registry (U-REG)

**Automatic Activation When:**
- New plugins are being created or registered
- Plugin compatibility or dependencies are discussed
- Plugin lifecycle management is needed (install, update, remove)
- Plugin metadata or registration information is updated
- Plugin conflicts or incompatibilities are identified
- Plugin validation or testing is required
- Plugin documentation or versioning is discussed

**Dependency Coordination:**
- Coordinates with: Automation Orchestrator (U-ORCH), Lead Developer (U-ENG), System Architect (U-ARCH), QA Engineer (U-QA)
- Escalates to: Team Meeting Council (U-COUNCIL)

---

## Cursor-Sourced Skills

### Writing Tests (U-WRITE-TESTS)

**Automatic Activation When:**
- Tests are being added or improved
- Test coverage analysis is needed
- Test framework setup is required
- Bug fixes need test coverage
- New features require test validation

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Lead Developer (U-ENG)
- Escalates to: QA Engineer (U-QA) for test strategy

---

### Python TDD with uv (U-PYTHON-TDD)

**Automatic Activation When:**
- Test-driven development approach is needed
- Python development with uv is being used
- New Python modules are being created
- Test-first development is requested

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Lead Developer (U-ENG)
- Escalates to: Lead Developer (U-ENG) for implementation questions

---

### Systematic Debugging (U-DEBUGGING)

**Automatic Activation When:**
- Bugs need systematic investigation
- Reproduction steps are unclear
- Root cause analysis is required
- Complex issues need methodical debugging

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Lead Developer (U-ENG)
- Escalates to: System Architect (U-ARCH) if architectural issues found

---

### Reviewing Code (U-CODE-REVIEW)

**Automatic Activation When:**
- Code reviews are being conducted
- PRs need comprehensive review
- Code quality assessment is needed
- Best practices validation is required

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Security Reviewer (U-SEC), System Architect (U-ARCH)
- Escalates to: Team Meeting Council (U-COUNCIL) for review disputes

---

### Writing Commit Messages (U-COMMIT-MSG)

**Automatic Activation When:**
- Git commits are being made
- Commit message standards need to be followed
- Conventional commit format is required
- Commit history organization is needed

**Dependency Coordination:**
- Coordinates with: Release Manager (U-REL), Documentation Steward (U-LIB)
- Escalates to: Release Manager (U-REL) for commit standards

---

### Building Skills from Patterns (U-SKILL-BUILD)

**Automatic Activation When:**
- Repeated workflows need to be automated
- New skills need to be created
- Pattern recognition is needed for skill creation
- Skill system expansion is required

**Dependency Coordination:**
- Coordinates with: Prompt Librarian (U-GOV-LIB), System Architect (U-ARCH)
- Escalates to: Prompt Librarian (U-GOV-LIB) for skill governance

---

### Grinding Until Pass (U-GRIND-UNTIL-PASS)

**Automatic Activation When:**
- Tests are failing and need automated fixing
- Build processes need iterative improvement
- Automated iteration is required for success
- Continuous improvement cycles are needed

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Lead Developer (U-ENG)
- Escalates to: System Architect (U-ARCH) if systemic issues found

---

### Architecture Decision Records (U-ADR)

**Automatic Activation When:**
- Architecture decisions need documentation
- ADR creation is required
- Design choices need formal documentation
- Architecture governance is invoked

**Dependency Coordination:**
- Coordinates with: System Architect (U-ARCH), Documentation Steward (U-LIB)
- Escalates to: System Architect (U-ARCH) for architecture guidance

---

### Performance Profiling (U-PROFILING)

**Automatic Activation When:**
- Performance issues are suspected or reported
- Code optimization is needed
- Resource usage analysis is required
- Performance bottlenecks need identification

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), Observability Engineer (U-OBS), System Architect (U-ARCH)
- Escalates to: System Architect (U-ARCH) for performance optimization strategies

---

### Incident Response (U-INCIDENT-RESPONSE)

**Automatic Activation When:**
- Production incidents occur or are simulated
- Network incidents need management
- Postmortem documentation is required
- Incident response procedures are invoked

**Dependency Coordination:**
- Coordinates with: Release Manager (U-REL), Observability Engineer (U-OBS), System Architect (U-ARCH)
- Escalates to: Team Meeting Council (U-COUNCIL) for major incidents

---

## Claude Skills Activation

### AI Security (U-AI-SECURITY)

**Automatic Activation When:**
- AI/ML systems are being developed or integrated
- LLM prompt injection vulnerabilities need assessment
- Model security concerns are raised
- AI safety and robustness need evaluation
- Adversarial AI attacks need analysis

**Dependency Coordination:**
- Coordinates with: Security Reviewer (U-SEC), System Architect (U-ARCH), Senior ML Engineer (U-SENIOR-ML)
- Escalates to: Security Reviewer (U-SEC) for security issues

---

### Code Reviewer Advanced (U-CODE-REVIEW-ADV)

**Automatic Activation When:**
- Comprehensive code reviews are needed
- Multi-language code quality assessment is required
- Code review with advanced rule sets is requested
- Security-focused code review is needed

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Security Reviewer (U-SEC), Lead Developer (U-ENG)
- Escalates to: System Architect (U-ARCH) for architectural concerns

---

### Threat Detection (U-THREAT-DETECTION)

**Automatic Activation When:**
- Network threat analysis is required
- IOC sweep generation is needed
- Security log analysis for threats is requested
- Behavioral anomaly detection is needed
- Threat hunting workflows are discussed

**Dependency Coordination:**
- Coordinates with: Security Reviewer (U-SEC), Observability Engineer (U-OBS), Incident Response (U-INCIDENT-RESPONSE)
- Escalates to: Security Reviewer (U-SEC) for security escalations

---

### Senior ML Engineer (U-SENIOR-ML)

**Automatic Activation When:**
- Machine learning models are being developed or deployed
- LLM integration is being implemented
- Model deployment and MLOps are discussed
- ML pipeline optimization is needed
- Feature engineering and data pipelines are involved

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), System Architect (U-ARCH), Senior Prompt Engineer (U-SENIOR-PROMPT)
- Escalates to: System Architect (U-ARCH) for architectural decisions

---

### Senior Prompt Engineer (U-SENIOR-PROMPT)

**Automatic Activation When:**
- Prompt engineering and optimization is needed
- LLM prompt design is being discussed
- Prompt A/B testing or optimization is required
- RAG system implementation is planned
- Multi-agent workflows with prompts are designed

**Dependency Coordination:**
- Coordinates with: Senior ML Engineer (U-SENIOR-ML), System Architect (U-ARCH), Prompt Architect (U-PROMPT-ARCH)
- Escalates to: Senior ML Engineer (U-SENIOR-ML) for ML integration issues

---

### Senior Architect Pro (U-SENIOR-ARCH-PRO)

**Automatic Activation When:**
- Advanced architectural design is needed
- System architecture patterns are being evaluated
- Microservices or distributed system design is discussed
- Performance architecture is being planned
- Enterprise architecture decisions are needed

**Dependency Coordination:**
- Coordinates with: System Architect (U-ARCH), Lead Developer (U-ENG), Observability Engineer (U-OBS)
- Escalates to: System Architect (U-ARCH) for architectural alignment

---

### Cloud Security (U-CLOUD-SECURITY)

**Automatic Activation When:**
- Cloud infrastructure security is being assessed
- IAM and access control reviews are needed
- S3 or storage security evaluation is required
- Cloud provider security best practices are discussed
- Cloud deployment security is being planned

**Dependency Coordination:**
- Coordinates with: Security Reviewer (U-SEC), System Architect (U-ARCH), Observability Engineer (U-OBS)
- Escalates to: Security Reviewer (U-SEC) for security findings

---

## Claude Prompts Skills Activation

### Prompt Architect (U-PROMPT-ARCH)

**Automatic Activation When:**
- New prompts are being created or refined
- Prompt quality improvement is needed
- Reusable prompting patterns are being established
- Prompt testing and validation is required
- Prompt documentation standards are being discussed

**Dependency Coordination:**
- Coordinates with: Senior Prompt Engineer (U-SENIOR-PROMPT), Prompt Librarian (U-GOV-LIB)
- Escalates to: Senior Prompt Engineer (U-SENIOR-PROMPT) for prompt integration

---

### Verification Agent (U-VERIFICATION-AGENT)

**Automatic Activation When:**
- Testing and verification strategies are needed
- Quality assurance methodologies are discussed
- Test plan creation is required
- Verification and validation processes are being designed
- Quality gates and checklists are needed

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Lead Developer (U-ENG), Coding Agent Standards (U-CODING-STANDARDS)
- Escalates to: QA Engineer (U-QA) for quality standards

---

### Coding Agent Standards (U-CODING-STANDARDS)

**Automatic Activation When:**
- Coding standards and best practices are being defined
- Code quality guidelines are being established
- Development standards documentation is needed
- Coding conventions are being discussed
- Developer onboarding standards are required

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), System Architect (U-ARCH), QA Engineer (U-QA)
- Escalates to: Lead Developer (U-ENG) for implementation guidance

---

## Antigravity Skills Activation

### Python Development (U-PYTHON-DEV)

**Automatic Activation When:**
- Python code is being written or reviewed
- Python best practices are being discussed
- Python project structure is being planned
- Python dependencies and packaging are involved
- Python development standards are needed

**Dependency Coordination:**
- Coordinates with: Lead Developer (U-ENG), QA Engineer (U-QA)
- Escalates to: Lead Developer (U-ENG) for Python-specific issues

---

### Python Performance Optimization (U-PYTHON-PERF)

**Automatic Activation When:**
- Python performance issues are suspected or reported
- Code optimization is needed for Python applications
- Performance profiling of Python code is required
- Memory optimization is discussed
- Python-specific performance bottlenecks need identification

**Dependency Coordination:**
- Coordinates with: Profiling Performance (U-PROFILING), Lead Developer (U-ENG), Observability Engineer (U-OBS)
- Escalates to: Lead Developer (U-ENG) for optimization implementation

---

### Python Testing Patterns (U-PYTHON-TESTING)

**Automatic Activation When:**
- Python test frameworks are being selected or implemented
- Testing patterns for Python code are being discussed
- Test coverage improvement is needed for Python
- Python testing best practices are required
- PyTest or unittest optimization is discussed

**Dependency Coordination:**
- Coordinates with: QA Engineer (U-QA), Writing Tests (U-WRITE-TESTS), Python TDD with uv (U-PYTHON-TDD)
- Escalates to: QA Engineer (U-QA) for testing strategy

---

## Skill Activation Matrix

| Task Type | Universal | Council Roles | Domain Specialists | Cursor Skills | Claude Skills | Claude Prompts | Antigravity Skills |
|-----------|-----------|--------------|-------------------|--------------|--------------|----------------|------------------|
| **Code Implementation** | RESYNC, Governance | U-ENG, U-ARCH, U-QA, U-SEC, U-OBS, U-LIB | U-ORCH, U-REG | U-WRITE-TESTS, U-PYTHON-TDD, U-DEBUGGING | U-CODE-REVIEW-ADV | U-CODING-STANDARDS | U-PYTHON-DEV |
| **Architecture Changes** | RESYNC, Governance | U-ARCH, U-ENG, U-QA, U-SEC, U-OBS, U-LIB, U-REL | U-TOPO, U-ORCH | U-ADR, U-PROFILING | U-SENIOR-ARCH-PRO | U-PROMPT-ARCH | - |
| **Quality Validation** | RESYNC, Governance | U-QA, U-ENG, U-ARCH, U-SEC | - | U-WRITE-TESTS, U-GRIND-UNTIL-PASS | - | U-VERIFICATION-AGENT | U-PYTHON-TESTING |
| **Security Review** | RESYNC, Governance | U-SEC, U-ARCH, U-ENG, U-REL | - | U-CODE-REVIEW | U-AI-SECURITY, U-CLOUD-SECURITY, U-THREAT-DETECTION | - | - |
| **Documentation** | RESYNC, Governance | U-LIB, U-GOV-LIB, U-REL | - | U-ADR | - | - | - |
| **Release Management** | RESYNC, Governance | U-REL, U-QA, U-SEC, U-OBS, U-LIB, U-ARCH | - | U-COMMIT-MSG, U-CODE-REVIEW | - | - | - |
| **Product Strategy** | RESYNC, Governance | U-PROD, U-ARCH, U-REL | - | U-ADR | - | - | - |
| **Prompt Governance** | RESYNC, Governance | U-GOV-LIB, U-LIB | - | U-SKILL-BUILD | - | U-PROMPT-ARCH | - |
| **Network Topology** | RESYNC, Governance | U-ARCH, U-ENG, U-QA | U-TOPO | U-DEBUGGING | - | - | - |
| **Workflow Automation** | RESYNC, Governance | U-ENG, U-QA, U-ARCH | U-ORCH, U-REG | U-DEBUGGING, U-PROFILING | - | - | - |
| **UI Development** | RESYNC, Governance | U-ENG, U-QA, U-SEC | U-UI | U-WRITE-TESTS | - | - | - |
| **Plugin Management** | RESYNC, Governance | U-ENG, U-ARCH, U-QA | U-REG, U-ORCH | U-WRITE-TESTS, U-DEBUGGING | - | - | - |
| **Dispute Resolution** | RESYNC, Governance | U-COUNCIL (all relevant roles) | - | - | - | - | - |
| **Performance Issues** | RESYNC, Governance | U-OBS, U-ENG, U-ARCH | - | U-PROFILING, U-DEBUGGING | - | - | U-PYTHON-PERF |
| **Incident Management** | RESYNC, Governance | U-REL, U-OBS, U-ARCH | - | U-INCIDENT-RESPONSE | U-THREAT-DETECTION | - | - |
| **Code Review** | RESYNC, Governance | U-QA, U-SEC, U-ARCH | - | U-CODE-REVIEW | U-CODE-REVIEW-ADV | U-VERIFICATION-AGENT | - |
| **Bug Investigation** | RESYNC, Governance | U-QA, U-ENG, U-ARCH | - | U-DEBUGGING, U-WRITE-TESTS | - | - | - |
| **Testing & Validation** | RESYNC, Governance | U-QA, U-ENG | - | U-WRITE-TESTS, U-PYTHON-TDD, U-GRIND-UNTIL-PASS | - | U-VERIFICATION-AGENT | U-PYTHON-TESTING |
| **AI/ML Development** | RESYNC, Governance | U-ARCH, U-ENG | - | - | U-SENIOR-ML, U-SENIOR-PROMPT, U-AI-SECURITY | U-PROMPT-ARCH | - |
| **Cloud Security** | RESYNC, Governance | U-SEC, U-ARCH, U-ENG, U-REL | - | - | U-CLOUD-SECURITY | - | - |
| **Python Development** | RESYNC, Governance | U-ENG, U-QA | - | U-WRITE-TESTS, U-PYTHON-TDD | - | U-CODING-STANDARDS | U-PYTHON-DEV, U-PYTHON-PERF, U-PYTHON-TESTING |
| **Threat Analysis** | RESYNC, Governance | U-SEC, U-ARCH | - | - | U-THREAT-DETECTION, U-AI-SECURITY | - | - |
| **Prompt Engineering** | RESYNC, Governance | U-GOV-LIB, U-LIB | - | U-SKILL-BUILD | U-SENIOR-PROMPT | U-PROMPT-ARCH | - |

---

## Dependency Execution Order

**Standard Execution Order:**
1. **RESYNC** - Context reconstruction
2. **Governance Framework** - Policy and compliance foundation
3. **Product Strategist** - Strategic validation (if applicable)
4. **System Architect** - Architecture review (if structural)
5. **Lead Developer** - Implementation (if code changes)
6. **Security Reviewer** - Security validation (if security impact)
7. **Observability Engineer** - Operational readiness (if observability impact)
8. **QA Engineer** - Quality validation (if testing needed)
9. **Documentation Steward** - Documentation updates (if doc changes)
10. **Release Manager** - Release planning (if deployment)
11. **Domain Specialists** - Domain-specific validation
12. **Team Meeting Council** - Dispute resolution (if conflicts)

**Parallel Execution:**
- Skills that don't have dependencies can execute in parallel
- U-QA, U-SEC, U-OBS often execute in parallel after U-ENG
- U-LIB can often execute in parallel with other roles
- Domain specialists can often execute in parallel with relevant council roles

---

## Conflict Resolution

**Skill Activation Conflicts:**
- Always prioritize RESYNC and Governance Framework
- Council roles take precedence over domain specialists for core tasks
- Domain specialists are activated for their specific domain expertise
- Team Meeting Council is activated when disputes cannot be resolved

**Escalation Rules:**
- Role disputes → Team Meeting Council (U-COUNCIL)
- Quality gate failures → Escalate to relevant blocking role
- Security blocks → Cannot be overridden without Team Meeting Council approval
- Architecture conflicts → Team Meeting Council for resolution

---

## Usage Notes

This configuration defines the automatic skill activation behavior for the NLAP platform. The AI assistant will automatically activate skills based on these rules without requiring manual user activation.

**Key Principles:**
- Skills activate based on task context and relevance
- Universal skills (RESYNC, Governance) always activate first
- Council roles activate based on their domain relevance
- Domain specialists activate for specific technical needs
- Team Meeting Council activates for dispute resolution
- Dependencies are respected in execution order
- Conflicts escalate to Team Meeting Council

This ensures comprehensive coverage of all relevant expertise while maintaining efficient coordination between skills.