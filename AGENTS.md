# AGENTS.md - Canonical Programming Excellence

This file defines the always-on agents that enforce world-class programming standards across all tools and contexts.

## Core Principles

1. **Correctness First**: Code must work correctly before any optimization.
2. **Security Non-Negotiable**: Validate all inputs. Never trust user data.
3. **Test Mandatory**: No code without tests. No exceptions.
4. **Simplicity Wins**: Simple solutions beat complex ones every time.
5. **Performance Measured**: Profile before optimizing. Measure impact.
6. **Maintainability**: Code is read more than written. Make it clear.

## Agent Behaviors

### Before Any Code Change
- Read existing code to understand context
- Check if relevant skills should be invoked
- Verify the change aligns with global rules
- Consider security implications

### While Coding
- Follow global rules at all times
- Write clean, simple code
- Add tests with implementation
- Document intent, not mechanics

### After Coding
- Run tests and ensure they pass
- Review changes for quality
- Check for security issues
- Verify performance is acceptable

### When Stuck
- Debug systematically
- Form hypotheses and test them
- Invoke debug-systematic skill
- Don't guess - verify

## Skill Invocation Protocol

Before any significant task, check if these skills should be invoked:
- **python-excellence**: When writing Python code
- **ui-ux-excellence**: When working on wizard or UI
- **architecture-review**: When reviewing module design
- **qa-deep**: When writing or verifying tests
- **nxos-config-excellence**: When generating NX-OS CLI
- **evolve-config**: When improving .devin configuration

## Non-Negotiable Standards

- Never skip tests
- Never commit broken code
- Never ignore security issues
- Never over-engineer solutions
- Always invoke relevant skills
- Always follow global rules
- Always measure before optimizing
- Always validate inputs
- Always handle errors gracefully

## Auto-Activation

These agents activate automatically on:
- Any code change request
- Any review request
- Any debugging request
- Any optimization request
- Vague prompts like "fix this", "add X", "make better"

## Evolution

This AGENTS.md file evolves over time through the evolve-config skill to incorporate best practices and maintain relevance.
