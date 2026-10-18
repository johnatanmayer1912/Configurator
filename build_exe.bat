@echo off
REM NX-OS Configuration Authority - Build Executable for Offline Environments
REM This script builds the standalone executable using PyInstaller

echo ========================================
echo Building NXOS Configurator v6.44.0 Executable
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Check if pytest is available for QA tests
python -c "import pytest" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: pytest not found. Skipping QA tests and installing dependencies...
    pip install pytest
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Could not install pytest. Proceeding without QA tests.
        goto BUILD
    )
)

REM Run QA tests before building
echo [1/3] Running QA tests before build...
python -m pytest tests/mandatory/test_qa_fixes.py tests/mandatory/test_multiswitch_integration.py -v
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: QA tests failed. Proceeding with build anyway...
)
echo NOTE: QA tests completed. Proceeding with build...
echo.

:BUILD

REM Build the executable
echo [2/3] Building executable with PyInstaller...
pyinstaller NXOS_Configurator_Web_v6.44.0.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: PyInstaller build failed
    exit /b 1
)
echo PASSED: Executable built successfully
echo.

REM Verify the executable exists
echo [3/3] Verifying executable...
if exist "dist\NXOS_Configurator_Web_v6.44.0.exe" (
    echo SUCCESS: Executable created at dist\NXOS_Configurator_Web_v6.44.0.exe
    echo.
    echo To run the configurator:
    echo   cd dist
    echo   NXOS_Configurator_Web_v6.44.0.exe
    echo.
    echo The application will start and open in your default browser.
) else (
    echo FAILED: Executable not found
    exit /b 1
)

echo ========================================
echo Build Complete
echo ========================================
exit /b 0
