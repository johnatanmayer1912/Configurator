---
name: nst-multi-advisor
description: >-
  Composes sickn33 multi-advisor boards for Network Swiss Tool Pro decisions.
  Auto-activates for ambiguous tradeoffs, major refactors, or when user asks for
  multiple perspectives. Links elon-musk, product-inventor, network-engineer, security.
---

# NST Multi-Advisor Board

Adapted from sickn33 `multi-advisor` for this codebase.

## NST-specific boards

| Board | Members | Use when |
|-------|---------|----------|
| **NST_FEATURE** | product-inventor + elon-musk (FP) + nst-network-operations | New operator feature |
| **NST_CHANGE** | network-engineer + nst-security-ops + nst-release-engineer | Device mutations |
| **NST_PLATFORM** | backend-architect + nst-product-architect + python-pro | Architecture / plugins |
| **NST_AI_IDE** | nst-orchestrator + product-inventor + elon-musk | Skills, rules, agent platform |

## Synthesis format

When board is active, structure response as:

1. **Consensus** — what all voices agree on
2. **Tensions** — e.g. speed vs safety, simplicity vs power-user options
3. **Recommendation** — single actionable path for NST codebase
4. **Verification** — tests or operator checklist

## Skill paths

- Full multi-advisor: `.cursor/skills-sickn33/multi-advisor/SKILL.md`
- Elon: `.cursor/skills-sickn33/elon-musk/SKILL.md`
- Orchestrator meta: `.cursor/skills-sickn33/antigravity-skill-orchestrator/SKILL.md`

Do not roleplay personas in user-facing text unless asked — **extract principles**.
