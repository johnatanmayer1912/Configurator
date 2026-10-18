---
name: Programming Skill
description: Engineering best practices, secure defaults, clean logic structures, unit testing, and software engineering principles.
---
# Programming Skill

Software engineering and code quality guidelines.

## Rules
1. **DRY (Don't Repeat Yourself)**: Extract reusable utilities (e.g. timestamp parsers or command regex filters).
2. **Defensive Coding**: Check inputs for None/null values, handle encoding faults, and define clear fallback defaults.
3. **Automated Testing**: Write regression test suites mocking all network IO boundaries to guarantee offline-build stability.

## Core Principles
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones
- **YAGNI (You Aren't Gonna Need It)**: Don't build features until they're needed
- **Separation of Concerns**: Keep different aspects of the program separate
- **Modularity**: Design with small, independent, reusable components

## Code Quality
- **Readability**: Code should be self-documenting with clear variable names
- **Consistency**: Follow consistent coding style throughout the project
- **Comments**: Comment "why" not "what" - code should explain itself
- **Refactoring**: Regularly refactor to improve code quality
- **Code Reviews**: All code should go through peer review

## Security
- **Input Validation**: Always validate and sanitize user inputs
- **Output Encoding**: Encode outputs to prevent injection attacks
- **Least Privilege**: Run with minimum required permissions
- **Secure Defaults**: Use secure defaults for all configurations
- **Error Handling**: Don't expose sensitive information in error messages

## Performance
- **Algorithm Efficiency**: Choose appropriate algorithms for the problem
- **Memory Management**: Be mindful of memory usage and leaks
- **Caching**: Cache expensive operations when appropriate
- **Lazy Loading**: Load resources only when needed
- **Profiling**: Profile code to identify bottlenecks

## Testing
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test how components work together
- **End-to-End Tests**: Test complete user workflows
- **Test Coverage**: Aim for high test coverage (80%+)
- **Test Automation**: Automate tests as part of CI/CD pipeline

## Version Control
- **Git Best Practices**: Use meaningful commit messages
- **Branching Strategy**: Use appropriate branching (Git Flow, GitHub Flow, etc.)
- **Code Reviews**: Review all code before merging
- **Continuous Integration**: Automate builds and tests
- **Documentation**: Document API changes and breaking changes

## Documentation
- **API Documentation**: Document all public APIs
- **Code Comments**: Comment complex logic and algorithms
- **README**: Maintain clear project documentation
- **Changelog**: Track changes between versions
- **Architecture Docs**: Document system architecture and design decisions
