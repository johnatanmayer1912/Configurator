---
description: AI IDE Automation Workflow - Comprehensive automation for software development
---

# AI IDE Automation Workflow

## Purpose

This workflow defines the comprehensive automation system for the AI IDE, ensuring that all software development tasks are handled with maximum efficiency and minimal manual intervention.

## Core Principles

1. **Zero Manual Intervention**: All standard development tasks are automated
2. **Automatic Skill Activation**: Relevant skills activate based on context
3. **Self-Improving Skills**: Skills continuously improve themselves
4. **Complete Task Handling**: From user input to deployment, everything is automated
5. **Quality Assurance**: All changes are automatically validated

## Workflow Stages

### Stage 1: Task Reception & Analysis
**Trigger**: User provides any input

**Actions**:
1. Analyze task scope and impact
2. Identify all affected components
3. Activate relevant skills automatically
4. Determine required follow-up actions
5. Create execution plan

**Skills Activated**:
- `planning-and-task-breakdown`
- `context-manager`
- Relevant domain skills (based on task)

### Stage 2: Task Execution
**Trigger**: Execution plan created

**Actions**:
1. Execute primary task
2. Apply best practices
3. Follow coding standards
4. Ensure code quality
5. Handle edge cases

**Skills Activated**:
- Domain-specific skills (e.g., `python-pro`, `javascript-pro`)
- `code-reviewer` (real-time)
- `security-auditor` (real-time)

### Stage 3: Automatic Follow-Up
**Trigger**: Task execution complete

**Actions**:
1. Update all documentation
2. Bump version numbers
3. Run QA checks
4. Trigger rebuild
5. Generate release notes

**Skills Activated**:
- `documentation-and-adrs`
- `code-reviewer`
- `security-auditor`
- `deployment-engineer`
- `product-manager`

See `.devin/workflows/automatic-task-completion.md` for detailed automatic task completion workflow.

### Stage 4: Validation & Deployment
**Trigger**: Follow-up actions complete

**Actions**:
1. Validate all changes
2. Run comprehensive tests
3. Build artifacts
4. Deploy if needed
5. Update project status

**Skills Activated**:
- `test-driven-development`
- `deployment-engineer`
- `observability-engineer`

## Task Types & Automation

### Bug Fix
**User Input**: "Fix the bug in network discovery"

**Automatic Actions**:
1. Fix bug in code
2. Update plugin README
3. Update CHANGELOG.md
4. Bump version
5. Run code review
6. Run security audit
7. Run tests
8. Trigger rebuild
9. Generate release notes
10. Update build spec

### Feature Addition
**User Input**: "Add new plugin for interface management"

**Automatic Actions**:
1. Create plugin code
2. Create plugin documentation
3. Update main README
4. Update CHANGELOG.md
5. Bump version
6. Run code review
7. Run security audit
8. Run tests
9. Trigger rebuild
10. Generate release notes
11. Update build spec
12. Create ADR

### Documentation Update
**User Input**: "Update the README with new features"

**Automatic Actions**:
1. Update README
2. Update CHANGELOG.md
3. Bump version
4. Run validation
5. Trigger rebuild
6. Generate release notes

### Configuration Change
**User Input**: "Update the config file"

**Automatic Actions**:
1. Update config
2. Validate config
3. Update documentation
4. Update CHANGELOG.md
5. Bump version
6. Run tests
7. Trigger rebuild
8. Generate release notes

### Dependency Update
**User Input**: "Update dependencies"

**Automatic Actions**:
1. Update dependencies
2. Run security audit
3. Update documentation
4. Update CHANGELOG.md
5. Bump version
6. Run tests
7. Trigger rebuild
8. Generate release notes

## Skill Coordination

### Dependency Chain
```
RESYNC (global-master-prompt-rules)
→ Product Strategist (product-manager, product-inventor)
→ System Architect (backend-architect, senior-architect, cloud-architect)
→ Lead Developer (python-pro, javascript-pro, etc.)
→ QA Engineer (code-reviewer, security-auditor)
→ Documentation Steward (documentation-and-adrs)
→ Release Manager (deployment-engineer)
→ Observability Engineer (observability-engineer)
→ Prompt Librarian (context-manager)
```

### Parallel Execution
- Code review runs in parallel with security audit
- Documentation updates run in parallel with version bumping
- Tests run in parallel with linting
- Build preparation runs in parallel with release note generation

## Quality Gates

### Gate 1: Code Quality
- Code review passes
- Linting passes
- Security audit passes
- Tests pass

### Gate 2: Documentation
- README updated
- CHANGELOG updated
- API docs updated
- Comments updated

### Gate 3: Version
- VERSION file updated
- README version updated
- Spec version updated
- Package version updated

### Gate 4: Build
- Build succeeds
- Artifacts valid
- Release notes generated
- Deployment config updated

## Error Handling

### If Code Review Fails
1. Log issues
2. Auto-fix if possible
3. Request user approval for manual fixes
4. Continue with other gates

### If Security Audit Fails
1. Log security issues
2. Block deployment
3. Request immediate user attention
4. Continue with documentation updates

### If Tests Fail
1. Log test failures
2. Auto-fix if possible
3. Request user approval for manual fixes
4. Block deployment

### If Build Fails
1. Log build errors
2. Attempt fix
3. Request user attention
4. Block deployment

## Monitoring

### Metrics Tracked
- Task completion time
- Automatic action success rate
- Skill activation accuracy
- Quality gate pass rate
- User satisfaction

### Alerts
- Failed quality gates
- Long-running tasks
- Skill activation failures
- Self-improvement failures

## Self-Improvement

The AI IDE continuously improves through workflow optimization and skill enhancement.

See `.devin/SKILL_ACTIVATION_SYSTEM.md` for detailed self-improvement system information.

## Documentation

### Required Documentation
- All workflows documented in `.devin/workflows/`
- All skill improvements documented in `docs/`
- Automatic processes documented in `docs/rebuilt-1-1/`
- Quality gates documented in `docs/quality/`

### Documentation Updates
- Automatically updated with each change
- Version controlled
- Peer reviewed
- User accessible

## Integration with Existing Systems

### docs/13-master-prompts
- Council roles integrated
- Domain specialists integrated
- Policies enforced
- Workflows aligned

### BUILD_GUIDE.md
- Build process automated
- Version management automated
- Release process automated

### Project Structure
- All changes respect project structure
- Documentation follows project conventions
- Code follows project standards

## Future Enhancements

### Planned Features
- Predictive task completion
- Automated issue tracking
- Automated PR creation
- Automated deployment to staging
- Automated rollback on failure

### Continuous Improvement
- User feedback integration
- Performance optimization
- Skill expansion
- Workflow refinement

## Related Documentation

- `.devin/DOCUMENTATION_STRUCTURE.md` - Documentation structure and single source of truth
- `.devin/workflows/automatic-task-completion.md` - Automatic task completion details (primary source)
- `.devin/SKILL_ACTIVATION_SYSTEM.md` - Skill activation system (primary source)
- `.devin/README.md` - Skill library overview
- `.devin/SKILL_TEMPLATE.md` - Skill template
- `BUILD_GUIDE.md` - Build process documentation
