#!/usr/bin/env python3
"""
Agent as Tool Example
=====================

This example demonstrates wrapping agents as tools that can be called by
a parent agent, enabling modular agent composition.

Key Concepts:
- Using SubagentTool to wrap agents as callable tools
- Parent agent deciding when to use specialist subagents
- Tool-like interface for subagent invocation
- Building composable agent systems

Usage:
    python agent_as_tool.py
    python agent_as_tool.py --interactive  # Interactive mode

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install openai python-dotenv
"""

import json
import os
import re
import sys
from typing import Dict, List

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from openai import OpenAI

from src.agent import BaseAgent
from src.tools import BaseTool, SubagentTool, ToolResult

load_dotenv()


def create_specialist_agents(client: OpenAI) -> Dict[str, SubagentTool]:
    """
    Create a set of specialist agents wrapped as tools.
    
    Returns:
        Dictionary mapping tool names to SubagentTools
    """
    
    # Code Review Specialist
    code_reviewer = BaseAgent(
        system_prompt="""You are a Code Review Specialist.

Your expertise:
- Identifying bugs and potential issues
- Suggesting improvements for code quality
- Checking for security vulnerabilities
- Reviewing code style and best practices

When reviewing code:
1. List any bugs or issues found
2. Suggest specific improvements
3. Rate the overall code quality (1-10)
4. Provide actionable feedback""",
        model="gpt-4o-mini",
        temperature=0.2,
        client=client,
    )
    
    # Documentation Specialist
    doc_writer = BaseAgent(
        system_prompt="""You are a Documentation Specialist.

Your expertise:
- Writing clear, concise documentation
- Creating docstrings and comments
- Explaining complex concepts simply
- Following documentation best practices

When documenting:
1. Use clear, simple language
2. Include examples where helpful
3. Follow the appropriate format (docstrings, README, etc.)
4. Make documentation actionable""",
        model="gpt-4o-mini",
        temperature=0.3,
        client=client,
    )
    
    # Testing Specialist
    test_writer = BaseAgent(
        system_prompt="""You are a Testing Specialist.

Your expertise:
- Writing unit tests
- Designing test cases
- Identifying edge cases
- Test-driven development

When creating tests:
1. Cover happy path and edge cases
2. Use descriptive test names
3. Follow testing best practices
4. Include setup and teardown when needed""",
        model="gpt-4o-mini",
        temperature=0.2,
        client=client,
    )
    
    # Wrap each agent as a tool
    tools = {
        "code_review": SubagentTool(
            agent=code_reviewer,
            name="code_review",
            description="Review code for bugs, issues, and improvements. Input: code snippet or description of code to review.",
        ),
        "documentation": SubagentTool(
            agent=doc_writer,
            name="documentation",
            description="Write documentation, docstrings, or explanations. Input: code or concept to document.",
        ),
        "testing": SubagentTool(
            agent=test_writer,
            name="testing",
            description="Create unit tests and test cases. Input: code or functionality to test.",
        ),
    }
    
    return tools


class OrchestratorAgent:
    """
    An orchestrator that uses specialist subagents as tools.
    
    This demonstrates the "agent as tool" pattern where the orchestrator
    can choose which specialist to invoke based on the task.
    """
    
    def __init__(self, client: OpenAI, tools: Dict[str, SubagentTool]):
        self.client = client
        self.tools = tools
        
        # Build tool descriptions for the orchestrator
        tool_list = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in tools.items()
        ])
        
        self.agent = BaseAgent(
            system_prompt=f"""You are a Development Team Orchestrator.

You have access to specialist agents that you can delegate tasks to:

{tool_list}

When given a task:
1. Analyze what needs to be done
2. Decide which specialist(s) to use
3. Format your delegation as: DELEGATE[tool_name]: <task for that specialist>
4. You can delegate to multiple specialists
5. After receiving results, synthesize them into a final response

Example delegation:
DELEGATE[code_review]: Review this Python function for bugs
DELEGATE[documentation]: Write a docstring for this function

If no specialist is needed, respond directly.""",
            model="gpt-4o-mini",
            temperature=0.3,
            client=client,
        )
    
    def _extract_delegations(self, response: str) -> List[tuple]:
        """Extract delegation requests from response."""
        pattern = r'DELEGATE\[(\w+)\]:\s*(.+?)(?=DELEGATE\[|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        return [(tool.strip(), task.strip()) for tool, task in matches]
    
    def process(self, user_request: str, verbose: bool = True) -> str:
        """
        Process a user request, delegating to specialists as needed.
        
        Args:
            user_request: The user's task or question
            verbose: Whether to print progress
            
        Returns:
            Final synthesized response
        """
        if verbose:
            print(f"\n📝 User Request: {user_request}")
            print("-" * 50)
        
        # Get orchestrator's initial analysis
        response = self.agent.complete(user_request)
        
        # Check for delegations
        delegations = self._extract_delegations(response)
        
        if not delegations:
            # No delegation needed
            if verbose:
                print("✓ Handled directly (no delegation)")
            return response
        
        # Execute delegations
        results = {}
        for tool_name, task in delegations:
            if tool_name not in self.tools:
                if verbose:
                    print(f"⚠️  Unknown tool: {tool_name}")
                continue
            
            if verbose:
                print(f"\n🔧 Delegating to {tool_name}...")
                print(f"   Task: {task[:60]}...")
            
            tool = self.tools[tool_name]
            result = tool.run(task)
            results[tool_name] = result.content
            
            if verbose:
                print(f"   ✓ {tool_name} completed")
        
        # Synthesize results
        if verbose:
            print("\n🔄 Synthesizing results...")
        
        synthesis_prompt = f"""
Original request: {user_request}

Specialist results:
{json.dumps(results, indent=2)}

Please synthesize these results into a cohesive final response."""
        
        final_response = self.agent.complete(synthesis_prompt)
        
        return final_response


def run_agent_as_tool_demo():
    """Demonstrate the agent-as-tool pattern."""
    
    print("=" * 60)
    print("Agent as Tool Demo")
    print("=" * 60)
    print()
    print("This demo shows an orchestrator using specialist agents as tools.")
    print()
    
    client = OpenAI()
    
    # Create specialist tools
    print("📦 Creating specialist agents...")
    tools = create_specialist_agents(client)
    for name in tools:
        print(f"   ✓ {name} specialist ready")
    print()
    
    # Create orchestrator
    orchestrator = OrchestratorAgent(client=client, tools=tools)
    
    # Example code to work with
    sample_code = '''
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)
'''
    
    # Task 1: Code review
    print("=" * 60)
    print("Task 1: Code Review")
    print("=" * 60)
    
    result = orchestrator.process(
        f"Please review this code and suggest improvements:\n{sample_code}"
    )
    print("\n📋 Final Result:")
    print(result)
    
    # Task 2: Documentation
    print("\n" + "=" * 60)
    print("Task 2: Documentation")
    print("=" * 60)
    
    result = orchestrator.process(
        f"Please write comprehensive documentation for this function:\n{sample_code}"
    )
    print("\n📋 Final Result:")
    print(result)
    
    # Task 3: Multiple specialists
    print("\n" + "=" * 60)
    print("Task 3: Full Code Analysis (Multiple Specialists)")
    print("=" * 60)
    
    result = orchestrator.process(
        f"""Please do a complete analysis of this code:
{sample_code}

I need:
1. A code review with improvement suggestions
2. Documentation/docstrings
3. Unit tests"""
    )
    print("\n📋 Final Result:")
    print(result)


def run_interactive_demo():
    """Run an interactive session with the orchestrator."""
    
    print("=" * 60)
    print("Interactive Agent-as-Tool Demo")
    print("=" * 60)
    print()
    print("Ask the orchestrator to help with code tasks.")
    print("It will delegate to specialists as needed.")
    print("Type 'quit' to exit.")
    print()
    
    client = OpenAI()
    tools = create_specialist_agents(client)
    orchestrator = OrchestratorAgent(client=client, tools=tools)
    
    print(f"Available specialists: {', '.join(tools.keys())}")
    print("-" * 60)
    
    while True:
        try:
            print()
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            if not user_input:
                continue
            
            result = orchestrator.process(user_input)
            print("\n🤖 Result:")
            print(result)
            
        except KeyboardInterrupt:
            break
    
    print("\n👋 Goodbye!")


def demonstrate_tool_chaining():
    """Show how tools can be chained together."""
    
    print("=" * 60)
    print("Tool Chaining Demo")
    print("=" * 60)
    print()
    print("This shows chaining: Code Review → Fix → Test")
    print()
    
    client = OpenAI()
    tools = create_specialist_agents(client)
    
    # Add a fixer agent
    fixer = BaseAgent(
        system_prompt="""You are a Code Fixer. Given code and review feedback,
you produce corrected code that addresses all issues.""",
        client=client,
    )
    fixer_tool = SubagentTool(
        agent=fixer,
        name="code_fixer",
        description="Fix code based on review feedback",
    )
    tools["code_fixer"] = fixer_tool
    
    # Buggy code
    buggy_code = '''
def divide_numbers(a, b):
    return a / b

def get_first_item(lst):
    return lst[0]
'''
    
    print(f"Original buggy code:\n{buggy_code}")
    print("-" * 50)
    
    # Step 1: Review
    print("\n🔍 Step 1: Code Review")
    review_result = tools["code_review"].run(f"Review this code for bugs:\n{buggy_code}")
    print(review_result.content)
    
    # Step 2: Fix
    print("\n🔧 Step 2: Apply Fixes")
    fix_result = tools["code_fixer"].run(
        f"Original code:\n{buggy_code}\n\nReview feedback:\n{review_result.content}\n\n"
        "Please provide the corrected code."
    )
    print(fix_result.content)
    
    # Step 3: Test
    print("\n🧪 Step 3: Create Tests")
    test_result = tools["testing"].run(
        f"Create unit tests for this code:\n{fix_result.content}"
    )
    print(test_result.content)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent as Tool Demo")
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run interactive mode"
    )
    parser.add_argument(
        "--chain", "-c",
        action="store_true",
        help="Run tool chaining demo"
    )
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_demo()
    elif args.chain:
        demonstrate_tool_chaining()
    else:
        run_agent_as_tool_demo()
