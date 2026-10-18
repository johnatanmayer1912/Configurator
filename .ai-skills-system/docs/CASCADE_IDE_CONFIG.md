# Cascade IDE Configuration Guide
**Version**: 1.0.0  
**Date**: 2026-08-06

## Overview

This guide provides step-by-step instructions for configuring Cascade IDE to use the AI Skills System.

## Configuration Steps

### Step 1: Open Cascade IDE Settings

1. Open Cascade IDE
2. Navigate to **Settings** (gear icon or Ctrl+,)
3. Locate the **Skills/Agents** configuration section

### Step 2: Add Skills System Path

1. In the Skills/Agents configuration section
2. Add the path to the AI Skills System folder:
   ```
   c:\Users\bbb12\OneDrive\Desktop\Antigravity Projects Folder\ACI-API\.ai-skills-system
   ```
3. Or relative path if in project root:
   ```
   .ai-skills-system
   ```

### Step 3: Enable Skill Activation

1. Find the **Skill Activation** setting
2. Set to **Enabled** or **True**
3. This allows skills to activate automatically based on context

### Step 4: Enable Skill Invocation

1. Find the **Skill Invocation** setting
2. Set to **Enabled** or **True**
3. This allows skills to invoke other skills dynamically

### Step 5: Enable Self-Improvement

1. Find the **Self-Improvement** setting
2. Set to **Enabled** or **True**
3. This allows skills to improve themselves using internet research

### Step 6: Configure Internet Access (Optional)

If you want skills to use internet for self-improvement:

1. Find the **Internet Access** setting
2. Set to **Enabled** or **True**
3. Configure rate limiting if needed (default: 100 requests/hour)

### Step 7: Save Configuration

1. Click **Save** or **Apply**
2. Restart Cascade IDE if required

## Configuration File

If Cascade IDE uses a configuration file, add this to your config:

```yaml
skills_config:
  path: ".ai-skills-system"
  auto_activation: true
  skill_invocation: true
  self_improvement: true
  internet_access: true
  
  activation_config:
    mode: automatic
    context_aware: true
    keyword_matching: true
    dependency_enforcement: true
    
  improvement_config:
    enabled: true
    internet_access: true
    automatic_triggers: true
```

## Verification

Test the configuration:

1. Open Cascade IDE
2. Start a new task related to one of the skills
3. Verify that the relevant skill activates automatically
4. Check that skills can invoke other skills
5. Verify that self-improvement is working (check logs)

## Troubleshooting

### Skills Not Activating

**Check**:
- Path is correct in configuration
- Skill activation is enabled
- Cascade IDE has permissions to access the folder

### Skill Invocation Failing

**Check**:
- Skill invocation is enabled
- Dependencies are satisfied
- Skills are registered in SKILL_REGISTRY.md

### Self-Improvement Not Working

**Check**:
- Self-improvement is enabled
- Internet access is enabled
- Skills have `auto_improve: true` in their metadata

## Advanced Configuration

### Custom Activation Triggers

You can customize activation triggers per skill:

```yaml
skill_config:
  python-pro:
    custom_triggers:
      - python
      - .py
      - pip
      - poetry
```

### Skill Priority Override

Override default skill priorities:

```yaml
skill_config:
  security-auditor:
    priority_override: 10
```

### Disable Specific Skills

Disable specific skills if needed:

```yaml
skill_config:
  elon-musk:
    enabled: false
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-08-06
