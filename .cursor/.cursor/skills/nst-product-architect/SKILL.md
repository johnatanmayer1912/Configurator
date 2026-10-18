---
name: nst-product-architect
description: >-
  Product and systems architecture for Network Swiss Tool Pro. Auto-activates for
  new features, UX overhauls, control plane, skill platform, and strategic tradeoffs.
  Combines product-inventor, elon-musk first principles, and backend-architect.
---

# NST Product Architect

## Mission

Ship tools the **network team loves** — fast, trustworthy, impossible to misuse accidentally.

## First principles (elon-musk lens — apply ideas, not persona roleplay)

1. **Question requirements** — "Must we add a modal, or can validation live inline?"
2. **Delete steps** — fewer clicks from inventory → validated → executed
3. **Optimize for operator time** — indicative HTML beats raw TXT for audits
4. **Fail loud early** — empty inventory, missing creds, zero devices in scope

## Product inventor lens

- Progressive disclosure: simple default, expert options collapsed
- Every feature: **input → progress → artifact path → summary in console**
- Consistency: same output folder contract across VLAN, search, topology, plugins

## Architecture lens

- Plugins: `modules/plugin_registry.py` — never break frozen EXE plugin bundle
- Threaded work: register in `utils/task_control_plane.py`
- Validation pipelines return same JSON shape (IM = VLAN = future plugins)

## When to convene PRODUCT_BOARD

Scope change, new tab, new operator workflow, or "make it user-friendly" → internally consult:

| Voice | Question |
|-------|----------|
| Product inventor | Is the happy path obvious? |
| Elon / first principles | What can we delete? |
| Steve Jobs (multi-advisor) | Is it simple and beautiful enough? |
| Network NOC | Will they trust this at night? |

## References

- `.cursor/skills-sickn33/product-inventor/SKILL.md`
- `.cursor/skills-sickn33/elon-musk/SKILL.md` (§ first principles, § When to Use)
- `.cursor/skills-sickn33/multi-advisor/SKILL.md` (PRODUCT_BOARD)
- `.cursor/skills-devin/product-manager/SKILL.md`
