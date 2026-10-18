---
name: qa-deep
description: Create comprehensive test suites with unit tests, integration tests, edge cases, vPC pair testing, multi-switch path testing
triggers: ["test", "testing", "qa", "coverage", "vpc", "multi-switch"]
allowed-tools: read_file write_to_file bash
---

# Deep QA Testing

1. Write tests before or with implementation. TDD preferred. No exceptions.
2. Aim for 80%+ coverage. Critical paths must be tested.
3. Write unit tests for functions. Integration tests for modules. E2E tests for flows.
4. Tests must be independent. No shared state between tests.
5. Mock external dependencies. Tests must be deterministic.
6. Test edge cases: boundaries, null inputs, empty arrays, error conditions.
7. Test vPC pairs: validate keepalive, peer-link, role priority.
8. Test multi-switch paths: scenario → intent → enrich → validate → render.
9. Use descriptive test names. Clear failure messages.
10. If the current task needs deeper help in another area, immediately invoke the matching skill before continuing.
