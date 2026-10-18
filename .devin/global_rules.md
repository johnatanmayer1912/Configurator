---
trigger: always_on
---

# Global Rules - Always-On Programming Doctrine

1. Read existing code before modifying. Understand patterns. No assumptions.
2. Write clean code: descriptive names, functions ≤50 lines, single responsibility.
3. Test everything: write tests with implementation, cover edge cases, mock dependencies.
4. Security first: validate all inputs, never trust user data, use parameterized queries.
5. Performance matters: profile before optimizing, cache expensive operations, measure impact.
6. Document intent: comment WHY not WHAT, keep docs current, self-documenting code preferred.
7. Error handling: handle errors gracefully, provide actionable error messages, log with context.
8. Before finishing: verify code compiles/runs, run tests and ensure they pass, check for security vulnerabilities, confirm performance is acceptable.
9. Check if a skill should be invoked before any action. Invoke it immediately if needed.
10. If the current task needs deeper help in another area, immediately invoke the matching skill before continuing.
