"""
Comparison: CrewAI vs Custom Multi-Agent Implementation

This file demonstrates the same task implemented in two ways:
1. Using CrewAI framework
2. Using custom code from this repository

This helps you understand:
- What CrewAI abstracts away
- When to use a framework vs custom code
- Trade-offs between convenience and control
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================================================
# APPROACH 1: Using CrewAI Framework
# ============================================================================

def run_with_crewai():
    """
    Implement a research and writing task using CrewAI.
    """
    from crewai import Agent, Task, Crew, Process

    print("\n" + "="*80)
    print("APPROACH 1: Using CrewAI Framework")
    print("="*80 + "\n")

    # Create agents - Notice how simple this is
    researcher = Agent(
        role='Researcher',
        goal='Gather key information about AI agents',
        backstory='You are an expert at finding and summarizing information.',
        verbose=False,  # Reduce output for comparison
    )

    writer = Agent(
        role='Writer',
        goal='Create clear, concise content',
        backstory='You are a skilled technical writer.',
        verbose=False,
    )

    # Define tasks
    research_task = Task(
        description='Research the key benefits of AI agents in software development.',
        agent=researcher,
        expected_output='A list of 3-5 key benefits with brief explanations.',
    )

    writing_task = Task(
        description='Write a short paragraph summarizing the benefits of AI agents.',
        agent=writer,
        expected_output='A well-written paragraph (3-4 sentences).',
    )

    # Create crew and run
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()

    print("CrewAI Result:")
    print("-" * 80)
    print(result)
    print("\n" + "="*80 + "\n")

    return result


# ============================================================================
# APPROACH 2: Using Custom Implementation
# ============================================================================

def run_with_custom():
    """
    Implement the same task using custom code from this repository.
    """
    from src.agent import BaseAgent
    from src.memory import ConversationBufferMemory

    print("\n" + "="*80)
    print("APPROACH 2: Using Custom Implementation")
    print("="*80 + "\n")

    # Create agents - More manual setup required
    researcher = BaseAgent(
        system_prompt=(
            "You are an expert researcher. Your goal is to gather key information "
            "about AI agents. You are skilled at finding and summarizing information."
        ),
        memory=ConversationBufferMemory(max_messages=5),
        temperature=0.3,
    )

    writer = BaseAgent(
        system_prompt=(
            "You are a skilled technical writer. Your goal is to create clear, "
            "concise content. You excel at summarizing complex topics."
        ),
        memory=ConversationBufferMemory(max_messages=5),
        temperature=0.7,
    )

    # Execute tasks manually
    print("Step 1: Researcher gathering information...")
    research_result = researcher.complete(
        "Research the key benefits of AI agents in software development. "
        "Provide a list of 3-5 key benefits with brief explanations."
    )

    print(f"Research Result:\n{research_result}\n")
    print("-" * 80)

    print("\nStep 2: Writer creating summary...")
    writing_result = writer.complete(
        f"Based on this research, write a short paragraph (3-4 sentences) "
        f"summarizing the benefits of AI agents:\n\n{research_result}"
    )

    print(f"Writing Result:\n{writing_result}\n")
    print("="*80 + "\n")

    return writing_result


# ============================================================================
# Comparison Analysis
# ============================================================================

def print_comparison_analysis():
    """
    Print a detailed comparison of both approaches.
    """
    print("\n" + "="*80)
    print("COMPARISON ANALYSIS")
    print("="*80 + "\n")

    comparison = """
┌─────────────────────┬──────────────────────────┬──────────────────────────┐
│ Aspect              │ CrewAI                   │ Custom Implementation    │
├─────────────────────┼──────────────────────────┼──────────────────────────┤
│ Setup Complexity    │ ⭐⭐⭐⭐⭐ Very Simple      │ ⭐⭐⭐ Moderate            │
│ Code Lines          │ ~30 lines                │ ~50 lines                │
│ Abstraction Level   │ High (role-based)        │ Low (manual control)     │
│ Learning Curve      │ Gentle                   │ Steep (learn internals)  │
│ Flexibility         │ Medium                   │ Very High                │
│ Orchestration       │ Built-in                 │ Manual                   │
│ Tool Integration    │ Simple (@tool)           │ Manual (define classes)  │
│ Memory Management   │ Optional, built-in       │ Manual configuration     │
│ Error Handling      │ Framework handles some   │ Full control             │
│ Debugging           │ Can be opaque            │ Full visibility          │
│ Best For            │ Quick prototyping        │ Learning & custom needs  │
└─────────────────────┴──────────────────────────┴──────────────────────────┘

KEY INSIGHTS:

1. CODE SIMPLICITY
   - CrewAI: Declarative, role-based. Define roles, goals, tasks.
   - Custom: Imperative, procedural. Manually orchestrate each step.

2. ABSTRACTION
   - CrewAI: Agents are "roles" (researcher, writer, editor)
   - Custom: Agents are LLM wrappers with system prompts

3. TASK FLOW
   - CrewAI: Automatic task chaining and context passing
   - Custom: Manual result passing between agents

4. FLEXIBILITY
   - CrewAI: Great for standard patterns, less for custom logic
   - Custom: Full control, can implement any pattern

5. LEARNING VALUE
   - CrewAI: Learn multi-agent patterns quickly
   - Custom: Understand how agents work under the hood

WHEN TO USE EACH:

Use CrewAI when:
✓ Building a prototype quickly
✓ Using standard multi-agent patterns
✓ You want role-based agent semantics
✓ You need built-in orchestration
✓ You value convention over configuration

Use Custom Implementation when:
✓ Learning AI agent fundamentals
✓ Need full control over behavior
✓ Implementing novel agent patterns
✓ Building educational projects
✓ Debugging and understanding internals matter

HYBRID APPROACH:
Many teams use BOTH:
- Custom code for learning and understanding
- CrewAI for rapid production development
- Custom implementations for specialized agents
- CrewAI for standard multi-agent workflows
    """

    print(comparison)


# ============================================================================
# Main Function
# ============================================================================

def main():
    """
    Run both implementations and compare results.
    """
    print("\n" + "="*80)
    print("CrewAI vs Custom Implementation Comparison")
    print("="*80)
    print("\nThis demo runs the same task using two different approaches:")
    print("  1. CrewAI framework (high-level, declarative)")
    print("  2. Custom implementation (low-level, imperative)")
    print("\nTask: Research AI agents and write a summary\n")

    # Get user choice
    print("What would you like to do?")
    print("  1. Run with CrewAI only")
    print("  2. Run with Custom implementation only")
    print("  3. Run both and compare")
    print("  4. Show comparison analysis only")

    choice = input("\nEnter choice (1-4, or press Enter for 3): ").strip()

    if not choice:
        choice = "3"

    if choice == "1":
        run_with_crewai()
    elif choice == "2":
        run_with_custom()
    elif choice == "3":
        # Run both
        crewai_result = run_with_crewai()
        custom_result = run_with_custom()

        # Show side-by-side comparison
        print("\n" + "="*80)
        print("SIDE-BY-SIDE RESULTS")
        print("="*80 + "\n")
        print("CrewAI Result:")
        print("-" * 80)
        print(crewai_result)
        print("\n" + "-" * 80 + "\n")
        print("Custom Result:")
        print("-" * 80)
        print(custom_result)
        print("\n" + "="*80 + "\n")

    if choice in ["3", "4"]:
        print_comparison_analysis()

    print("\n" + "="*80)
    print("KEY TAKEAWAY")
    print("="*80)
    print("""
CrewAI is excellent for rapid multi-agent development, but understanding
the custom implementation helps you:

1. Debug issues when they arise
2. Implement custom patterns not supported by frameworks
3. Optimize performance and costs
4. Make informed decisions about when to use frameworks

Both approaches are valuable. Start with custom to learn fundamentals,
then use CrewAI for production efficiency!
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
