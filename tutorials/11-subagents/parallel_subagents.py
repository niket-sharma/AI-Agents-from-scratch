#!/usr/bin/env python3
"""
Parallel Subagents Example
==========================

This example demonstrates running multiple subagents concurrently to improve
performance when tasks are independent.

Key Concepts:
- Using asyncio to run subagents in parallel
- Aggregating results from multiple concurrent subagents
- Performance comparison: sequential vs parallel execution

Usage:
    python parallel_subagents.py
    python parallel_subagents.py --compare  # Compare sequential vs parallel

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install openai python-dotenv
"""

import asyncio
import os
import sys
import time
from typing import List, Tuple

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from openai import OpenAI

from src.agent import BaseAgent
from src.tools import SubagentManager

load_dotenv()


class ParallelSubagentExecutor:
    """
    Executes multiple subagents in parallel using asyncio.
    
    This class demonstrates how to:
    1. Spawn multiple specialized subagents
    2. Run them concurrently on independent tasks
    3. Aggregate their results
    """
    
    def __init__(self, client: OpenAI = None):
        self.client = client or OpenAI()
        self.manager = SubagentManager(client=self.client)
    
    async def run_subagent_async(
        self,
        role: str,
        task: str,
        prompt: str
    ) -> Tuple[str, str, float]:
        """
        Run a single subagent asynchronously.
        
        Returns:
            Tuple of (role, result, execution_time)
        """
        start = time.time()
        
        # Spawn the subagent
        subagent = self.manager.spawn(
            role=role,
            task=task,
        )
        
        # Run in thread pool to not block the event loop
        # (OpenAI client is synchronous)
        result = await asyncio.to_thread(subagent.complete, prompt)
        
        elapsed = time.time() - start
        
        # Cleanup this specific subagent
        self.manager.terminate(role)
        
        return (role, result, elapsed)
    
    async def run_parallel(
        self,
        tasks: List[dict]
    ) -> List[Tuple[str, str, float]]:
        """
        Run multiple subagent tasks in parallel.
        
        Args:
            tasks: List of dicts with keys: role, task, prompt
            
        Returns:
            List of (role, result, time) tuples
        """
        coroutines = [
            self.run_subagent_async(
                role=t["role"],
                task=t["task"],
                prompt=t["prompt"]
            )
            for t in tasks
        ]
        
        results = await asyncio.gather(*coroutines)
        return results
    
    def run_sequential(
        self,
        tasks: List[dict]
    ) -> List[Tuple[str, str, float]]:
        """
        Run multiple subagent tasks sequentially (for comparison).
        
        Args:
            tasks: List of dicts with keys: role, task, prompt
            
        Returns:
            List of (role, result, time) tuples
        """
        results = []
        
        for t in tasks:
            start = time.time()
            
            subagent = self.manager.spawn(
                role=t["role"],
                task=t["task"],
            )
            
            result = subagent.complete(t["prompt"])
            elapsed = time.time() - start
            
            self.manager.terminate(t["role"])
            results.append((t["role"], result, elapsed))
        
        return results


def create_research_tasks() -> List[dict]:
    """Create sample research tasks for parallel execution."""
    return [
        {
            "role": "tech_researcher",
            "task": "Research technology trends",
            "prompt": "What are the top 3 emerging technology trends in 2024? Keep it brief."
        },
        {
            "role": "market_analyst",
            "task": "Analyze market conditions",
            "prompt": "What are the key factors affecting the AI market in 2024? Brief overview."
        },
        {
            "role": "competitor_analyst",
            "task": "Analyze competitive landscape",
            "prompt": "Who are the major players in the AI agent space? Brief list with strengths."
        },
    ]


def run_parallel_demo():
    """Demonstrate parallel subagent execution."""
    
    print("=" * 60)
    print("Parallel Subagents Demo")
    print("=" * 60)
    print()
    print("Running 3 research subagents in parallel...")
    print()
    
    client = OpenAI()
    executor = ParallelSubagentExecutor(client=client)
    
    tasks = create_research_tasks()
    
    # Run in parallel
    total_start = time.time()
    results = asyncio.run(executor.run_parallel(tasks))
    total_time = time.time() - total_start
    
    # Display results
    print("-" * 60)
    for role, result, elapsed in results:
        print(f"\n📊 {role.replace('_', ' ').title()} ({elapsed:.2f}s):")
        print("-" * 40)
        print(result)
    
    print("\n" + "=" * 60)
    print(f"⏱️  Total parallel time: {total_time:.2f}s")
    print(f"   (Individual times: {', '.join(f'{t[2]:.2f}s' for t in results)})")
    print("=" * 60)
    
    # Aggregate results with a synthesizer agent
    print("\n🔄 Synthesizing results...")
    
    synthesizer = BaseAgent(
        system_prompt="""You are a Research Synthesizer. 
Combine multiple research findings into a cohesive executive summary.
Be concise and highlight key insights.""",
        client=client,
    )
    
    combined_research = "\n\n".join([
        f"## {role.replace('_', ' ').title()}\n{result}"
        for role, result, _ in results
    ])
    
    summary = synthesizer.complete(f"""
Please synthesize these research findings into a brief executive summary:

{combined_research}

Create a 2-3 paragraph summary highlighting the most important insights.""")
    
    print("\n" + "=" * 60)
    print("📋 EXECUTIVE SUMMARY")
    print("=" * 60)
    print(summary)


def run_comparison_demo():
    """Compare sequential vs parallel execution times."""
    
    print("=" * 60)
    print("Sequential vs Parallel Comparison")
    print("=" * 60)
    print()
    
    client = OpenAI()
    executor = ParallelSubagentExecutor(client=client)
    
    tasks = create_research_tasks()
    
    # Sequential execution
    print("🔄 Running SEQUENTIAL execution...")
    seq_start = time.time()
    seq_results = executor.run_sequential(tasks)
    seq_total = time.time() - seq_start
    
    print(f"   Sequential total: {seq_total:.2f}s")
    print()
    
    # Parallel execution
    print("⚡ Running PARALLEL execution...")
    par_start = time.time()
    par_results = asyncio.run(executor.run_parallel(tasks))
    par_total = time.time() - par_start
    
    print(f"   Parallel total: {par_total:.2f}s")
    print()
    
    # Comparison
    speedup = seq_total / par_total if par_total > 0 else 0
    
    print("=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print(f"Sequential: {seq_total:.2f}s")
    print(f"Parallel:   {par_total:.2f}s")
    print(f"Speedup:    {speedup:.2f}x faster")
    print()
    
    # Individual times
    print("Individual task times:")
    print("-" * 40)
    print("Sequential:")
    for role, _, elapsed in seq_results:
        print(f"  - {role}: {elapsed:.2f}s")
    print("Parallel:")
    for role, _, elapsed in par_results:
        print(f"  - {role}: {elapsed:.2f}s")


async def run_with_progress():
    """Demonstrate parallel execution with progress updates."""
    
    print("=" * 60)
    print("Parallel Execution with Progress Tracking")
    print("=" * 60)
    print()
    
    client = OpenAI()
    manager = SubagentManager(client=client)
    
    tasks = create_research_tasks()
    completed = []
    
    async def run_with_callback(task: dict) -> Tuple[str, str]:
        """Run a task and report when done."""
        subagent = manager.spawn(
            role=task["role"],
            task=task["task"],
        )
        
        result = await asyncio.to_thread(
            subagent.complete, 
            task["prompt"]
        )
        
        # Report completion
        print(f"   ✓ {task['role']} completed")
        completed.append(task["role"])
        
        manager.terminate(task["role"])
        return (task["role"], result)
    
    print(f"Starting {len(tasks)} parallel tasks...")
    print("-" * 40)
    
    start = time.time()
    
    # Create all tasks
    coros = [run_with_callback(t) for t in tasks]
    
    # Run with as_completed for progress tracking
    results = []
    for coro in asyncio.as_completed(coros):
        result = await coro
        results.append(result)
    
    elapsed = time.time() - start
    
    print("-" * 40)
    print(f"All {len(results)} tasks completed in {elapsed:.2f}s")
    print()
    
    # Show results
    for role, result in results:
        print(f"\n📊 {role.replace('_', ' ').title()}:")
        print(result[:200] + "..." if len(result) > 200 else result)
    
    manager.terminate_all()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Parallel Subagents Demo")
    parser.add_argument(
        "--compare", "-c",
        action="store_true",
        help="Compare sequential vs parallel execution"
    )
    parser.add_argument(
        "--progress", "-p",
        action="store_true",
        help="Show progress tracking demo"
    )
    args = parser.parse_args()
    
    if args.compare:
        run_comparison_demo()
    elif args.progress:
        asyncio.run(run_with_progress())
    else:
        run_parallel_demo()
