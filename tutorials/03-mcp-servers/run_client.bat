@echo off
REM MCP Client Launcher for Windows
REM This script handles paths with spaces correctly

echo ========================================
echo MCP Client Launcher
echo ========================================
echo.

REM Go to project root and activate venv
cd /d "%~dp0..\.."
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [Virtual environment activated]
    echo.
)

REM Run the client
python tutorials\03-mcp-servers\client\mcp_client_example.py

pause
