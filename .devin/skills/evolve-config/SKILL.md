---
name: evolve-config
description: Improve the .devin configuration over time by detecting better practices and keeping it lean
triggers: ["evolve", "improve-config", "update-config", "optimize-config"]
allowed-tools: read_file write_to_file edit list_dir find_by_name
---

# Evolve .devin Configuration

1. Scan the .devin folder structure.
2. Analyze each file for relevance to programming excellence.
3. Check auto-activation effectiveness.
4. Check connection to other files.
5. Check for redundancy or bloat.
6. Identify improvements: missing capabilities, outdated practices, weak triggers, unused files.
7. Update files to incorporate best practices: tighten triggers, strengthen connections, improve clarity, remove unnecessary content.
8. Keep the folder lean: delete files without clear purpose, merge overlapping rules, consolidate similar skills.
9. Before any change: verify the change improves programming outcomes, ensure auto-activation still works, confirm connections remain intact.
10. After changes: test with sample prompts, verify all skills still invoke correctly, confirm folder remains minimal.
11. This skill can be invoked by the model when it detects configuration improvements are needed.
