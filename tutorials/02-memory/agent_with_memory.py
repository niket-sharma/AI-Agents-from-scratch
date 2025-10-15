"""
Tutorial 02: AI Agent with Memory
Demonstrates various memory implementations for AI agents.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken


class MemoryAgent:
    """
    An AI agent with basic conversation memory.

    This agent maintains a full conversation history, allowing it to
    remember all previous interactions in the current session.
    """

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
        """Initialize agent with memory capabilities."""
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.conversation_history = []

    def add_to_history(self, role, content):
        """Add a message to the conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def get_context_messages(self):
        """Build message list with system prompt and history."""
        return [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

    def generate_response(self, user_message):
        """Generate a response with full conversation context."""
        # Add user message to history
        self.add_to_history("user", user_message)

        # Build messages with context
        messages = self.get_context_messages()

        # Generate response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        response_text = response.choices[0].message.content

        # Add agent response to history
        self.add_to_history("assistant", response_text)

        return response_text

    def run(self):
        """Run interactive conversation loop."""
        print("\n" + "="*60)
        print("Memory Agent - Interactive Mode")
        print("="*60)
        print("This agent remembers your conversation!")
        print("Type 'quit' to exit, 'history' to see conversation history.")
        print("="*60 + "\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Goodbye!\n")
                break

            if user_input.lower() == 'history':
                self.show_history()
                continue

            if not user_input:
                continue

            try:
                response = self.generate_response(user_input)
                print(f"\nAgent: {response}\n")
            except Exception as e:
                print(f"\nError: {e}\n")

    def show_history(self):
        """Display conversation history."""
        print("\n" + "="*60)
        print("Conversation History")
        print("="*60)
        for i, msg in enumerate(self.conversation_history, 1):
            role = msg['role'].capitalize()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"{i}. {role}: {content}")
        print("="*60 + "\n")


class BufferMemoryAgent(MemoryAgent):
    """
    An agent with buffer memory (sliding window).

    Keeps only the last N messages to avoid exceeding token limits.
    """

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None, max_history=10):
        """
        Initialize agent with buffer memory.

        Args:
            max_history: Maximum number of messages to keep in memory
        """
        super().__init__(model=model, system_prompt=system_prompt)
        self.max_history = max_history

    def add_to_history(self, role, content):
        """Add message and maintain buffer size."""
        super().add_to_history(role, content)

        # Keep only last max_history messages
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_memory_info(self):
        """Get information about memory usage."""
        return {
            "current_messages": len(self.conversation_history),
            "max_messages": self.max_history,
            "buffer_full": len(self.conversation_history) >= self.max_history
        }


class TokenAwareAgent(BufferMemoryAgent):
    """
    An agent that manages memory based on token count.

    This ensures the context stays within the model's token limits.
    """

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None, max_tokens=2000):
        """
        Initialize token-aware agent.

        Args:
            max_tokens: Maximum tokens to use for context
        """
        super().__init__(model=model, system_prompt=system_prompt)
        self.max_context_tokens = max_tokens

        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base encoding
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def count_messages_tokens(self, messages):
        """Count total tokens in a list of messages."""
        total = 0
        for message in messages:
            # Count content tokens
            total += self.count_tokens(message["content"])
            # Add overhead for message formatting
            total += 4

        # Add overhead for the message list
        total += 2
        return total

    def trim_history_to_fit(self):
        """Remove old messages to fit within token limit."""
        messages = self.get_context_messages()
        total_tokens = self.count_messages_tokens(messages)

        # Remove messages from history until we fit
        while (total_tokens > self.max_context_tokens and
               len(self.conversation_history) > 2):
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

    def get_token_info(self):
        """Get information about token usage."""
        current_tokens = self.count_messages_tokens(self.get_context_messages())
        return {
            "current_tokens": current_tokens,
            "max_tokens": self.max_context_tokens,
            "utilization": f"{(current_tokens / self.max_context_tokens) * 100:.1f}%"
        }


class PersistentMemoryAgent(BufferMemoryAgent):
    """
    An agent that can save and load conversations from disk.
    """

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

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Conversation saved to {filename}")
        return filename

    def load_conversation(self, filename):
        """Load conversation from a JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.conversation_history = data["history"]
        if "system_prompt" in data:
            self.system_prompt = data["system_prompt"]

        print(f"Loaded {len(self.conversation_history)} messages from {filename}")
        return len(self.conversation_history)

    def clear_history(self):
        """Clear conversation history."""
        message_count = len(self.conversation_history)
        self.conversation_history = []
        print(f"Cleared {message_count} messages from history.")
        return message_count

    def run(self):
        """Enhanced run with save/load commands."""
        print("\n" + "="*60)
        print("Persistent Memory Agent - Interactive Mode")
        print("="*60)
        print("Commands:")
        print("  - 'quit': Exit")
        print("  - 'history': Show conversation history")
        print("  - 'save': Save conversation to file")
        print("  - 'load <filename>': Load conversation from file")
        print("  - 'clear': Clear conversation history")
        print("="*60 + "\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Goodbye!\n")
                break

            if user_input.lower() == 'history':
                self.show_history()
                continue

            if user_input.lower() == 'save':
                self.save_conversation()
                continue

            if user_input.lower().startswith('load '):
                filename = user_input[5:].strip()
                try:
                    self.load_conversation(filename)
                except FileNotFoundError:
                    print(f"Error: File '{filename}' not found.\n")
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON in '{filename}'.\n")
                continue

            if user_input.lower() == 'clear':
                self.clear_history()
                continue

            if not user_input:
                continue

            try:
                response = self.generate_response(user_input)
                print(f"\nAgent: {response}\n")
            except Exception as e:
                print(f"\nError: {e}\n")


# Demonstration functions
def demo_basic_memory():
    """Demonstrate basic memory functionality."""
    print("\n=== Demo: Basic Memory ===\n")
    agent = MemoryAgent()

    # Conversation that tests memory
    responses = []
    responses.append(agent.generate_response("My name is Alice"))
    responses.append(agent.generate_response("I like Python programming"))
    responses.append(agent.generate_response("What's my name?"))
    responses.append(agent.generate_response("What do I like?"))

    for i, response in enumerate(responses, 1):
        print(f"Response {i}: {response}\n")


def demo_buffer_memory():
    """Demonstrate buffer memory with size limits."""
    print("\n=== Demo: Buffer Memory ===\n")
    agent = BufferMemoryAgent(max_history=4)

    # Add more messages than buffer can hold
    for i in range(6):
        agent.generate_response(f"Message {i+1}")

    # Check what's in memory
    info = agent.get_memory_info()
    print(f"Memory Info: {info}")
    print(f"Messages in history: {len(agent.conversation_history)}")
    print("(Should be 4, as older messages were removed)\n")


def demo_token_aware():
    """Demonstrate token-aware memory management."""
    print("\n=== Demo: Token-Aware Memory ===\n")
    agent = TokenAwareAgent(max_tokens=500)

    # Check initial tokens
    print(f"Initial: {agent.get_token_info()}")

    # Add some conversation
    agent.generate_response("Tell me about artificial intelligence in detail")
    print(f"After message: {agent.get_token_info()}\n")


if __name__ == "__main__":
    # Run interactive agent
    agent = PersistentMemoryAgent(max_history=10)
    agent.run()

    # Uncomment to run demos:
    # demo_basic_memory()
    # demo_buffer_memory()
    # demo_token_aware()
