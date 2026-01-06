# Skills vs Tools vs Standard: Detailed Comparison

A comprehensive comparison of different approaches for building AI agents with Claude.

## Table of Contents

1. [Overview](#overview)
2. [Approach Definitions](#approach-definitions)
3. [Feature Comparison](#feature-comparison)
4. [Performance Analysis](#performance-analysis)
5. [Cost Analysis](#cost-analysis)
6. [Use Case Matrix](#use-case-matrix)
7. [Decision Framework](#decision-framework)

---

## Overview

Claude offers three primary approaches for building agents:

1. **Standard Mode**: Basic LLM interactions without special capabilities
2. **Tools (Function Calling)**: External functions the model can invoke
3. **Skills**: Native capabilities (Extended Thinking, Computer Use)

Understanding when to use each approach is critical for building effective agents.

---

## Approach Definitions

### Standard Mode

```python
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Question"}]
)
```

**Characteristics:**
- Simple text-based interaction
- Fast responses (0.5-2 seconds)
- No special capabilities
- Lower cost per request

### Tools (Function Calling)

```python
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=4096,
    tools=[{
        "name": "calculator",
        "description": "Perform calculations",
        "input_schema": {...}
    }],
    messages=[{"role": "user", "content": "Calculate..."}]
)
```

**Characteristics:**
- External function integration
- Precise operations (calculations, API calls, database queries)
- Requires implementation of tool execution
- Multiple round-trips possible

### Skills: Extended Thinking

```python
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 5000
    },
    messages=[{"role": "user", "content": "Complex problem"}]
)
```

**Characteristics:**
- Deep reasoning and analysis
- Transparent thinking process
- Higher latency (5-30+ seconds)
- Higher token usage

### Skills: Computer Use

```python
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=4096,
    tools=[{
        "type": "computer_20241022",
        "name": "computer",
        "display_width_px": 1920,
        "display_height_px": 1080
    }],
    messages=[...]
)
```

**Characteristics:**
- GUI interaction capabilities
- Screenshot analysis
- Mouse and keyboard control
- Beta feature (may change)

---

## Feature Comparison

### Capabilities Matrix

| Feature | Standard | Tools | Extended Thinking | Computer Use |
|---------|----------|-------|-------------------|--------------|
| **Speed** | ⚡⚡⚡ | ⚡⚡ | ⚡ | ⚡ |
| **Cost** | $ | $$ | $$$ | $$ |
| **Reasoning Depth** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Precision** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **External Access** | ❌ | ✅ | ❌ | ✅ (GUI only) |
| **Transparency** | ❌ | ⚠️ | ✅ | ⚠️ |
| **Setup Complexity** | Easy | Medium | Easy | Hard |
| **Real-time Capable** | ✅ | ✅ | ❌ | ❌ |

---

## Performance Analysis

### Latency Comparison

```
Simple Question (factual):
├─ Standard:           0.5-1s    ████░░░░░░
├─ Tools:              1-2s      ██████░░░░
├─ Extended Thinking:  3-5s      ██████████
└─ Computer Use:       5-10s     ████████████████

Complex Analysis:
├─ Standard:           1-2s      ████░░░░░░
├─ Tools:              2-4s      ████████░░
├─ Extended Thinking:  10-30s    ████████████████████████████
└─ Computer Use:       15-60s    ████████████████████████████████████
```

### Throughput Comparison

**Requests per Minute (typical):**

| Approach | Simple Tasks | Complex Tasks |
|----------|-------------|---------------|
| Standard | 60-120 | 30-60 |
| Tools | 30-60 | 15-30 |
| Extended Thinking | 5-10 | 2-5 |
| Computer Use | 3-6 | 1-2 |

---

## Cost Analysis

### Token Usage Patterns

**Simple Request (1000 input tokens):**

| Approach | Input | Output | Thinking | Total Cost* |
|----------|-------|--------|----------|-------------|
| Standard | 1000 | 500 | 0 | $0.015 |
| Tools (1 call) | 1000 | 500 | 0 | $0.016 |
| Extended Thinking | 1000 | 500 | 3000 | $0.030 |
| Computer Use | 2500† | 500 | 0 | $0.025 |

*Approximate costs based on Claude Opus pricing
†Includes image tokens

**Complex Request (2000 input tokens):**

| Approach | Input | Output | Thinking | Total Cost* |
|----------|-------|--------|----------|-------------|
| Standard | 2000 | 1000 | 0 | $0.030 |
| Tools (3 calls) | 2000 | 1000 | 0 | $0.035 |
| Extended Thinking | 2000 | 1000 | 8000 | $0.080 |
| Computer Use | 3500† | 1000 | 0 | $0.045 |

### Cost Optimization Strategies

```python
def cost_optimized_request(task: str, complexity: str) -> dict:
    """Choose approach based on cost-benefit analysis."""
    
    # Simple tasks: use standard mode
    if complexity == "simple":
        return standard_request(task)
    
    # Precise operations: use tools (most cost-effective)
    elif complexity == "precise":
        return tools_request(task)
    
    # Complex reasoning: thinking justified
    elif complexity == "complex_analytical":
        return thinking_request(task)
    
    # UI automation: computer use only option
    elif complexity == "ui_automation":
        return computer_use_request(task)
```

---

## Use Case Matrix

### When to Use Each Approach

#### Standard Mode ✅

**Best For:**
- Factual questions
- Simple conversations
- Content generation
- Summarization
- Translation
- Quick responses

**Examples:**
```python
# Good uses of standard mode
"What is the capital of France?"
"Summarize this article: [text]"
"Translate 'Hello' to Spanish"
"Write a haiku about summer"
```

**Avoid For:**
- Complex analysis
- Precise calculations
- External system access
- Deep reasoning tasks

---

#### Tools (Function Calling) ✅

**Best For:**
- Mathematical calculations
- Database queries
- API calls
- File operations
- Web searches
- Custom business logic

**Examples:**
```python
# Good uses of tools
"Calculate compound interest on $10,000 at 5% for 3 years"
"Query database for users older than 30"
"Get current weather in San Francisco"
"Search for recent papers on quantum computing"
```

**Avoid For:**
- Pure reasoning tasks
- Strategic planning
- When tools aren't available
- Real-time UI automation

---

#### Extended Thinking ✅

**Best For:**
- Complex problem-solving
- Strategic planning
- Multi-factor decision making
- Code architecture design
- System design
- Trade-off analysis
- Research and analysis

**Examples:**
```python
# Good uses of Extended Thinking
"Design a microservices architecture for a fintech platform"
"Compare 5 different approaches to solve this algorithmic problem"
"Analyze the strategic implications of entering a new market"
"Review this codebase architecture and suggest improvements"
```

**Avoid For:**
- Simple factual questions
- Real-time interactions
- When speed is critical
- Cost-sensitive applications

---

#### Computer Use ✅

**Best For:**
- UI testing and automation
- Screenshot analysis
- Application interaction
- Browser automation
- Legacy system integration
- Visual workflows

**Examples:**
```python
# Good uses of Computer Use
"Test the checkout flow in our web application"
"Extract data from this spreadsheet interface"
"Navigate to the settings page and change the theme"
"Fill out this form with test data"
```

**Avoid For:**
- Production systems
- Security-sensitive operations
- High-frequency operations
- When APIs are available

---

## Decision Framework

### Decision Tree

```
Start: What type of task?
│
├─ Factual/Simple Question
│  └─→ Use STANDARD MODE
│
├─ Requires External System Access
│  │
│  ├─ Has API/Tools Available?
│  │  ├─ Yes → Use TOOLS
│  │  └─ No → Use COMPUTER USE (if UI access needed)
│  │
│  └─ Pure Reasoning?
│     └─→ Consider EXTENDED THINKING
│
├─ Complex Analysis/Planning
│  │
│  ├─ Needs Transparency?
│  │  └─ Yes → Use EXTENDED THINKING
│  │
│  ├─ Also Needs Tool Access?
│  │  └─ Yes → Use HYBRID (Thinking + Tools)
│  │
│  └─ Cost-Sensitive?
│     ├─ Yes → Use STANDARD or TOOLS
│     └─ No → Use EXTENDED THINKING
│
└─ UI Automation
   └─→ Use COMPUTER USE (with safety measures)
```

### Scoring System

Use this scoring system to choose the optimal approach:

```python
def score_approach(task_characteristics: dict) -> dict:
    """Score each approach based on task characteristics."""
    
    scores = {
        "standard": 0,
        "tools": 0,
        "extended_thinking": 0,
        "computer_use": 0
    }
    
    # Speed requirement
    if task_characteristics.get("needs_realtime"):
        scores["standard"] += 3
        scores["tools"] += 2
    
    # Precision requirement
    if task_characteristics.get("needs_precision"):
        scores["tools"] += 4
        scores["standard"] += 1
    
    # Complexity
    complexity = task_characteristics.get("complexity", 0)
    if complexity > 7:
        scores["extended_thinking"] += 5
    elif complexity > 4:
        scores["extended_thinking"] += 2
        scores["tools"] += 2
    else:
        scores["standard"] += 3
    
    # External access needed
    if task_characteristics.get("needs_external_access"):
        if task_characteristics.get("has_api"):
            scores["tools"] += 4
        else:
            scores["computer_use"] += 3
    
    # Reasoning depth
    if task_characteristics.get("needs_deep_reasoning"):
        scores["extended_thinking"] += 5
    
    # UI interaction
    if task_characteristics.get("needs_ui_interaction"):
        scores["computer_use"] += 5
    
    # Budget sensitivity
    if task_characteristics.get("budget_sensitive"):
        scores["standard"] += 2
        scores["tools"] += 1
        scores["extended_thinking"] -= 2
    
    return max(scores, key=scores.get)
```

### Example Usage

```python
# Example 1: Complex strategic task
task1 = {
    "needs_realtime": False,
    "needs_precision": False,
    "complexity": 9,
    "needs_external_access": False,
    "needs_deep_reasoning": True,
    "needs_ui_interaction": False,
    "budget_sensitive": False
}
# Result: extended_thinking

# Example 2: Database query with analysis
task2 = {
    "needs_realtime": False,
    "needs_precision": True,
    "complexity": 5,
    "needs_external_access": True,
    "has_api": True,
    "needs_deep_reasoning": False,
    "needs_ui_interaction": False,
    "budget_sensitive": True
}
# Result: tools

# Example 3: UI testing
task3 = {
    "needs_realtime": False,
    "needs_precision": False,
    "complexity": 4,
    "needs_external_access": True,
    "has_api": False,
    "needs_deep_reasoning": False,
    "needs_ui_interaction": True,
    "budget_sensitive": False
}
# Result: computer_use
```

---

## Hybrid Approaches

### Combining Strategies

Often the best solution combines multiple approaches:

#### Pattern 1: Think Then Execute

```python
# 1. Use Extended Thinking for planning
plan = extended_thinking_request("Plan approach for task X")

# 2. Use Tools for execution
result = tools_request(f"Execute this plan: {plan}")
```

#### Pattern 2: Execute Then Analyze

```python
# 1. Use Tools to gather data
data = tools_request("Query database for metrics")

# 2. Use Extended Thinking for analysis
analysis = extended_thinking_request(f"Analyze this data: {data}")
```

#### Pattern 3: Adaptive Approach

```python
def adaptive_agent(task: str) -> dict:
    """Adaptively choose and combine approaches."""
    
    # Start with quick standard assessment
    assessment = standard_request(f"Assess complexity of: {task}")
    
    # Based on assessment, choose approach
    if "complex" in assessment.lower():
        # Use thinking for planning
        plan = extended_thinking_request(task)
        
        # Use tools for execution if needed
        if requires_tools(plan):
            return tools_request(f"Execute: {plan}")
        return {"result": plan}
    
    else:
        # Direct execution with tools or standard
        return tools_request(task) if requires_tools(task) else standard_request(task)
```

---

## Best Practices

### General Guidelines

1. **Start Simple**: Begin with standard mode, add complexity only when needed
2. **Measure Performance**: Track latency, cost, and quality metrics
3. **Consider Context**: Same task may need different approaches in different contexts
4. **User Experience**: Balance thoroughness with responsiveness
5. **Cost Management**: Monitor token usage and optimize budgets

### Specific Recommendations

#### For Production Systems

```python
production_guidelines = {
    "real_time_chat": "Use standard mode with optional tools",
    "batch_analysis": "Use extended thinking for better quality",
    "api_integration": "Always use tools, never computer use",
    "critical_decisions": "Use extended thinking with human review",
    "ui_automation": "Use computer use only in isolated/test environments"
}
```

#### For Development/Testing

```python
development_guidelines = {
    "rapid_prototyping": "Start with standard, add thinking later",
    "testing_thinking": "Use smaller token budgets initially",
    "tool_development": "Test tools independently before integration",
    "computer_use": "Always use sandboxed environments"
}
```

---

## Conclusion

**Key Takeaways:**

1. **No Universal Solution**: Choose based on specific task requirements
2. **Hybrid is Powerful**: Combining approaches often yields best results
3. **Consider Trade-offs**: Speed vs depth, cost vs quality, simplicity vs capability
4. **Safety First**: Especially for Computer Use
5. **Measure and Iterate**: Track metrics and optimize over time

**Decision Summary:**

- **Standard Mode**: Fast, cheap, good for simple tasks
- **Tools**: Precise, versatile, best for external operations
- **Extended Thinking**: Deep reasoning, transparent, best for complex analysis
- **Computer Use**: UI automation, use with extreme caution
- **Hybrid**: Often the optimal real-world solution

For more detailed examples and implementations, see:
- [skills_comparison.py](skills_comparison.py) - Side-by-side comparisons
- [basic_skills_agent.py](basic_skills_agent.py) - Extended Thinking examples
- [advanced_skills_agent.py](advanced_skills_agent.py) - Computer Use examples
