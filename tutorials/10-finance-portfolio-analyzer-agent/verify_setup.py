#!/usr/bin/env python3
"""
Setup Verification Script

Run this script to verify your Finance Portfolio Analyzer installation.
"""

import os
import sys


def main():
    print("🔍 Verifying Finance Portfolio Analyzer Setup...\n")

    # Check for .env in repository root (two levels up)
    repo_env = os.path.join("..", "..", ".env")

    checks = {
        "Python version >= 3.10": sys.version_info >= (3, 10),
        "Repository .env file exists": os.path.exists(repo_env),
        "agent.py exists": os.path.exists("src/agent.py"),
        "agent_memory.py exists": os.path.exists("src/agent_memory.py"),
        "main.py exists": os.path.exists("main.py"),
        "portfolio skill exists": os.path.exists(".claude/skills/portfolio-analysis/SKILL.md"),
        "excel skill exists": os.path.exists(".claude/skills/excel-reporting/SKILL.md"),
        "benchmarks context exists": os.path.exists(".claude/skills/portfolio-analysis/context/benchmarks.md"),
        "sample data exists": os.path.exists("data/sample_portfolio.csv"),
        "MCP config exists": os.path.exists("mcp_config.json"),
        "MCP server exists": os.path.exists("mcp-servers/stock-data/server.py"),
        "tests exist": os.path.exists("tests/test_agent.py"),
    }

    # Test dependencies
    try:
        from dotenv import load_dotenv
        checks["python-dotenv installed"] = True
        load_dotenv()
        checks["API key set"] = bool(os.getenv("ANTHROPIC_API_KEY"))
    except ImportError:
        checks["python-dotenv installed"] = False
        checks["API key set"] = False

    try:
        import anthropic
        checks["anthropic installed"] = True
    except ImportError:
        checks["anthropic installed"] = False

    try:
        import pandas
        checks["pandas installed"] = True
    except ImportError:
        checks["pandas installed"] = False

    try:
        import openpyxl
        checks["openpyxl installed"] = True
    except ImportError:
        checks["openpyxl installed"] = False

    try:
        import pytest
        checks["pytest installed"] = True
    except ImportError:
        checks["pytest installed"] = False

    # Print results
    passed = 0
    failed = 0

    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n📊 Results: {passed}/{len(checks)} checks passed")

    if failed == 0:
        print("\n🎉 All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Try: 'I'm a conservative investor focused on retirement'")
        print("3. Try: 'Analyze data/sample_portfolio.csv'")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        if not checks.get("python-dotenv installed"):
            print("- Install dependencies: pip install -r requirements.txt")
        if not checks.get("API key set"):
            print("- Add ANTHROPIC_API_KEY to repository root .env file (../../.env)")
        if not checks.get("Repository .env file exists"):
            print("- Create .env file in repository root with: ANTHROPIC_API_KEY=your_key_here")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
