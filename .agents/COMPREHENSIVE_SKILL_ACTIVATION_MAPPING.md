# COMPREHENSIVE SKILL ACTIVATION MAPPING
**Version**: 1.0.0  
**Date**: 2026-08-06  
**Scope**: Complete skill activation rules, dependencies, and coordination for all skills in .agents and .devin directories

---

## Purpose

This document provides comprehensive skill activation mapping, including automatic activation rules, dependency chains, conflict resolution, and coordination protocols. This is the operational guide for skill activation in the AI-IDE system.

---

## Activation Philosophy

### Principles

1. **Context-Aware Activation**: Skills activate based on task context, keywords, and user intent
2. **Dependency Enforcement**: Required dependencies activate automatically before primary skill
3. **Conflict Resolution**: Clear rules for handling skill conflicts and priority
4. **Performance Optimization**: Minimal skill activation to avoid overhead
5. **User Control**: Users can override automatic activation when needed

### Activation Levels

- **Mandatory**: Always active for specific task types
- **Context-Based**: Activates based on task context and keywords
- **Optional**: Activates only when explicitly requested
- **Suppressed**: Explicitly disabled for specific contexts

---

## Skill Activation Matrix

### Architecture & Design Tasks

| Task Type | Primary Skill | Dependencies | Optional Skills |
|-----------|--------------|--------------|-----------------|
| System Architecture | system-architect | None | backend-architect, database-architect, cloud-architect |
| Backend Architecture | backend-architect | database-architect | system-architect, security-auditor |
| Database Architecture | database-architect | None | backend-architect, cloud-architect |
| Cloud Architecture | cloud-architect | None | system-architect, security-auditor |
| API Design | api-design-principles | backend-architect | api-patterns, api-security-best-practices |
| Network Architecture | networking | None | cisco_professional, nxos |

### Development Tasks

| Task Type | Primary Skill | Dependencies | Optional Skills |
|-----------|--------------|--------------|-----------------|
| Python Development | python-pro | programming | security-auditor, code-reviewer |
| Backend Development | backend-architect | database-architect | python-pro, security-auditor |
| Frontend Development | ui-ux | None | accessibility-compliance-accessibility-audit |
| Full-Stack Development | backend-architect, ui-ux | database-architect, networking | python-pro, security-auditor |
| API Development | api-patterns | backend-architect | api-security-best-practices, api-testing-observability-api-mock |

### Security Tasks

| Task Type | Primary Skill | Dependencies | Optional Skills |
|-----------|--------------|--------------|-----------------|
| Security Audit | security-auditor | None | code-reviewer, backend-architect |
| Vulnerability Assessment | security-auditor | None | code-reviewer, python-pro |
| Penetration Testing | security-auditor | None | api-security-testing, backend-security-coder |
| Security Review | security-auditor | code-reviewer | backend-architect, cloud-architect |
| Compliance Audit | security-auditor | None | cloud-architect, database-architect |

### Testing & QA Tasks

| Task Type | Primary Skill | Dependencies | Optional Skills |
|-----------|--------------|--------------|-----------------|
| Code Review | code-reviewer | programming | security-auditor, python-pro |
| QA Testing | qa-engineer | programming | python-pro, security-auditor |
| E2E Testing | qa-engineer | programming | python-pro, ui-ux |
| Performance Testing | application-performance-performance-optimization | None | backend-architect, database-architect |
| API Testing | api-testing-observability-api-mock | api-patterns | api-security-testing |

### Network & Infrastructure Tasks

| Task Type | Primary Skill | Dependencies | Optional Skills |
|-----------|--------------|--------------|-----------------|
| Network Design | networking | None | cisco_professional, nxos |
| Cisco Configuration | cisco_professional | networking | nxos, forensics |
| NX-OS Configuration | nxos | cisco_professional, networking | forensics |
| Network Forensics | forensics | networking, cisco_professional | None |
| Infrastructure as Code | cloud-architect | None | devops-engineer |

### Data & Analytics Tasks

| Task Type | Primary Skill | Dependencies | Optional Skills |
|-----------|--------------|--------------|-----------------|
| Data Modeling | database-architect | None | backend-architect |
| Data Pipeline | backend-architect | database-architect | python-pro |
| Data Analysis | python-pro | programming | None |
| Machine Learning | ai-engineer | python-pro | backend-architect, cloud-architect |

---

## Keyword-Based Activation Rules

### Architecture Keywords

```
Keywords → Skill Activation

"architecture", "design", "structure", "system" → system-architect
"backend", "api", "service", "microservice" → backend-architect
"database", "schema", "data model", "storage" → database-architect
"cloud", "aws", "azure", "gcp", "infrastructure" → cloud-architect
"network", "routing", "switching", "vlan" → networking
```

### Development Keywords

```
Keywords → Skill Activation

"python", ".py", "pip", "poetry", "async" → python-pro
"code", "programming", "development", "software" → programming
"frontend", "ui", "ux", "interface" → ui-ux
"backend", "api", "service" → backend-architect
"full-stack", "fullstack" → backend-architect + ui-ux
```

### Security Keywords

```
Keywords → Skill Activation

"security", "vulnerability", "audit", "penetration" → security-auditor
"owasp", "injection", "xss", "csrf" → security-auditor
"authentication", "authorization", "oauth", "jwt" → security-auditor
"encryption", "tls", "ssl", "crypto" → security-auditor
"compliance", "gdpr", "hipaa", "pci" → security-auditor
```

### Testing Keywords

```
Keywords → Skill Activation

"test", "qa", "validation", "quality" → qa-engineer
"review", "pr", "pull request", "code review" → code-reviewer
"e2e", "end-to-end", "integration" → qa-engineer
"unit test", "pytest", "jest" → qa-engineer
"performance", "optimization", "latency" → application-performance-performance-optimization
```

### Network Keywords

```
Keywords → Skill Activation

"cisco", "ios", "nx-os", "nexus" → cisco_professional
"vpc", "vxlan", "otv", "lisp" → nxos
"ospf", "bgp", "eigrp", "routing" → networking
"stp", "lacp", "vlan", "switching" → networking
"forensic", "incident", "log analysis" → forensics
```

### Data Keywords

```
Keywords → Skill Activation

"database", "sql", "nosql", "schema" → database-architect
"data", "analytics", "pipeline", "etl" → python-pro
"machine learning", "ml", "ai", "model" → ai-engineer
"query", "index", "optimization" → database-architect
```

---

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
networking → cisco_professional → nxos → forensics
```

**Activation Sequence**:
1. networking activates first (foundational knowledge)
2. cisco_professional activates second (Cisco-specific)
3. nxos activates third (NX-OS specific)
4. forensics activates fourth (incident analysis)

### API Development Chain

```
api-design-principles → api-patterns → api-security-best-practices → api-testing-observability-api-mock
```

**Activation Sequence**:
1. api-design-principles activates first (design principles)
2. api-patterns activates second (pattern selection)
3. api-security-best-practices activates third (security implementation)
4. api-testing-observability-api-mock activates fourth (testing)

### Python Development Chain

```
programming → python-pro → security-auditor → code-reviewer → qa-engineer
```

**Activation Sequence**:
1. programming activates first (foundational principles)
2. python-pro activates second (Python-specific)
3. security-auditor activates third (security review)
4. code-reviewer activates fourth (code quality)
5. qa-engineer activates fifth (testing)

---

## Conflict Resolution

### Skill Conflicts

| Conflict Type | Conflicting Skills | Resolution Rule |
|---------------|-------------------|-----------------|
| Vendor Conflict | cisco_professional vs networking | cisco_professional takes priority for Cisco-specific tasks |
| Layer Conflict | backend-architect vs database-architect | database-architect activates first for data layer |
| Review Conflict | code-reviewer vs security-auditor | Both activate, security-auditor takes priority for security |
| Testing Conflict | qa-engineer vs code-reviewer | qa-engineer for testing, code-reviewer for code quality |

### Priority Rules

1. **Vendor-Specific > Generic**: Vendor-specific skills take priority over generic skills
2. **Security > Performance**: Security skills take priority over performance skills
3. **Data Layer > Service Layer**: Database skills activate before backend skills
4. **Review > Implementation**: Review skills activate after implementation skills
5. **Testing > Review**: Testing skills activate after review skills

### Conflict Examples

**Example 1: Cisco Network Configuration**
- **Task**: Configure Cisco switch
- **Conflict**: networking vs cisco_professional
- **Resolution**: cisco_professional activates (vendor-specific takes priority)

**Example 2: Backend API Development**
- **Task**: Design and implement REST API
- **Conflict**: backend-architect vs database-architect
- **Resolution**: database-architect activates first, then backend-architect

**Example 3: Security Code Review**
- **Task**: Review code for security vulnerabilities
- **Conflict**: code-reviewer vs security-auditor
- **Resolution**: Both activate, security-auditor takes priority for security issues

---

## Context-Based Activation

### Project Context

**ACI Fabric Explorer Project**:
- **Always Active**: python, programming, qa
- **Context-Specific**: 
  - Network operations → networking, cisco_professional
  - UI development → ui_ux
  - Backend development → python-pro, backend-architect
  - Security review → security-auditor

### Environment Context

**Development Environment**:
- **Always Active**: programming, python-pro
- **Context-Specific**: code-reviewer, qa-engineer

**Production Environment**:
- **Always Active**: security-auditor, qa-engineer
- **Context-Specific**: forensics, networking

**Testing Environment**:
- **Always Active**: qa-engineer, python-pro
- **Context-Specific**: api-testing-observability-api-mock

### Task Context

**Feature Development**:
- **Primary**: backend-architect or ui-ux (depending on feature)
- **Dependencies**: database-architect, programming
- **Quality**: code-reviewer, qa-engineer

**Bug Fix**:
- **Primary**: programming or python-pro
- **Dependencies**: None
- **Quality**: code-reviewer, qa-engineer

**Incident Response**:
- **Primary**: forensics
- **Dependencies**: networking, cisco_professional
- **Quality**: security-auditor

**Architecture Review**:
- **Primary**: system-architect
- **Dependencies**: None
- **Quality**: security-auditor, qa-engineer

---

## Activation Performance Optimization

### Minimal Activation Strategy

**Goal**: Activate only necessary skills to minimize overhead

**Rules**:
1. Activate primary skill for task type
2. Activate only required dependencies
3. Activate optional skills only when explicitly requested
4. Deactivate skills when task context changes
5. Cache skill activation state for reuse

### Skill Activation Caching

**Cache Strategy**:
- Cache activation state for 5 minutes
- Invalidate cache on task context change
- Reuse cached activation when context matches
- Clear cache on explicit skill request

### Activation Optimization

**Optimization Techniques**:
1. **Lazy Activation**: Activate skills only when needed
2. **Early Deactivation**: Deactivate skills when no longer needed
3. **Batch Activation**: Activate multiple skills in single operation
4. **Dependency Pre-loading**: Pre-load dependencies for common tasks
5. **Context Prediction**: Predict and pre-load likely skills

---

## Skill Coordination Protocols

### Inter-Skill Communication

**Communication Channels**:
1. **Shared Context**: Skills share task context and user intent
2. **Dependency Handoff**: Skills hand off control through dependencies
3. **Conflict Notification**: Skills notify of conflicts and resolution
4. **Status Updates**: Skills provide status updates to coordination system

### Coordination Patterns

**Sequential Pattern**:
```
Skill A → Skill B → Skill C
(database-architect → backend-architect → security-auditor)
```

**Parallel Pattern**:
```
Skill A + Skill B (simultaneous)
(code-reviewer + security-auditor)
```

**Hierarchical Pattern**:
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

### Skill Handoff

**Handoff Triggers**:
1. **Dependency Satisfied**: Primary skill signals dependency complete
2. **Task Phase Change**: Task moves to next phase
3. **Explicit Request**: User explicitly requests skill handoff
4. **Conflict Resolution**: Conflict resolution requires handoff

**Handoff Protocol**:
1. Source skill signals completion
2. Target skill activates
3. Context and state transferred
4. Source skill deactivates (if no longer needed)

---

## Skill Activation API

### Activation Request

```yaml
activation_request:
  task_type: string
  context: object
  keywords: array
  user_intent: string
  explicit_skills: array (optional)
  suppress_skills: array (optional)
```

### Activation Response

```yaml
activation_response:
  primary_skill: string
  active_skills: array
  dependencies: array
  conflicts: array
  resolution: string
  performance_metrics: object
```

### Activation Status

```yaml
activation_status:
  skill_id: string
  status: active | inactive | pending
  activation_time: timestamp
  context: object
  dependencies: array
```

---

## Monitoring and Analytics

### Activation Metrics

**Metrics to Track**:
1. **Activation Frequency**: How often each skill activates
2. **Activation Duration**: How long skills remain active
3. **Dependency Satisfaction**: How often dependencies are satisfied
4. **Conflict Rate**: How often conflicts occur
5. **Resolution Time**: Time to resolve conflicts
6. **Performance Impact**: Performance impact of skill activation

### Analytics Dashboard

**Dashboard Metrics**:
- Skill activation heatmap
- Dependency chain visualization
- Conflict resolution timeline
- Performance impact charts
- User satisfaction scores

### Optimization Recommendations

**Based on Analytics**:
1. Identify frequently activated skills for optimization
2. Identify rarely used skills for deprecation
3. Identify common conflicts for resolution
4. Identify performance bottlenecks for optimization
5. Identify user patterns for prediction

---

## Maintenance and Updates

### Skill Addition Process

1. **Identify Need**: Determine skill gap or requirement
2. **Design Skill**: Create skill following template
3. **Define Activation**: Define activation rules and dependencies
4. **Test Activation**: Test skill activation and coordination
5. **Update Mapping**: Update this activation mapping
6. **Communicate**: Notify users of new skill

### Skill Removal Process

1. **Identify Obsolete**: Identify obsolete or redundant skill
2. **Check Dependencies**: Check for dependent skills
3. **Plan Migration**: Plan migration or replacement
4. **Update Activation**: Update activation rules
5. **Remove Skill**: Remove skill from system
6. **Update Mapping**: Update this activation mapping

### Activation Rule Updates

1. **Review Performance**: Review activation performance metrics
2. **Identify Issues**: Identify activation issues or conflicts
3. **Update Rules**: Update activation rules based on findings
4. **Test Changes**: Test updated activation rules
5. **Deploy Changes**: Deploy updated activation rules
6. **Monitor Impact**: Monitor impact of changes

---

## Troubleshooting

### Common Issues

**Issue 1: Skill Not Activating**
- **Symptoms**: Expected skill not activating
- **Causes**: Incorrect keywords, missing dependencies, conflict resolution
- **Resolution**: Check activation rules, verify dependencies, check conflicts

**Issue 2: Skill Conflict**
- **Symptoms**: Multiple skills conflicting
- **Causes**: Overlapping activation rules, ambiguous context
- **Resolution**: Review conflict resolution rules, update activation rules

**Issue 3: Dependency Not Satisfied**
- **Symptoms**: Dependency not activating
- **Causes**: Missing dependency definition, circular dependency
- **Resolution**: Check dependency definition, resolve circular dependencies

**Issue 4: Performance Degradation**
- **Symptoms**: System slow with skill activation
- **Causes**: Too many active skills, inefficient activation
- **Resolution**: Optimize activation rules, implement caching

### Debugging Tools

**Activation Debugger**:
- Trace skill activation sequence
- View dependency chain status
- Monitor conflict resolution
- Analyze performance metrics

**Activation Simulator**:
- Simulate skill activation scenarios
- Test activation rules
- Validate dependency chains
- Predict performance impact

---

## Best Practices

### For Users

1. **Provide Clear Context**: Provide clear task context and user intent
2. **Use Specific Keywords**: Use specific keywords for accurate activation
3. **Override When Needed**: Override automatic activation when needed
4. **Provide Feedback**: Provide feedback on skill activation quality
5. **Monitor Performance**: Monitor skill activation performance

### For Skill Developers

1. **Define Clear Activation Rules**: Define clear activation triggers and keywords
2. **Specify Dependencies**: Specify all required dependencies
3. **Test Activation**: Test skill activation thoroughly
4. **Document Behavior**: Document skill behavior and coordination
5. **Monitor Performance**: Monitor skill activation performance

### For System Administrators

1. **Monitor Activation Metrics**: Monitor activation metrics regularly
2. **Optimize Rules**: Optimize activation rules based on metrics
3. **Update Mapping**: Keep activation mapping up to date
4. **Test Changes**: Test activation changes before deployment
5. **Communicate Changes**: Communicate activation changes to users

---

## Related Documentation

- `.agents/MASTER_SKILL_INDEX.md` - Complete skill inventory
- `.agents/SKILL_QUALITY_AUDIT.md` - Skill quality assessment
- `.agents/SKILL_ACTIVATION_CONFIG.md` - Skill activation configuration
- `.agents/SKILL_ACTIVATION_SYSTEM.md` - Skill activation system
- `.devin/SKILL_ACTIVATION_CONFIG.md` - .devin activation configuration
- `.devin/SKILL_ACTIVATION_SYSTEM.md` - .devin activation system

---

**Last Updated**: 2026-08-06  
**Next Review**: 2026-11-06  
**Maintained By**: AI-IDE Skill Library Governance
