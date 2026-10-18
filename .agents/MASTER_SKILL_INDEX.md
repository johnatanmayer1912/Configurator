# MASTER SKILL INDEX
**Version**: 1.0.0  
**Date**: 2026-08-06  
**Scope**: Complete skill inventory across .agents and .devin directories

---

## Purpose

This document provides a comprehensive index of all professional skills available in the AI-IDE skill library, including their metadata, capabilities, activation triggers, and interdependencies. This is the single source of truth for skill discovery and activation.

---

## Skill Categories

### 1. Council Roles (Professional Governance)
### 2. Domain Specialists (Technical Expertise)
### 3. Antigravity Skills (Project-Specific)
### 4. Cursor Skills (IDE Integration)
### 5. Claude Skills (AI Assistant)
### 6. Community Skills (External Sources)

---

## .AGENTS/SKILLS (Project-Specific Skills)

### Cisco Professional Skill
- **Path**: `.agents/skills/cisco_professional/skill.md`
- **Category**: Antigravity Skills
- **Description**: Core guidelines for Cisco IOS, IOS-XE, and NX-OS command interface interaction
- **Capabilities**:
  - Command Syntax Fallbacks
  - Output Parsing
  - Mnemonic Analysis
- **Activation Triggers**: Cisco commands, IOS, NX-OS, syslog analysis
- **Dependencies**: networking skill
- **Priority**: High
- **Status**: Basic (needs enhancement)

### Forensics Skill
- **Path**: `.agents/skills/forensics/skill.md`
- **Category**: Antigravity Skills
- **Description**: Core guidelines and procedures for network forensic investigations and offline log incident analysis
- **Capabilities**:
  - Preserve Integrity
  - Reconstruction
  - Correlation
  - Time Alignment
- **Activation Triggers**: Forensic analysis, log investigation, incident reconstruction
- **Dependencies**: networking, cisco_professional
- **Priority**: High
- **Status**: Basic (needs enhancement)

### Networking Skill
- **Path**: `.agents/skills/networking/skill.md`
- **Category**: Antigravity Skills
- **Description**: Foundations of IP routing, Layer 2/3 interfaces, STP, LACP, and network troubleshooting
- **Capabilities**:
  - L2 Protocols (STP, vPC, EtherChannel)
  - L3 Protocols (OSPF, BGP, HSRP/VRRP)
  - Telemetry (interface counters, signal degradation)
- **Activation Triggers**: Network analysis, routing, switching, telemetry
- **Dependencies**: None
- **Priority**: High
- **Status**: Basic (needs enhancement)

### NX-OS Skill
- **Path**: `.agents/skills/nxos/skill.md`
- **Category**: Antigravity Skills
- **Description**: Cisco NX-OS architecture, filesystem paths, logs, and vPC validation rules
- **Capabilities**:
  - vPC Diagnostics
  - Filesystem navigation
  - Command Semantics
- **Activation Triggers**: NX-OS, Nexus switches, vPC
- **Dependencies**: cisco_professional, networking
- **Priority**: High
- **Status**: Basic (needs enhancement)

### UI/UX Skill
- **Path**: `.agents/skills/ui_ux/skill.md`
- **Category**: Antigravity Skills
- **Description**: Core standards for responsive design, clear typography, and visual timeline presentation
- **Capabilities**:
  - Typography & Icons
  - Accessible Layouts
  - Responsive Details
- **Activation Triggers**: UI design, frontend, responsive layouts
- **Dependencies**: None
- **Priority**: Medium
- **Status**: Basic (needs enhancement)

### Python Skill
- **Path**: `.agents/skills/python/skill.md`
- **Category**: Antigravity Skills
- **Description**: Enhanced Python skill with comprehensive best practices
- **Capabilities**:
  - Code Quality (PEP 8, type hints, docstrings)
  - Error Handling (custom exceptions, logging)
  - Performance (async/await, caching, optimization)
  - Dependencies (poetry, venv, requirements.txt)
  - Testing (pytest, coverage, fixtures)
- **Activation Triggers**: Python files, .py, pip, poetry, venv
- **Dependencies**: programming skill
- **Priority**: High
- **Status**: Enhanced

### QA Skill
- **Path**: `.agents/skills/qa/skill.md`
- **Category**: Antigravity Skills
- **Description**: Comprehensive QA skill with testing strategies and quality gates
- **Capabilities**:
  - Test Strategy (unit, integration, E2E)
  - E2E Testing (Playwright, test automation)
  - Test Planning (coverage, prioritization)
  - Defect Management (tracking, triage)
  - Quality Governance (gates, standards)
- **Activation Triggers**: Testing, QA, validation, quality checks
- **Dependencies**: programming skill
- **Priority**: High
- **Status**: Comprehensive

### Product Skill
- **Path**: `.agents/skills/product/skill.md`
- **Category**: Antigravity Skills
- **Description**: Enhanced product management skill with comprehensive guidelines
- **Capabilities**:
  - Product Strategy (vision, roadmap, positioning)
  - Product Planning (requirements, prioritization)
  - Product Development (agile, user stories)
  - Product Launch (go-to-market, metrics)
  - Post-Launch (analytics, iteration)
- **Activation Triggers**: Product management, roadmap, features, user needs
- **Dependencies**: None
- **Priority**: Medium
- **Status**: Enhanced

### Programming Skill
- **Path**: `.agents/skills/programming/skill.md`
- **Category**: Antigravity Skills
- **Description**: Enhanced programming skill with comprehensive software engineering guidelines
- **Capabilities**:
  - Core Principles (SOLID, DRY, KISS)
  - Code Quality (readability, maintainability)
  - Security (input validation, encryption)
  - Performance (optimization, caching)
  - Testing (TDD, BDD, coverage)
  - Version Control (Git, branching)
  - Documentation (comments, docs)
- **Activation Triggers**: Code, programming, development, software engineering
- **Dependencies**: None
- **Priority**: High
- **Status**: Enhanced

---

## .DEVIN/SKILLS (Professional Council & Domain Skills)

### System Architect (R-ARCH)
- **Path**: `.devin/skills/system-architect/SKILL.md`
- **Category**: Council Roles
- **Registry ID**: R-ARCH
- **Version**: 3.0.0
- **Description**: Ensure platform coherence, scalability, maintainability, security, observability, and strategic alignment
- **Mission**: Best network management tool in the world
- **Responsibilities**:
  - Review structure before implementation
  - Define or approve boundaries
  - Identify coupling and migration needs
  - Coordinate with Lead Developer, QA, Security, Observability, Documentation, Release
- **Authority**: Approve/reject architecture changes, require migration plans
- **Collaborators**: U-ENG, U-QA, U-SEC, U-OBS, U-REL, U-PROD, U-TOPO, U-COUNCIL
- **Auto-Activation**: Architecture changes, new subsystems, core design changes
- **Status**: Professional (Complete)

### QA Engineer (R-QA)
- **Path**: `.devin/skills/qa-engineer/SKILL.md`
- **Category**: Council Roles
- **Registry ID**: R-QA / U-QA
- **Version**: 3.0.0
- **Description**: Verify changes work correctly, do not regress existing behavior, remain backward compatible
- **Mission**: Quality assurance for Network Log Analysis Platform
- **Responsibilities**:
  - Test expected and edge behaviors
  - Check regression and compatibility
  - Confirm fixes solve reported issues
  - Report failures with reproduction steps
  - Coordinate with Release Manager
- **Quality Gates**: Prebuild, VPC script, smoke, Jinja, plugins
- **Collaborators**: U-ENG, U-ARCH, U-SEC, U-REL, U-TOPO, U-COUNCIL
- **Auto-Activation**: Feature changes, regression risk, release validation
- **Status**: Professional (Complete)

### Backend Architect
- **Path**: `.devin/skills/backend-architect/SKILL.md`
- **Category**: Domain Specialists
- **Description**: Expert backend architect specializing in scalable API design, microservices architecture, and distributed systems
- **Capabilities**:
  - API Design (REST, GraphQL, gRPC, WebSocket)
  - Microservices Architecture (service boundaries, communication patterns)
  - Event-Driven Architecture (message queues, event streaming)
  - Authentication & Authorization (OAuth 2.0, JWT, RBAC)
  - Security Patterns (input validation, rate limiting, CORS)
  - Resilience & Fault Tolerance (circuit breaker, retry, timeout)
  - Observability & Monitoring (logging, metrics, tracing)
  - Data Integration (ORM, caching, consistency)
  - Framework Expertise (Node.js, Python, Java, Go, C#, Rust)
- **Activation Triggers**: Backend design, API design, microservices, distributed systems
- **Dependencies**: database-architect (data layer first)
- **Status**: Professional (Complete)

### Python Pro
- **Path**: `.devin/skills/python-pro/SKILL.md`
- **Category**: Domain Specialists
- **Description**: Master Python 3.12+ with modern features, async programming, performance optimization, and production-ready practices
- **Capabilities**:
  - Modern Python Features (3.12+, async/await, type hints)
  - Modern Tooling (uv, ruff, mypy, pyproject.toml)
  - Testing & QA (pytest, Hypothesis, coverage)
  - Performance & Optimization (profiling, async, multiprocessing)
  - Web Development (FastAPI, Django, Flask, Pydantic)
  - Data Science & ML (NumPy, Pandas, Scikit-learn)
  - DevOps & Deployment (Docker, Kubernetes, cloud)
  - Advanced Patterns (SOLID, dependency injection, metaprogramming)
- **Activation Triggers**: Python code, .py files, pip, poetry, async
- **Status**: Professional (Complete)

### Security Auditor
- **Path**: `.devin/skills/security-auditor/SKILL.md`
- **Category**: Domain Specialists
- **Description**: Expert security auditor specializing in DevSecOps, comprehensive cybersecurity, and compliance frameworks
- **Capabilities**:
  - DevSecOps & Security Automation (SAST, DAST, IAST, supply chain)
  - Modern Authentication (OAuth 2.0, OpenID Connect, JWT, zero-trust)
  - OWASP & Vulnerability Management (Top 10, ASVS, threat modeling)
  - Application Security Testing (SAST, DAST, IAST, dependency scanning)
  - Cloud Security (posture, infrastructure, serverless, container)
  - Compliance & Governance (GDPR, HIPAA, PCI-DSS, SOC 2)
  - Secure Coding (input validation, IDOR prevention, encryption)
  - Network & Infrastructure Security (segmentation, firewall, IDS/IPS, SSRF)
  - Security Monitoring (SIEM/SOAR, log analysis, threat intelligence)
- **Activation Triggers**: Security audit, vulnerability assessment, compliance, threat modeling
- **Status**: Professional (Complete)

### Code Reviewer
- **Path**: `.devin/skills/code-reviewer/SKILL.md`
- **Category**: Domain Specialists
- **Description**: Elite code review expert specializing in modern AI-powered code analysis
- **Capabilities**:
  - AI-Powered Code Analysis (Trag, Bito, Codiga, Copilot)
  - Modern Static Analysis (SonarQube, CodeQL, Semgrep)
  - Security Code Review (OWASP, input validation, authentication)
  - Performance & Scalability (query optimization, memory leaks, caching)
  - Configuration & Infrastructure Review (production config, IaC, CI/CD)
  - Modern Development Practices (TDD, BDD, contract testing, feature flags)
  - Code Quality & Maintainability (Clean Code, SOLID, technical debt)
  - Team Collaboration & Process (PR workflow, checklists, automation)
  - Language-Specific Expertise (JS/TS, Python, Java, Go, Rust, C#)
- **Activation Triggers**: Code review, PR analysis, quality assessment, static analysis
- **Status**: Professional (Complete)

### Database Architect
- **Path**: `.devin/skills/database-architect/SKILL.md`
- **Category**: Domain Specialists
- **Description**: Expert database architect specializing in data layer design from scratch, technology selection, schema modeling, and scalable database architectures
- **Capabilities**:
  - Technology Selection (relational, NoSQL, time-series, NewSQL, graph)
  - Data Modeling & Schema Design (conceptual, logical, physical)
  - Normalization vs Denormalization (trade-offs, OLTP vs OLAP)
  - Indexing Strategy (B-tree, composite, partial, full-text, JSON)
  - Query Design & Optimization (JOIN, subquery, window functions)
  - Caching Architecture (cache layers, strategies, invalidation)
  - Scalability & Performance (partitioning, sharding, replication)
  - Migration Planning (zero-downtime, schema versioning, rollback)
  - Transaction Design (ACID, isolation levels, distributed transactions)
  - Security & Compliance (RBAC, encryption, GDPR, HIPAA)
  - Cloud Database Architecture (AWS, Azure, GCP, serverless)
  - ORM & Framework Integration (SQLAlchemy, Prisma, TypeORM)
- **Activation Triggers**: Database design, schema modeling, technology selection, migration
- **Dependencies**: Before backend-architect (data layer first)
- **Status**: Professional (Complete)

### Cloud Architect
- **Path**: `.devin/skills/cloud-architect/SKILL.md`
- **Category**: Domain Specialists
- **Description**: Expert cloud architect specializing in AWS/Azure/GCP multi-cloud infrastructure design, advanced IaC, FinOps cost optimization, and modern architectural patterns
- **Capabilities**:
  - Cloud Platform Expertise (AWS, Azure, GCP, multi-cloud, edge)
  - Infrastructure as Code (Terraform, CloudFormation, CDK, Pulumi, GitOps)
  - Cost Optimization & FinOps (monitoring, resource optimization, cost allocation)
  - Architecture Patterns (microservices, serverless, event-driven, AI/ML)
  - Security & Compliance (zero-trust, IAM, SOC2, HIPAA, GDPR)
  - Scalability & Performance (auto-scaling, load balancing, caching)
  - Disaster Recovery (multi-region, backup strategies, RPO/RTO)
  - Modern DevOps Integration (CI/CD, Kubernetes, observability)
  - Emerging Technologies (cloud-native, edge computing, quantum)
- **Activation Triggers**: Cloud infrastructure, IaC, cost optimization, multi-cloud
- **Status**: Professional (Complete)

---

## Additional .DEVIN/SKILLS (Community Skills)

The following skills are available in the .devin/skills directory (37+ skills total):

### API Skills
- `api-and-interface-design` - API design and interface patterns
- `api-design-principles` - API design best practices
- `api-documenter` - API documentation generation
- `api-patterns` - Comprehensive API patterns (REST, GraphQL, auth, security, etc.)
- `api-security-best-practices` - API security implementation
- `api-security-testing` - API security testing methodologies
- `api-testing-observability-api-mock` - API testing, observability, and mocking

### Architecture Skills
- `architecture` - General architecture patterns and principles
- `architecture-decision-records` - ADR creation and management
- `architecture-patterns` - Design patterns and architectural patterns
- `architect-review` - Architecture review and validation

### AI & ML Skills
- `ai-engineer` - AI/ML engineering and model deployment
- `ai-security` - AI security and adversarial machine learning

### Performance Skills
- `application-performance-performance-optimization` - Performance optimization techniques

### Security Skills
- `anti-reversing-techniques` - Reverse engineering protection
- `attack-tree-construction` - Threat modeling with attack trees
- `auth-implementation-patterns` - Authentication implementation patterns

### Development Skills
- `async-python-patterns` - Async/await patterns in Python
- `angular-migration` - Angular framework migration
- `airflow-dag-patterns` - Airflow DAG design patterns
- `arm-cortex-expert` - ARM Cortex embedded development
- `agent-orchestration-improve-agent` - Agent orchestration improvement
- `agent-orchestration-multi-agent-optimize` - Multi-agent optimization
- `accessibility-compliance-accessibility-audit` - Accessibility compliance and auditing

### Automation Skills
- `automation-orchestrator` - Automation and orchestration patterns

### AWS Skills
- `aws-cost-optimizer` - AWS cost optimization
- `aws-serverless` - AWS serverless architecture
- `aws-skills` - General AWS expertise

### Backend Skills
- `backend-dev-guidelines` - Backend development guidelines
- `backend-development-feature-development` - Backend feature development
- `backend-security-coder` - Backend security implementation

### Data Skills
- `backtesting-frameworks` - Backtesting for financial/trading systems
- `billing-automation` - Billing and payment automation
- `binary-analysis-patterns` - Binary code analysis

---

## Skill Activation Matrix

### Mandatory Skills (Always Active)
- **programming** - Core software engineering principles
- **python** - Python-specific best practices (when working with Python)
- **qa** - Quality assurance mindset
- **product** - Product thinking and user focus

### Context-Based Activation

#### Architecture & Design
- **system-architect** (R-ARCH) - Architecture changes, new subsystems
- **backend-architect** - Backend service design, API design
- **database-architect** - Data layer design, schema modeling
- **cloud-architect** - Cloud infrastructure, IaC, multi-cloud
- **architecture** - General architecture patterns
- **architecture-patterns** - Design pattern selection

#### Security
- **security-auditor** - Security audits, vulnerability assessment
- **api-security-best-practices** - API security implementation
- **api-security-testing** - API security testing
- **ai-security** - AI/ML security
- **backend-security-coder** - Backend security

#### Quality & Testing
- **qa-engineer** (R-QA) - QA validation, release readiness
- **code-reviewer** - Code review, quality assessment
- **api-testing-observability-api-mock** - API testing

#### Performance
- **application-performance-performance-optimization** - Performance optimization
- **async-python-patterns** - Async performance (Python)

#### Domain-Specific
- **cisco_professional** - Cisco networking equipment
- **nxos** - Cisco NX-OS specifically
- **networking** - General networking
- **forensics** - Network forensics and incident analysis
- **ui_ux** - UI/UX design

#### Technology-Specific
- **python-pro** - Python 3.12+ modern development
- **api-patterns** - API design patterns
- **api-documenter** - API documentation
- **angular-migration** - Angular framework
- **airflow-dag-patterns** - Airflow workflows
- **arm-cortex-expert** - ARM embedded

---

## Skill Dependencies

### Dependency Chains

#### Backend Development Chain
```
database-architect → backend-architect → security-auditor → qa-engineer
```

#### Cloud Infrastructure Chain
```
cloud-architect → security-auditor → devops-engineer → qa-engineer
```

#### Python Development Chain
```
python-pro → security-auditor → code-reviewer → qa-engineer
```

#### Network Analysis Chain
```
networking → cisco_professional → nxos → forensics
```

#### API Development Chain
```
api-design-principles → api-patterns → api-security-best-practices → api-testing-observability-api-mock
```

---

## Skill Quality Assessment

### Professional Skills (Complete & Comprehensive)
- system-architect (R-ARCH) - Council Role, Complete
- qa-engineer (R-QA) - Council Role, Complete
- backend-architect - Domain Specialist, Complete
- python-pro - Domain Specialist, Complete
- security-auditor - Domain Specialist, Complete
- code-reviewer - Domain Specialist, Complete
- database-architect - Domain Specialist, Complete
- cloud-architect - Domain Specialist, Complete

### Enhanced Skills (Recently Improved)
- python (.agents) - Enhanced with best practices
- qa (.agents) - Comprehensive testing strategies
- product (.agents) - Enhanced product management
- programming (.agents) - Enhanced software engineering

### Basic Skills (Need Enhancement)
- cisco_professional - Basic, needs expansion
- forensics - Basic, needs expansion
- networking - Basic, needs expansion
- nxos - Basic, needs expansion
- ui_ux - Basic, needs expansion

### Community Skills (External Sources)
- All .devin/skills community skills - Varying quality, need audit

---

## Enhancement Priorities

### Priority 1: Critical (Immediate)
1. **Enhance cisco_professional skill** - Expand with comprehensive Cisco best practices
2. **Enhance forensics skill** - Add detailed forensic procedures and tools
3. **Enhance networking skill** - Expand with modern networking protocols and patterns

### Priority 2: High (Short-term)
1. **Enhance nxos skill** - Add NX-OS specific commands and diagnostics
2. **Enhance ui_ux skill** - Expand with modern UI/UX frameworks and patterns
3. **Audit community skills** - Review and enhance key .devin/skills

### Priority 3: Medium (Long-term)
1. **Create missing skills** - devops-engineer, performance-engineer, frontend-architect
2. **Skill integration** - Improve skill activation and coordination
3. **Documentation** - Create skill usage examples and tutorials

---

## Skill Activation API

### Automatic Activation Rules

#### Keyword-Based Triggers
```
Keywords → Skill Activation

"architecture", "design", "structure" → system-architect
"backend", "api", "service" → backend-architect
"database", "schema", "data model" → database-architect
"cloud", "aws", "azure", "gcp" → cloud-architect
"security", "vulnerability", "audit" → security-auditor
"python", ".py", "async" → python-pro
"test", "qa", "validation" → qa-engineer
"review", "pr", "quality" → code-reviewer
"cisco", "ios", "nx-os" → cisco_professional
"network", "routing", "switching" → networking
"forensic", "incident", "log analysis" → forensics
"ui", "ux", "frontend" → ui_ux
```

#### Context-Based Triggers
```
Context → Skill Activation

Architecture changes → system-architect + backend-architect + database-architect
Backend development → backend-architect + python-pro + security-auditor
Cloud deployment → cloud-architect + security-auditor + qa-engineer
Security audit → security-auditor + code-reviewer + qa-engineer
Python development → python-pro + code-reviewer + qa-engineer
API development → api-patterns + api-security-best-practices + api-testing-observability-api-mock
Network analysis → networking + cisco_professional + forensics
UI development → ui_ux + accessibility-compliance-accessibility-audit
```

### Dependency Enforcement
```
When activating a skill, automatically activate dependencies:

database-architect → (no dependencies)
backend-architect → database-architect (must be activated first)
cloud-architect → (no dependencies)
security-auditor → (no dependencies)
qa-engineer → (no dependencies, but coordinates with others)
code-reviewer → (no dependencies)
python-pro → (no dependencies)
cisco_professional → networking
nxos → cisco_professional + networking
forensics → networking + cisco_professional
```

---

## Maintenance

### Skill Update Process
1. Review skill quarterly for relevance
2. Update with latest best practices and tools
3. Enhance based on usage patterns and feedback
4. Validate skill activation rules
5. Update dependencies and integration points

### Skill Addition Process
1. Identify skill gap or need
2. Design skill with comprehensive capabilities
3. Define activation triggers and dependencies
4. Create skill following template
5. Test skill activation and integration
6. Document skill in this index

### Skill Removal Process
1. Identify obsolete or redundant skill
2. Check for dependencies and usages
3. Plan migration or replacement
4. Update activation rules
5. Remove skill and update index
6. Communicate changes to users

---

## Related Documentation

- `.agents/README.md` - .agents folder overview
- `.agents/SKILLS_INDEX.md` - Original skills index
- `.agents/SKILL_ACTIVATION_CONFIG.md` - Skill activation configuration
- `.agents/SKILL_ACTIVATION_SYSTEM.md` - Skill activation system
- `.devin/README.md` - .devin folder overview
- `.devin/SKILLS_INDEX.md` - .devin skills index
- `.devin/SKILL_ACTIVATION_CONFIG.md` - .devin activation config
- `.devin/SKILL_ACTIVATION_SYSTEM.md` - .devin activation system
- `.agents/SKILL_TEMPLATE.md` - Skill template for new skills
- `.agents/DOCUMENTATION_STRUCTURE.md` - Documentation structure
- `.agents/DOCUMENTATION_VALIDATION.md` - Documentation validation

---

**Last Updated**: 2026-08-06  
**Next Review**: 2026-11-06  
**Maintained By**: AI-IDE Skill Library Governance
