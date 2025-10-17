"""
Enhanced Memory Agent with Visualization
Shows exactly what's stored in memory after each interaction.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken


class MemoryAgentVisualized:
    """AI agent with memory visualization."""

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
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

    def get_context_messages(self):
        """Build message list with system prompt and history."""
        return [
            {"role": "system", "content": self.system_prompt}
        ] + [{"role": m["role"], "content": m["content"]}
             for m in self.conversation_history]

    def visualize_memory(self):
        """Show what's currently in memory."""
        print("\n" + "┌" + "─"*78 + "┐")
        print("│" + " MEMORY CONTENTS ".center(78) + "│")
        print("├" + "─"*78 + "┤")

        if not self.conversation_history:
            print("│" + " [EMPTY - No messages in memory yet] ".center(78) + "│")
        else:
            print(f"│ Total messages in memory: {len(self.conversation_history)}".ljust(79) + "│")
            print("├" + "─"*78 + "┤")

            for i, msg in enumerate(self.conversation_history, 1):
                role = msg['role'].upper()
                timestamp = msg.get('timestamp', 'N/A')
                content = msg['content']

                # Truncate long messages
                if len(content) > 150:
                    content = content[:150] + "..."

                print(f"│ [{i}] {timestamp} - {role}:".ljust(79) + "│")

                # Word wrap content
                words = content.split()
                line = "│   "
                for word in words:
                    if len(line) + len(word) + 1 > 77:
                        print(line.ljust(79) + "│")
                        line = "│   " + word + " "
                    else:
                        line += word + " "
                if line.strip() != "│":
                    print(line.ljust(79) + "│")

                if i < len(self.conversation_history):
                    print("│" + "─"*78 + "│")

        print("└" + "─"*78 + "┘\n")

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
        """Run interactive conversation loop with memory visualization."""
        print("\n" + "="*80)
        print(" MEMORY AGENT WITH VISUALIZATION ".center(80, "="))
        print("="*80)
        print("This agent shows you exactly what's stored in memory!")
        print("\nCommands:")
        print("  • Type your message to chat")
        print("  • 'memory' or 'm' - Show current memory contents")
        print("  • 'stats' or 's' - Show memory statistics")
        print("  • 'quit' or 'q' - Exit")
        print("="*80 + "\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye!\n")
                break

            if user_input.lower() in ['memory', 'm']:
                self.visualize_memory()
                continue

            if user_input.lower() in ['stats', 's']:
                self.show_stats()
                continue

            if not user_input:
                continue

            try:
                response = self.generate_response(user_input)
                print(f"\n🤖 Agent: {response}\n")

                # Auto-show memory after each interaction
                print("📝 Memory updated. Type 'memory' to see what's stored.")

            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    def show_stats(self):
        """Show memory statistics."""
        print("\n" + "┌" + "─"*50 + "┐")
        print("│" + " MEMORY STATISTICS ".center(50) + "│")
        print("├" + "─"*50 + "┤")
        print(f"│ Total messages: {len(self.conversation_history)}".ljust(51) + "│")

        user_msgs = sum(1 for m in self.conversation_history if m['role'] == 'user')
        assistant_msgs = sum(1 for m in self.conversation_history if m['role'] == 'assistant')

        print(f"│ User messages: {user_msgs}".ljust(51) + "│")
        print(f"│ Assistant messages: {assistant_msgs}".ljust(51) + "│")

        total_chars = sum(len(m['content']) for m in self.conversation_history)
        print(f"│ Total characters: {total_chars}".ljust(51) + "│")

        print("└" + "─"*50 + "┘\n")


class BufferMemoryAgentVisualized(MemoryAgentVisualized):
    """Buffer memory with visualization - keeps only last N messages."""

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None, max_history=10):
        super().__init__(model=model, system_prompt=system_prompt)
        self.max_history = max_history
        self.total_messages_ever = 0  # Track total across buffer

    def add_to_history(self, role, content):
        """Add message and maintain buffer size."""
        super().add_to_history(role, content)
        self.total_messages_ever += 1

        # Keep only last max_history messages
        if len(self.conversation_history) > self.max_history:
            removed = len(self.conversation_history) - self.max_history
            self.conversation_history = self.conversation_history[-self.max_history:]
            print(f"⚠️  Buffer full! Removed {removed} oldest message(s) from memory.")

    def show_stats(self):
        """Show buffer memory statistics."""
        print("\n" + "┌" + "─"*50 + "┐")
        print("│" + " BUFFER MEMORY STATISTICS ".center(50) + "│")
        print("├" + "─"*50 + "┤")
        print(f"│ Messages in memory: {len(self.conversation_history)}".ljust(51) + "│")
        print(f"│ Maximum capacity: {self.max_history}".ljust(51) + "│")
        print(f"│ Total messages (all time): {self.total_messages_ever}".ljust(51) + "│")
        print(f"│ Messages forgotten: {self.total_messages_ever - len(self.conversation_history)}".ljust(51) + "│")

        utilization = (len(self.conversation_history) / self.max_history) * 100
        print(f"│ Buffer utilization: {utilization:.1f}%".ljust(51) + "│")

        print("└" + "─"*50 + "┘\n")


class TokenAwareAgentVisualized(BufferMemoryAgentVisualized):
    """Token-aware memory with visualization."""

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None, max_tokens=2000):
        super().__init__(model=model, system_prompt=system_prompt)
        self.max_context_tokens = max_tokens

        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def count_messages_tokens(self, messages):
        """Count total tokens in a list of messages."""
        total = 0
        for message in messages:
            total += self.count_tokens(message["content"])
            total += 4  # Message formatting overhead

        total += 2  # Message list overhead
        return total

    def trim_history_to_fit(self):
        """Remove old messages to fit within token limit."""
        messages = self.get_context_messages()
        total_tokens = self.count_messages_tokens(messages)

        removed_count = 0
        while (total_tokens > self.max_context_tokens and
               len(self.conversation_history) > 2):
            # Remove oldest pair (user + assistant)
            self.conversation_history = self.conversation_history[2:]
            messages = self.get_context_messages()
            total_tokens = self.count_messages_tokens(messages)
            removed_count += 2

        if removed_count > 0:
            print(f"⚠️  Token limit! Removed {removed_count} oldest message(s) to fit within {self.max_context_tokens} tokens.")

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

    def show_stats(self):
        """Show token-aware memory statistics."""
        current_tokens = self.count_messages_tokens(self.get_context_messages())

        print("\n" + "┌" + "─"*50 + "┐")
        print("│" + " TOKEN-AWARE MEMORY STATISTICS ".center(50) + "│")
        print("├" + "─"*50 + "┤")
        print(f"│ Messages in memory: {len(self.conversation_history)}".ljust(51) + "│")
        print(f"│ Current tokens: {current_tokens}".ljust(51) + "│")
        print(f"│ Maximum tokens: {self.max_context_tokens}".ljust(51) + "│")
        print(f"│ Available tokens: {self.max_context_tokens - current_tokens}".ljust(51) + "│")

        utilization = (current_tokens / self.max_context_tokens) * 100
        print(f"│ Token utilization: {utilization:.1f}%".ljust(51) + "│")

        # Visual progress bar
        bar_width = 40
        filled = int(bar_width * current_tokens / self.max_context_tokens)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"│ [{bar}]".ljust(51) + "│")

        print("└" + "─"*50 + "┘\n")


def demo_memory_visualization():
    """Interactive demo showing memory in action."""
    print("\n" + "="*80)
    print(" MEMORY VISUALIZATION DEMO ".center(80, "="))
    print("="*80)
    print("\nChoose an agent type to see how memory works:\n")
    print("1. Basic Memory - Stores ALL messages (unlimited)")
    print("2. Buffer Memory - Stores only last 6 messages (sliding window)")
    print("3. Token-Aware Memory - Manages memory based on token count")
    print("\n" + "="*80 + "\n")

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        agent = MemoryAgentVisualized()
        print("\n✅ Using Basic Memory Agent (unlimited history)\n")
    elif choice == "2":
        agent = BufferMemoryAgentVisualized(max_history=6)
        print("\n✅ Using Buffer Memory Agent (max 6 messages)\n")
    elif choice == "3":
        agent = TokenAwareAgentVisualized(max_tokens=500)
        print("\n✅ Using Token-Aware Memory Agent (max 500 tokens)\n")
    else:
        print("Invalid choice, using Basic Memory Agent")
        agent = MemoryAgentVisualized()

    agent.run()


if __name__ == "__main__":
    demo_memory_visualization()
