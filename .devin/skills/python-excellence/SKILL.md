---
name: python-excellence
description: Write world-class Python code with type hints, clean functions, FastAPI patterns, error handling, pytest
triggers: ["python", "fastapi", "pydantic", "async", "type hints", "pytest"]
allowed-tools: read_file write_to_file edit bash
---

# Python Excellence

1. Use type hints on all function signatures. No exceptions.
2. Keep functions under 50 lines. Split longer functions immediately.
3. Use dataclasses for data structures. No raw dicts.
4. Use FastAPI patterns: Pydantic models for validation.
5. Handle errors with try/except. Never swallow exceptions.
6. Use async/await for I/O. Never block on network calls.
7. Use f-strings for formatting. No % or .format().
8. Use list comprehensions for simple transformations.
9. Import only what you use. Keep imports organized.
10. Write pytest tests with fixtures. Mock external dependencies.
11. If the current task needs deeper help in another area, immediately invoke the matching skill before continuing.
