"""
Exercises: Claude Skills Practice

Complete these exercises to master Extended Thinking and Computer Use.
Each exercise includes a problem, hints, and solution.

Author: AI Agents Tutorial
Tutorial: 12-claude-skills
"""

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Exercise 1: Basic Extended Thinking
# =============================================================================

def exercise_1_problem():
    """
    Exercise 1: Algorithm Analysis
    
    Problem:
    Create an agent that uses Extended Thinking to analyze and compare
    three sorting algorithms (Bubble Sort, Merge Sort, Quick Sort).
    
    Requirements:
    - Use Extended Thinking with appropriate token budget
    - Compare time complexity, space complexity, and use cases
    - Provide a recommendation for different scenarios
    - Show the thinking process
    
    Hints:
    - Set thinking_budget to at least 5000 tokens
    - Ask for detailed analysis of trade-offs
    - Extract and display the thinking process
    """
    print("="*70)
    print("EXERCISE 1: Algorithm Analysis with Extended Thinking")
    print("="*70)
    print("\nTODO: Implement an agent that analyzes sorting algorithms")
    print("See solution_exercise_1() for reference\n")


def solution_exercise_1():
    """Solution for Exercise 1."""
    print("="*70)
    print("SOLUTION 1: Algorithm Analysis")
    print("="*70)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    problem = """
    Analyze and compare these three sorting algorithms:
    1. Bubble Sort
    2. Merge Sort
    3. Quick Sort
    
    For each, consider:
    - Time complexity (best, average, worst case)
    - Space complexity
    - Stability
    - When to use each one
    
    Provide a detailed recommendation for different scenarios.
    """
    
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=16000,
        thinking={
            "type": "enabled",
            "budget_tokens": 6000
        },
        messages=[{
            "role": "user",
            "content": problem
        }]
    )
    
    # Extract and display
    for block in response.content:
        if block.type == "thinking":
            print("\n🧠 THINKING PROCESS:")
            print("-" * 70)
            print(block.thinking[:500] + "...\n")
        elif block.type == "text":
            print("💡 ANALYSIS & RECOMMENDATION:")
            print("-" * 70)
            print(block.text)
    
    print("\n✅ Exercise 1 Complete!")


# =============================================================================
# Exercise 2: Adaptive Thinking Budget
# =============================================================================

def exercise_2_problem():
    """
    Exercise 2: Adaptive Thinking Budget
    
    Problem:
    Implement a function that automatically determines the appropriate
    thinking budget based on problem complexity.
    
    Requirements:
    - Analyze the input question to estimate complexity
    - Return a thinking budget between 1000-10000 tokens
    - Consider keywords, length, and structural complexity
    - Test with various questions
    
    Hints:
    - Look for complexity indicators (design, analyze, compare, etc.)
    - Consider question length
    - Check for multiple sub-questions
    """
    print("="*70)
    print("EXERCISE 2: Adaptive Thinking Budget")
    print("="*70)
    print("\nTODO: Implement adaptive_thinking_budget() function")
    print("See solution_exercise_2() for reference\n")


def solution_exercise_2():
    """Solution for Exercise 2."""
    print("="*70)
    print("SOLUTION 2: Adaptive Thinking Budget")
    print("="*70)
    
    def adaptive_thinking_budget(question: str) -> int:
        """Calculate appropriate thinking budget for a question."""
        
        # Base budget
        budget = 2000
        
        # Complexity indicators
        high_complexity = ["design", "architect", "analyze", "compare", 
                          "optimize", "strategy", "evaluate"]
        medium_complexity = ["explain", "describe", "implement", "create"]
        
        question_lower = question.lower()
        
        # Check for high complexity keywords
        for keyword in high_complexity:
            if keyword in question_lower:
                budget += 1500
        
        # Check for medium complexity keywords
        for keyword in medium_complexity:
            if keyword in question_lower:
                budget += 800
        
        # Consider length (longer questions often more complex)
        word_count = len(question.split())
        if word_count > 100:
            budget += 2000
        elif word_count > 50:
            budget += 1000
        
        # Check for multiple questions
        question_marks = question.count("?")
        budget += (question_marks - 1) * 500
        
        # Check for numbered lists (indicates multi-part question)
        if any(f"{i}." in question for i in range(1, 10)):
            budget += 1000
        
        # Cap at reasonable maximum
        return min(max(budget, 1000), 10000)
    
    # Test with various questions
    test_questions = [
        "What is 2 + 2?",
        "Explain how binary search works.",
        "Design a distributed system for real-time analytics handling 1M users. "
        "Consider: scalability, fault tolerance, data consistency, cost optimization, "
        "and deployment strategy. Compare at least 3 architectural approaches.",
        "Compare SQL and NoSQL databases. What are the trade-offs?"
    ]
    
    print("\nTesting adaptive budget calculation:\n")
    for i, question in enumerate(test_questions, 1):
        budget = adaptive_thinking_budget(question)
        print(f"Question {i}:")
        print(f"  Text: {question[:60]}...")
        print(f"  Estimated Budget: {budget} tokens")
        print(f"  Complexity: {'Low' if budget < 3000 else 'Medium' if budget < 6000 else 'High'}\n")
    
    print("✅ Exercise 2 Complete!")


# =============================================================================
# Exercise 3: Thinking Analysis
# =============================================================================

def exercise_3_problem():
    """
    Exercise 3: Analyze Thinking Patterns
    
    Problem:
    Create a function that analyzes the thinking process from a response
    and extracts useful metrics and insights.
    
    Requirements:
    - Count reasoning steps
    - Identify alternatives considered
    - Extract key decision points
    - Measure thinking depth
    - Generate a summary report
    
    Hints:
    - Look for numbered steps or bullet points
    - Count occurrences of words like "consider", "alternative", "however"
    - Analyze sentence structure
    """
    print("="*70)
    print("EXERCISE 3: Thinking Pattern Analysis")
    print("="*70)
    print("\nTODO: Implement analyze_thinking() function")
    print("See solution_exercise_3() for reference\n")


def solution_exercise_3():
    """Solution for Exercise 3."""
    print("="*70)
    print("SOLUTION 3: Thinking Pattern Analysis")
    print("="*70)
    
    def analyze_thinking(thinking_text: str) -> dict:
        """Analyze thinking patterns and extract insights."""
        
        if not thinking_text:
            return {"error": "No thinking content provided"}
        
        lines = thinking_text.split("\n")
        words = thinking_text.split()
        sentences = thinking_text.split(".")
        
        analysis = {
            "metrics": {
                "total_lines": len(lines),
                "total_words": len(words),
                "total_sentences": len(sentences),
                "avg_words_per_sentence": len(words) / max(len(sentences), 1)
            },
            "reasoning_patterns": {
                "steps_identified": thinking_text.count("Step"),
                "considerations": thinking_text.count("consider"),
                "alternatives": thinking_text.count("alternative"),
                "comparisons": thinking_text.count("compare") + thinking_text.count("versus"),
                "questions_asked": thinking_text.count("?"),
                "caveats": thinking_text.count("however") + thinking_text.count("but"),
            },
            "decision_indicators": {
                "pros_cons": thinking_text.count("pro") + thinking_text.count("con"),
                "trade_offs": thinking_text.count("trade-off") + thinking_text.count("tradeoff"),
                "recommendations": thinking_text.count("recommend") + thinking_text.count("suggest"),
            },
            "depth_score": 0  # Will calculate below
        }
        
        # Calculate depth score (0-100)
        depth_score = 0
        depth_score += min(analysis["reasoning_patterns"]["steps_identified"] * 5, 20)
        depth_score += min(analysis["reasoning_patterns"]["alternatives"] * 10, 30)
        depth_score += min(analysis["reasoning_patterns"]["considerations"] * 3, 20)
        depth_score += min(analysis["decision_indicators"]["trade_offs"] * 10, 15)
        depth_score += min(len(lines) / 10, 15)
        
        analysis["depth_score"] = min(int(depth_score), 100)
        
        return analysis
    
    # Test with example thinking
    example_thinking = """
    Let me think through this step by step.
    
    Step 1: Consider the requirements
    We need to handle high throughput and low latency.
    
    Step 2: Evaluate alternatives
    Alternative 1: Use a monolithic architecture - simpler but less scalable
    Alternative 2: Use microservices - more complex but better scalability
    
    Step 3: Compare trade-offs
    The trade-off here is complexity versus scalability. However, given the 
    scale requirements, microservices seem necessary.
    
    Step 4: Consider implementation
    What about data consistency? This is a key question.
    
    I would recommend starting with microservices, but...
    """
    
    result = analyze_thinking(example_thinking)
    
    print("\n📊 THINKING ANALYSIS REPORT:\n")
    print("Metrics:")
    for key, value in result["metrics"].items():
        print(f"  {key}: {value}")
    
    print("\nReasoning Patterns:")
    for key, value in result["reasoning_patterns"].items():
        print(f"  {key}: {value}")
    
    print("\nDecision Indicators:")
    for key, value in result["decision_indicators"].items():
        print(f"  {key}: {value}")
    
    print(f"\nDepth Score: {result['depth_score']}/100")
    
    print("\n✅ Exercise 3 Complete!")


# =============================================================================
# Exercise 4: Hybrid Agent
# =============================================================================

def exercise_4_problem():
    """
    Exercise 4: Build a Hybrid Agent
    
    Problem:
    Create an agent that intelligently combines Extended Thinking with
    traditional tools based on the task requirements.
    
    Requirements:
    - Define at least 2 traditional tools (calculator, database)
    - Use Extended Thinking for planning phase
    - Use tools for execution phase
    - Handle errors gracefully
    - Return comprehensive results
    
    Hints:
    - First request uses thinking to plan
    - Second request uses tools to execute
    - Track both thinking and tool usage
    """
    print("="*70)
    print("EXERCISE 4: Hybrid Agent Implementation")
    print("="*70)
    print("\nTODO: Implement HybridSkillsAgent class")
    print("See solution_exercise_4() for reference\n")


def solution_exercise_4():
    """Solution for Exercise 4."""
    print("="*70)
    print("SOLUTION 4: Hybrid Agent")
    print("="*70)
    
    class HybridSkillsAgent:
        """Agent combining Extended Thinking and traditional tools."""
        
        def __init__(self):
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.tools = self._define_tools()
        
        def _define_tools(self):
            return [{
                "name": "calculator",
                "description": "Perform precise calculations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    },
                    "required": ["expression"]
                }
            }]
        
        def process(self, task: str) -> dict:
            """Process task with thinking then tools."""
            
            # Phase 1: Plan with thinking
            print("🧠 Phase 1: Planning with Extended Thinking...")
            plan_response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=8000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 3000
                },
                messages=[{
                    "role": "user",
                    "content": f"Plan how to solve this: {task}"
                }]
            )
            
            plan = None
            for block in plan_response.content:
                if block.type == "text":
                    plan = block.text
            
            print(f"✅ Plan created: {plan[:100]}...")
            
            # Phase 2: Execute with tools
            print("\n🔧 Phase 2: Executing with Tools...")
            exec_response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=4096,
                tools=self.tools,
                messages=[{
                    "role": "user",
                    "content": f"Execute this plan: {plan}"
                }]
            )
            
            # Check for tool uses
            tool_calls = []
            final_answer = None
            
            for block in exec_response.content:
                if block.type == "tool_use":
                    tool_calls.append({
                        "tool": block.name,
                        "input": block.input
                    })
                elif block.type == "text":
                    final_answer = block.text
            
            return {
                "plan": plan,
                "tool_calls": tool_calls,
                "answer": final_answer,
                "success": True
            }
    
    # Test the hybrid agent
    agent = HybridSkillsAgent()
    
    task = "Calculate the compound interest on $10,000 at 5% for 3 years"
    
    result = agent.process(task)
    
    print("\n" + "="*70)
    print("RESULTS:")
    print("="*70)
    print(f"\nPlan:\n{result['plan']}\n")
    print(f"Tool Calls: {len(result['tool_calls'])}")
    print(f"Answer: {result['answer']}")
    
    print("\n✅ Exercise 4 Complete!")


# =============================================================================
# Exercise 5: Error Recovery
# =============================================================================

def exercise_5_problem():
    """
    Exercise 5: Implement Error Recovery
    
    Problem:
    Create a robust skills agent that handles various error scenarios
    and implements fallback strategies.
    
    Requirements:
    - Handle API errors (rate limits, invalid requests)
    - Implement fallback from Extended Thinking to standard mode
    - Retry logic with exponential backoff
    - Comprehensive error reporting
    
    Hints:
    - Use try-except blocks
    - Check for specific error types
    - Implement retry counter
    - Provide meaningful error messages
    """
    print("="*70)
    print("EXERCISE 5: Error Recovery")
    print("="*70)
    print("\nTODO: Implement RobustSkillsAgent with error handling")
    print("See solution_exercise_5() for reference\n")


def solution_exercise_5():
    """Solution for Exercise 5."""
    print("="*70)
    print("SOLUTION 5: Error Recovery")
    print("="*70)
    
    import time
    
    class RobustSkillsAgent:
        """Agent with comprehensive error handling."""
        
        def __init__(self):
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        def process_with_retry(self, task: str, max_retries: int = 3) -> dict:
            """Process with retry logic and fallbacks."""
            
            for attempt in range(max_retries):
                try:
                    # Try with Extended Thinking
                    print(f"Attempt {attempt + 1}: Using Extended Thinking...")
                    
                    response = self.client.messages.create(
                        model="claude-opus-4-20250514",
                        max_tokens=8000,
                        thinking={
                            "type": "enabled",
                            "budget_tokens": 5000
                        },
                        messages=[{
                            "role": "user",
                            "content": task
                        }]
                    )
                    
                    # Extract answer
                    answer = None
                    for block in response.content:
                        if block.type == "text":
                            answer = block.text
                    
                    return {
                        "success": True,
                        "answer": answer,
                        "mode": "extended_thinking",
                        "attempts": attempt + 1
                    }
                
                except anthropic.RateLimitError:
                    print(f"⚠️  Rate limit hit, waiting...")
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                
                except Exception as e:
                    if "thinking" in str(e).lower():
                        # Fallback to standard mode
                        print(f"⚠️  Extended Thinking unavailable, using standard mode...")
                        
                        try:
                            response = self.client.messages.create(
                                model="claude-opus-4-20250514",
                                max_tokens=4096,
                                messages=[{
                                    "role": "user",
                                    "content": task
                                }]
                            )
                            
                            answer = response.content[0].text
                            
                            return {
                                "success": True,
                                "answer": answer,
                                "mode": "standard_fallback",
                                "attempts": attempt + 1
                            }
                        
                        except Exception as fallback_error:
                            print(f"❌ Fallback also failed: {fallback_error}")
                            continue
                    else:
                        print(f"❌ Error: {e}")
                        continue
            
            return {
                "success": False,
                "error": "Max retries exceeded",
                "attempts": max_retries
            }
    
    # Test the robust agent
    agent = RobustSkillsAgent()
    
    test_cases = [
        "What is the capital of France?",  # Simple
        "Design a scalable API architecture"  # Complex
    ]
    
    for task in test_cases:
        print(f"\nTesting: {task}")
        print("-" * 70)
        result = agent.process_with_retry(task, max_retries=2)
        
        if result["success"]:
            print(f"✅ Success (mode: {result['mode']}, attempts: {result['attempts']})")
            print(f"Answer: {result['answer'][:100]}...")
        else:
            print(f"❌ Failed: {result.get('error')}")
        print()
    
    print("✅ Exercise 5 Complete!")


# =============================================================================
# Main Runner
# =============================================================================

def run_all_exercises():
    """Run all exercise problems."""
    print("\n" + "="*70)
    print("CLAUDE SKILLS - PRACTICE EXERCISES")
    print("="*70)
    print("\nComplete each exercise to master Claude Skills!\n")
    
    exercise_1_problem()
    exercise_2_problem()
    exercise_3_problem()
    exercise_4_problem()
    exercise_5_problem()
    
    print("\n" + "="*70)
    print("💡 When ready, run solutions with:")
    print("   python exercises.py --solutions")
    print("="*70)


def run_all_solutions():
    """Run all exercise solutions."""
    print("\n" + "="*70)
    print("CLAUDE SKILLS - EXERCISE SOLUTIONS")
    print("="*70)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ Error: ANTHROPIC_API_KEY not found")
        exit(1)
    
    try:
        solution_exercise_1()
        print("\n" + "─"*70 + "\n")
        
        solution_exercise_2()
        print("\n" + "─"*70 + "\n")
        
        solution_exercise_3()
        print("\n" + "─"*70 + "\n")
        
        solution_exercise_4()
        print("\n" + "─"*70 + "\n")
        
        solution_exercise_5()
        
        print("\n" + "="*70)
        print("🎉 All exercises completed!")
        print("="*70)
        
        print("\n📚 Additional Challenges:")
        print("  1. Combine exercises 2 and 4 for an adaptive hybrid agent")
        print("  2. Add Computer Use capabilities to the hybrid agent")
        print("  3. Implement caching for thinking results")
        print("  4. Build a skills orchestrator that chooses optimal approach")
        print("  5. Create a production-ready agent with monitoring")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if "--solutions" in sys.argv:
        run_all_solutions()
    else:
        run_all_exercises()
