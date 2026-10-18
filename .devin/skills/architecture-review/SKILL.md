---
name: architecture-review
description: Review architecture for clear module boundaries, separation of concerns, maintainable design, no tight coupling
triggers: ["architecture", "design", "module", "coupling", "separation of concerns"]
allowed-tools: read_file grep_search
---

# Architecture Review

1. Check module boundaries. One responsibility per module. No ambiguity.
2. Verify separation of concerns: scenario → intent → enrich → validate → render.
3. Check for tight coupling. Modules must communicate through interfaces.
4. Verify data flows unidirectionally. No circular dependencies.
5. Check dependency injection. No hardcoded dependencies.
6. Verify configuration externalization. Use YAML or environment variables.
7. Check template version awareness. Handle NX-OS 7.x vs 9.x/10.x.
8. Verify validation at boundaries. Check inputs before processing.
9. Check error propagation. Handle errors at appropriate level.
10. If the current task needs deeper help in another area, immediately invoke the matching skill before continuing.
