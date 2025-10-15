# Tutorial 02: Adding Memory to Your Agent

In Tutorial 01, we built a basic agent, but it had a critical limitation: it couldn't remember past conversations. Every interaction was isolated. In this tutorial, we'll give our agent memory!

## Learning Objectives

By the end of this tutorial, you will:
- Understand different types of agent memory
- Implement conversation history tracking
- Create a memory buffer system
- Handle context window limitations
- Implement memory summarization
- Build a context-aware agent

## Prerequisites

- Completed Tutorial 01
- Understanding of Python lists and dictionaries
- Familiarity with basic agent structure

## Time Required

Approximately 45 minutes

## What You'll Build

An agent with memory that can:
1. Remember previous messages in the conversation
2. Maintain context across multiple exchanges
3. Handle long conversations efficiently
4. Summarize old conversations to save space

## Why Memory Matters

### Without Memory:
```
You: My name is Alice
Agent: Nice to meet you, Alice!

You: What's my name?
Agent: I don't know your name. Could you tell me?
```

### With Memory:
```
You: My name is Alice
Agent: Nice to meet you, Alice!

You: What's my name?
Agent: Your name is Alice!
```

## Types of Memory

### 1. Short-term Memory (Working Memory)
Recent conversation history used for immediate context.

**Characteristics:**
- Fast access
- Limited capacity
- Temporary

### 2. Long-term Memory (Persistent Storage)
Important information stored for future use.

**Characteristics:**
- Larger capacity
- Slower access (requires search)
- Persistent across sessions

### 3. Buffer Memory
A simple sliding window of recent messages.

**Characteristics:**
- Easiest to implement
- Fixed size (e.g., last 10 messages)
- Good for most use cases

## Step 1: Understanding the Challenge

### Context Window Limits

LLMs have token limits:
- GPT-3.5-turbo: 4,096 tokens (~3,000 words)
- GPT-4: 8,192 tokens (~6,000 words)
- GPT-4-32k: 32,768 tokens (~24,000 words)

A long conversation can exceed these limits!

### Memory Strategies

1. **Keep Everything**: Simple but hits limits quickly
2. **Sliding Window**: Keep last N messages
3. **Summarization**: Summarize old messages
4. **Selective**: Keep only important information

## Step 2: Implementing Conversation History

Let's enhance our agent with memory:

```python
class MemoryAgent:
    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = system_prompt or "You are a helpful AI assistant."

        # NEW: Conversation history
        self.conversation_history = []

    def add_to_history(self, role, content):
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def generate_response(self, user_message):
        """Generate a response with conversation context."""
        # Add user message to history
        self.add_to_history("user", user_message)

        # Build messages with full history
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        # Get response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        # Extract response content
        response_text = response.choices[0].message.content

        # Add agent response to history
        self.add_to_history("assistant", response_text)

        return response_text
```

## Step 3: Implementing Buffer Memory

To avoid hitting token limits, use a sliding window:

```python
class BufferMemoryAgent:
    def __init__(self, model="gpt-3.5-turbo", system_prompt=None,
                 max_history=10):
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = system_prompt or "You are a helpful AI assistant."

        # Memory configuration
        self.max_history = max_history  # Maximum messages to keep
        self.conversation_history = []

    def add_to_history(self, role, content):
        """Add a message and maintain buffer size."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

        # Keep only the last max_history messages
        if len(self.conversation_history) > self.max_history:
            # Remove oldest message (but keep in pairs for context)
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_context_messages(self):
        """Get messages for LLM with system prompt."""
        return [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

    def generate_response(self, user_message):
        """Generate response with buffered context."""
        # Add user message
        self.add_to_history("user", user_message)

        # Get messages with context
        messages = self.get_context_messages()

        # Generate response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        response_text = response.choices[0].message.content

        # Add response to history
        self.add_to_history("assistant", response_text)

        return response_text

    def get_history_summary(self):
        """Get a summary of the conversation history."""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history
                                 if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.conversation_history
                                      if m["role"] == "assistant"]),
            "buffer_size": self.max_history
        }
```

## Step 4: Token Counting

To manage context efficiently, count tokens:

```python
import tiktoken

class TokenAwareAgent(BufferMemoryAgent):
    def __init__(self, model="gpt-3.5-turbo", system_prompt=None,
                 max_tokens=2000):
        super().__init__(model=model, system_prompt=system_prompt)
        self.max_context_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model)

    def count_tokens(self, text):
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def count_messages_tokens(self, messages):
        """Count total tokens in a list of messages."""
        total = 0
        for message in messages:
            # Add tokens for message content
            total += self.count_tokens(message["content"])
            # Add overhead for message structure
            total += 4  # Approximate overhead per message
        return total

    def trim_history_to_fit(self):
        """Remove old messages to fit within token limit."""
        messages = self.get_context_messages()
        total_tokens = self.count_messages_tokens(messages)

        while total_tokens > self.max_context_tokens and len(self.conversation_history) > 2:
            # Remove oldest pair (user + assistant)
            self.conversation_history = self.conversation_history[2:]
            messages = self.get_context_messages()
            total_tokens = self.count_messages_tokens(messages)

        return total_tokens

    def generate_response(self, user_message):
        """Generate response with token-aware context management."""
        self.add_to_history("user", user_message)

        # Trim history to fit token limit
        tokens_used = self.trim_history_to_fit()

        messages = self.get_context_messages()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        response_text = response.choices[0].message.content
        self.add_to_history("assistant", response_text)

        return response_text
```

## Step 5: Memory Summarization

For very long conversations, summarize old context:

```python
class SummarizingAgent(TokenAwareAgent):
    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
        super().__init__(model=model, system_prompt=system_prompt)
        self.summary = ""

    def summarize_conversation(self, messages_to_summarize):
        """Create a summary of old conversation."""
        # Build text from messages
        conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in messages_to_summarize
        ])

        # Ask LLM to summarize
        summary_prompt = f"""Summarize this conversation concisely,
focusing on key information and context:

{conversation_text}

Summary:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )

        return response.choices[0].message.content

    def manage_context_with_summary(self):
        """Summarize old messages when context gets too long."""
        if len(self.conversation_history) > 10:
            # Summarize oldest messages
            messages_to_summarize = self.conversation_history[:6]
            self.summary = self.summarize_conversation(messages_to_summarize)

            # Keep only recent messages
            self.conversation_history = self.conversation_history[6:]

    def get_context_messages(self):
        """Get messages including summary if available."""
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add summary if available
        if self.summary:
            messages.append({
                "role": "system",
                "content": f"Conversation summary: {self.summary}"
            })

        # Add recent history
        messages.extend(self.conversation_history)

        return messages
```

## Step 6: Persistent Memory (Save/Load)

Save conversations to disk:

```python
import json
from datetime import datetime

class PersistentMemoryAgent(BufferMemoryAgent):
    def save_conversation(self, filename=None):
        """Save conversation to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"

        data = {
            "system_prompt": self.system_prompt,
            "model": self.model,
            "timestamp": datetime.now().isoformat(),
            "history": self.conversation_history
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Conversation saved to {filename}")
        return filename

    def load_conversation(self, filename):
        """Load conversation from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        self.conversation_history = data["history"]
        print(f"Loaded {len(self.conversation_history)} messages from {filename}")

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("Conversation history cleared.")
```

## Testing Your Memory Agent

```python
def test_memory():
    agent = BufferMemoryAgent(max_history=10)

    # Test memory
    print("Test 1: Name memory")
    response1 = agent.generate_response("My name is Alice")
    print(f"Agent: {response1}\n")

    response2 = agent.generate_response("What's my name?")
    print(f"Agent: {response2}\n")

    # Check history
    summary = agent.get_history_summary()
    print(f"History: {summary}")
```

## Exercises

### Exercise 1: Conversation Statistics
Add a method to show conversation statistics:
```python
def get_stats(self):
    # Return: total words, average message length, etc.
    pass
```

### Exercise 2: Selective Memory
Implement memory that only keeps "important" messages:
```python
def is_important(self, message):
    # Determine if a message is important
    # (e.g., contains names, facts, preferences)
    pass
```

### Exercise 3: Memory Search
Add ability to search conversation history:
```python
def search_history(self, query):
    # Find messages mentioning a keyword
    pass
```

## Best Practices

1. **Start Small**: Begin with buffer memory
2. **Monitor Tokens**: Track token usage to avoid limits
3. **Test Edge Cases**: Very long conversations, empty messages
4. **Save Important Conversations**: Implement persistence
5. **Clear Old Memory**: Provide a way to reset

## Common Patterns

### Pattern 1: User Preferences
```python
# Remember user preferences
agent.generate_response("I prefer concise answers")
# Later...
agent.generate_response("Explain quantum physics")
# Agent remembers to be concise
```

### Pattern 2: Multi-turn Tasks
```python
# Build on previous context
agent.generate_response("I need help planning a trip")
agent.generate_response("I like beaches")
agent.generate_response("My budget is $2000")
# Agent uses all context to make recommendations
```

## What's Next?

In [Tutorial 03: Tool Integration](../03-tools/), you'll learn how to:
- Give your agent access to external tools
- Implement function calling
- Create custom tools
- Handle tool execution

## Key Concepts Learned

- Conversation history management
- Buffer memory implementation
- Token counting and limits
- Memory summarization
- Persistent storage
- Context-aware responses

---

**Well done!** Your agent can now remember conversations. Ready to give it tools? Move on to Tutorial 03!
