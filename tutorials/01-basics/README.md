# Tutorial 01: Building Your First AI Agent

Welcome to the first tutorial! In this lesson, you'll build a simple AI agent that can have conversations with users. This is the foundation for all the more complex agents we'll build later.

## Learning Objectives

By the end of this tutorial, you will:
- Understand the basic structure of an AI agent
- Set up and use LLM APIs (OpenAI or Anthropic)
- Implement a simple conversation loop
- Create a basic agent class
- Understand prompt engineering basics

## Prerequisites

- Python 3.8 or higher installed
- An OpenAI or Anthropic API key
- Basic Python knowledge (classes, functions, loops)

## Time Required

Approximately 30 minutes

## What You'll Build

A simple conversational agent that:
1. Accepts user input
2. Sends it to an LLM with a system prompt
3. Returns the AI's response
4. Maintains a basic conversation loop

## Step 1: Environment Setup

### Install Dependencies

First, install the required packages:

```bash
pip install openai anthropic python-dotenv
```

### Set Up API Keys

Create a `.env` file in the project root:

```env
# Choose one or both
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Getting API Keys:**
- **OpenAI**: Sign up at https://platform.openai.com/ and create an API key
- **Anthropic**: Sign up at https://console.anthropic.com/ and create an API key

## Step 2: Understanding the Components

### System Prompt

The system prompt defines your agent's behavior:

```python
SYSTEM_PROMPT = """You are a helpful AI assistant. You provide clear,
concise, and accurate responses to user questions. You are friendly and
professional."""
```

### Message Format

LLMs expect messages in a specific format:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help you today?"},
    {"role": "user", "content": "What's the weather?"}
]
```

## Step 3: Build the Basic Agent

Let's create our first agent! Open `simple_agent.py` and follow along:

### Import Libraries

```python
import os
from dotenv import load_dotenv
from openai import OpenAI
# Or for Anthropic:
# from anthropic import Anthropic
```

### Create the Agent Class

```python
class SimpleAgent:
    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
        """
        Initialize the agent with an LLM model and system prompt.

        Args:
            model: The LLM model to use
            system_prompt: Instructions that define agent behavior
        """
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.system_prompt = system_prompt or """You are a helpful AI assistant.
        You provide clear, concise, and accurate responses."""

    def generate_response(self, user_message):
        """
        Generate a response to a user message.

        Args:
            user_message: The user's input text

        Returns:
            The agent's response as a string
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    def run(self):
        """
        Run the agent in an interactive loop.
        """
        print("Agent: Hello! I'm your AI assistant. Type 'quit' to exit.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Agent: Goodbye!")
                break

            if not user_input:
                continue

            try:
                response = self.generate_response(user_input)
                print(f"Agent: {response}\n")
            except Exception as e:
                print(f"Error: {e}\n")
```

## Step 4: Run Your Agent

Create a simple runner:

```python
if __name__ == "__main__":
    # Create agent with default settings
    agent = SimpleAgent()

    # Run interactive loop
    agent.run()
```

Run it:

```bash
python tutorials/01-basics/simple_agent.py
```

## Step 5: Customize Your Agent

### Different System Prompts

Try these variations:

**Pirate Agent:**
```python
pirate_prompt = """You are a helpful AI assistant who speaks like a pirate.
Use pirate slang and sayings while still being helpful and accurate."""

pirate_agent = SimpleAgent(system_prompt=pirate_prompt)
```

**Expert Agent:**
```python
expert_prompt = """You are an expert Python programming tutor. Provide
detailed, educational responses with code examples when appropriate."""

expert_agent = SimpleAgent(system_prompt=expert_prompt)
```

**Concise Agent:**
```python
concise_prompt = """You are a helpful assistant who gives brief, one or
two sentence answers. Be direct and concise."""

concise_agent = SimpleAgent(system_prompt=concise_prompt)
```

### Adjust Parameters

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    temperature=0.7,    # Creativity (0.0 - 2.0)
    max_tokens=500,     # Maximum response length
    top_p=1.0,          # Nucleus sampling
    frequency_penalty=0.0,  # Penalize repetition
    presence_penalty=0.0    # Encourage new topics
)
```

**Parameter Guide:**
- **temperature**: Higher = more creative, Lower = more focused
- **max_tokens**: Maximum length of response
- **top_p**: Alternative to temperature (0.0 - 1.0)

## Step 6: Using Anthropic Claude (Alternative)

If you prefer Claude:

```python
from anthropic import Anthropic

class SimpleAgentClaude:
    def __init__(self, model="claude-3-sonnet-20240229", system_prompt=None):
        load_dotenv()
        self.model = model
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.system_prompt = system_prompt or "You are a helpful AI assistant."

    def generate_response(self, user_message):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text
```

## Understanding What's Happening

### The Flow

```
1. User types message
   ↓
2. Agent creates message list [system, user]
   ↓
3. Sends to LLM API
   ↓
4. LLM processes and generates response
   ↓
5. Agent extracts and displays response
   ↓
6. Loop continues
```

### API Call Breakdown

```python
response = client.chat.completions.create(...)
```

This:
1. Sends your messages to OpenAI's servers
2. The model processes your prompt
3. Generates a response token by token
4. Returns the complete response

### Cost Considerations

Each API call costs money based on tokens used:
- **Tokens**: Roughly 4 characters = 1 token
- **Pricing**: Check provider pricing pages
- **Tip**: Use `max_tokens` to control costs

## Exercises

### Exercise 1: Custom Agent
Create an agent with a unique personality:
```python
# Your code here
my_agent = SimpleAgent(system_prompt="...")
```

### Exercise 2: Response Counter
Add a counter to track the number of responses:
```python
class SimpleAgent:
    def __init__(self, ...):
        # ... existing code ...
        self.response_count = 0

    def generate_response(self, user_message):
        # ... existing code ...
        self.response_count += 1
        return response
```

### Exercise 3: Save Conversation
Save the conversation to a file:
```python
def save_conversation(self, filename="conversation.txt"):
    # Your implementation
    pass
```

### Exercise 4: Error Handling
Improve error handling for common issues:
- No API key
- Network errors
- Rate limits
- Invalid responses

## Common Issues and Solutions

### Issue: "OpenAI API key not found"
**Solution**: Check your `.env` file exists and has the correct key.

### Issue: "Rate limit exceeded"
**Solution**: You're making too many requests. Wait a moment and try again.

### Issue: "Model not found"
**Solution**: Check you're using a valid model name (e.g., "gpt-3.5-turbo").

### Issue: Slow responses
**Solution**: Normal for API calls. Consider adding a loading indicator.

## Key Concepts Learned

- **Agent Structure**: Simple class with initialize, generate, and run methods
- **System Prompts**: Define agent behavior and personality
- **Message Format**: How LLMs expect conversation structure
- **API Integration**: Calling LLM services
- **Error Handling**: Graceful failure and user feedback

## What's Next?

In [Tutorial 02: Adding Memory](../02-memory/), you'll learn how to:
- Give your agent memory of past conversations
- Implement conversation history
- Create context-aware responses
- Manage memory efficiently

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [Prompt Engineering Guide](../../docs/concepts.md)

## Challenge Project

Build a **Specialized Assistant** that:
1. Has a specific domain (e.g., cooking, fitness, coding)
2. Maintains a consistent persona
3. Provides structured responses
4. Handles errors gracefully
5. Includes a help command

Example:
```python
fitness_agent = SimpleAgent(
    system_prompt="""You are a certified personal trainer. Provide
    workout advice, nutrition tips, and motivation. Always prioritize
    safety and recommend consulting healthcare providers."""
)
```

---

**Congratulations!** You've built your first AI agent. Move on to Tutorial 02 when you're ready to add memory capabilities.
