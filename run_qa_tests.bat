@echo off
REM NX-OS Configuration Authority - Automated QA Test Runner
REM Run this script after any code changes to ensure functionality

echo ========================================
echo Running Automated QA Tests
echo ========================================
echo.

REM Run mandatory tests
echo [1/9] Running mandatory tests...
python -m pytest tests/mandatory/ -v -m mandatory
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Mandatory tests failed
    exit /b 1
)
echo PASSED: Mandatory tests
echo.

REM Run port matrix bugfix tests (v6.20.0 fixes)
echo [2/9] Running port matrix bugfix tests...
python -m pytest tests/mandatory/test_port_matrix_bugfixes.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Port matrix bugfix tests failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: Port matrix bugfix tests
echo.

REM Run multi-switch bugfix tests (v6.21.0 fixes)
echo [3/9] Running multi-switch bugfix tests...
python -m pytest tests/mandatory/test_multiswitch_bugfixes.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Multi-switch bugfix tests failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: Multi-switch bugfix tests
echo.

REM Run network architecture multi-switch test
echo [4/9] Running network architecture multi-switch test...
python -m pytest tests/mandatory/test_network_architecture_multiswitch.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Network architecture test failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: Network architecture test
echo.

REM Run multi-switch e2e tests (v6.22.0 fixes)
echo [5/9] Running multi-switch e2e tests...
python -m pytest tests/mandatory/test_multiswitch_e2e.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Multi-switch e2e tests failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: Multi-switch e2e tests
echo.

REM Run custom uplinks tests (v6.23.0 fixes)
echo [6/9] Running custom uplinks tests...
python -m pytest tests/mandatory/test_custom_uplinks.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Custom uplinks tests failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: Custom uplinks tests
echo.

REM Run network architecture tests (v6.24.0 fixes)
echo [7/9] Running network architecture tests...
python -m pytest tests/mandatory/test_network_architecture.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Network architecture tests failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: Network architecture tests
echo.

REM Run QA fixes tests (v6.25.0 fixes)
echo [8/9] Running QA fixes tests...
python -m pytest tests/mandatory/test_qa_fixes.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: QA fixes tests failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: QA fixes tests
echo.

REM Run port mapping validation test (mandatory for all builds)
echo [9/10] Running port mapping validation test...
python -m pytest tests/test_port_mapping_validation.py -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Port mapping validation test failed - CRITICAL for deployment
    exit /b 1
)
echo PASSED: Port mapping validation test
echo.

REM Run all tests
echo [10/10] Running full test suite...
python -m pytest tests/ -v
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Full test suite failed
    exit /b 1
)
echo PASSED: Full test suite
echo.

echo ========================================
echo All QA Tests PASSED
echo ========================================
exit /b 0
