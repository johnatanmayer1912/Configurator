# SKILL INVOCATION RULES
**Version**: 1.0.0  
**Date**: 2026-08-06  
**Purpose**: Complete skill invocation rules for all skills in the AI Skills System

---

## Invocation Rules by Skill

### Council Skills

#### system-architect

**Can Invoke**:
- backend-architect (when backend architecture needed)
- database-architect (when data layer design needed)
- cloud-architect (when cloud infrastructure needed)
- security-auditor (when security review needed)
- qa-engineer (when quality gates needed)

**Invocation Logic**:
```yaml
IF architecture_change_detected THEN invoke backend-architect
IF data_layer_involved THEN invoke database-architect
IF cloud_infrastructure THEN invoke cloud-architect
IF security_concerns THEN invoke security-auditor
IF quality_gates THEN invoke qa-engineer
```

**Invoked By**:
- User (explicit activation)
- Any skill requiring architectural guidance

#### qa-engineer

**Can Invoke**:
- code-reviewer (when code review needed)
- python-pro (when Python testing needed)
- security-auditor (when security testing needed)
- backend-architect (when backend testing needed)

**Invocation Logic**:
```yaml
IF code_review_needed THEN invoke code-reviewer
IF python_testing THEN invoke python-pro
IF security_testing THEN invoke security-auditor
IF backend_testing THEN invoke backend-architect
```

**Invoked By**:
- system-architect (quality gates)
- backend-architect (testing)
- User (explicit activation)

### Architecture Skills (Additional)

#### backend-dev-guidelines

**Can Invoke**:
- backend-architect (when architecture guidance needed)
- python-pro (when Python implementation needed)
- security-auditor (when security review needed)
- qa-engineer (when testing needed)

**Invocation Logic**:
```yaml
IF architecture_guidance THEN invoke backend-architect
IF python_implementation THEN invoke python-pro
IF security_review THEN invoke security-auditor
IF testing_needed THEN invoke qa-engineer
```

**Invoked By**:
- backend-architect (development guidelines)
- User (explicit activation)

#### backend-security-coder

**Can Invoke**:
- security-auditor (when security review needed)
- backend-architect (when architecture review needed)
- api-security-best-practices (when API security needed)

**Invocation Logic**:
```yaml
IF security_review THEN invoke security-auditor
IF architecture_review THEN invoke backend-architect
IF api_security THEN invoke api-security-best-practices
```

**Invoked By**:
- backend-architect (security implementation)
- security-auditor (security coding)
- User (explicit activation)

### Architecture Skills

#### backend-architect

**Can Invoke**:
- database-architect (dependency - data layer design)
- security-auditor (when security review needed)
- python-pro (when Python implementation needed)
- api-design-principles (when API design needed)
- qa-engineer (when testing needed)

**Invocation Logic**:
```yaml
IF database_design_needed THEN invoke database-architect
IF security_review_needed THEN invoke security-auditor
IF python_implementation THEN invoke python-pro
IF api_design THEN invoke api-design-principles
IF testing_needed THEN invoke qa-engineer
```

**Invoked By**:
- system-architect (architecture changes)
- User (explicit activation)

#### database-architect

**Can Invoke**:
- backend-architect (when backend integration needed)
- cloud-architect (when cloud deployment needed)
- security-auditor (when security review needed)
- database-optimizer (when performance optimization needed)

**Invocation Logic**:
```yaml
IF backend_integration THEN invoke backend-architect
IF cloud_deployment THEN invoke cloud-architect
IF security_requirements THEN invoke security-auditor
IF performance_concerns THEN invoke database-optimizer
```

**Invoked By**:
- backend-architect (dependency)
- system-architect (data layer)
- User (explicit activation)

#### cloud-architect

**Can Invoke**:
- backend-architect (when backend services needed)
- database-architect (when database services needed)
- security-auditor (when cloud security needed)
- devops-engineer (when DevOps implementation needed)

**Invocation Logic**:
```yaml
IF backend_services THEN invoke backend-architect
IF database_services THEN invoke database-architect
IF cloud_security THEN invoke security-auditor
IF devops_implementation THEN invoke devops-engineer
```

**Invoked By**:
- system-architect (cloud infrastructure)
- User (explicit activation)

### Development Skills

#### python-pro

**Can Invoke**:
- security-auditor (when security review needed)
- code-reviewer (when code review needed)
- qa-engineer (when testing needed)
- python-testing-patterns (when testing patterns needed)

**Invocation Logic**:
```yaml
IF security_review_needed THEN invoke security-auditor
IF code_review_needed THEN invoke code-reviewer
IF testing_needed THEN invoke qa-engineer
IF testing_patterns THEN invoke python-testing-patterns
```

**Invoked By**:
- backend-architect (Python implementation)
- qa-engineer (Python testing)
- User (explicit activation)

#### javascript-pro

**Can Invoke**:
- security-auditor (when security review needed)
- code-reviewer (when code review needed)
- qa-engineer (when testing needed)
- frontend-developer (when frontend integration needed)

**Invocation Logic**:
```yaml
IF security_review_needed THEN invoke security-auditor
IF code_review_needed THEN invoke code-reviewer
IF testing_needed THEN invoke qa-engineer
IF frontend_integration THEN invoke frontend-developer
```

**Invoked By**:
- frontend-developer (JavaScript implementation)
- User (explicit activation)

#### java-pro

**Can Invoke**:
- security-auditor (when security review needed)
- code-reviewer (when code review needed)
- qa-engineer (when testing needed)

**Invocation Logic**:
```yaml
IF security_review_needed THEN invoke security-auditor
IF code_review_needed THEN invoke code-reviewer
IF testing_needed THEN invoke qa-engineer
```

**Invoked By**:
- backend-architect (Java implementation)
- User (explicit activation)

#### golang-pro

**Can Invoke**:
- security-auditor (when security review needed)
- code-reviewer (when code review needed)
- qa-engineer (when testing needed)

**Invocation Logic**:
```yaml
IF security_review_needed THEN invoke security-auditor
IF code_review_needed THEN invoke code-reviewer
IF testing_needed THEN invoke qa-engineer
```

**Invoked By**:
- backend-architect (Go implementation)
- User (explicit activation)

### API Skills

#### api-design-principles

**Can Invoke**:
- backend-architect (when backend implementation needed)
- api-patterns (when API patterns needed)
- api-documenter (when documentation needed)
- api-security-best-practices (when security needed)

**Invocation Logic**:
```yaml
IF backend_implementation THEN invoke backend-architect
IF api_patterns THEN invoke api-patterns
IF documentation_needed THEN invoke api-documenter
IF security_needed THEN invoke api-security-best-practices
```

**Invoked By**:
- backend-architect (API design)
- User (explicit activation)

#### api-patterns

**Can Invoke**:
- api-design-principles (when design principles needed)
- backend-architect (when implementation needed)
- api-documenter (when documentation needed)

**Invocation Logic**:
```yaml
IF design_principles THEN invoke api-design-principles
IF implementation_needed THEN invoke backend-architect
IF documentation_needed THEN invoke api-documenter
```

**Invoked By**:
- api-design-principles (patterns)
- User (explicit activation)

#### api-documenter

**Can Invoke**:
- api-design-principles (when design review needed)
- backend-architect (when implementation review needed)

**Invocation Logic**:
```yaml
IF design_review THEN invoke api-design-principles
IF implementation_review THEN invoke backend-architect
```

**Invoked By**:
- api-design-principles (documentation)
- api-patterns (documentation)
- User (explicit activation)

#### api-security-best-practices

**Can Invoke**:
- security-auditor (when security review needed)
- backend-architect (when implementation needed)
- api-security-testing (when security testing needed)

**Invocation Logic**:
```yaml
IF security_review THEN invoke security-auditor
IF implementation_needed THEN invoke backend-architect
IF security_testing THEN invoke api-security-testing
```

**Invoked By**:
- api-design-principles (security)
- backend-architect (security)
- User (explicit activation)

#### api-security-testing

**Can Invoke**:
- security-auditor (when security review needed)
- qa-engineer (when testing needed)
- backend-architect (when backend testing needed)

**Invocation Logic**:
```yaml
IF security_review THEN invoke security-auditor
IF testing_needed THEN invoke qa-engineer
IF backend_testing THEN invoke backend-architect
```

**Invoked By**:
- api-security-best-practices (testing)
- qa-engineer (API security testing)
- User (explicit activation)

### Security Skills

#### security-auditor

**Can Invoke**:
- code-reviewer (when code review needed)
- backend-architect (when backend security review needed)
- cloud-architect (when cloud security review needed)
- forensics (when incident investigation needed)

**Invocation Logic**:
```yaml
IF code_review_needed THEN invoke code-reviewer
IF backend_security THEN invoke backend-architect
IF cloud_security THEN invoke cloud-architect
IF incident_investigation THEN invoke forensics
```

**Invoked By**:
- system-architect (security concerns)
- backend-architect (security review)
- python-pro (security review)
- qa-engineer (security testing)
- User (explicit activation)

#### code-reviewer

**Can Invoke**:
- security-auditor (when security vulnerabilities found)
- python-pro (when Python-specific review needed)
- qa-engineer (when quality assurance needed)

**Invocation Logic**:
```yaml
IF security_vulnerabilities THEN invoke security-auditor
IF python_specific THEN invoke python-pro
IF quality_assurance THEN invoke qa-engineer
```

**Invoked By**:
- security-auditor (code review)
- qa-engineer (code review)
- python-pro (code review)
- User (explicit activation)

### Testing Skills

#### e2e-testing

**Can Invoke**:
- qa-engineer (when quality assurance needed)
- frontend-developer (when frontend testing needed)
- backend-architect (when backend testing needed)
- python-pro (when Python testing needed)

**Invocation Logic**:
```yaml
IF quality_assurance THEN invoke qa-engineer
IF frontend_testing THEN invoke frontend-developer
IF backend_testing THEN invoke backend-architect
IF python_testing THEN invoke python-pro
```

**Invoked By**:
- qa-engineer (E2E testing)
- User (explicit activation)

#### test-driven-development

**Can Invoke**:
- python-testing-patterns (when Python testing needed)
- qa-engineer (when quality assurance needed)
- python-pro (when Python implementation needed)

**Invocation Logic**:
```yaml
IF python_testing THEN invoke python-testing-patterns
IF quality_assurance THEN invoke qa-engineer
IF python_implementation THEN invoke python-pro
```

**Invoked By**:
- python-pro (TDD implementation)
- qa-engineer (TDD testing)
- User (explicit activation)

#### python-testing-patterns

**Can Invoke**:
- python-pro (when Python implementation needed)
- qa-engineer (when quality assurance needed)
- test-driven-development (when TDD needed)

**Invocation Logic**:
```yaml
IF python_implementation THEN invoke python-pro
IF quality_assurance THEN invoke qa-engineer
IF tdd_needed THEN invoke test-driven-development
```

**Invoked By**:
- python-pro (testing patterns)
- test-driven-development (testing patterns)
- User (explicit activation)

### Networking Skills

#### networking

**Can Invoke**:
- cisco (when Cisco equipment involved)
- nxos (when NX-OS involved)
- forensics (when incident analysis needed)
- security-auditor (when security review needed)

**Invocation Logic**:
```yaml
IF cisco_equipment THEN invoke cisco
IF nx_os THEN invoke nxos
IF incident_analysis THEN invoke forensics
IF security_review THEN invoke security-auditor
```

**Invoked By**:
- User (explicit activation)
- system-architect (network architecture)

#### cisco

**Can Invoke**:
- nxos (when NX-OS specific)
- forensics (when incident analysis needed)
- security-auditor (when configuration review needed)
- networking (dependency - foundational networking)

**Invocation Logic**:
```yaml
IF nx_os_specific THEN invoke nxos
IF incident_analysis THEN invoke forensics
IF configuration_review THEN invoke security-auditor
```

**Invoked By**:
- networking (Cisco equipment)
- User (explicit activation)

#### nxos

**Can Invoke**:
- cisco (dependency - Cisco expertise)
- forensics (when incident analysis needed)
- security-auditor (when configuration review needed)
- networking (dependency - foundational networking)

**Invocation Logic**:
```yaml
IF incident_analysis THEN invoke forensics
IF configuration_review THEN invoke security-auditor
```

**Invoked By**:
- cisco (NX-OS specific)
- networking (NX-OS involved)
- User (explicit activation)

#### forensics

**Can Invoke**:
- networking (dependency - network analysis)
- cisco (when Cisco logs involved)
- security-auditor (when security incident)
- system-architect (when system-wide incident)

**Invocation Logic**:
```yaml
IF network_analysis THEN invoke networking
IF cisco_logs THEN invoke cisco
IF security_incident THEN invoke security-auditor
IF system_wide_incident THEN invoke system-architect
```

**Invoked By**:
- networking (incident analysis)
- cisco (incident analysis)
- nxos (incident analysis)
- security-auditor (incident investigation)
- User (explicit activation)

### Product Skills

#### product-manager

**Can Invoke**:
- product-strategist (when strategic guidance needed)
- system-architect (when architecture alignment needed)
- ui-ux (when UX guidance needed)
- backend-architect (when feature implementation needed)

**Invocation Logic**:
```yaml
IF strategic_guidance THEN invoke product-strategist
IF architecture_alignment THEN invoke system-architect
IF ux_guidance THEN invoke ui-ux
IF feature_implementation THEN invoke backend-architect
```

**Invoked By**:
- User (explicit activation)
- system-architect (product alignment)

#### product-strategist

**Can Invoke**:
- product-manager (when product management needed)
- system-architect (when strategic alignment needed)
- backend-architect (when feature strategy needed)

**Invocation Logic**:
```yaml
IF product_management THEN invoke product-manager
IF strategic_alignment THEN invoke system-architect
IF feature_strategy THEN invoke backend-architect
```

**Invoked By**:
- system-architect (strategic guidance)
- User (explicit activation)

### UI/UX Skills

#### ui-ux

**Can Invoke**:
- accessibility-compliance-accessibility-audit (when accessibility review needed)
- frontend-developer (when frontend implementation needed)

**Invocation Logic**:
```yaml
IF accessibility_review THEN invoke accessibility-compliance-accessibility-audit
IF frontend_implementation THEN invoke frontend-developer
```

**Invoked By**:
- User (explicit activation)
- system-architect (UI/UX design)

#### frontend-developer

**Can Invoke**:
- javascript-pro (when JavaScript implementation needed)
- accessibility-compliance-accessibility-audit (when accessibility review needed)
- ui-ux (when design guidance needed)
- qa-engineer (when testing needed)

**Invocation Logic**:
```yaml
IF javascript_implementation THEN invoke javascript-pro
IF accessibility_review THEN invoke accessibility-compliance-accessibility-audit
IF design_guidance THEN invoke ui-ux
IF testing_needed THEN invoke qa-engineer
```

**Invoked By**:
- ui-ux (frontend implementation)
- javascript-pro (frontend integration)
- User (explicit activation)

#### accessibility-compliance-accessibility-audit

**Can Invoke**:
- ui-ux (when design review needed)
- frontend-developer (when implementation review needed)
- qa-engineer (when testing needed)

**Invocation Logic**:
```yaml
IF design_review THEN invoke ui-ux
IF implementation_review THEN invoke frontend-developer
IF testing_needed THEN invoke qa-engineer
```

**Invoked By**:
- ui-ux (accessibility review)
- frontend-developer (accessibility review)
- User (explicit activation)

## Dependency Chains

### Backend Development Chain

```
database-architect → backend-architect → security-auditor → qa-engineer
```

**Activation Sequence**:
1. database-architect activates first (data layer design)
2. backend-architect activates second (service design)
3. security-auditor activates third (security review)
4. qa-engineer activates fourth (testing and validation)

### Cloud Infrastructure Chain

```
cloud-architect → security-auditor → devops-engineer → qa-engineer
```

**Activation Sequence**:
1. cloud-architect activates first (infrastructure design)
2. security-auditor activates second (security review)
3. devops-engineer activates third (implementation)
4. qa-engineer activates fourth (testing and validation)

### Network Analysis Chain

```
networking → cisco → nxos → forensics
```

**Activation Sequence**:
1. networking activates first (foundational knowledge)
2. cisco activates second (Cisco-specific)
3. nxos activates third (NX-OS specific)
4. forensics activates fourth (incident analysis)

### Security Review Chain

```
python-pro → security-auditor → code-reviewer → qa-engineer
```

**Activation Sequence**:
1. python-pro activates first (code implementation)
2. security-auditor activates second (security review)
3. code-reviewer activates third (code quality)
4. qa-engineer activates fourth (testing)

## Invocation Patterns

### Sequential Invocation

```
Skill A → Skill B → Skill C
(database-architect → backend-architect → security-auditor)
```

**Protocol**:
1. Skill A completes its phase
2. Skill A invokes Skill B
3. Skill B activates and executes
4. Skill B invokes Skill C
5. Skill C activates and executes
6. Skills deactivate in reverse order

### Parallel Invocation

```
Skill A + Skill B (simultaneous)
(code-reviewer + security-auditor)
```

**Protocol**:
1. Skill A invokes Skill B with parallel flag
2. Both skills activate simultaneously
3. Both skills execute independently
4. Results are merged
5. Both skills deactivate

### Hierarchical Invocation

```
Primary Skill
  ├── Dependency 1
  ├── Dependency 2
  └── Optional Skill
(system-architect)
  ├── backend-architect
  ├── database-architect
  └── security-auditor
```

**Protocol**:
1. Primary skill activates
2. Dependencies activate in parallel
3. Optional skill activates on condition
4. All skills coordinate through shared context
5. Skills deactivate when complete

## Invocation Conditions

### Conditional Invocation Rules

**Backend Architect**:
```yaml
invocation_conditions:
  - condition: database_design_needed
    target: database-architect
    priority: high
    required: true
  - condition: security_review_needed
    target: security-auditor
    priority: high
    required: true
  - condition: python_implementation
    target: python-pro
    priority: medium
    required: false
```

**Security Auditor**:
```yaml
invocation_conditions:
  - condition: code_review_needed
    target: code-reviewer
    priority: high
    required: true
  - condition: backend_security
    target: backend-architect
    priority: medium
    required: false
  - condition: incident_investigation
    target: forensics
    priority: high
    required: true
```

**Networking**:
```yaml
invocation_conditions:
  - condition: cisco_equipment
    target: cisco
    priority: high
    required: false
  - condition: nx_os
    target: nxos
    priority: high
    required: false
  - condition: incident_analysis
    target: forensics
    priority: high
    required: false
```

## Invocation Priority

### Priority Levels

**Critical (Priority 10)**:
- system-architect
- qa-engineer
- security-auditor

**High (Priority 9)**:
- backend-architect
- database-architect
- cloud-architect
- networking
- cisco
- forensics

**Medium (Priority 8)**:
- python-pro
- nxos
- code-reviewer

**Low (Priority 7)**:
- ui-ux

### Priority-Based Invocation

When multiple skills could be invoked:
1. Invoke higher priority skills first
2. Invoke required dependencies before optional skills
3. Invoke security skills before performance skills
4. Invoke foundational skills before specialized skills

## Conflict Resolution

### Conflict Types

**Circular Dependency**:
- Skill A invokes B, B invokes A
- **Resolution**: Break at lowest priority skill, implement handoff

**Multiple Invocations**:
- Multiple skills invoke same skill
- **Resolution**: Merge invocation requests, activate once with combined context

**Priority Conflict**:
- High and low priority invocations
- **Resolution**: High priority takes precedence, queue low priority

**Resource Conflict**:
- Limited resources for multiple skills
- **Resolution**: Prioritize critical skills, deactivate non-critical

## Invocation Performance

### Caching Strategy

```yaml
invocation_cache:
  skill_id: string
  invocation_context: object
  result: object
  timestamp: timestamp
  ttl: 300 (5 minutes)
```

### Optimization Techniques

1. **Invocation Caching**: Cache invocation results
2. **Lazy Invocation**: Invoke only when needed
3. **Batch Invocation**: Batch multiple invocations
4. **Pre-loading**: Pre-load likely skills
5. **Context Prediction**: Predict and pre-load skills

---

**Version**: 1.0.0  
**Last Updated**: 2026-08-06  
**Maintained By**: AI Skills System Invocation Engine
