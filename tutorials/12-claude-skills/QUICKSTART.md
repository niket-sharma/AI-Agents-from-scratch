# Quick Start: Claude Skills in 5 Minutes

Get up and running with Claude Skills quickly!

## Prerequisites

```bash
pip install anthropic python-dotenv pillow
```

## Setup

Create `.env` file:

```env
ANTHROPIC_API_KEY=your-key-here
```

## Example 1: Extended Thinking (2 minutes)

Create `quick_thinking.py`:

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Ask a complex question
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 5000
    },
    messages=[{
        "role": "user",
        "content": "Design an efficient algorithm to find the shortest path in a weighted graph with negative edges. Explain the trade-offs."
    }]
)

# Print thinking process and answer
for block in response.content:
    if block.type == "thinking":
        print("🧠 Thinking Process:")
        print(block.thinking)
        print("\n" + "="*50 + "\n")
    elif block.type == "text":
        print("💡 Final Answer:")
        print(block.text)
```

Run it:

```bash
python quick_thinking.py
```

**Output:**
```
🧠 Thinking Process:
Let me think through this step by step...
1. First, I need to consider algorithms for negative edge weights
2. Bellman-Ford can handle negative edges, unlike Dijkstra...
[detailed reasoning]

==================================================

💡 Final Answer:
For graphs with negative edges, the Bellman-Ford algorithm is appropriate...
[complete solution]
```

## Example 2: Simple Skills Agent (3 minutes)

Create `quick_agent.py`:

```python
import anthropic
import os

class QuickSkillsAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def think(self, problem: str) -> dict:
        """Use extended thinking for complex problems."""
        response = self.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=8000,
            thinking={"type": "enabled", "budget_tokens": 3000},
            messages=[{"role": "user", "content": problem}]
        )
        
        result = {"thinking": None, "answer": None}
        for block in response.content:
            if block.type == "thinking":
                result["thinking"] = block.thinking
            elif block.type == "text":
                result["answer"] = block.text
        
        return result

# Create agent
agent = QuickSkillsAgent()

# Test with complex problem
result = agent.think(
    "I have $10,000 to invest. Design a diversified portfolio "
    "considering risk tolerance, time horizon, and current market conditions."
)

print("💭 Reasoning:")
print(result["thinking"][:500] + "...\n")  # First 500 chars

print("📊 Recommendation:")
print(result["answer"])
```

Run it:

```bash
python quick_agent.py
```

## Key Concepts

### Extended Thinking
```python
thinking={
    "type": "enabled",
    "budget_tokens": 5000  # How much "thinking time" to allocate
}
```

### Response Structure
```python
for block in response.content:
    if block.type == "thinking":
        # Internal reasoning process
        print(block.thinking)
    elif block.type == "text":
        # Final answer
        print(block.text)
```

## When to Use Extended Thinking

✅ **Use for:**
- Complex problem-solving
- Strategic planning
- Mathematical proofs
- Code architecture
- Research analysis

❌ **Don't use for:**
- Simple questions
- Quick lookups
- Real-time chat
- Factual queries

## Next Steps

1. Read the full [README.md](README.md)
2. Try [basic_skills_agent.py](basic_skills_agent.py)
3. Explore [SKILLS_EXPLAINED.md](SKILLS_EXPLAINED.md)
4. Build your own agent!

## Troubleshooting

**Error: "thinking not available"**
- Check your API tier supports Extended Thinking
- Verify model version is correct

**Error: "Invalid API key"**
- Ensure `.env` file is in the correct location
- Check API key is active on Anthropic console

**Slow responses**
- Reduce `budget_tokens` value
- Use Extended Thinking only for complex tasks

## Common Patterns

### Pattern 1: Conditional Thinking
```python
def smart_agent(question: str, complexity: str = "medium"):
    params = {
        "model": "claude-opus-4-20250514",
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": question}]
    }
    
    # Only use thinking for complex questions
    if complexity == "high":
        params["thinking"] = {"type": "enabled", "budget_tokens": 5000}
    
    return client.messages.create(**params)
```

### Pattern 2: Thinking Analysis
```python
def analyze_thinking(response):
    """Extract insights from thinking process."""
    for block in response.content:
        if block.type == "thinking":
            # Analyze the reasoning
            steps = block.thinking.split("\n")
            print(f"Reasoning steps: {len(steps)}")
            print(f"Consideration depth: {len([s for s in steps if 'consider' in s.lower()])}")
```

### Pattern 3: Fallback Strategy
```python
def robust_think(problem: str):
    try:
        # Try with thinking
        return client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=8000,
            thinking={"type": "enabled", "budget_tokens": 5000},
            messages=[{"role": "user", "content": problem}]
        )
    except Exception as e:
        # Fallback to standard mode
        print(f"Thinking unavailable: {e}, using standard mode")
        return client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": problem}]
        )
```

---

**That's it!** You now have a working Skills agent. Explore the full tutorial for advanced features.
