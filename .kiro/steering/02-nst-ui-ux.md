---
inclusion: fileMatch
fileMatchPattern: ['modules/web/**/*.html', 'utils/*formatter*.py']
---

# UI/UX for Network Operators

- Sort interfaces naturally (Gi1/0/2 before Gi1/0/10); use table rows when lists exceed ~50 items
- Search results: rank exact matches first, then prefix, then partial; highlight matched substrings
- Validation pipelines must mirror Interface Manager (dry-run → syntax → platform → conflict → approval)
- Reports: HTML + TXT + manifest.json in `outputs/<category>/<date>/<run_id>/`
- Control plane: surface running tasks with stop affordance in the console sidebar

Reference: `.devin/skills/ui-ux-designer/SKILL.md`, `.devin/skills/product-inventor/SKILL.md`
