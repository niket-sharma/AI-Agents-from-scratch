# Tutorial 12: Claude Skills - Extended Thinking & Computer Use

Welcome to Tutorial 12! In this advanced tutorial, you'll learn how to leverage Claude's powerful **Skills** capabilities, including Extended Thinking for enhanced reasoning and Computer Use for real-world interactions.

## Learning Objectives

By the end of this tutorial, you will:
- Understand Claude's Extended Thinking mode for complex reasoning
- Implement agents that use Computer Use capabilities
- Know when to use Skills vs traditional tools
- Build agents that combine multiple skills
- Handle skill-specific errors and limitations
- Apply best practices for production deployments

## Prerequisites

- Completed Tutorials 01-03 (Basics, Memory, Tools)
- Anthropic API key with appropriate tier access
- Python 3.9 or higher
- Understanding of async/await patterns
- Basic knowledge of system permissions (for Computer Use)

## Time Required

Approximately 1.5-2 hours

## What Are Claude Skills?

Claude Skills are specialized capabilities that enhance the model's ability to:

### 1. **Extended Thinking** 
Enhanced reasoning mode where Claude takes more time to think through complex problems:
- Deep analytical reasoning
- Multi-step problem solving
- Strategic planning
- Complex mathematical computations
- Logical deduction

### 2. **Computer Use (Beta)**
Ability to interact with computer interfaces:
- View and analyze screenshots
- Control mouse and keyboard
- Navigate applications
- Execute shell commands
- Interact with web browsers

## What You'll Build

In this tutorial, you'll create:
1. A reasoning agent that uses Extended Thinking for complex problems
2. A computer automation agent that performs real tasks
3. A hybrid agent combining both skills
4. Comparison examples showing skills vs traditional tools

## Quick Start

If you're eager to get started, check out [QUICKSTART.md](QUICKSTART.md) for a minimal working example.

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Your Application                │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│      Skills Agent Framework             │
│  ┌─────────────────────────────────┐   │
│  │  Extended Thinking Module       │   │
│  │  - Reasoning engine             │   │
│  │  - Problem decomposition        │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Computer Use Module            │   │
│  │  - Screen capture               │   │
│  │  - Input control                │   │
│  │  - Command execution            │   │
│  └─────────────────────────────────┘   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       Claude API (Anthropic)            │
└─────────────────────────────────────────┘
```

## Step 1: Environment Setup

### Install Dependencies

```bash
cd tutorials/12-claude-skills
pip install -r requirements.txt
```

### Required Packages
- `anthropic>=0.40.0` - Official Anthropic SDK with skills support
- `pillow>=10.0.0` - Image processing for Computer Use
- `python-dotenv>=1.0.0` - Environment variable management

### Set Up API Keys

Create or update your `.env` file:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Set tier for rate limiting awareness
ANTHROPIC_TIER=2  # 1, 2, 3, or 4
```

### Verify Access

Not all API tiers have access to all skills. Check your account:

```python
# Check your API tier and available features
import anthropic

client = anthropic.Anthropic()
# Extended Thinking is available on most tiers
# Computer Use may require higher tier access
```

## Step 2: Extended Thinking Basics

### What is Extended Thinking?

Extended Thinking allows Claude to spend more time reasoning through complex problems before responding. It's like giving the model "thinking time" to work through challenges systematically.

### When to Use Extended Thinking

✅ **Good Use Cases:**
- Complex mathematical problems
- Strategic planning and analysis
- Multi-step logical reasoning
- Code architecture decisions
- Research and analysis tasks

❌ **Poor Use Cases:**
- Simple factual questions
- Quick responses needed
- Straightforward tasks
- Real-time conversations

### Basic Implementation

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def thinking_agent(problem: str) -> str:
    """Agent that uses extended thinking for complex problems."""
    
    response = client.messages.create(
        model="claude-opus-4-20250514",  # Use latest model with thinking
        max_tokens=16000,
        thinking={
            "type": "enabled",
            "budget_tokens": 10000  # Tokens allocated for thinking
        },
        messages=[{
            "role": "user",
            "content": problem
        }]
    )
    
    # Extract thinking and response
    thinking_content = None
    response_content = None
    
    for block in response.content:
        if block.type == "thinking":
            thinking_content = block.thinking
        elif block.type == "text":
            response_content = block.text
    
    return {
        "thinking": thinking_content,
        "response": response_content
    }

# Example usage
result = thinking_agent(
    "Design a distributed system for handling 1 million concurrent users. "
    "Consider scalability, fault tolerance, and cost optimization."
)

print("Thinking Process:")
print(result["thinking"])
print("\nFinal Response:")
print(result["response"])
```

### Understanding the Thinking Block

The thinking block contains Claude's internal reasoning:
- Problem breakdown
- Exploration of alternatives
- Decision-making process
- Verification steps

This transparency helps you:
- Debug agent reasoning
- Improve prompts
- Build trust with users
- Audit decision-making

## Step 3: Computer Use Basics

### What is Computer Use?

Computer Use (Beta) enables Claude to interact with computer interfaces through:
- Screenshot analysis
- Mouse movements and clicks
- Keyboard input
- Command execution

### Safety Considerations

⚠️ **Important Security Notes:**
- Run in isolated/sandboxed environments
- Never give access to sensitive systems
- Review all actions before execution
- Implement strict permission controls
- Monitor all operations

### When to Use Computer Use

✅ **Good Use Cases:**
- UI testing and automation
- Data entry from visual sources
- Browser automation
- Application integration
- Workflow automation

❌ **Poor Use Cases:**
- High-security operations
- Mission-critical systems
- Real-time requirements
- Simple API-based tasks

### Basic Implementation

```python
import anthropic
import base64
from PIL import ImageGrab
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def computer_use_agent(task: str) -> dict:
    """Agent that uses computer use to perform tasks."""
    
    # Capture current screen
    screenshot = ImageGrab.grab()
    screenshot.save("/tmp/screen.png")
    
    # Encode screenshot
    with open("/tmp/screen.png", "rb") as img_file:
        screenshot_data = base64.b64encode(img_file.read()).decode()
    
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=4096,
        tools=[{
            "type": "computer_20241022",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080,
            "display_number": 1
        }],
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_data
                    }
                },
                {
                    "type": "text",
                    "text": task
                }
            ]
        }]
    )
    
    return response

# Example usage
result = computer_use_agent(
    "Open the calculator application and compute 1847 * 923"
)
```

## Step 4: Combining Skills

### Hybrid Agent Architecture

The most powerful agents combine multiple skills:

```python
class SkillsAgent:
    """Advanced agent combining Extended Thinking and Computer Use."""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.conversation_history = []
    
    def process_task(self, task: str, use_thinking: bool = False, 
                     use_computer: bool = False) -> dict:
        """Process task with appropriate skills."""
        
        # Build tools list
        tools = []
        if use_computer:
            tools.append({
                "type": "computer_20241022",
                "name": "computer",
                "display_width_px": 1920,
                "display_height_px": 1080
            })
        
        # Build request
        request_params = {
            "model": "claude-opus-4-20250514",
            "max_tokens": 16000,
            "messages": self.conversation_history + [{
                "role": "user",
                "content": task
            }]
        }
        
        # Add thinking if requested
        if use_thinking:
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 10000
            }
        
        # Add tools if requested
        if tools:
            request_params["tools"] = tools
        
        response = self.client.messages.create(**request_params)
        
        # Update conversation history
        self.conversation_history.append({
            "role": "user",
            "content": task
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response.content
        })
        
        return self._parse_response(response)
    
    def _parse_response(self, response) -> dict:
        """Parse response into components."""
        result = {
            "thinking": None,
            "text": None,
            "tool_uses": []
        }
        
        for block in response.content:
            if block.type == "thinking":
                result["thinking"] = block.thinking
            elif block.type == "text":
                result["text"] = block.text
            elif block.type == "tool_use":
                result["tool_uses"].append(block)
        
        return result

# Example usage
agent = SkillsAgent()

# Use thinking for planning
plan = agent.process_task(
    "I need to analyze sales data in a spreadsheet and create a report. "
    "Plan the approach.",
    use_thinking=True
)

# Use computer use for execution
execution = agent.process_task(
    "Execute the plan: open the spreadsheet and extract key metrics.",
    use_computer=True
)
```

## Step 5: Error Handling

### Common Errors and Solutions

```python
def robust_skills_agent(task: str) -> dict:
    """Skills agent with comprehensive error handling."""
    
    client = anthropic.Anthropic()
    
    try:
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=16000,
            thinking={"type": "enabled", "budget_tokens": 10000},
            messages=[{"role": "user", "content": task}]
        )
        return {"success": True, "data": response}
        
    except anthropic.APIError as e:
        if "thinking_not_available" in str(e):
            return {
                "success": False,
                "error": "Extended Thinking not available for your tier",
                "fallback": "Consider upgrading or using standard mode"
            }
        elif "rate_limit" in str(e):
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "fallback": "Implement exponential backoff"
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {str(e)}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
```

## Step 6: Best Practices

### 1. Resource Management

```python
# Set appropriate token budgets
thinking_budget = min(10000, max_tokens // 2)  # Don't exceed 50% of total

# Monitor usage
def track_usage(response):
    usage = response.usage
    print(f"Input tokens: {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    if hasattr(usage, 'thinking_tokens'):
        print(f"Thinking tokens: {usage.thinking_tokens}")
```

### 2. When to Use Which Skill

| Task Type | Extended Thinking | Computer Use | Traditional Tools |
|-----------|------------------|--------------|-------------------|
| Complex reasoning | ✅ Best | ❌ | ⚠️ Possible |
| Math calculations | ✅ Good | ❌ | ✅ Best |
| UI automation | ❌ | ✅ Best | ❌ |
| API calls | ❌ | ⚠️ Possible | ✅ Best |
| Data analysis | ✅ Good | ⚠️ Possible | ✅ Good |
| File operations | ❌ | ✅ Good | ✅ Best |

### 3. Security Guidelines

```python
# Sandboxing for Computer Use
import docker

def safe_computer_use(task: str) -> dict:
    """Execute computer use in isolated container."""
    
    client = docker.from_env()
    
    # Run in isolated container
    container = client.containers.run(
        "ubuntu:latest",
        command=f"python3 /app/computer_agent.py '{task}'",
        volumes={'/path/to/agent': {'bind': '/app', 'mode': 'ro'}},
        network_disabled=False,  # Set True for full isolation
        mem_limit="1g",
        cpu_quota=50000,
        detach=True
    )
    
    # Get results
    result = container.wait()
    output = container.logs()
    container.remove()
    
    return {"output": output, "exit_code": result}
```

### 4. Performance Optimization

```python
# Caching thinking results
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_thinking(problem_hash: str, problem: str) -> dict:
    """Cache thinking results for similar problems."""
    # Only cache deterministic problems
    return thinking_agent(problem)

def smart_thinking_agent(problem: str) -> dict:
    """Use cached results when possible."""
    problem_hash = hashlib.md5(problem.encode()).hexdigest()
    return cached_thinking(problem_hash, problem)
```

## Examples

We've included several complete examples:

1. **[basic_skills_agent.py](basic_skills_agent.py)** - Simple Extended Thinking agent
2. **[advanced_skills_agent.py](advanced_skills_agent.py)** - Full-featured Computer Use agent
3. **[skills_comparison.py](skills_comparison.py)** - Comparing skills with traditional approaches
4. **[examples/code_assistant.py](examples/code_assistant.py)** - Code review with thinking
5. **[examples/browser_automation.py](examples/browser_automation.py)** - Web automation

## Testing Your Agent

```bash
# Run basic example
python basic_skills_agent.py

# Run advanced example (requires appropriate permissions)
python advanced_skills_agent.py

# Run comparison
python skills_comparison.py
```

## Exercises

Complete the exercises in [exercises.py](exercises.py):

1. Build a research agent that uses Extended Thinking
2. Create a file organizer using Computer Use
3. Implement a hybrid agent for complex tasks
4. Add error recovery mechanisms
5. Build a skills orchestrator

## Common Pitfalls

### 1. Over-using Extended Thinking
```python
# ❌ Bad: Using thinking for simple tasks
result = thinking_agent("What's 2 + 2?")

# ✅ Good: Use standard mode for simple tasks
result = standard_agent("What's 2 + 2?")
```

### 2. Insufficient Sandboxing
```python
# ❌ Bad: Direct system access
computer_use_agent("Delete all files in /home")

# ✅ Good: Restricted environment
computer_use_agent("Delete files in /sandbox/temp", sandbox=True)
```

### 3. Ignoring Token Budgets
```python
# ❌ Bad: Unlimited thinking
thinking={"type": "enabled", "budget_tokens": 100000}

# ✅ Good: Reasonable limits
thinking={"type": "enabled", "budget_tokens": 10000}
```

## Further Reading

- [SKILLS_EXPLAINED.md](SKILLS_EXPLAINED.md) - Deep dive into how skills work
- [COMPARISON.md](COMPARISON.md) - Skills vs Tools detailed comparison
- [Anthropic Skills Documentation](https://docs.anthropic.com/en/docs/skills)
- [Computer Use Safety Guide](https://docs.anthropic.com/en/docs/computer-use-safety)

## Next Steps

After completing this tutorial:
1. Combine with Tutorial 04 (Planning) for strategic agents
2. Integrate with Tutorial 05 (Advanced) for production systems
3. Explore Tutorial 06 (LangGraph) for complex workflows
4. Build your own skills-powered agent

## Troubleshooting

### Extended Thinking Not Working
- Check your API tier supports Extended Thinking
- Verify you're using a compatible model version
- Ensure token budget is reasonable

### Computer Use Errors
- Verify permissions for screen capture
- Check Docker/sandbox configuration
- Ensure display settings match actual setup
- Review security restrictions

### Performance Issues
- Reduce thinking token budget
- Optimize prompt engineering
- Implement caching strategies
- Use async operations for parallelism

## Contributing

Found an issue or want to improve this tutorial? See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

This tutorial is part of the AI-Agents-from-scratch project, licensed under MIT.

---

**Ready to get started?** Jump to [QUICKSTART.md](QUICKSTART.md) or dive into [basic_skills_agent.py](basic_skills_agent.py)!
