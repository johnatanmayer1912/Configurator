---
name: Python Skill
description: Python scripting standards, type-hinting, async operations, robust error handling, and best practices.
---
# Python Skill

Development guidelines for core backend services and platform scripts.

## Standards
1. **Type Safety**: Use annotations (`Dict[str, Any]`, `List[str]`, etc.) to enhance code legibility.
2. **Error Isolation**: Never allow a secondary task (like fetching environmental stats or compressed logs) to crash the primary application flow. Wrap blocks in specific `try-except` statements.
3. **Regex Robustness**: Pre-compile regular expressions and handle potentially missing groups gracefully.
4. **PEP 8 Compliance**: Follow PEP 8 style guide for Python code.
5. **Type Hints**: Use typing module for all public APIs and functions.
6. **Context Managers**: Use `with` statements for resource management (files, connections, etc.).
7. **No Mutable Defaults**: Avoid mutable default arguments in function definitions.
8. **DRY Principle**: Don't Repeat Yourself - extract common logic into functions.
9. **Logging**: Use `logging` module instead of `print` statements.
10. **Async/Await**: Use async/await for I/O-bound operations when beneficial.

## Code Quality
- **Functions**: Keep functions small and focused (single responsibility principle)
- **Naming**: Use snake_case for variables, functions, and modules
- **Docstrings**: Use Google-style docstrings for functions, classes, and modules
- **Imports**: Group imports at the top of the file (standard library, third-party, local)
- **Testing**: Use pytest for testing with minimum 80% coverage

## Error Handling
- **Specific Exceptions**: Catch specific exception types, not bare `except`
- **Early Validation**: Validate inputs at function entry
- **Proper Messages**: Provide clear, actionable error messages
- **Logging Errors**: Log errors with context using structured logging

## Performance
- **List Comprehensions**: Prefer over loops when appropriate
- **Generators**: Use for memory efficiency with large datasets
- **String Formatting**: Use f-strings for string formatting
- **Set Lookups**: Use sets for O(1) membership testing

## Dependencies
- **Virtual Environments**: Always use virtual environments
- **pyproject.toml**: Define all dependencies in pyproject.toml
- **Version Pinning**: Pin critical dependencies for reproducibility
