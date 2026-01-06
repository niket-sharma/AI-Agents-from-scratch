"""
Advanced Skills Agent - Computer Use Example

This module demonstrates advanced Claude Skills usage including Computer Use
capabilities for real-world automation tasks.

⚠️  WARNING: Computer Use is a BETA feature that can interact with your system.
    Always run in a sandboxed or isolated environment for safety.

Author: AI Agents Tutorial
Tutorial: 12-claude-skills
"""

import anthropic
import os
import base64
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from PIL import Image, ImageGrab
import io

# Load environment variables
load_dotenv()


class AdvancedSkillsAgent:
    """
    Advanced agent combining Extended Thinking and Computer Use.
    
    Features:
    - Extended Thinking for complex planning
    - Computer Use for UI automation
    - Multi-step task execution
    - Error recovery
    - Safety controls
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 sandbox_mode: bool = True):
        """
        Initialize the advanced agent.
        
        Args:
            api_key: Anthropic API key
            sandbox_mode: If True, adds safety restrictions
        """
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.sandbox_mode = sandbox_mode
        self.conversation_history = []
        self.screen_size = self._get_screen_size()
        
    def _get_screen_size(self) -> tuple:
        """Get screen dimensions."""
        try:
            img = ImageGrab.grab()
            return img.size
        except:
            return (1920, 1080)  # Default
    
    def capture_screen(self, region: Optional[tuple] = None) -> str:
        """
        Capture screen and return as base64.
        
        Args:
            region: Optional (x, y, width, height) to capture specific region
        
        Returns:
            Base64 encoded screenshot
        """
        try:
            if region:
                img = ImageGrab.grab(bbox=region)
            else:
                img = ImageGrab.grab()
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            
            return base64.b64encode(img_bytes).decode()
        except Exception as e:
            print(f"⚠️  Screenshot capture failed: {e}")
            return None
    
    def think_and_plan(self, task: str, thinking_budget: int = 5000) -> Dict:
        """
        Use Extended Thinking to plan a task before execution.
        
        Args:
            task: Task description
            thinking_budget: Tokens for thinking
        
        Returns:
            Planning result with thinking and plan
        """
        print(f"🧠 Planning task with Extended Thinking...")
        
        try:
            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=8000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                },
                messages=[{
                    "role": "user",
                    "content": f"""Plan how to accomplish this task step-by-step:
                    
{task}

Provide a clear, numbered plan with specific actions."""
                }]
            )
            
            result = {"thinking": None, "plan": None}
            
            for block in response.content:
                if block.type == "thinking":
                    result["thinking"] = block.thinking
                elif block.type == "text":
                    result["plan"] = block.text
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def computer_use(self, task: str, max_steps: int = 10, 
                     use_thinking: bool = False) -> Dict:
        """
        Execute a task using Computer Use capability.
        
        ⚠️  This feature can interact with your computer!
        
        Args:
            task: Task to perform
            max_steps: Maximum action steps
            use_thinking: Whether to use Extended Thinking
        
        Returns:
            Execution result
        """
        if self.sandbox_mode:
            print("⚠️  Sandbox mode: Computer Use is simulated")
            return self._simulate_computer_use(task)
        
        print(f"🖥️  Executing Computer Use task...")
        print(f"   Task: {task}")
        print(f"   Max steps: {max_steps}")
        
        steps_taken = 0
        conversation = []
        
        while steps_taken < max_steps:
            # Capture screen
            screenshot = self.capture_screen()
            if not screenshot:
                return {"error": "Failed to capture screen"}
            
            # Build message
            message_content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot
                    }
                },
                {
                    "type": "text",
                    "text": task if steps_taken == 0 else "Continue."
                }
            ]
            
            conversation.append({
                "role": "user",
                "content": message_content
            })
            
            # Build request
            request_params = {
                "model": "claude-opus-4-20250514",
                "max_tokens": 4096,
                "tools": [{
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": self.screen_size[0],
                    "display_height_px": self.screen_size[1]
                }],
                "messages": conversation
            }
            
            # Add thinking if requested
            if use_thinking and steps_taken == 0:
                request_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": 3000
                }
            
            try:
                response = self.client.messages.create(**request_params)
            except Exception as e:
                return {
                    "error": str(e),
                    "steps_taken": steps_taken
                }
            
            # Check if task is complete
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            
            if not tool_uses:
                # Task completed
                text_blocks = [b.text for b in response.content if b.type == "text"]
                return {
                    "success": True,
                    "message": " ".join(text_blocks),
                    "steps_taken": steps_taken
                }
            
            # Execute tool uses (in real implementation)
            # NOTE: Actual execution would happen here
            print(f"   Step {steps_taken + 1}: {len(tool_uses)} action(s)")
            
            conversation.append({
                "role": "assistant",
                "content": response.content
            })
            
            steps_taken += len(tool_uses)
            time.sleep(1)  # Rate limiting
        
        return {
            "success": False,
            "message": "Max steps reached",
            "steps_taken": steps_taken
        }
    
    def _simulate_computer_use(self, task: str) -> Dict:
        """Simulate Computer Use for demo purposes."""
        return {
            "simulated": True,
            "message": f"Would execute: {task}",
            "note": "Set sandbox_mode=False for real execution (use caution!)"
        }
    
    def hybrid_task(self, task: str, thinking_budget: int = 5000,
                   max_execution_steps: int = 10) -> Dict:
        """
        Execute a task using both Extended Thinking and Computer Use.
        
        Process:
        1. Use Extended Thinking to plan
        2. Use Computer Use to execute plan
        3. Verify and report results
        
        Args:
            task: Task description
            thinking_budget: Tokens for planning
            max_execution_steps: Max steps for execution
        
        Returns:
            Complete execution result
        """
        print("="*60)
        print("🚀 Hybrid Task Execution")
        print("="*60)
        
        # Step 1: Plan with thinking
        print("\n📋 Phase 1: Planning")
        plan_result = self.think_and_plan(task, thinking_budget)
        
        if "error" in plan_result:
            return {"error": f"Planning failed: {plan_result['error']}"}
        
        print(f"✅ Plan created:")
        print(plan_result["plan"][:300] + "..." if len(plan_result["plan"]) > 300 else plan_result["plan"])
        
        # Step 2: Execute with Computer Use
        print("\n🖥️  Phase 2: Execution")
        exec_result = self.computer_use(task, max_execution_steps)
        
        if "error" in exec_result:
            return {
                "planning": plan_result,
                "execution": exec_result,
                "success": False
            }
        
        print(f"✅ Execution completed in {exec_result.get('steps_taken', 0)} steps")
        
        return {
            "planning": plan_result,
            "execution": exec_result,
            "success": True
        }


def demo_extended_thinking_planning():
    """Demo: Use Extended Thinking for complex planning."""
    print("\n" + "="*60)
    print("Demo 1: Extended Thinking for Planning")
    print("="*60)
    
    agent = AdvancedSkillsAgent(sandbox_mode=True)
    
    task = """
    Automate the process of:
    1. Opening a spreadsheet application
    2. Creating a new sheet
    3. Adding headers: Name, Email, Status
    4. Filling in 5 sample rows
    5. Saving the file as 'contacts.xlsx'
    """
    
    result = agent.think_and_plan(task, thinking_budget=5000)
    
    if "error" not in result:
        print("\n🧠 THINKING PROCESS (First 500 chars):")
        print("-" * 60)
        print(result["thinking"][:500] + "...")
        print("-" * 60)
        
        print("\n📋 EXECUTION PLAN:")
        print("-" * 60)
        print(result["plan"])
        print("-" * 60)


def demo_computer_use_simulation():
    """Demo: Simulate Computer Use (safe for demo)."""
    print("\n" + "="*60)
    print("Demo 2: Computer Use Simulation")
    print("="*60)
    
    agent = AdvancedSkillsAgent(sandbox_mode=True)
    
    tasks = [
        "Open calculator and compute 157 * 89",
        "Open text editor and type 'Hello World'",
        "Take a screenshot of the current screen"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{'─'*60}")
        print(f"Task {i}: {task}")
        print(f"{'─'*60}")
        
        result = agent.computer_use(task, max_steps=5)
        
        print(f"Result: {result}")


def demo_hybrid_execution():
    """Demo: Combine thinking and computer use."""
    print("\n" + "="*60)
    print("Demo 3: Hybrid Execution (Thinking + Computer Use)")
    print("="*60)
    
    agent = AdvancedSkillsAgent(sandbox_mode=True)
    
    task = """
    Create a simple to-do list:
    - Open a note-taking app
    - Create a list with 3 items
    - Save it as 'My Tasks'
    """
    
    result = agent.hybrid_task(
        task,
        thinking_budget=3000,
        max_execution_steps=8
    )
    
    if result.get("success"):
        print("\n✅ HYBRID TASK COMPLETED SUCCESSFULLY")
        print("\nPlanning insights:")
        print(f"  - Plan length: {len(result['planning']['plan'].split())} words")
        print("\nExecution results:")
        print(f"  - Steps taken: {result['execution'].get('steps_taken', 0)}")
        print(f"  - Status: {result['execution'].get('message', 'N/A')}")
    else:
        print("\n❌ TASK FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")


def demo_screen_analysis():
    """Demo: Analyze screen content (requires actual screen)."""
    print("\n" + "="*60)
    print("Demo 4: Screen Content Analysis")
    print("="*60)
    
    agent = AdvancedSkillsAgent(sandbox_mode=True)
    
    print("\n📸 Capturing screen...")
    screenshot = agent.capture_screen()
    
    if screenshot:
        print(f"✅ Screen captured successfully")
        print(f"   Data size: {len(screenshot)} bytes")
        print(f"   Screen size: {agent.screen_size}")
        
        # In real scenario, would send to Claude for analysis
        print("\n💡 In production, this screenshot would be sent to Claude")
        print("   for analysis and action planning.")
    else:
        print("❌ Screen capture unavailable")


def demo_error_handling():
    """Demo: Error handling and recovery."""
    print("\n" + "="*60)
    print("Demo 5: Error Handling")
    print("="*60)
    
    agent = AdvancedSkillsAgent(sandbox_mode=True)
    
    # Test error scenarios
    scenarios = [
        {
            "name": "Invalid task",
            "task": "",  # Empty task
            "expected": "Should handle empty input"
        },
        {
            "name": "Complex task with thinking",
            "task": "Design and implement a complete CI/CD pipeline",
            "expected": "Should plan thoroughly"
        },
        {
            "name": "Step limit test",
            "task": "Perform 100 sequential operations",
            "expected": "Should stop at max_steps"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'─'*60}")
        print(f"Scenario: {scenario['name']}")
        print(f"Expected: {scenario['expected']}")
        print(f"{'─'*60}")
        
        try:
            result = agent.think_and_plan(scenario['task'], thinking_budget=2000)
            if "error" in result:
                print(f"⚠️  Error caught: {result['error']}")
            else:
                print(f"✅ Handled successfully")
        except Exception as e:
            print(f"❌ Exception: {e}")


def demo_multi_step_workflow():
    """Demo: Complex multi-step workflow."""
    print("\n" + "="*60)
    print("Demo 6: Multi-Step Workflow")
    print("="*60)
    
    agent = AdvancedSkillsAgent(sandbox_mode=True)
    
    workflow = [
        "Analyze current system state",
        "Identify optimization opportunities",
        "Plan implementation steps",
        "Execute optimizations",
        "Verify improvements"
    ]
    
    print("\n📋 Workflow Steps:")
    for i, step in enumerate(workflow, 1):
        print(f"  {i}. {step}")
    
    print("\n🔄 Executing workflow...\n")
    
    for i, step in enumerate(workflow, 1):
        print(f"{'─'*60}")
        print(f"Step {i}/{len(workflow)}: {step}")
        print(f"{'─'*60}")
        
        # Plan each step
        result = agent.think_and_plan(step, thinking_budget=2000)
        
        if "error" not in result:
            print(f"✅ Planned")
            print(f"   Preview: {result['plan'][:100]}...")
        else:
            print(f"❌ Failed: {result['error']}")
            break
        
        time.sleep(0.5)  # Simulate work
    
    print("\n✅ Workflow completed")


class SafetyController:
    """Safety controls for Computer Use."""
    
    BLOCKED_ACTIONS = [
        "delete system",
        "format drive",
        "sudo rm",
        "shutdown",
        "reboot"
    ]
    
    ALLOWED_DIRECTORIES = [
        "/tmp",
        "/home/user/sandbox",
        "/home/user/Documents/test"
    ]
    
    @staticmethod
    def validate_action(action: str) -> tuple[bool, str]:
        """
        Validate if an action is safe to execute.
        
        Returns:
            (is_safe, reason)
        """
        action_lower = action.lower()
        
        # Check for blocked actions
        for blocked in SafetyController.BLOCKED_ACTIONS:
            if blocked in action_lower:
                return False, f"Blocked action detected: {blocked}"
        
        # Check directory restrictions
        if "cd " in action_lower or "chdir" in action_lower:
            for directory in action_lower.split():
                if directory.startswith("/"):
                    if not any(directory.startswith(allowed) 
                             for allowed in SafetyController.ALLOWED_DIRECTORIES):
                        return False, f"Directory not allowed: {directory}"
        
        return True, "Action approved"


def demo_safety_controls():
    """Demo: Safety controls for Computer Use."""
    print("\n" + "="*60)
    print("Demo 7: Safety Controls")
    print("="*60)
    
    test_actions = [
        "open calculator app",
        "delete system files",  # Should be blocked
        "cd /tmp && create test.txt",
        "sudo rm -rf /",  # Should be blocked
        "open text editor"
    ]
    
    print("\n🛡️  Testing safety controls:\n")
    
    for action in test_actions:
        is_safe, reason = SafetyController.validate_action(action)
        status = "✅ SAFE" if is_safe else "🚫 BLOCKED"
        print(f"{status} | {action}")
        print(f"         → {reason}\n")


if __name__ == "__main__":
    """Run all demonstrations."""
    
    print("\n" + "="*60)
    print("ADVANCED SKILLS AGENT - DEMONSTRATIONS")
    print("="*60)
    print("\n⚠️  NOTE: Running in SANDBOX MODE for safety")
    print("   Set sandbox_mode=False for real Computer Use (use caution!)\n")
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found")
        print("Please set your API key in .env file")
        exit(1)
    
    try:
        # Run demos
        demo_extended_thinking_planning()
        demo_computer_use_simulation()
        demo_hybrid_execution()
        demo_screen_analysis()
        demo_error_handling()
        demo_multi_step_workflow()
        demo_safety_controls()
        
        print("\n" + "="*60)
        print("✅ All demonstrations completed!")
        print("="*60)
        
        print("\n⚠️  IMPORTANT SAFETY REMINDERS:")
        print("  • Always run Computer Use in isolated environments")
        print("  • Implement strict safety controls")
        print("  • Never use on production systems")
        print("  • Monitor all actions closely")
        print("  • Review safety guidelines in SKILLS_EXPLAINED.md")
        
        print("\n💡 Next Steps:")
        print("  1. Review the safety controls implementation")
        print("  2. Test in a Docker container or VM")
        print("  3. Build your own automation tasks")
        print("  4. Check out skills_comparison.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
