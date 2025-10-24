@echo off
REM Setup script for MCP Tutorial
REM This installs all required dependencies

echo =========================================================
echo MCP Tutorial - Setup Script
echo =========================================================
echo.
echo This script will:
echo 1. Activate the virtual environment
echo 2. Install the MCP package and dependencies
echo 3. Verify installation
echo.
echo =========================================================
echo.

REM Go to project root
cd /d "%~dp0..\.."

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run this from the project root:
    echo   python -m venv venv
    echo.
    pause
    exit /b 1
)

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Installing MCP package...
pip install mcp

echo.
echo Step 3: Verifying installation...
python -c "import mcp; print('MCP version:', mcp.__version__)" 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: MCP verification failed
    echo Trying alternative installation...
    pip install --upgrade mcp
    python -c "import mcp; print('MCP installed successfully!')"
) else (
    echo MCP installed successfully!
)

echo.
echo =========================================================
echo Setup Complete!
echo =========================================================
echo.
echo You can now run the MCP examples:
echo   run_calculator_server.bat
echo   run_weather_server.bat
echo   run_file_server.bat
echo.
echo Or run them manually:
echo   python tutorials\03-mcp-servers\basic\simple_mcp_server.py
echo.
echo =========================================================
echo.

pause
