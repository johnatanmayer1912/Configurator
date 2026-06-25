---
description: Batch Skill Update Workflow - Systematic update of all skills with best practices and self-improvement capabilities
---

# Batch Skill Update Workflow

## Purpose

This workflow provides a systematic approach to update all 234 skills in the `.devin/skills/` directory with best practices for devin.ai usage and self-improvement capabilities.

## Update Strategy

### Priority Classification

#### High Priority Skills (Core Skills)
- `python-pro`
- `javascript-pro`
- `code-reviewer`
- `security-auditor`
- `backend-architect`
- `senior-architect`
- `cloud-architect`
- `database-admin`
- `database-architect`
- `network-engineer`
- `product-manager`
- `product-inventor`
- `api-design-principles`
- `deployment-engineer`
- `documentation-and-adrs`

**Update Schedule**: Weekly

#### Medium Priority Skills (Domain-Specific)
- All language-specific skills (golang-pro, java-pro, cpp-pro, etc.)
- All framework-specific skills (django-pro, fastapi-pro, react-best-practices, etc.)
- All cloud platform skills (aws-skills, azure-ai-projects-py, etc.)
- All database skills (postgresql, database-design, etc.)
- All security skills (backend-security-coder, frontend-security-coder, etc.)

**Update Schedule**: Bi-weekly

#### Low Priority Skills (Specialized)
- SEO skills
- Startup skills
- Game development skills
- Blockchain skills
- Embedded systems skills
- Reverse engineering skills
- Compliance skills
- Automation skills
- Workflow orchestration skills
- Functional programming skills
- Testing patterns skills
- Build systems skills
- Package management skills
- Temporal workflows skills
- Search skills
- Secrets management skills
- SLOs skills
- Screen reader skills
- Shell scripting skills
- SQL skills
- Spark skills
- Solidity skills
- SAST skills
- Shellcheck skills
- TDD skills
- Team collaboration skills
- Tutorial skills
- UI/UX skills
- Unit testing skills
- Validation skills
- Vector database skills
- WCAG skills
- Workflows skills

**Update Schedule**: Monthly

## Update Process

### Step 1: Skill Analysis
For each skill:
1. Read existing SKILL.md
2. Analyze current structure
3. Identify missing sections
4. Assess activation triggers
5. Review dependencies

### Step 2: Template Application
Apply the standard template from `.devin/SKILL_TEMPLATE.md`:
1. Add required metadata
2. Add self-improvement configuration
3. Add activation triggers
4. Add dependencies
5. Add priority

### Step 3: Best Practices Update
Update skill-specific best practices:
1. Research latest best practices
2. Update skill guidelines
3. Add new patterns
4. Remove outdated practices
5. Update examples

### Step 4: Self-Improvement Configuration
Configure self-improvement capabilities:
1. Enable periodic web search
2. Enable GitHub monitoring
3. Enable documentation tracking
4. Enable community learning
5. Enable self-validation

### Step 5: Automatic Actions Configuration
Configure automatic actions:
1. Documentation updates
2. Version management
3. QA checks
4. Build triggers
5. Release note generation

### Step 6: Validation
Validate the updated skill:
1. Test activation triggers
2. Test skill recommendations
3. Test skill integration
4. Test error handling
5. Test self-improvement

### Step 7: Deployment
Deploy the updated skill:
1. Commit changes
2. Update documentation
3. Update CHANGELOG
4. Bump version
5. Notify stakeholders

## Automation Script

### Python Script for Batch Updates

```python
import os
import json
from pathlib import Path

SKILLS_DIR = Path(".devin/skills/")
TEMPLATE_FILE = Path(".devin/SKILL_TEMPLATE.md")

def update_skill(skill_dir):
    """Update a single skill with best practices and self-improvement"""
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        print(f"Skipping {skill_dir.name} - no SKILL.md found")
        return
    
    # Read existing skill
    with open(skill_md, 'r') as f:
        existing_content = f.read()
    
    # Apply template updates
    # (Implementation details would go here)
    
    print(f"Updated {skill_dir.name}")

def batch_update_skills(priority="high"):
    """Batch update skills based on priority"""
    skills_dir = Path(".devin/skills/")
    
    # Define priority lists
    high_priority = [
        "python-pro", "javascript-pro", "code-reviewer", "security-auditor",
        "backend-architect", "senior-architect", "cloud-architect",
        "database-admin", "database-architect", "network-engineer",
        "product-manager", "product-inventor", "api-design-principles",
        "deployment-engineer", "documentation-and-adrs"
    ]
    
    medium_priority = [
        # Language skills
        "golang-pro", "java-pro", "cpp-pro", "csharp-pro", "typescript-pro",
        "ruby-pro", "rust-pro", "elixir-pro", "haskell-pro", "julia-pro", "php-pro",
        # Framework skills
        "django-pro", "fastapi-pro", "react-best-practices", "angular",
        # Cloud skills
        "aws-skills", "azure-ai-projects-py", "gcp-cloud-run",
        # Database skills
        "postgresql", "database-design",
        # Security skills
        "backend-security-coder", "frontend-security-coder"
    ]
    
    # Get all skill directories
    all_skills = [d for d in skills_dir.iterdir() if d.is_dir()]
    
    # Filter by priority
    if priority == "high":
        skills_to_update = [s for s in all_skills if s.name in high_priority]
    elif priority == "medium":
        skills_to_update = [s for s in all_skills if s.name in medium_priority]
    else:
        skills_to_update = all_skills
    
    # Update each skill
    for skill_dir in skills_to_update:
        update_skill(skill_dir)

if __name__ == "__main__":
    import sys
    
    priority = sys.argv[1] if len(sys.argv) > 1 else "high"
    batch_update_skills(priority)
```

## Update Checklist

For each skill, ensure:

- [ ] SKILL.md follows standard template
- [ ] Self-improvement is enabled
- [ ] Activation triggers are defined
- [ ] Dependencies are listed
- [ ] Priority is set
- [ ] Best practices are current
- [ ] Automatic actions are configured
- [ ] Error handling is robust
- [ ] Documentation is accurate
- [ ] Examples are provided (if applicable)

## Monitoring

Track:
- Number of skills updated
- Update success rate
- Time taken for updates
- Skill activation accuracy after updates
- User satisfaction with updated skills

## Rollback

If an update causes issues:
1. Identify problematic skill
2. Rollback to previous version
3. Log rollback reason
4. Investigate issue
5. Fix issue
6. Re-deploy fix

## Quality Assurance

### Pre-Update QA
- Backup existing skills
- Test update script on sample skills
- Validate template structure
- Review update checklist

### Post-Update QA
- Test skill activation
- Test skill recommendations
- Test skill integration
- Test self-improvement
- Validate documentation

## Documentation Updates

After batch updates:
1. Update `.devin/README.md` with updated skill count
2. Update `docs/skill-improvement-process.md` with update results
3. Update `docs/rebuilt-1-1/automatic-processes.md` with process changes
4. Update CHANGELOG with update summary

## Communication

Notify stakeholders of:
- Update schedule
- Update progress
- Update completion
- Any issues or rollbacks

## Related Documentation

- `.devin/SKILL_TEMPLATE.md` - Standard skill template
- `.devin/SKILL_ACTIVATION_SYSTEM.md` - Skill activation system
- `docs/skill-improvement-process.md` - Skill improvement process
- `.devin/workflows/automatic-task-completion.md` - Automatic task completion
