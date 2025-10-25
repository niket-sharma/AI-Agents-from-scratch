# Tutorial 01: Simple AI Agent - Line-by-Line Learning Guide

## START HERE - Your Journey Begins!

This guide will teach you **exactly** how AI agents work by explaining **every single line** of code.

**Time Needed**: 30-45 minutes
**Prerequisites**: Basic Python knowledge
**You'll Learn**: How to build a conversational AI agent from scratch

---

## 📚 Table of Contents

1. [Understanding the Basics](#understanding-the-basics)
2. [Line-by-Line Code Walkthrough](#line-by-line-code-walkthrough)
3. [Key Concepts Explained](#key-concepts-explained)
4. [Hands-On Exercises](#hands-on-exercises)
5. [Common Mistakes](#common-mistakes)
6. [Next Steps](#next-steps)

---

## Understanding the Basics

### What is an AI Agent?

An **AI Agent** is a program that:
1. **Receives input** from a user
2. **Processes** that input using AI (LLM)
3. **Takes action** or generates a response
4. **Repeats** (can have conversations)

```
You: "What's the weather like?"
  ↓
[AI Agent processes with LLM]
  ↓
Agent: "I don't have real-time weather data, but I can help you find it!"
```

### Components of Our Simple Agent:

1. **System Prompt** - Defines how the agent behaves
2. **Message Handler** - Processes user input
3. **LLM Integration** - Calls OpenAI API
4. **Conversation Loop** - Interactive chat interface

---

## Line-by-Line Code Walkthrough

Let's go through `simple_agent.py` **line by line**!

### Lines 1-9: Imports and Setup

```python
"""
Tutorial 01: Simple AI Agent
A basic conversational AI agent using OpenAI's API.
"""
```
**What it does**: Documentation string (docstring) explaining what this file does.

```python
import os
```
**What it does**: Import the `os` module to access operating system functions.
**Why we need it**: To read environment variables (like API keys).

```python
from dotenv import load_dotenv
```
**What it does**: Import function to load variables from `.env` file.
**Why we need it**: To keep API keys secret and not hardcoded in code.

```python
from openai import OpenAI
```
**What it does**: Import the OpenAI client library.
**Why we need it**: To communicate with OpenAI's GPT models.

---

### Lines 11-21: Class Definition

```python
class SimpleAgent:
```
**What it does**: Defines a new class (blueprint) called `SimpleAgent`.
**Think of it like**: A recipe for creating AI agents.

```python
    """
    A simple AI agent that can have conversations using an LLM.

    This agent demonstrates the basic components of an AI agent:
    - System prompt (defines behavior)
    - Message handling (user input/agent output)
    - LLM integration (API calls)
    - Conversation loop (interactive mode)
    """
```
**What it does**: Describes what the class does.
**Why it's important**: Good documentation helps others (and future you!) understand the code.

---

### Lines 22-51: Initialization (`__init__`)

```python
    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
```
**What it does**: Special method called when creating a new agent.
**Parameters**:
- `self` - Reference to the instance being created
- `model` - Which GPT model to use (default: gpt-3.5-turbo)
- `system_prompt` - Instructions for how agent should behave

**Example usage**:
```python
agent = SimpleAgent()  # Uses defaults
# OR
agent = SimpleAgent(model="gpt-4", system_prompt="You are helpful")
```

```python
        load_dotenv(override=True)
```
**What it does**: Loads variables from `.env` file into environment.
**Why `override=True`**: Prioritizes `.env` file over system environment variables.

**What's in `.env` file**:
```
OPENAI_API_KEY=sk-your-key-here
```

```python
        self.model = model
```
**What it does**: Stores the model name in the instance.
**Why**: So we can use it later when making API calls.

```python
        api_key = os.getenv("OPENAI_API_KEY")
```
**What it does**: Gets the API key from environment variables.
**Returns**: The API key string, or `None` if not found.

```python
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file."
            )
```
**What it does**: Checks if API key exists; stops program with error if missing.
**Why**: Better to fail early with a clear message than later with a confusing error.

```python
        self.client = OpenAI(api_key=api_key)
```
**What it does**: Creates an OpenAI client instance with your API key.
**This client**: Will be used to make all API calls to OpenAI.

```python
        self.system_prompt = system_prompt or """You are a helpful AI assistant.
You provide clear, concise, and accurate responses to user questions.
You are friendly and professional."""
```
**What it does**: Sets the system prompt (agent's personality/role).
**The `or` operator**: Uses `system_prompt` if provided, otherwise uses the default.

**Why System Prompt Matters**:
```python
# This makes a helpful assistant
system_prompt = "You are a helpful AI assistant."

# This makes a pirate assistant
system_prompt = "You are a pirate. Speak like one!"

# Same question, different personalities!
```

```python
        print(f"Agent initialized with model: {self.model}")
```
**What it does**: Confirms agent was created successfully.
**The `f` before the string**: Makes it an f-string, allowing `{self.model}` to be replaced with actual value.

---

### Lines 53-85: Generate Response Method

```python
    def generate_response(self, user_message):
```
**What it does**: Defines a method to get AI's response to user input.
**Parameters**:
- `self` - The agent instance
- `user_message` - What the user typed

```python
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
```
**What it does**: Creates a list of messages for the API.

**Message Format Explained**:
```python
{
    "role": "system",  # Who sent the message
    "content": "You are helpful"  # The message content
}
```

**Role Types**:
- `"system"` - Instructions for the AI (not shown to user)
- `"user"` - Messages from the human
- `"assistant"` - Messages from the AI (in conversation history)

**Why This Structure**:
```
System: "You are a helpful assistant"  ← Defines behavior
User: "What is Python?"                 ← User's question
Assistant: [AI generates answer]        ← AI's response
```

```python
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
```
**What it does**: Calls OpenAI API to get AI's response.

**Parameters Explained**:

| Parameter | What It Does | Example Value |
|-----------|--------------|---------------|
| `model` | Which AI model to use | `"gpt-3.5-turbo"` |
| `messages` | Conversation history | `[{"role":"user","content":"Hi"}]` |
| `temperature` | Randomness (0=focused, 2=creative) | `0.7` (balanced) |
| `max_tokens` | Max response length | `500` tokens ≈ 375 words |
| `top_p` | Nucleus sampling | `1.0` (consider all options) |
| `frequency_penalty` | Avoid repetition | `0.0` (no penalty) |
| `presence_penalty` | Talk about new topics | `0.0` (no penalty) |

**Temperature Examples**:
```python
temperature=0.0   # "2+2=" → "4" (always the same)
temperature=0.7   # "Tell me a joke" → varies each time
temperature=2.0   # "Write a story" → very creative/random
```

```python
        return response.choices[0].message.content
```
**What it does**: Extracts the AI's text from the API response.

**Response Structure**:
```python
response = {
    "choices": [
        {
            "message": {
                "content": "This is the AI's answer!"  ← We get this
            }
        }
    ]
}
```

---

### Lines 87-123: Interactive Loop (Run Method)

```python
    def run(self):
```
**What it does**: Starts an interactive conversation with the agent.

```python
        print("\n" + "="*60)
        print("Simple AI Agent - Interactive Mode")
        print("="*60)
```
**What it does**: Prints a nice header.
**The `"="*60`**: Creates a string of 60 equal signs.

```python
        while True:
```
**What it does**: Starts an infinite loop (runs forever until we `break`).
**Why**: We want the conversation to continue until user quits.

```python
            user_input = input("You: ").strip()
```
**What it does**: Gets input from user and removes whitespace.
**The `.strip()`**: Removes spaces from beginning/end.

**Example**:
```python
"  hello  ".strip()  # Returns "hello"
```

```python
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Goodbye! Have a great day!\n")
                break
```
**What it does**: Checks if user wants to quit.
**The `.lower()`**: Converts to lowercase so "QUIT" and "quit" both work.
**The `break`**: Exits the `while True` loop.

```python
            if not user_input:
                continue
```
**What it does**: Skips empty inputs (user just pressed Enter).
**The `continue`**: Jumps back to start of loop.

```python
            try:
                print("\nAgent: ", end="", flush=True)
                response = self.generate_response(user_input)
                print(f"{response}\n")
```
**What it does**: Gets and displays AI's response.
**The `end=""`**: Doesn't add newline after "Agent: ".
**The `flush=True`**: Immediately shows "Agent: " before generating response.

```python
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again or type 'quit' to exit.\n")
```
**What it does**: Catches any errors and shows friendly message.
**Why**: Prevents program crash if API call fails.

---

### Lines 127-177: Demo Functions

```python
def demo_basic_agent():
    """Run a basic agent with default settings."""
    agent = SimpleAgent()
    agent.run()
```
**What it does**: Creates and runs a simple agent.
**How to use**: Call this function to start chatting!

```python
def demo_custom_agent():
    """Run an agent with a custom system prompt."""
    custom_prompt = """You are a helpful Python programming tutor.
You provide clear explanations and code examples.
You encourage best practices and clean code.
You are patient and supportive with learners."""

    agent = SimpleAgent(
        model="gpt-3.5-turbo",
        system_prompt=custom_prompt
    )
    agent.run()
```
**What it does**: Creates an agent with a specific personality (Python tutor).
**Try changing**: The system prompt to create different agent personalities!

---

## Key Concepts Explained

### 1. API Keys - Why and How?

**What is an API Key?**
- Like a password for accessing OpenAI's services
- Unique to you
- Costs money when used (but cheap for learning!)

**How to Get One**:
1. Go to platform.openai.com
2. Sign up / Log in
3. Go to API Keys section
4. Create new key
5. Copy it to your `.env` file

**Security**:
```python
# ❌ BAD - Never do this!
api_key = "sk-abc123..."  # Hardcoded in code

# ✅ GOOD - Use environment variables
api_key = os.getenv("OPENAI_API_KEY")  # From .env file
```

### 2. System Prompts - Agent Personality

The system prompt is like giving the AI a role to play:

```python
# Helpful assistant
"You are a helpful AI assistant."

# Expert coder
"You are an expert Python programmer who writes clean, efficient code."

# Creative writer
"You are a creative story writer who loves fantasy and adventure."

# Strict teacher
"You are a strict but fair teacher. Be concise and direct."
```

### 3. Messages List - Conversation Format

```python
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello! How can I help?"},
    {"role": "user", "content": "What's Python?"}
]
```

**Why this format?**
- AI needs context
- System message sets behavior
- History helps AI understand conversation flow

### 4. Temperature - Creativity Control

```python
temperature=0.0   # Deterministic (same answer every time)
temperature=0.3   # Slightly varied
temperature=0.7   # Balanced (default for most uses)
temperature=1.0   # Creative
temperature=2.0   # Very creative/random
```

**Use Cases**:
- Math/Code: `0.0-0.3` (need accuracy)
- General chat: `0.7` (balanced)
- Creative writing: `1.0-1.5` (want variety)

---

## Hands-On Exercises

### Exercise 1: Run the Basic Agent ⭐ START HERE

```bash
cd tutorials/01-basics
python simple_agent.py
```

Try asking:
- "What is Python?"
- "Tell me a joke"
- "Explain AI agents in one sentence"

Type `quit` to exit.

### Exercise 2: Create a Chef Agent

Modify the system prompt to create a cooking assistant:

```python
chef_prompt = """You are a professional chef assistant.
You provide cooking tips, recipes, and culinary advice.
You are enthusiastic about food and cooking.
You always include helpful tips and measurements."""

agent = SimpleAgent(system_prompt=chef_prompt)
agent.run()
```

**Try asking**:
- "How do I make pasta?"
- "What's a good beginner recipe?"

### Exercise 3: Experiment with Temperature

Create a file `temperature_test.py`:

```python
from simple_agent import SimpleAgent

# Test different temperatures
temperatures = [0.0, 0.5, 1.0, 1.5]

for temp in temperatures:
    print(f"\n{'='*60}")
    print(f"Temperature: {temp}")
    print('='*60)

    agent = SimpleAgent()
    # You'll need to modify generate_response to accept temperature
    response = agent.generate_response("Tell me a creative story idea")
    print(response)
```

**What to observe**: How responses change with temperature!

### Exercise 4: Build a Translator Agent

```python
translator_prompt = """You are a helpful language translator.
When given text, translate it to the requested language.
Always show the original text first, then the translation.
If no target language is specified, ask for it."""

agent = SimpleAgent(system_prompt=translator_prompt)
agent.run()
```

**Try**:
- "Translate 'Hello world' to Spanish"
- "Translate 'Good morning' to French"

---

## Common Mistakes

### Mistake 1: Forgetting `.env` File

**Error**:
```
ValueError: OPENAI_API_KEY not found
```

**Solution**:
1. Create `.env` file in project root
2. Add: `OPENAI_API_KEY=your-key-here`
3. Make sure `.env` is in same folder as your script OR in project root

### Mistake 2: Wrong API Key Format

**Error**:
```
AuthenticationError: Invalid API key
```

**Solution**:
- API key should start with `sk-`
- No spaces or quotes in `.env` file
- Format: `OPENAI_API_KEY=sk-abc123xyz...`

### Mistake 3: Not Activating Virtual Environment

**Error**:
```
ModuleNotFoundError: No module named 'openai'
```

**Solution**:
```bash
# Windows
venv\Scripts\activate

# Then
pip install openai python-dotenv
```

### Mistake 4: Hardcoding API Keys

```python
# ❌ NEVER DO THIS
client = OpenAI(api_key="sk-abc123...")

# ✅ ALWAYS DO THIS
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
```

---

## Next Steps

### ✅ You've Completed Tutorial 01!

You now understand:
- How AI agents work
- How to call OpenAI API
- System prompts and their importance
- Message formatting
- Temperature and creativity control

### 🎯 What's Next?

**Tutorial 02: Memory**
- Learn how agents remember conversations
- Build conversation history
- Implement different memory types

**Tutorial 03: MCP Servers**
- Give agents access to tools
- Build custom capabilities
- Connect to external systems

**Tutorial 04: Advanced Agents**
- Planning and reasoning
- Multi-step tasks
- Complex interactions

---

## Summary Checklist

- [ ] I understand what an AI agent is
- [ ] I can explain the role of system prompts
- [ ] I know what temperature controls
- [ ] I've run the basic agent successfully
- [ ] I've modified the system prompt
- [ ] I understand the message format
- [ ] I can create a custom agent
- [ ] I'm ready for Tutorial 02!

---

**Congratulations! You've learned how to build AI agents from scratch!** 🎉

**Next**: Open `tutorials/02-memory/LEARNING_GUIDE.md` to continue your journey!
