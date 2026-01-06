"""
Skills vs Tools Comparison

This module demonstrates the differences between using Claude Skills
(Extended Thinking, Computer Use) and traditional tools (function calling).

Shows when to use which approach and how they complement each other.

Author: AI Agents Tutorial
Tutorial: 12-claude-skills
"""

import anthropic
import os
import time
from typing import Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()


# =============================================================================
# Traditional Tools Implementation
# =============================================================================

def calculator_tool(expression: str) -> float:
    """Traditional tool: Calculator."""
    try:
        # Safe evaluation (in production, use a proper expression parser)
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        return f"Error: {e}"


def database_tool(query: str) -> list:
    """Traditional tool: Database query (simulated)."""
    # Simulate database
    fake_db = {
        "users": [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
            {"id": 3, "name": "Charlie", "age": 35}
        ]
    }
    
    # Simple query parser
    if "SELECT" in query.upper():
        return fake_db.get("users", [])
    return []


def file_tool(operation: str, path: str, content: str = None) -> str:
    """Traditional tool: File operations (simulated)."""
    if operation == "read":
        return f"[Content of {path}]"
    elif operation == "write":
        return f"Written to {path}"
    elif operation == "list":
        return f"[Files in {path}]"
    return "Invalid operation"


class TraditionalToolAgent:
    """Agent using traditional function calling."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tools = self._define_tools()
    
    def _define_tools(self) -> list:
        """Define available tools."""
        return [
            {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "database_query",
                "description": "Query database for information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "file_operation",
                "description": "Perform file operations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["read", "write", "list"]
                        },
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["operation", "path"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a tool by name."""
        if tool_name == "calculator":
            return calculator_tool(tool_input["expression"])
        elif tool_name == "database_query":
            return database_tool(tool_input["query"])
        elif tool_name == "file_operation":
            return file_tool(
                tool_input["operation"],
                tool_input["path"],
                tool_input.get("content")
            )
        return "Unknown tool"
    
    def process(self, task: str) -> Dict:
        """Process task using traditional tools."""
        start_time = time.time()
        
        conversation = [{
            "role": "user",
            "content": task
        }]
        
        # Initial request
        response = self.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=4096,
            tools=self.tools,
            messages=conversation
        )
        
        tool_calls = 0
        
        # Handle tool uses
        while any(block.type == "tool_use" for block in response.content):
            tool_calls += 1
            
            # Execute tools
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = self.execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            
            # Continue conversation
            conversation.append({
                "role": "assistant",
                "content": response.content
            })
            conversation.append({
                "role": "user",
                "content": tool_results
            })
            
            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=4096,
                tools=self.tools,
                messages=conversation
            )
        
        # Extract final answer
        final_answer = " ".join(
            block.text for block in response.content if block.type == "text"
        )
        
        elapsed = time.time() - start_time
        
        return {
            "approach": "Traditional Tools",
            "answer": final_answer,
            "tool_calls": tool_calls,
            "elapsed_time": elapsed,
            "tokens_used": response.usage.output_tokens
        }


# =============================================================================
# Skills-Based Implementation
# =============================================================================

class SkillsAgent:
    """Agent using Claude Skills (Extended Thinking)."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def process(self, task: str, thinking_budget: int = 5000) -> Dict:
        """Process task using Extended Thinking."""
        start_time = time.time()
        
        response = self.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=8000,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget
            },
            messages=[{
                "role": "user",
                "content": task
            }]
        )
        
        thinking_content = None
        final_answer = None
        
        for block in response.content:
            if block.type == "thinking":
                thinking_content = block.thinking
            elif block.type == "text":
                final_answer = block.text
        
        elapsed = time.time() - start_time
        
        return {
            "approach": "Extended Thinking",
            "answer": final_answer,
            "thinking": thinking_content,
            "elapsed_time": elapsed,
            "tokens_used": response.usage.output_tokens
        }


# =============================================================================
# Hybrid Implementation
# =============================================================================

class HybridAgent:
    """Agent combining Skills and Tools."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tools = TraditionalToolAgent()._define_tools()
    
    def process(self, task: str, use_thinking: bool = True) -> Dict:
        """Process task using both skills and tools."""
        start_time = time.time()
        
        request_params = {
            "model": "claude-opus-4-20250514",
            "max_tokens": 8000,
            "tools": self.tools,
            "messages": [{"role": "user", "content": task}]
        }
        
        if use_thinking:
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 3000
            }
        
        response = self.client.messages.create(**request_params)
        
        thinking_content = None
        tool_calls = 0
        final_answer = None
        
        for block in response.content:
            if block.type == "thinking":
                thinking_content = block.thinking
            elif block.type == "tool_use":
                tool_calls += 1
            elif block.type == "text":
                final_answer = block.text
        
        elapsed = time.time() - start_time
        
        return {
            "approach": "Hybrid (Skills + Tools)",
            "answer": final_answer,
            "thinking": thinking_content[:200] + "..." if thinking_content else None,
            "tool_calls": tool_calls,
            "elapsed_time": elapsed,
            "tokens_used": response.usage.output_tokens
        }


# =============================================================================
# Comparison Demonstrations
# =============================================================================

def compare_simple_calculation():
    """Compare approaches for simple calculation."""
    print("\n" + "="*70)
    print("Comparison 1: Simple Calculation")
    print("="*70)
    
    task = "Calculate 1847 * 923 + 456 / 12"
    print(f"\nTask: {task}\n")
    
    # Traditional tools (faster for precise calculations)
    print("🔧 Traditional Tools:")
    tool_agent = TraditionalToolAgent()
    tool_result = tool_agent.process(task)
    print(f"   Answer: {tool_result['answer']}")
    print(f"   Time: {tool_result['elapsed_time']:.2f}s")
    print(f"   Tool calls: {tool_result['tool_calls']}")
    
    # Extended thinking (slower, may be less precise)
    print("\n🧠 Extended Thinking:")
    skills_agent = SkillsAgent()
    skills_result = skills_agent.process(task, thinking_budget=2000)
    print(f"   Answer: {skills_result['answer']}")
    print(f"   Time: {skills_result['elapsed_time']:.2f}s")
    
    print("\n📊 Verdict: Traditional tools are better for precise calculations")


def compare_complex_reasoning():
    """Compare approaches for complex reasoning."""
    print("\n" + "="*70)
    print("Comparison 2: Complex Strategic Reasoning")
    print("="*70)
    
    task = """
    Analyze the trade-offs between microservices and monolithic architecture
    for a startup with 5 engineers building a social media platform.
    Consider: scalability, development speed, costs, and team expertise.
    """
    print(f"\nTask: {task[:100]}...\n")
    
    # Traditional approach (limited reasoning)
    print("🔧 Traditional Approach (No Thinking):")
    tool_agent = TraditionalToolAgent()
    # Simulate by using skills agent without thinking
    basic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    start = time.time()
    response = basic_client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": task}]
    )
    elapsed = time.time() - start
    basic_answer = response.content[0].text
    print(f"   Answer length: {len(basic_answer)} chars")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Preview: {basic_answer[:150]}...")
    
    # Extended thinking (deeper analysis)
    print("\n🧠 Extended Thinking:")
    skills_agent = SkillsAgent()
    skills_result = skills_agent.process(task, thinking_budget=7000)
    print(f"   Answer length: {len(skills_result['answer'])} chars")
    print(f"   Time: {skills_result['elapsed_time']:.2f}s")
    print(f"   Thinking depth: {len(skills_result['thinking'].split())} words")
    print(f"   Preview: {skills_result['answer'][:150]}...")
    
    print("\n📊 Verdict: Extended Thinking better for complex strategic analysis")


def compare_data_operations():
    """Compare approaches for data operations."""
    print("\n" + "="*70)
    print("Comparison 3: Data Operations")
    print("="*70)
    
    task = "Get all users from the database and calculate their average age"
    print(f"\nTask: {task}\n")
    
    # Traditional tools (direct and efficient)
    print("🔧 Traditional Tools:")
    tool_agent = TraditionalToolAgent()
    tool_result = tool_agent.process(task)
    print(f"   Answer: {tool_result['answer']}")
    print(f"   Time: {tool_result['elapsed_time']:.2f}s")
    print(f"   Tool calls: {tool_result['tool_calls']}")
    
    # Hybrid approach
    print("\n🔄 Hybrid Approach:")
    hybrid_agent = HybridAgent()
    hybrid_result = hybrid_agent.process(task, use_thinking=True)
    print(f"   Answer: {hybrid_result['answer']}")
    print(f"   Time: {hybrid_result['elapsed_time']:.2f}s")
    print(f"   Tool calls: {hybrid_result['tool_calls']}")
    
    print("\n📊 Verdict: Traditional tools better for straightforward data ops")


def compare_multi_step_analysis():
    """Compare approaches for multi-step analytical tasks."""
    print("\n" + "="*70)
    print("Comparison 4: Multi-Step Analysis")
    print("="*70)
    
    task = """
    Design a caching strategy for our API. Consider:
    1. What to cache (database queries, API responses, computed results)
    2. Cache invalidation strategy
    3. Distributed caching vs local caching
    4. Cost-benefit analysis
    Provide a detailed recommendation with justification.
    """
    print(f"\nTask: {task[:100]}...\n")
    
    # Hybrid approach (best of both worlds)
    print("🔄 Hybrid Approach (Thinking + Tools):")
    hybrid_agent = HybridAgent()
    hybrid_result = hybrid_agent.process(task, use_thinking=True)
    print(f"   Answer length: {len(hybrid_result['answer'])} chars")
    print(f"   Time: {hybrid_result['elapsed_time']:.2f}s")
    print(f"   Used thinking: {'Yes' if hybrid_result['thinking'] else 'No'}")
    print(f"   Tool calls: {hybrid_result['tool_calls']}")
    print(f"   Preview: {hybrid_result['answer'][:200]}...")
    
    print("\n📊 Verdict: Hybrid approach best for complex analytical tasks")


def performance_benchmark():
    """Benchmark performance across approaches."""
    print("\n" + "="*70)
    print("Performance Benchmark")
    print("="*70)
    
    test_cases = [
        {
            "name": "Simple Math",
            "task": "What is 25 * 47 + 123?",
            "best_approach": "Tools"
        },
        {
            "name": "Factual Query",
            "task": "What is the capital of France?",
            "best_approach": "Standard (no skills/tools)"
        },
        {
            "name": "Complex Analysis",
            "task": "Analyze the pros and cons of different database indexing strategies",
            "best_approach": "Extended Thinking"
        }
    ]
    
    print("\n")
    print(f"{'Task':<20} {'Best Approach':<25} {'Reason':<30}")
    print("-" * 75)
    
    for case in test_cases:
        print(f"{case['name']:<20} {case['best_approach']:<25} {'Speed/Precision' if case['best_approach'] == 'Tools' else 'Deep Reasoning':<30}")


def decision_matrix():
    """Display decision matrix for choosing approach."""
    print("\n" + "="*70)
    print("Decision Matrix: When to Use What")
    print("="*70)
    
    matrix = """
    ┌─────────────────────────┬──────────────┬─────────────────┬─────────────┐
    │ Task Type               │ Tools        │ Ext. Thinking   │ Hybrid      │
    ├─────────────────────────┼──────────────┼─────────────────┼─────────────┤
    │ Precise calculations    │ ✅ Best      │ ⚠️  Slower      │ ✅ Good     │
    │ Database operations     │ ✅ Best      │ ❌ No access    │ ✅ Good     │
    │ API calls               │ ✅ Best      │ ❌ No access    │ ✅ Good     │
    │ File operations         │ ✅ Best      │ ❌ No access    │ ✅ Good     │
    │ Complex reasoning       │ ⚠️  Limited  │ ✅ Best         │ ✅ Best     │
    │ Strategic planning      │ ⚠️  Limited  │ ✅ Best         │ ✅ Best     │
    │ Code architecture       │ ⚠️  Limited  │ ✅ Best         │ ✅ Best     │
    │ Multi-step analysis     │ ✅ Good      │ ✅ Good         │ ✅ Best     │
    │ Real-time responses     │ ✅ Fast      │ ❌ Too slow     │ ⚠️  Depends │
    │ Cost optimization       │ ✅ Cheaper   │ ⚠️  More tokens │ ⚠️  Balanced │
    └─────────────────────────┴──────────────┴─────────────────┴─────────────┘
    """
    print(matrix)


def cost_comparison():
    """Compare costs of different approaches."""
    print("\n" + "="*70)
    print("Cost Comparison (Approximate)")
    print("="*70)
    
    costs = {
        "Standard Request": {
            "input_tokens": 1000,
            "output_tokens": 500,
            "thinking_tokens": 0,
            "total_cost": 0.015
        },
        "Extended Thinking": {
            "input_tokens": 1000,
            "output_tokens": 500,
            "thinking_tokens": 5000,
            "total_cost": 0.045
        },
        "Tools (3 calls)": {
            "input_tokens": 1000,
            "output_tokens": 500,
            "thinking_tokens": 0,
            "total_cost": 0.018
        },
        "Hybrid": {
            "input_tokens": 1000,
            "output_tokens": 500,
            "thinking_tokens": 3000,
            "total_cost": 0.032
        }
    }
    
    print("\n")
    print(f"{'Approach':<20} {'Input':<10} {'Output':<10} {'Thinking':<12} {'Cost':<10}")
    print("-" * 72)
    
    for approach, data in costs.items():
        print(f"{approach:<20} {data['input_tokens']:<10} {data['output_tokens']:<10} "
              f"{data['thinking_tokens']:<12} ${data['total_cost']:.3f}")
    
    print("\n💡 Note: Costs are approximate and vary by API tier and model version")


def recommendations():
    """Provide recommendations for choosing approaches."""
    print("\n" + "="*70)
    print("Recommendations")
    print("="*70)
    
    print("""
    🎯 GENERAL GUIDELINES:
    
    1. Use Traditional Tools when:
       • You need precise calculations or data operations
       • Task requires external system access (DB, API, files)
       • Speed is critical
       • Cost optimization is important
    
    2. Use Extended Thinking when:
       • Problem requires deep analysis or strategic thinking
       • Multiple alternatives need evaluation
       • Transparency in reasoning is important
       • Complexity is high
    
    3. Use Hybrid Approach when:
       • Task has both analytical and operational components
       • You want reasoning transparency + precise execution
       • Building production-grade agents
       • Task is complex but needs tool access
    
    4. Use Standard (No Skills/Tools) when:
       • Simple factual questions
       • Quick conversational responses
       • Low-complexity tasks
       • Cost minimization is critical
    
    🚀 BEST PRACTICES:
    
    • Start with simplest approach that works
    • Add complexity only when needed
    • Monitor costs and performance
    • Consider task characteristics
    • Test different approaches for your use case
    
    ⚡ PERFORMANCE TIPS:
    
    • Cache thinking results for similar problems
    • Use adaptive thinking budgets
    • Combine approaches strategically
    • Implement fallback mechanisms
    """)


if __name__ == "__main__":
    """Run all comparisons."""
    
    print("\n" + "="*70)
    print("CLAUDE SKILLS VS TRADITIONAL TOOLS - COMPREHENSIVE COMPARISON")
    print("="*70)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ Error: ANTHROPIC_API_KEY not found")
        exit(1)
    
    try:
        # Run comparisons
        compare_simple_calculation()
        compare_complex_reasoning()
        compare_data_operations()
        compare_multi_step_analysis()
        
        # Display analysis
        performance_benchmark()
        decision_matrix()
        cost_comparison()
        recommendations()
        
        print("\n" + "="*70)
        print("✅ Comparison completed!")
        print("="*70)
        
        print("\n💡 Key Takeaway:")
        print("   There's no 'best' approach - choose based on your specific needs.")
        print("   Often, a hybrid approach combining skills and tools is optimal.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
