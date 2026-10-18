# Documentation Structure - Single Source of Truth

## Purpose

This document defines the single source of truth for all AI IDE documentation, eliminating duplicates and ensuring each piece of information has one authoritative location.

## Documentation Hierarchy

### Level 1: Core Documentation (Primary Sources)

#### `.devin/README.md`
**Purpose**: Main entry point and overview
**Contains**:
- Skill library purpose and sources
- Directory structure
- Professional roles inventory
- Integration with docs/13-master-prompts
- Usage summary
- Links to detailed documentation

**Does NOT contain**:
- Detailed implementation details
- Duplicate workflow information
- Duplicate self-improvement details

#### `.devin/SKILL_ACTIVATION_SYSTEM.md`
**Purpose**: Authoritative source for skill activation
**Contains**:
- Auto-activation rules (mandatory, professional, special skills)
- Skill loading order
- Self-improvement system (detailed)
- Automatic task completion (summary)
- Skill activation API
- Configuration details
- Testing and monitoring

**Does NOT contain**:
- Duplicate workflow details
- Duplicate skill inventory

#### `.devin/SKILL_TEMPLATE.md`
**Purpose**: Standard template for all skills
**Contains**:
- Required structure
- Required sections
- Self-improvement configuration
- Best practices guidelines
- Implementation notes

**Does NOT contain**:
- Duplicate process documentation
- Duplicate workflow information

### Level 2: Workflow Documentation

#### `.devin/workflows/automatic-task-completion.md`
**Purpose**: Detailed automatic task completion workflow
**Contains**:
- Workflow steps
- Trigger conditions
- Skill activation for workflow
- Configuration details
- Implementation examples
- Validation and rollback

**Does NOT contain**:
- Duplicate self-improvement details
- Duplicate skill activation rules

#### `.devin/workflows/ai-ide-automation.md`
**Purpose**: High-level AI IDE automation overview
**Contains**:
- Core principles
- Workflow stages (high-level)
- Task types and automation (high-level)
- Skill coordination
- Quality gates
- Error handling
- Monitoring
- Self-improvement (workflow-level)
- Integration with existing systems

**Does NOT contain**:
- Duplicate detailed workflow steps
- Duplicate self-improvement system details
- Duplicate skill activation rules

#### `.devin/workflows/skill-batch-update.md`
**Purpose**: Systematic skill update process
**Contains**:
- Update strategy (priority classification)
- Update process steps
- Automation script
- Update checklist
- Monitoring and rollback
- Quality assurance

**Does NOT contain**:
- Duplicate skill template details
- Duplicate self-improvement details

### Level 3: Process Documentation

#### `docs/skill-improvement-process.md`
**Purpose**: Detailed skill improvement framework
**Contains**:
- Self-improvement capabilities (detailed)
- Best practices for devin.ai usage
- Skill update process
- Skill validation process
- Batch update process
- Skill metrics
- Documentation requirements
- Quality assurance
- Rollback process
- Communication

**Does NOT contain**:
- Duplicate skill activation rules
- Duplicate workflow details

#### `docs/rebuilt-1-1/automatic-processes.md`
**Purpose**: Automatic processes documentation for 1:1 rebuild
**Contains**:
- Automatic skill activation (summary)
- Automatic task completion (summary)
- Self-improving skills (summary)
- Automatic quality assurance
- Automatic documentation
- Automatic version management
- Automatic build & release
- Automatic communication
- Error handling
- Monitoring
- Performance optimization
- Integration with existing systems
- Documentation of automatic processes

**Does NOT contain**:
- Duplicate detailed implementation
- Duplicate workflow steps

## Cross-Reference Guidelines

### When to Reference vs. Duplicate

**Reference (Link) when:**
- Information is detailed in another document
- Information is the authoritative source
- Information is implementation detail

**Duplicate when:**
- Information is a high-level summary needed for context
- Information is essential for understanding the current document
- Information is a brief overview (not detailed)

### Reference Format

```markdown
See `[DOCUMENT_PATH]` for details
```

## Information Ownership

### Skill Activation
**Primary Source**: `.devin/SKILL_ACTIVATION_SYSTEM.md`
**Secondary References**:
- `.devin/README.md` (summary)
- `.devin/workflows/ai-ide-automation.md` (overview)
- `docs/rebuilt-1-1/automatic-processes.md` (summary)

### Self-Improvement System
**Primary Source**: `.devin/SKILL_ACTIVATION_SYSTEM.md` (system-level) and `docs/skill-improvement-process.md` (process-level)
**Secondary References**:
- `.devin/README.md` (summary)
- `.devin/SKILL_TEMPLATE.md` (configuration)
- `docs/rebuilt-1-1/automatic-processes.md` (summary)

### Automatic Task Completion
**Primary Source**: `.devin/workflows/automatic-task-completion.md`
**Secondary References**:
- `.devin/SKILL_ACTIVATION_SYSTEM.md` (summary)
- `.devin/workflows/ai-ide-automation.md` (overview)
- `docs/rebuilt-1-1/automatic-processes.md` (summary)

### Skill Template
**Primary Source**: `.devin/SKILL_TEMPLATE.md`
**Secondary References**:
- `docs/skill-improvement-process.md` (usage)
- `.devin/workflows/skill-batch-update.md` (application)

### Skill Inventory
**Primary Source**: `.devin/README.md`
**Secondary References**:
- `.devin/SKILL_ACTIVATION_SYSTEM.md` (activation mapping)

## Cleanup Actions Required

### 1. Remove Duplicates from `.devin/README.md`
- Keep: Overview, structure, inventory, usage summary
- Remove: Detailed self-improvement details (link to SKILL_ACTIVATION_SYSTEM.md)
- Remove: Detailed automatic task completion details (link to automatic-task-completion.md)

### 2. Remove Duplicates from `.devin/SKILL_ACTIVATION_SYSTEM.md`
- Keep: Activation rules, loading order, self-improvement system, automatic task completion summary
- Remove: Detailed workflow steps (link to automatic-task-completion.md)
- Remove: Detailed skill improvement process (link to skill-improvement-process.md)

### 3. Remove Duplicates from `.devin/workflows/ai-ide-automation.md`
- Keep: High-level overview, stages, coordination, quality gates
- Remove: Detailed self-improvement system (link to SKILL_ACTIVATION_SYSTEM.md)
- Remove: Detailed automatic task completion (link to automatic-task-completion.md)

### 4. Remove Duplicates from `docs/rebuilt-1-1/automatic-processes.md`
- Keep: Summary-level information for 1:1 rebuild context
- Remove: Detailed implementation (link to primary sources)
- Remove: Detailed workflow steps (link to automatic-task-completion.md)

### 5. Remove Duplicates from `docs/skill-improvement-process.md`
- Keep: Detailed process documentation
- Remove: Duplicate skill activation rules (link to SKILL_ACTIVATION_SYSTEM.md)
- Remove: Duplicate workflow details (link to automatic-task-completion.md)

## Validation Checklist

After cleanup:
- [ ] Each piece of information has one primary source
- [ ] Secondary sources link to primary sources
- [ ] No duplicate detailed information
- [ ] Cross-references are consistent
- [ ] Documentation is navigable
- [ ] Information is easy to find
- [ ] No orphaned information
- [ ] All related documentation is linked

## Maintenance

When updating documentation:
1. Identify the primary source for the information
2. Update the primary source
3. Update secondary references if needed
4. Verify cross-references are still valid
5. Check for new duplicates created

## Related Documentation

- `.devin/README.md` - Main entry point
- `.devin/SKILL_ACTIVATION_SYSTEM.md` - Skill activation system
- `.devin/SKILL_TEMPLATE.md` - Skill template
- `.devin/workflows/automatic-task-completion.md` - Automatic task completion
- `.devin/workflows/ai-ide-automation.md` - AI IDE automation
- `.devin/workflows/skill-batch-update.md` - Skill batch update
- `docs/skill-improvement-process.md` - Skill improvement process
- `docs/rebuilt-1-1/automatic-processes.md` - Automatic processes
