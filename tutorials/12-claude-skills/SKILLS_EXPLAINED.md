# Claude Skills: Deep Dive

A comprehensive guide to understanding how Claude's Skills work under the hood.

## Table of Contents

1. [What Are Skills?](#what-are-skills)
2. [Extended Thinking](#extended-thinking)
3. [Computer Use](#computer-use)
4. [Skills vs Tools](#skills-vs-tools)
5. [Technical Architecture](#technical-architecture)
6. [Performance Characteristics](#performance-characteristics)
7. [Limitations](#limitations)

---

## What Are Skills?

Skills are specialized capabilities built into Claude that extend beyond traditional language model interactions. Unlike tools (which are external functions the model can call), Skills are **native capabilities** that change how Claude processes information.

### Core Differences

| Aspect | Traditional LLM | Skills-Enhanced LLM |
|--------|----------------|---------------------|
| Processing | Single-pass generation | Multi-step reasoning |
| Interaction | Text only | Text + environment |
| Reasoning | Fast, intuitive | Deep, analytical |
| Transparency | Opaque | Transparent (thinking visible) |

---

## Extended Thinking

### How It Works

Extended Thinking is a mode where Claude allocates additional computational resources to reason through problems before generating a response.

#### Normal Mode
```
User Input → Model Processing → Response
    (0.5-2 seconds)
```

#### Extended Thinking Mode
```
User Input → Thinking Phase → Response Generation
            (2-30 seconds)    (1-5 seconds)
```

### The Thinking Process

When Extended Thinking is enabled, Claude:

1. **Problem Analysis**
   - Breaks down the question into components
   - Identifies key constraints and requirements
   - Determines what knowledge is needed

2. **Exploration**
   - Considers multiple approaches
   - Evaluates pros and cons
   - Explores edge cases

3. **Refinement**
   - Synthesizes insights
   - Validates reasoning
   - Structures final response

4. **Response Generation**
   - Presents conclusions
   - Provides explanations
   - Offers recommendations

### Example: Problem Decomposition

**Problem:** "Design a caching system for a web application"

**Without Extended Thinking:**
```
Response: "Here's a basic caching approach using Redis:
[direct implementation]"
```

**With Extended Thinking:**
```
🧠 Thinking:
Let me break this down:

1. Requirements analysis:
   - Need to understand: scale, data types, consistency needs
   - Consider: read/write ratio, data volatility, budget

2. Caching strategies:
   - Cache-aside: Good for read-heavy, but cache misses expensive
   - Write-through: Better consistency, higher latency
   - Write-behind: Best performance, risk of data loss

3. Technology options:
   - Redis: Fast, but in-memory, limited by RAM
   - Memcached: Simpler, no persistence
   - CDN: Great for static assets

4. Architecture considerations:
   - Need cache invalidation strategy
   - Consider distributed caching for scale
   - Plan for cache warming

💡 Response:
Based on the analysis, here's a comprehensive caching design:
[detailed, well-reasoned implementation]
```

### Token Budget

The `budget_tokens` parameter controls thinking depth:

```python
# Light thinking (quick problems)
thinking={"type": "enabled", "budget_tokens": 1000}

# Moderate thinking (standard complexity)
thinking={"type": "enabled", "budget_tokens": 5000}

# Deep thinking (very complex problems)
thinking={"type": "enabled", "budget_tokens": 10000}
```

**Token Usage Guidelines:**

| Problem Type | Recommended Budget | Expected Thinking Time |
|-------------|-------------------|----------------------|
| Simple analysis | 1,000-2,000 | 2-5 seconds |
| Medium complexity | 3,000-5,000 | 5-15 seconds |
| Complex reasoning | 5,000-10,000 | 15-30 seconds |
| Research tasks | 10,000+ | 30+ seconds |

### Accessing Thinking Content

```python
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 5000},
    messages=[{"role": "user", "content": "Complex problem..."}]
)

for block in response.content:
    if block.type == "thinking":
        # This is the internal reasoning
        thinking_text = block.thinking
        
        # You can analyze it
        steps = thinking_text.count("Step")
        considerations = thinking_text.count("Consider")
        alternatives = thinking_text.count("alternative")
        
        print(f"Reasoning depth: {steps} steps")
        print(f"Considerations: {considerations}")
        print(f"Alternatives explored: {alternatives}")
        
    elif block.type == "text":
        # This is the final response
        final_answer = block.text
```

### Best Practices for Extended Thinking

#### 1. Appropriate Problem Selection

```python
def should_use_thinking(question: str) -> bool:
    """Determine if a question benefits from extended thinking."""
    
    complexity_indicators = [
        "design", "architect", "strategy", "compare",
        "optimize", "trade-offs", "analyze", "plan"
    ]
    
    # Check for complexity indicators
    question_lower = question.lower()
    complexity_score = sum(
        1 for indicator in complexity_indicators 
        if indicator in question_lower
    )
    
    # Also check length (longer questions often more complex)
    length_score = len(question.split()) > 50
    
    return complexity_score >= 2 or length_score
```

#### 2. Dynamic Budget Allocation

```python
def adaptive_thinking_budget(question: str) -> int:
    """Allocate thinking budget based on question complexity."""
    
    # Base budget
    budget = 2000
    
    # Increase for certain keywords
    complex_keywords = ["multiple", "various", "comprehensive", "detailed"]
    for keyword in complex_keywords:
        if keyword in question.lower():
            budget += 1000
    
    # Increase for longer questions
    word_count = len(question.split())
    if word_count > 100:
        budget += 2000
    elif word_count > 50:
        budget += 1000
    
    # Cap at maximum
    return min(budget, 10000)
```

#### 3. Thinking Transparency

```python
def transparent_thinking_agent(problem: str, show_thinking: bool = True) -> dict:
    """Agent that optionally shows thinking to users."""
    
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=16000,
        thinking={"type": "enabled", "budget_tokens": 5000},
        messages=[{"role": "user", "content": problem}]
    )
    
    result = {"answer": None, "reasoning_summary": None}
    
    for block in response.content:
        if block.type == "thinking":
            if show_thinking:
                # Show full thinking
                result["reasoning_summary"] = block.thinking
            else:
                # Show summary only
                lines = block.thinking.split("\n")
                key_points = [l for l in lines if l.startswith(("1.", "2.", "3.", "-"))]
                result["reasoning_summary"] = "\n".join(key_points[:5])
                
        elif block.type == "text":
            result["answer"] = block.text
    
    return result
```

---

## Computer Use

### How It Works

Computer Use enables Claude to interact with computer interfaces through a multi-modal approach:

1. **Vision**: Analyze screenshots to understand UI state
2. **Planning**: Determine necessary actions
3. **Execution**: Issue mouse/keyboard commands
4. **Verification**: Check if actions succeeded

### Architecture

```
┌─────────────────────────────────────┐
│         Your Application            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│      Computer Use Interface         │
│  ┌─────────────────────────────┐   │
│  │  Screen Capture Module      │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  Action Executor            │   │
│  │  - Mouse control            │   │
│  │  - Keyboard input           │   │
│  │  - Shell commands           │   │
│  └─────────────────────────────┘   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│       Operating System              │
└─────────────────────────────────────┘
```

### Available Actions

#### 1. Mouse Operations

```python
# Click at coordinates
{
    "type": "mouse_click",
    "x": 500,
    "y": 300,
    "button": "left"  # or "right", "middle"
}

# Move mouse
{
    "type": "mouse_move",
    "x": 750,
    "y": 400
}

# Drag
{
    "type": "mouse_drag",
    "start_x": 100,
    "start_y": 100,
    "end_x": 500,
    "end_y": 500
}
```

#### 2. Keyboard Operations

```python
# Type text
{
    "type": "keyboard_type",
    "text": "Hello World"
}

# Press keys
{
    "type": "keyboard_press",
    "key": "Enter"
}

# Keyboard shortcuts
{
    "type": "keyboard_combo",
    "keys": ["Ctrl", "C"]  # Copy
}
```

#### 3. Shell Commands

```python
# Execute command
{
    "type": "shell_execute",
    "command": "ls -la /home/user/documents",
    "timeout": 10
}
```

### Implementation Example

```python
import anthropic
import base64
from PIL import ImageGrab
import pyautogui
import time

class ComputerUseAgent:
    """Agent that can interact with computer interfaces."""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.screen_size = pyautogui.size()
    
    def capture_screen(self) -> str:
        """Capture and encode screen."""
        screenshot = ImageGrab.grab()
        screenshot.save("/tmp/screen.png")
        
        with open("/tmp/screen.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    
    def execute_action(self, action: dict):
        """Execute a computer action."""
        action_type = action.get("type")
        
        if action_type == "mouse_click":
            pyautogui.click(action["x"], action["y"], button=action.get("button", "left"))
        
        elif action_type == "mouse_move":
            pyautogui.moveTo(action["x"], action["y"])
        
        elif action_type == "keyboard_type":
            pyautogui.typewrite(action["text"], interval=0.1)
        
        elif action_type == "keyboard_press":
            pyautogui.press(action["key"])
        
        elif action_type == "keyboard_combo":
            pyautogui.hotkey(*action["keys"])
        
        time.sleep(0.5)  # Allow UI to update
    
    def perform_task(self, task: str, max_steps: int = 10) -> dict:
        """Perform a computer task."""
        
        conversation = []
        steps_taken = 0
        
        while steps_taken < max_steps:
            # Capture current screen
            screen_data = self.capture_screen()
            
            # Send to Claude
            messages = conversation + [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screen_data
                        }
                    },
                    {
                        "type": "text",
                        "text": task if steps_taken == 0 else "Continue with the task."
                    }
                ]
            }]
            
            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=4096,
                tools=[{
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": self.screen_size[0],
                    "display_height_px": self.screen_size[1]
                }],
                messages=messages
            )
            
            # Process response
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            
            if not tool_uses:
                # Task completed
                text_blocks = [block.text for block in response.content if block.type == "text"]
                return {
                    "success": True,
                    "steps": steps_taken,
                    "message": " ".join(text_blocks)
                }
            
            # Execute actions
            for tool_use in tool_uses:
                self.execute_action(tool_use.input)
                steps_taken += 1
            
            # Update conversation
            conversation = messages
            conversation.append({
                "role": "assistant",
                "content": response.content
            })
        
        return {
            "success": False,
            "steps": steps_taken,
            "message": "Max steps reached"
        }

# Usage
agent = ComputerUseAgent()
result = agent.perform_task("Open calculator and compute 157 * 89")
print(result)
```

### Safety Considerations

#### Sandboxing

```python
import docker

def sandboxed_computer_use(task: str) -> dict:
    """Run computer use in isolated Docker container."""
    
    client = docker.from_env()
    
    # Create isolated container
    container = client.containers.run(
        image="ubuntu:22.04",
        command=f"python3 /app/computer_agent.py '{task}'",
        volumes={
            '/path/to/agent': {'bind': '/app', 'mode': 'ro'}
        },
        network_mode="none",  # No network access
        mem_limit="1g",
        cpu_quota=50000,
        detach=True,
        remove=True
    )
    
    # Wait and get results
    result = container.wait()
    logs = container.logs()
    
    return {
        "output": logs.decode(),
        "exit_code": result["StatusCode"]
    }
```

#### Permission Controls

```python
class RestrictedComputerUse:
    """Computer use with restricted permissions."""
    
    ALLOWED_DIRECTORIES = ["/tmp", "/home/user/sandbox"]
    BLOCKED_COMMANDS = ["rm -rf", "sudo", "chmod", "chown"]
    
    def validate_action(self, action: dict) -> bool:
        """Validate action against security policies."""
        
        if action["type"] == "shell_execute":
            command = action["command"].lower()
            
            # Check for blocked commands
            if any(blocked in command for blocked in self.BLOCKED_COMMANDS):
                return False
            
            # Ensure working in allowed directories
            if not any(allowed in command for allowed in self.ALLOWED_DIRECTORIES):
                return False
        
        return True
```

---

## Skills vs Tools

### Conceptual Differences

| Aspect | Tools | Skills |
|--------|-------|--------|
| **Nature** | External functions | Native capabilities |
| **Definition** | User-defined | Built into Claude |
| **Execution** | By your code | By Claude |
| **Scope** | Specific tasks | Broad capabilities |
| **Integration** | Function calling | API parameters |

### When to Use What

```python
def choose_approach(task_type: str) -> str:
    """Decide between tools, skills, or hybrid."""
    
    approaches = {
        "complex_reasoning": "extended_thinking",
        "ui_automation": "computer_use",
        "api_call": "tool",
        "database_query": "tool",
        "file_operations": "tool",
        "math_calculation": "tool",  # Faster than thinking
        "strategic_planning": "extended_thinking",
        "system_integration": "tool",
        "web_scraping": "computer_use_or_tool",
        "data_analysis": "thinking_plus_tools"
    }
    
    return approaches.get(task_type, "tool")
```

### Hybrid Approach Example

```python
class HybridAgent:
    """Agent that combines skills and tools intelligently."""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.tools = self.define_tools()
    
    def define_tools(self):
        """Define traditional tools."""
        return [{
            "name": "calculator",
            "description": "Perform precise calculations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                }
            }
        }, {
            "name": "database_query",
            "description": "Query database",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        }]
    
    def process(self, task: str, task_complexity: str = "medium") -> dict:
        """Process task with optimal approach."""
        
        # Build request
        request = {
            "model": "claude-opus-4-20250514",
            "max_tokens": 16000,
            "messages": [{"role": "user", "content": task}],
            "tools": self.tools  # Always include tools
        }
        
        # Add thinking for complex tasks
        if task_complexity in ["high", "complex"]:
            request["thinking"] = {
                "type": "enabled",
                "budget_tokens": 5000
            }
        
        response = self.client.messages.create(**request)
        
        return self.handle_response(response)
    
    def handle_response(self, response) -> dict:
        """Handle response with both thinking and tool uses."""
        
        result = {
            "thinking": None,
            "tool_calls": [],
            "final_answer": None
        }
        
        for block in response.content:
            if block.type == "thinking":
                result["thinking"] = block.thinking
            elif block.type == "tool_use":
                result["tool_calls"].append({
                    "tool": block.name,
                    "input": block.input
                })
            elif block.type == "text":
                result["final_answer"] = block.text
        
        return result
```

---

## Performance Characteristics

### Latency Comparison

```
Standard Request:     ████░░░░░░ 0.5-2s
With Thinking (light): ███████░░░ 3-5s
With Thinking (deep):  ████████████████ 15-30s
Computer Use (simple): ██████████ 5-10s
Computer Use (complex): ████████████████████ 20-60s
```

### Cost Considerations

```python
# Token usage patterns
standard_request = {
    "input_tokens": 1000,
    "output_tokens": 500,
    "total_cost": "$0.015"  # Example pricing
}

thinking_request = {
    "input_tokens": 1000,
    "thinking_tokens": 5000,
    "output_tokens": 500,
    "total_cost": "$0.045"  # ~3x more
}

computer_use_request = {
    "input_tokens": 1000 + 1500,  # +image tokens
    "output_tokens": 500,
    "action_steps": 5,
    "total_cost": "$0.025"
}
```

---

## Limitations

### Extended Thinking Limitations

1. **Not Always Better**: Simple tasks don't benefit
2. **Latency**: Takes longer (not suitable for real-time)
3. **Cost**: Uses more tokens
4. **Availability**: May be tier-restricted

### Computer Use Limitations

1. **Beta Status**: APIs may change
2. **Environment-Specific**: Requires proper setup
3. **Safety Concerns**: Needs careful sandboxing
4. **Reliability**: UI changes can break automation
5. **Platform Support**: May work differently across OS

### General Limitations

```python
def check_limitations(task: str) -> list:
    """Check if task has known limitations."""
    
    limitations = []
    
    # Thinking limitations
    if "real-time" in task.lower():
        limitations.append("Extended thinking adds latency")
    
    # Computer use limitations
    if "secure system" in task.lower():
        limitations.append("Computer use should not access secure systems")
    
    if "mission-critical" in task.lower():
        limitations.append("Computer use not reliable enough for mission-critical tasks")
    
    return limitations
```

---

## Conclusion

Skills represent a significant evolution in AI agent capabilities:

- **Extended Thinking** enables deeper, more transparent reasoning
- **Computer Use** bridges the gap between AI and real-world interfaces
- **Hybrid approaches** combine the best of skills and traditional tools

Understanding when and how to use each capability is key to building effective AI agents.

For practical examples, see:
- [basic_skills_agent.py](basic_skills_agent.py)
- [advanced_skills_agent.py](advanced_skills_agent.py)
- [skills_comparison.py](skills_comparison.py)
