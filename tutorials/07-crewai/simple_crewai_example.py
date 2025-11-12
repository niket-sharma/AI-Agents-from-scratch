"""
Simple CrewAI Introduction: Getting Started with Multi-Agent Systems

This is a minimal example to help you understand CrewAI basics:
- How to create agents with specific roles
- How to define tasks
- How to orchestrate agents using a Crew

This example creates a simple product launch team with a market researcher
and a marketing strategist.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================================================
# Step 1: Create Agents
# ============================================================================

# Agent 1: Market Researcher
market_researcher = Agent(
    role='Market Research Analyst',
    goal='Analyze market trends and identify target audiences',
    backstory="""You are an experienced market researcher who excels at
    understanding consumer behavior, market trends, and competitive landscapes.
    You provide data-driven insights that inform business decisions.""",
    verbose=True,  # Show detailed output
    allow_delegation=False,  # This agent works independently
)

# Agent 2: Marketing Strategist
marketing_strategist = Agent(
    role='Marketing Strategist',
    goal='Develop effective marketing strategies based on research',
    backstory="""You are a creative marketing strategist with a proven track
    record of successful product launches. You excel at crafting compelling
    marketing messages and choosing the right channels to reach target audiences.""",
    verbose=True,
    allow_delegation=False,
)


# ============================================================================
# Step 2: Define Tasks
# ============================================================================

# Task 1: Market Research
research_task = Task(
    description="""
    Conduct market research for a new AI-powered productivity app.

    Focus on:
    1. Target audience demographics (age, profession, tech-savviness)
    2. Main competitors and their strengths/weaknesses
    3. Key market trends in productivity software
    4. Potential challenges and opportunities

    Provide a concise market analysis report.
    """,
    agent=market_researcher,
    expected_output="A comprehensive market analysis report covering target audience, competitors, trends, and opportunities."
)

# Task 2: Marketing Strategy
strategy_task = Task(
    description="""
    Based on the market research, develop a marketing strategy for launching
    the AI-powered productivity app.

    Include:
    1. Key marketing messages and value propositions
    2. Recommended marketing channels (social media, content, ads, etc.)
    3. Target audience segments to prioritize
    4. Launch timeline and milestones
    5. Success metrics to track

    Create a clear, actionable marketing plan.
    """,
    agent=marketing_strategist,
    expected_output="A detailed marketing strategy with messaging, channels, timeline, and success metrics."
)


# ============================================================================
# Step 3: Create and Run the Crew
# ============================================================================

# Assemble the crew
product_launch_crew = Crew(
    agents=[market_researcher, marketing_strategist],
    tasks=[research_task, strategy_task],
    process=Process.sequential,  # Tasks run one after another
    verbose=True,
)


def main():
    """
    Run the simple CrewAI example.
    """
    print("\n" + "="*80)
    print("Simple CrewAI Example: Product Launch Team")
    print("="*80)
    print("\nThis example demonstrates:")
    print("  1. Creating agents with specific roles")
    print("  2. Defining tasks for each agent")
    print("  3. Running a crew in sequential process")
    print("\n" + "="*80 + "\n")

    # Start the crew
    print("Starting the product launch crew...\n")
    result = product_launch_crew.kickoff()

    # Display results
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80 + "\n")
    print(result)

    # Save to file
    output_file = Path("product_launch_strategy.txt")
    output_file.write_text(str(result), encoding='utf-8')
    print(f"\n\nStrategy saved to: {output_file.absolute()}")


if __name__ == "__main__":
    main()
