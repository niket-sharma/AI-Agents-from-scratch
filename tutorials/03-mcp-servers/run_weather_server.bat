@echo off
REM Weather MCP Server Launcher for Windows

echo ========================================
echo Starting Weather MCP Server
echo ========================================
echo.

REM Go to project root and activate venv
cd /d "%~dp0..\.."
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [Virtual environment activated]
    echo.
)

echo Press Ctrl+C to stop the server
echo.

REM Run the server
python tutorials\03-mcp-servers\tools\weather_mcp_server.py

pause
