@echo off
REM Interactive Calculator - Test MCP Tools Without JSON-RPC

echo ========================================
echo Interactive Calculator Demo
echo ========================================
echo.
echo This lets you test the calculator tools
echo directly without needing MCP protocol!
echo.

REM Go to project root and activate venv
cd /d "%~dp0..\.."
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [Virtual environment activated]
    echo.
)

REM Run the interactive calculator
python tutorials\03-mcp-servers\interactive_calculator.py

pause
