#!/usr/bin/env python3
"""
Simple Subagent Example
=======================

This example demonstrates the basic parent-child agent relationship:
- A Manager agent that orchestrates work
- A Researcher subagent that handles research tasks
- A Writer subagent that handles content creation

The manager delegates tasks to specialized subagents and synthesizes results.

Usage:
    python simple_subagent.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install openai python-dotenv
"""

import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from openai import OpenAI

from src.agent import BaseAgent
from src.tools import SubagentManager

load_dotenv()


def create_manager_agent(client: OpenAI) -> BaseAgent:
    """Create the orchestrator/manager agent."""
    return BaseAgent(
        system_prompt="""You are a Project Manager agent that orchestrates complex tasks.

Your role:
1. Break down user requests into subtasks
2. Delegate research tasks to the Researcher
3. Delegate writing tasks to the Writer
4. Synthesize results into a final deliverable

When you receive a task:
- First, identify what research is needed
- Then, identify what content needs to be created
- Finally, combine everything into a cohesive response

Always be clear about which subtasks you're delegating and why.""",
        model="gpt-4o-mini",
        temperature=0.3,
        client=client,
    )


def run_simple_subagent_demo():
    """Demonstrate basic subagent usage."""
    
    print("=" * 60)
    print("Simple Subagent Demo")
    print("=" * 60)
    print()
    
    # Initialize shared client (more efficient than separate clients)
    client = OpenAI()
    
    # Create the subagent manager
    manager = SubagentManager(client=client)
    
    # Spawn specialized subagents
    print("📦 Spawning subagents...")
    
    researcher = manager.spawn(
        role="researcher",
        task="Research topics thoroughly and provide factual information",
        system_prompt_template="""You are a Research Specialist agent.

Your expertise: {task}

Guidelines:
- Provide accurate, well-organized information
- Include key facts and statistics when relevant
- Structure your response with clear sections
- Be concise but comprehensive"""
    )
    print("   ✓ Researcher subagent ready")
    
    writer = manager.spawn(
        role="writer", 
        task="Create engaging, well-structured content",
        system_prompt_template="""You are a Content Writer agent.

Your expertise: {task}

Guidelines:
- Write in a clear, engaging style
- Use appropriate formatting (headers, bullet points)
- Adapt tone to the content type
- Keep the audience in mind"""
    )
    print("   ✓ Writer subagent ready")
    
    print(f"\n📋 Active subagents: {manager.list_active()}")
    print()
    
    # Create manager agent
    orchestrator = create_manager_agent(client)
    
    # Example task: Create a brief about AI agents
    user_task = "Create a brief introduction to AI agents for beginners"
    
    print(f"📝 User Task: {user_task}")
    print("-" * 60)
    print()
    
    # Step 1: Manager plans the work
    plan = orchestrator.complete(f"""
Task: {user_task}

Please create a plan with:
1. What research is needed?
2. What content needs to be written?
3. How will you combine them?

Be specific about the subtasks.""")
    
    print("🎯 Manager's Plan:")
    print(plan)
    print()
    
    # Step 2: Execute research subtask
    print("-" * 60)
    print("🔬 Researcher Working...")
    research_result = researcher.complete(
        "Provide a beginner-friendly overview of AI agents: what they are, "
        "how they work, and common use cases. Keep it concise."
    )
    print("\nResearch Output:")
    print(research_result)
    print()
    
    # Step 3: Execute writing subtask
    print("-" * 60)
    print("✍️  Writer Working...")
    writing_result = writer.complete(f"""
Based on this research, write a friendly introduction for beginners:

Research notes:
{research_result}

Create a 2-3 paragraph introduction that's welcoming and easy to understand.""")
    
    print("\nWriter Output:")
    print(writing_result)
    print()
    
    # Step 4: Manager synthesizes final result
    print("-" * 60)
    print("🔄 Manager Synthesizing...")
    final_result = orchestrator.complete(f"""
Please synthesize these subagent outputs into a final deliverable:

RESEARCH OUTPUT:
{research_result}

WRITER OUTPUT:
{writing_result}

Create the final brief, adding any necessary polish or organization.""")
    
    print("\n" + "=" * 60)
    print("📄 FINAL DELIVERABLE")
    print("=" * 60)
    print(final_result)
    print()
    
    # Cleanup
    print("-" * 60)
    terminated = manager.terminate_all()
    print(f"🧹 Cleaned up {terminated} subagents")
    print(f"📋 Active subagents: {manager.list_active()}")


def run_interactive_demo():
    """Run an interactive session with subagents."""
    
    print("=" * 60)
    print("Interactive Subagent Demo")
    print("=" * 60)
    print()
    print("This demo lets you interact with a manager that delegates to subagents.")
    print("Type 'quit' to exit.")
    print()
    
    client = OpenAI()
    manager = SubagentManager(client=client)
    
    # Spawn subagents
    manager.spawn(
        role="analyst",
        task="Analyze problems and provide structured insights",
    )
    manager.spawn(
        role="coder",
        task="Write clean, well-documented code examples",
    )
    
    print(f"Available specialists: {manager.list_active()}")
    print("-" * 60)
    
    # Create orchestrator with subagent tools
    analyst_tool = manager.as_tool("analyst", "Delegate analytical tasks")
    coder_tool = manager.as_tool("coder", "Delegate coding tasks")
    
    orchestrator = BaseAgent(
        system_prompt="""You are a helpful assistant with access to specialist subagents.

Available specialists:
- Analyst: For breaking down problems and providing insights
- Coder: For writing code examples and solutions

For each user request:
1. Determine if you need specialist help
2. If yes, describe what you're delegating and to whom
3. Use the specialist's output in your response

You can handle simple requests directly without delegating.""",
        client=client,
    )
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            if not user_input:
                continue
            
            # Simple routing based on keywords
            if any(word in user_input.lower() for word in ['analyze', 'explain', 'why', 'how does']):
                print("\n🔄 Delegating to Analyst...")
                specialist_result = manager.get("analyst").complete(user_input)
                response = orchestrator.complete(
                    f"The analyst provided this insight:\n\n{specialist_result}\n\n"
                    f"Please present this to the user in a helpful way."
                )
            elif any(word in user_input.lower() for word in ['code', 'write', 'implement', 'function']):
                print("\n🔄 Delegating to Coder...")
                specialist_result = manager.get("coder").complete(user_input)
                response = orchestrator.complete(
                    f"The coder provided this solution:\n\n{specialist_result}\n\n"
                    f"Please present this to the user, adding any helpful context."
                )
            else:
                response = orchestrator.complete(user_input)
            
            print(f"\n🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            break
    
    manager.terminate_all()
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Subagent Demo")
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run interactive mode"
    )
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_demo()
    else:
        run_simple_subagent_demo()
