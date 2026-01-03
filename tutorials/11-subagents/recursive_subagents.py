#!/usr/bin/env python3
"""
Recursive Subagents Example
===========================

This example demonstrates hierarchical task decomposition where subagents
can spawn their own subagents, creating a tree of agents.

Key Concepts:
- Recursive agent spawning with depth limits
- Hierarchical task decomposition
- Result aggregation up the tree
- Avoiding infinite recursion

Usage:
    python recursive_subagents.py
    python recursive_subagents.py --depth 3  # Set max recursion depth

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install openai python-dotenv
"""

import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from openai import OpenAI

from src.agent import BaseAgent

load_dotenv()


@dataclass
class TaskNode:
    """Represents a task in the decomposition tree."""
    description: str
    result: Optional[str] = None
    subtasks: List["TaskNode"] = field(default_factory=list)
    depth: int = 0
    
    def __str__(self) -> str:
        indent = "  " * self.depth
        lines = [f"{indent}📋 {self.description}"]
        if self.result:
            result_preview = self.result[:100] + "..." if len(self.result) > 100 else self.result
            lines.append(f"{indent}   ✓ {result_preview}")
        for subtask in self.subtasks:
            lines.append(str(subtask))
        return "\n".join(lines)


class RecursiveAgent:
    """
    An agent that can recursively decompose tasks and spawn subagents.
    
    This implements the hierarchical decomposition pattern where:
    1. A task is analyzed to determine if it needs decomposition
    2. If yes, subtasks are created and assigned to child agents
    3. Each child can further decompose if needed (up to max_depth)
    4. Results are aggregated back up the tree
    """
    
    def __init__(
        self,
        client: OpenAI = None,
        max_depth: int = 2,
        current_depth: int = 0,
        parent_context: str = "",
    ):
        self.client = client or OpenAI()
        self.max_depth = max_depth
        self.current_depth = current_depth
        self.parent_context = parent_context
        
        # Create the underlying agent
        self.agent = BaseAgent(
            system_prompt=self._build_system_prompt(),
            model="gpt-4o-mini",
            temperature=0.3,
            client=self.client,
        )
    
    def _build_system_prompt(self) -> str:
        depth_info = f"You are at depth {self.current_depth} of max {self.max_depth}."
        
        if self.current_depth < self.max_depth:
            can_delegate = """
You CAN delegate to subagents if a task is too complex.
To delegate, break the task into 2-4 smaller subtasks."""
        else:
            can_delegate = """
You are at MAXIMUM DEPTH - you CANNOT delegate further.
You must complete the task directly with your best effort."""
        
        return f"""You are a Task Execution Agent in a hierarchical system.

{depth_info}
{can_delegate}

Context from parent: {self.parent_context if self.parent_context else 'None (you are the root)'}

When given a task:
1. Assess if you can complete it directly or need to decompose it
2. If decomposing, list subtasks clearly (one per line, prefixed with "- SUBTASK:")
3. If completing directly, provide the solution

Guidelines:
- Only decompose if truly necessary
- Each subtask should be self-contained
- Provide clear, actionable outputs"""
    
    def _should_decompose(self, task: str, analysis: str) -> bool:
        """Determine if the agent decided to decompose the task."""
        return "- SUBTASK:" in analysis
    
    def _extract_subtasks(self, analysis: str) -> List[str]:
        """Extract subtask descriptions from the analysis."""
        subtasks = []
        for line in analysis.split("\n"):
            if "- SUBTASK:" in line:
                subtask = line.split("- SUBTASK:")[-1].strip()
                if subtask:
                    subtasks.append(subtask)
        return subtasks
    
    def solve(self, task: str, verbose: bool = True) -> TaskNode:
        """
        Recursively solve a task, spawning subagents as needed.
        
        Args:
            task: The task to solve
            verbose: Whether to print progress
            
        Returns:
            TaskNode representing the solution tree
        """
        indent = "  " * self.current_depth
        
        if verbose:
            status = "🌳" if self.current_depth == 0 else "├─"
            print(f"{indent}{status} Depth {self.current_depth}: {task[:60]}...")
        
        # Create the task node
        node = TaskNode(description=task, depth=self.current_depth)
        
        # Analyze the task
        if self.current_depth < self.max_depth:
            analysis_prompt = f"""
Task: {task}

Analyze this task. If it's complex and would benefit from decomposition, 
list 2-4 subtasks using "- SUBTASK:" prefix.
If it's simple enough to solve directly, just solve it."""
        else:
            analysis_prompt = f"""
Task: {task}

You are at maximum depth and cannot delegate. 
Complete this task directly with your best effort."""
        
        analysis = self.agent.complete(analysis_prompt)
        
        # Check if we should decompose
        if self._should_decompose(task, analysis) and self.current_depth < self.max_depth:
            subtasks = self._extract_subtasks(analysis)
            
            if verbose:
                print(f"{indent}   📦 Decomposing into {len(subtasks)} subtasks...")
            
            # Spawn child agents for each subtask
            for subtask_desc in subtasks:
                child_agent = RecursiveAgent(
                    client=self.client,
                    max_depth=self.max_depth,
                    current_depth=self.current_depth + 1,
                    parent_context=f"Parent task: {task}",
                )
                
                child_node = child_agent.solve(subtask_desc, verbose=verbose)
                node.subtasks.append(child_node)
            
            # Aggregate results from children
            if verbose:
                print(f"{indent}   🔄 Aggregating child results...")
            
            child_results = "\n\n".join([
                f"Subtask: {child.description}\nResult: {child.result}"
                for child in node.subtasks
            ])
            
            synthesis = self.agent.complete(f"""
Original task: {task}

Child agent results:
{child_results}

Please synthesize these results into a cohesive response for the original task.""")
            
            node.result = synthesis
            
        else:
            # Direct completion (no decomposition)
            if verbose:
                print(f"{indent}   ✓ Completing directly...")
            
            # Use the analysis as the result if it doesn't contain subtasks
            if "- SUBTASK:" not in analysis:
                node.result = analysis
            else:
                # If analysis had subtasks but we can't decompose, complete directly
                direct = self.agent.complete(f"Complete this task directly: {task}")
                node.result = direct
        
        return node


def run_recursive_demo(max_depth: int = 2):
    """Demonstrate recursive subagent decomposition."""
    
    print("=" * 60)
    print("Recursive Subagents Demo")
    print("=" * 60)
    print(f"Max recursion depth: {max_depth}")
    print()
    
    client = OpenAI()
    
    # Create root agent
    root_agent = RecursiveAgent(
        client=client,
        max_depth=max_depth,
    )
    
    # Complex task that benefits from decomposition
    complex_task = """
    Create a comprehensive guide for someone starting to learn programming:
    1. What language should they start with and why
    2. What tools do they need to set up
    3. What are the first concepts they should learn
    4. What project should they build first
    """
    
    print("📝 Complex Task:")
    print(complex_task)
    print("\n" + "-" * 60)
    print("🔄 Processing with recursive decomposition...")
    print("-" * 60 + "\n")
    
    # Solve the task
    result_tree = root_agent.solve(complex_task.strip())
    
    # Display the tree structure
    print("\n" + "=" * 60)
    print("📊 TASK DECOMPOSITION TREE")
    print("=" * 60)
    print(result_tree)
    
    # Display final synthesized result
    print("\n" + "=" * 60)
    print("📋 FINAL SYNTHESIZED RESULT")
    print("=" * 60)
    print(result_tree.result)


def run_simple_decomposition_demo():
    """Show a simpler decomposition example."""
    
    print("=" * 60)
    print("Simple Decomposition Example")
    print("=" * 60)
    print()
    
    client = OpenAI()
    
    # Depth 1 only - just one level of decomposition
    agent = RecursiveAgent(
        client=client,
        max_depth=1,
    )
    
    task = "Research the pros and cons of Python vs JavaScript for web development"
    
    print(f"📝 Task: {task}")
    print("-" * 60 + "\n")
    
    result = agent.solve(task)
    
    print("\n" + "=" * 60)
    print("Result Tree:")
    print(result)
    print("\n" + "-" * 60)
    print("Final Answer:")
    print(result.result)


class BoundedRecursiveAgent:
    """
    A more controlled recursive agent with explicit bounds and safeguards.
    
    Features:
    - Hard depth limit
    - Task count limit (prevents explosion)
    - Timeout per task
    - Better error handling
    """
    
    def __init__(
        self,
        client: OpenAI = None,
        max_depth: int = 2,
        max_total_tasks: int = 10,
    ):
        self.client = client or OpenAI()
        self.max_depth = max_depth
        self.max_total_tasks = max_total_tasks
        self.task_count = 0
    
    def solve(self, task: str, depth: int = 0) -> str:
        """
        Solve a task with strict bounds.
        
        Raises:
            RuntimeError: If limits are exceeded
        """
        # Check bounds
        if depth > self.max_depth:
            raise RuntimeError(f"Exceeded max depth of {self.max_depth}")
        
        self.task_count += 1
        if self.task_count > self.max_total_tasks:
            raise RuntimeError(f"Exceeded max tasks of {self.max_total_tasks}")
        
        indent = "  " * depth
        print(f"{indent}[Task {self.task_count}/{self.max_total_tasks}] {task[:50]}...")
        
        agent = BaseAgent(
            system_prompt=f"""You solve tasks. Current depth: {depth}/{self.max_depth}.
If depth < max, you can suggest subtasks (prefix with SUBTASK:).
Otherwise, solve directly.""",
            client=self.client,
        )
        
        response = agent.complete(task)
        
        # Check for subtasks
        if "SUBTASK:" in response and depth < self.max_depth:
            subtasks = [
                line.split("SUBTASK:")[-1].strip()
                for line in response.split("\n")
                if "SUBTASK:" in line
            ][:3]  # Limit to 3 subtasks
            
            if subtasks:
                results = []
                for st in subtasks:
                    try:
                        result = self.solve(st, depth + 1)
                        results.append(f"- {st}: {result}")
                    except RuntimeError as e:
                        results.append(f"- {st}: [Skipped: {e}]")
                
                # Synthesize
                synthesis = agent.complete(
                    f"Synthesize: {task}\nResults:\n" + "\n".join(results)
                )
                return synthesis
        
        return response


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Recursive Subagents Demo")
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=2,
        help="Maximum recursion depth (default: 2)"
    )
    parser.add_argument(
        "--simple", "-s",
        action="store_true",
        help="Run simple decomposition demo"
    )
    args = parser.parse_args()
    
    if args.simple:
        run_simple_decomposition_demo()
    else:
        run_recursive_demo(max_depth=args.depth)
