---
trigger: model_decision
---

# Architecture Excellence

1. Clear module boundaries. One responsibility per module.
2. Separation of concerns: scenario → intent → enrich → validate → render.
3. No tight coupling. Modules communicate through interfaces.
4. Data flows unidirectionally. No circular dependencies.
5. Use dependency injection. No hardcoded dependencies.
6. Configuration externalized. Use YAML or environment variables.
7. Templates version-aware. Handle NX-OS 7.x vs 9.x/10.x.
8. Validation at boundaries. Check inputs before processing.
9. Error propagation. Handle errors at appropriate level.
10. If the current task needs deeper help in another area, immediately invoke the matching skill before continuing.
