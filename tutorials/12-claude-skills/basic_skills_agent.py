"""
Basic Skills Agent - Extended Thinking Example

This module demonstrates how to build a basic agent using Claude's
Extended Thinking capability for enhanced reasoning.

Author: AI Agents Tutorial
Tutorial: 12-claude-skills
"""

import anthropic
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BasicSkillsAgent:
    """
    A simple agent that uses Extended Thinking for complex problem-solving.
    
    This agent demonstrates:
    - Basic Extended Thinking setup
    - Thinking process visualization
    - Response parsing
    - Token usage tracking
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent.
        
        Args:
            api_key: Anthropic API key (defaults to env variable)
        """
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.conversation_history = []
    
    def think(self, problem: str, thinking_budget: int = 5000, 
              show_thinking: bool = True) -> Dict:
        """
        Process a problem using Extended Thinking.
        
        Args:
            problem: The problem to solve
            thinking_budget: Tokens allocated for thinking (1000-10000)
            show_thinking: Whether to return thinking process
        
        Returns:
            Dictionary with thinking process and final answer
        """
        try:
            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=16000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                },
                messages=[{
                    "role": "user",
                    "content": problem
                }]
            )
            
            # Parse response
            result = {
                "thinking": None,
                "answer": None,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            }
            
            # Extract thinking and answer
            for block in response.content:
                if block.type == "thinking":
                    result["thinking"] = block.thinking if show_thinking else "[Thinking hidden]"
                elif block.type == "text":
                    result["answer"] = block.text
            
            # Add thinking tokens if available
            if hasattr(response.usage, 'thinking_tokens'):
                result["usage"]["thinking_tokens"] = response.usage.thinking_tokens
            
            return result
            
        except anthropic.APIError as e:
            return {
                "error": str(e),
                "thinking": None,
                "answer": None
            }
    
    def analyze_thinking(self, thinking_text: str) -> Dict:
        """
        Analyze the thinking process to extract insights.
        
        Args:
            thinking_text: The thinking content from response
        
        Returns:
            Dictionary with analysis metrics
        """
        if not thinking_text or thinking_text == "[Thinking hidden]":
            return {"error": "No thinking content to analyze"}
        
        lines = thinking_text.split("\n")
        
        return {
            "total_lines": len(lines),
            "steps_identified": thinking_text.count("Step"),
            "considerations": thinking_text.count("consider"),
            "alternatives_explored": thinking_text.count("alternative"),
            "questions_asked": thinking_text.count("?"),
            "first_100_chars": thinking_text[:100] + "..."
        }


def demo_basic_usage():
    """Demonstrate basic Extended Thinking usage."""
    print("="*60)
    print("Demo 1: Basic Extended Thinking")
    print("="*60)
    
    agent = BasicSkillsAgent()
    
    problem = """
    Design a scalable microservices architecture for an e-commerce platform
    that needs to handle:
    - 100,000 concurrent users
    - Real-time inventory updates
    - Payment processing
    - Order fulfillment
    
    Consider fault tolerance, data consistency, and cost optimization.
    """
    
    print(f"\n📝 Problem:\n{problem}")
    print("\n⏳ Processing with Extended Thinking...\n")
    
    result = agent.think(problem, thinking_budget=7000)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print("🧠 THINKING PROCESS:")
    print("-" * 60)
    print(result["thinking"])
    print("-" * 60)
    
    print("\n💡 FINAL ANSWER:")
    print("-" * 60)
    print(result["answer"])
    print("-" * 60)
    
    print("\n📊 TOKEN USAGE:")
    for key, value in result["usage"].items():
        print(f"  {key}: {value}")
    
    # Analyze thinking
    analysis = agent.analyze_thinking(result["thinking"])
    print("\n🔍 THINKING ANALYSIS:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")


def demo_problem_comparison():
    """Compare thinking depth for different problem complexities."""
    print("\n" + "="*60)
    print("Demo 2: Comparing Thinking for Different Problems")
    print("="*60)
    
    agent = BasicSkillsAgent()
    
    problems = {
        "Simple": "What is the capital of France?",
        "Medium": "Explain the trade-offs between SQL and NoSQL databases.",
        "Complex": """
        Analyze the algorithmic complexity of implementing a distributed
        consensus protocol like Raft. Consider network partitions,
        leader election, and log replication.
        """
    }
    
    for complexity, problem in problems.items():
        print(f"\n{'─'*60}")
        print(f"Problem Complexity: {complexity}")
        print(f"{'─'*60}")
        print(f"Problem: {problem[:100]}...")
        
        # Adjust thinking budget based on complexity
        budget = {"Simple": 1000, "Medium": 3000, "Complex": 7000}[complexity]
        
        result = agent.think(problem, thinking_budget=budget, show_thinking=False)
        
        if "error" not in result:
            print(f"\n✅ Answer: {result['answer'][:200]}...")
            print(f"\n📊 Tokens used:")
            for key, value in result["usage"].items():
                print(f"  {key}: {value}")
            
            # Quick analysis
            if result["thinking"]:
                lines = len(result["thinking"].split("\n"))
                print(f"  Thinking depth: {lines} lines")


def demo_iterative_thinking():
    """Demonstrate how thinking helps with iterative problem-solving."""
    print("\n" + "="*60)
    print("Demo 3: Iterative Problem Solving")
    print("="*60)
    
    agent = BasicSkillsAgent()
    
    # Step 1: Initial problem
    print("\n📝 Step 1: Initial Design Problem")
    result1 = agent.think(
        "Design a REST API for a task management system. Include main endpoints.",
        thinking_budget=3000,
        show_thinking=False
    )
    print(f"✅ Initial Design:\n{result1['answer'][:300]}...\n")
    
    # Step 2: Add complexity
    print("📝 Step 2: Adding Security Requirements")
    result2 = agent.think(
        "Now add authentication, authorization, and rate limiting to the API design.",
        thinking_budget=4000,
        show_thinking=False
    )
    print(f"✅ Security Layer:\n{result2['answer'][:300]}...\n")
    
    # Step 3: Scale consideration
    print("📝 Step 3: Scaling Considerations")
    result3 = agent.think(
        "How would this API need to change to handle 1 million daily active users?",
        thinking_budget=5000,
        show_thinking=False
    )
    print(f"✅ Scaling Strategy:\n{result3['answer'][:300]}...\n")
    
    print(f"📊 Total tokens used across all steps:")
    total_tokens = sum(r["usage"]["output_tokens"] for r in [result1, result2, result3])
    print(f"  Total output tokens: {total_tokens}")


def demo_thinking_transparency():
    """Show how thinking provides transparency in decision-making."""
    print("\n" + "="*60)
    print("Demo 4: Thinking Transparency")
    print("="*60)
    
    agent = BasicSkillsAgent()
    
    problem = """
    Should we use GraphQL or REST for our new mobile app API?
    The app needs to support offline mode, real-time updates,
    and has limited bandwidth constraints.
    """
    
    print(f"\n📝 Decision Problem:\n{problem}")
    print("\n⏳ Processing...\n")
    
    result = agent.think(problem, thinking_budget=5000)
    
    if "error" not in result:
        print("🧠 DECISION-MAKING PROCESS:")
        print("-" * 60)
        # Show first part of thinking
        thinking_lines = result["thinking"].split("\n")[:20]
        print("\n".join(thinking_lines))
        print("\n[... more thinking ...]")
        print("-" * 60)
        
        print("\n💡 FINAL RECOMMENDATION:")
        print(result["answer"])
        
        # Analyze decision-making
        analysis = agent.analyze_thinking(result["thinking"])
        print("\n🔍 Decision Process Metrics:")
        print(f"  Alternatives considered: {analysis['alternatives_explored']}")
        print(f"  Considerations made: {analysis['considerations']}")
        print(f"  Questions asked: {analysis['questions_asked']}")


def demo_adaptive_thinking():
    """Show how to adapt thinking budget based on problem complexity."""
    print("\n" + "="*60)
    print("Demo 5: Adaptive Thinking Budget")
    print("="*60)
    
    def estimate_complexity(problem: str) -> int:
        """Estimate problem complexity and return appropriate thinking budget."""
        complexity_indicators = {
            "design": 1000,
            "architecture": 1500,
            "optimize": 1000,
            "compare": 800,
            "analyze": 1000,
            "complex": 1500,
            "multiple": 800,
            "trade-off": 1000
        }
        
        problem_lower = problem.lower()
        budget = 2000  # Base budget
        
        for indicator, bonus in complexity_indicators.items():
            if indicator in problem_lower:
                budget += bonus
        
        # Cap at reasonable maximum
        return min(budget, 10000)
    
    agent = BasicSkillsAgent()
    
    test_problems = [
        "What is 2 + 2?",
        "Explain binary search algorithm.",
        "Design a distributed caching system with fault tolerance and auto-scaling."
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n{'─'*60}")
        print(f"Test Problem {i}:")
        print(f"{'─'*60}")
        print(f"Problem: {problem}")
        
        budget = estimate_complexity(problem)
        print(f"Estimated complexity → Budget: {budget} tokens")
        
        result = agent.think(problem, thinking_budget=budget, show_thinking=False)
        
        if "error" not in result:
            print(f"✅ Answer: {result['answer'][:150]}...")
            actual_thinking = result["usage"].get("thinking_tokens", 0)
            print(f"📊 Actual thinking used: {actual_thinking} tokens")


if __name__ == "__main__":
    """Run all demonstrations."""
    
    print("\n" + "="*60)
    print("BASIC SKILLS AGENT - EXTENDED THINKING DEMONSTRATIONS")
    print("="*60)
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("Please set your API key in .env file or environment variable")
        exit(1)
    
    try:
        # Run all demos
        demo_basic_usage()
        demo_problem_comparison()
        demo_iterative_thinking()
        demo_thinking_transparency()
        demo_adaptive_thinking()
        
        print("\n" + "="*60)
        print("✅ All demonstrations completed successfully!")
        print("="*60)
        
        print("\n💡 Next Steps:")
        print("  1. Try modifying the thinking_budget values")
        print("  2. Test with your own problems")
        print("  3. Analyze the thinking patterns")
        print("  4. Move on to advanced_skills_agent.py for Computer Use")
        
    except Exception as e:
        print(f"\n❌ Error during demonstrations: {e}")
        print("Please check your API key and internet connection")
