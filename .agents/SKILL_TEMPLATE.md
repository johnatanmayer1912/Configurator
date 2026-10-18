---
description: Standard skill template with self-improvement capabilities for devin.ai
---

# SKILL_TEMPLATE.md

## Purpose

This is the standard template for all skills in the `.devin/skills/` directory. All skills should follow this structure and include the self-improvement capabilities defined below.

## Required Structure

```yaml
skill_name: [skill-name]
skill_category: [category]
version: 1.0.0
last_updated: [YYYY-MM-DD]
auto_activate: true
activation_triggers:
  - [keyword1]
  - [keyword2]
dependencies:
  - [skill1]
  - [skill2]
priority: [1-10]
```

## Required Sections

### 1. Skill Description
Clear description of what the skill does and when it should be used.

### 2. Activation Triggers
List of keywords and signals that trigger automatic activation of this skill.

### 3. Dependencies
List of skills that must be activated before this skill.

### 4. Self-Improvement Configuration
```yaml
self_improvement:
  enabled: true
  update_frequency: 7_days
  web_search_enabled: true
  github_monitoring: true
  documentation_tracking: true
  community_learning: true
```

### 5. Best Practices
List of best practices that this skill follows and enforces.

### 6. Automatic Actions
List of automatic actions that this skill triggers when activated.

## Self-Improvement Capabilities

### Periodic Web Search
Every 7 days, the skill should:
- Search for latest best practices in its domain
- Update its knowledge base with new information
- Improve its prompts and guidelines
- Stay current with industry standards

### GitHub Monitoring
The skill should:
- Monitor relevant GitHub repositories for updates
- Track official documentation changes
- Learn from community best practices
- Adapt to new tools and frameworks

### Self-Validation
The skill should:
- Validate its own recommendations
- Check for outdated practices
- Flag potential improvements
- Request updates when needed

## Automatic Task Completion

When this skill is activated and performs actions, it should automatically:
1. Update relevant documentation
2. Bump version numbers if needed
3. Run QA checks
4. Trigger rebuild if needed
5. Generate release notes if needed

## Example SKILL.md

```markdown
# SKILL.md

## Skill Name
python-pro

## Description
Python 3.12+ with modern features and best practices

## Activation Triggers
- python
- .py files
- pip
- poetry
- venv
- virtualenv

## Dependencies
- code-reviewer
- security-auditor

## Priority
8

## Self-Improvement
Enabled: true
Update Frequency: 7 days
Web Search: true
GitHub Monitoring: true

## Best Practices
- Use type hints
- Follow PEP 8
- Use async/await for I/O operations
- Use context managers for resource management
- Write docstrings for all functions and classes
- Use f-strings for string formatting
- Use dataclasses for data structures

## Automatic Actions
- Run code review on Python files
- Run security audit on Python files
- Run linting (ruff, black, mypy)
- Run tests (pytest)
- Update documentation
```

## Implementation Notes

When creating a new skill:
1. Copy this template to the skill directory
2. Fill in the required sections
3. Customize activation triggers
4. Add skill-specific best practices
5. Test automatic activation
6. Validate self-improvement capabilities

## Maintenance

Regularly review and update:
- Activation triggers
- Dependencies
- Best practices
- Self-improvement configuration
- Automatic actions
