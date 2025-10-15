"""
Tutorial 01: Simple AI Agent (Anthropic Claude Version)
A basic conversational AI agent using Anthropic's Claude API.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic


class SimpleAgentClaude:
    """
    A simple AI agent that can have conversations using Anthropic's Claude.

    This is an alternative implementation using Claude instead of OpenAI.
    The core concepts remain the same.
    """

    def __init__(self, model="claude-3-5-sonnet-20241022", system_prompt=None):
        """
        Initialize the agent with Claude model and system prompt.

        Args:
            model (str): The Claude model to use
            system_prompt (str): Instructions that define agent behavior
        """
        # Load environment variables
        load_dotenv()

        self.model = model

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Please set it in your .env file."
            )

        self.client = Anthropic(api_key=api_key)

        # Set default system prompt
        self.system_prompt = system_prompt or """You are a helpful AI assistant.
You provide clear, concise, and accurate responses to user questions.
You are friendly and professional."""

        print(f"Agent initialized with model: {self.model}")

    def generate_response(self, user_message):
        """
        Generate a response to a user message.

        Args:
            user_message (str): The user's input text

        Returns:
            str: The agent's response
        """
        # Call the Anthropic API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.7,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Extract and return the response text
        return response.content[0].text

    def run(self):
        """
        Run the agent in an interactive loop.
        """
        print("\n" + "="*60)
        print("Simple AI Agent (Claude) - Interactive Mode")
        print("="*60)
        print("Agent: Hello! I'm your AI assistant powered by Claude.")
        print("       Type your message and press Enter.")
        print("       Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("="*60 + "\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Goodbye! Have a great day!\n")
                break

            if not user_input:
                continue

            try:
                print("\nAgent: ", end="", flush=True)
                response = self.generate_response(user_input)
                print(f"{response}\n")

            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    agent = SimpleAgentClaude()
    agent.run()
