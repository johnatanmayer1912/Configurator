---
description: Automatic Task Completion Workflow - Ensures all necessary follow-up actions are performed automatically
---

# Automatic Task Completion Workflow

## Purpose

This workflow ensures that any task performed by the AI automatically triggers all necessary follow-up actions without requiring explicit user instructions. This includes documentation updates, version bumps, QA checks, rebuilds, and other standard software development practices.

## Workflow Steps

### Step 1: Task Analysis
When a user provides a task, the AI must:
1. Analyze the task scope and impact
2. Identify all affected components
3. Determine necessary follow-up actions
4. Activate relevant skills automatically

### Step 2: Task Execution
Execute the primary task as requested by the user.

### Step 3: Automatic Follow-Up Actions
After task completion, automatically perform:

#### 3.1 Documentation Updates
- Update relevant README files
- Update CHANGELOG.md
- Update API documentation
- Update inline code comments
- Create/update ADRs (Architecture Decision Records) if architectural changes were made

#### 3.2 Version Management
- Bump version in VERSION file
- Update version in README.md
- Update version in spec files
- Update version in package.json (if applicable)

#### 3.3 Quality Assurance
- Run code review
- Run security audit
- Run linting
- Run tests
- Validate configuration files

#### 3.4 Build & Release
- Trigger rebuild (1:1 rebuild process)
- Update build artifacts
- Generate release notes
- Update deployment configurations

#### 3.5 Communication
- Update project status
- Notify relevant stakeholders (if applicable)
- Update project metrics

## Trigger Conditions

This workflow is automatically triggered when:
- Any code modification is made
- Any configuration change is made
- Any documentation change is made
- Any build-related change is made
- Any dependency change is made

## Skill Activation

The following skills are automatically activated for this workflow:
- `code-reviewer` - For code review
- `documentation-and-adrs` - For documentation
- `security-auditor` - For security checks
- `deployment-engineer` - For build and deployment
- `product-manager` - For release notes
- `system-architect` - For architectural validation

## Configuration

### Automatic Activation Rules
```yaml
auto_activate: true
trigger_on:
  - code_change
  - config_change
  - doc_change
  - build_change
  - dependency_change
```

### Follow-Up Actions Configuration
```yaml
follow_up_actions:
  documentation:
    - update_readme
    - update_changelog
    - update_api_docs
    - update_comments
    - create_adr_if_needed
  
  version:
    - bump_version
    - update_readme_version
    - update_spec_version
    - update_package_version
  
  qa:
    - code_review
    - security_audit
    - linting
    - tests
    - validate_config
  
  build:
    - trigger_rebuild
    - update_artifacts
    - generate_release_notes
    - update_deployment_config
```

## Implementation

### Example Scenario

**User Request:** "Fix the bug in the network discovery module"

**Automatic Actions Performed:**
1. Fix the bug in `modules/plugins/network_discovery.py`
2. Update `docs/05-plugins/network_discovery/README.md` with bug fix details
3. Update `CHANGELOG.md` with bug fix entry
4. Bump version in `VERSION` file
5. Update version in `README.md`
6. Run code review on changes
7. Run security audit on changes
8. Run tests
9. Trigger 1:1 rebuild
10. Generate release notes
11. Update build spec file

### Example Scenario 2

**User Request:** "Add a new plugin for interface management"

**Automatic Actions Performed:**
1. Create new plugin in `modules/plugins/interface_manager/`
2. Create documentation in `docs/05-plugins/interface_manager/README.md`
3. Update main README.md with new plugin
4. Update CHANGELOG.md
5. Bump version
6. Run code review
7. Run security audit
8. Run tests
9. Trigger 1:1 rebuild
10. Generate release notes
11. Update build spec file
12. Create ADR for new plugin architecture

## Validation

After each automatic action, validate:
- Action was successful
- No errors occurred
- Changes are consistent
- Documentation is accurate
- Version numbers are correct
- Build artifacts are valid

## Rollback

If any automatic action fails:
1. Log the failure
2. Rollback the failed action
3. Notify the user
4. Continue with other non-dependent actions
5. Provide clear error message and next steps

## Monitoring

Track:
- Number of automatic actions performed
- Success rate of automatic actions
- Time taken for automatic actions
- User satisfaction with automatic actions
- Errors and their resolutions

## Maintenance

Regularly review and update:
- Follow-up action lists
- Skill activation rules
- Validation criteria
- Rollback procedures
- Monitoring metrics

## Related Documentation

- `.devin/SKILL_ACTIVATION_SYSTEM.md` - Skill activation system
- `.devin/README.md` - Skill library overview
- `BUILD_GUIDE.md` - Build process documentation
- `docs/13-master-prompts/INDEX_PROMPT.md` - Master prompt entry point
