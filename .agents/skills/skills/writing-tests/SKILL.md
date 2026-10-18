---
name: writing-tests
description: Analyze existing code and write comprehensive unit and integration tests for it. Detects the test framework, identifies untested code paths, and generates tests with proper mocking, edge cases, and assertions. Use when the user asks to add tests, improve coverage, or test a specific module.
---

# Writing Tests (Python Adapted for NLAP)

Use this skill when the user asks to add tests to existing code, improve test coverage, or write tests for a specific file or module in the Network Log Analysis Platform.

## Steps

1. **Detect the test setup** — check what's already configured:

   ```bash
   # Check for test configuration files
   ls -la | grep -E "pytest|unittest|setup.py|pyproject.toml|requirements.txt"
   ```

   Look for config files: `pytest.ini`, `setup.cfg`, `pyproject.toml`, `tox.ini`. Check for existing test files to understand the project's test patterns and conventions.

2. **If no test runner exists** — set one up:

   ```bash
   pip install pytest pytest-cov pytest-mock
   ```

   Add a test script to project configuration:
   
   ```toml
   # pyproject.toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = ["test_*.py"]
   python_classes = ["Test*"]
   python_functions = ["test_*"]
   ```

3. **Analyze the target code** — read the file(s) to test and identify:
   - **Public API**: exported functions, classes, methods
   - **Code paths**: conditionals, error handling, edge cases
   - **Dependencies**: external services, databases, APIs that need mocking
   - **Side effects**: file I/O, network calls, device interactions

4. **Create the test file** — place it next to the source file or in a `tests/` directory, matching the project's convention:

   - `modules/analysis/network_incident_story.py` → `tests/test_network_incident_story.py`
   - `modules/investigation/log_collectors.py` → `tests/test_log_collectors.py`

5. **Write tests following this structure**:

   ```python
   import pytest
   from unittest.mock import Mock, patch
   from modules.analysis.network_incident_story import IncidentStoryGenerator

   class TestIncidentStoryGenerator:
       # Happy path
       def test_generates_story_for_valid_logs(self):
           generator = IncidentStoryGenerator()
           logs = [...]
           story = generator.generate_story(logs)
           assert story is not None
           assert "title" in story
       
       # Edge cases
       def test_handles_empty_log_list(self):
           generator = IncidentStoryGenerator()
           story = generator.generate_story([])
           assert story is not None
           assert story["title"] == "No incident data"
       
       # Error cases
       def test_handles_malformed_logs(self):
           generator = IncidentStoryGenerator()
           malformed_logs = [...]
           story = generator.generate_story(malformed_logs)
           assert story is not None
           assert "error" in story.lower()
       
       # Boundary conditions
       def test_handles_large_log_volume(self):
           generator = IncidentStoryGenerator()
           large_logs = [...] * 1000
           story = generator.generate_story(large_logs)
           assert story is not None
   ```

6. **Mock external dependencies** — don't make real API calls or database queries in unit tests:

   ```python
   from unittest.mock import Mock, patch
   
   @patch('modules.investigation.log_collectors.NetmikoConnector')
   def test_collects_logs_with_mock_connector(self, mock_connector):
       mock_instance = Mock()
       mock_connector.return_value = mock_instance
       mock_instance.get_logs.return_value = ["log1", "log2"]
       
       from modules.investigation.log_collectors import LogCollector
       collector = LogCollector()
       logs = collector.collect_logs("device1")
       
       assert len(logs) == 2
       mock_instance.get_logs.assert_called_once()
   ```

   For network device interactions, mock the device connections:

   ```python
   @patch('modules.f5.f5_device.F5Device')
   def test_analyzes_f5_config_with_mock(self, mock_device):
       mock_instance = Mock()
       mock_device.return_value = mock_instance
       mock_instance.get_config.return_value = "config data"
       
       from modules.f5.f5_analyzer import F5ConfigAnalyzer
       analyzer = F5ConfigAnalyzer()
       result = analyzer.analyze_config("bigip1")
       
       assert "analysis" in result
       mock_instance.get_config.assert_called_once()
   ```

7. **Test network operations** with proper mocking:

   ```python
   def test_parses_cisco_logs(self):
       from modules.parsers.cisco_parser import CiscoLogParser
       parser = CiscoLogParser()
       
       log_sample = "Jun 14 14:30:15 router1: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up"
       result = parser.parse(log_sample)
       
       assert result is not None
       assert result["interface"] == "GigabitEthernet0/1"
       assert result["state"] == "up"
       assert result["timestamp"] is not None
   ```

8. **Run the tests** and verify they pass:

   ```bash
   pytest tests/
   ```

   If any fail, fix the test or the code (depending on whether the test expectation or the implementation is wrong).

## What to Test

- **Always test**: public API, error handling, edge cases (empty, null, zero, negative), state transitions, async behavior, network device parsing
- **Skip testing**: private implementation details, third-party library internals, simple getters/setters, type-only code

## NLAP-Specific Testing Focus

- **Network device parsing**: Test log parsing from different vendors (Cisco, Juniper, F5)
- **File operations**: Test log file reading and processing
- **Configuration translation**: Test config parsing and conversion
- **Incident story generation**: Test incident narrative generation
- **Multi-vendor compatibility**: Test vendor-specific parsing logic
- **Offline operation**: Ensure tests work without network dependencies

## Notes

- Match the project's existing test style — if they use `unittest` instead of `pytest`, follow that
- Don't test implementation details — test behavior and outputs, not internal method calls
- Use descriptive test names that explain the scenario: "returns 0 when cart is empty" not "test1"
- One assertion concept per test — multiple `assert` calls are fine if they verify the same behavior
- For async code, always `await` the result or use `async` test functions
- Use fixtures (pytest fixtures) for common test setup
- Mock network device connections to avoid dependency on actual hardware
- Test with realistic sample data when possible