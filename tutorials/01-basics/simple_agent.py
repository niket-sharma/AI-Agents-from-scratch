"""
Tutorial 01: Simple AI Agent
A basic conversational AI agent using OpenAI's API.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI


class SimpleAgent:
    """
    A simple AI agent that can have conversations using an LLM.

    This agent demonstrates the basic components of an AI agent:
    - System prompt (defines behavior)
    - Message handling (user input/agent output)
    - LLM integration (API calls)
    - Conversation loop (interactive mode)
    """

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
        """
        Initialize the agent with an LLM model and system prompt.

        Args:
            model (str): The LLM model to use (default: gpt-3.5-turbo)
            system_prompt (str): Instructions that define agent behavior
        """
        # Load environment variables from .env file
        load_dotenv()

        # Set up the model
        self.model = model

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file."
            )

        self.client = OpenAI(api_key=api_key)

        # Set default system prompt if none provided
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

        Raises:
            Exception: If the API call fails
        """
        # Construct the messages list
        # System message defines behavior, user message is the input
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,      # Controls randomness (0.0 - 2.0)
            max_tokens=500,       # Maximum length of response
            top_p=1.0,           # Nucleus sampling parameter
            frequency_penalty=0.0,  # Penalize repeated tokens
            presence_penalty=0.0    # Penalize tokens based on presence
        )

        # Extract and return the response text
        return response.choices[0].message.content

    def run(self):
        """
        Run the agent in an interactive loop.

        The user can type messages and receive responses until they
        type 'quit', 'exit', or 'bye'.
        """
        print("\n" + "="*60)
        print("Simple AI Agent - Interactive Mode")
        print("="*60)
        print("Agent: Hello! I'm your AI assistant.")
        print("       Type your message and press Enter.")
        print("       Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("="*60 + "\n")

        while True:
            # Get user input
            user_input = input("You: ").strip()

            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Goodbye! Have a great day!\n")
                break

            # Skip empty inputs
            if not user_input:
                continue

            try:
                # Generate and display response
                print("\nAgent: ", end="", flush=True)
                response = self.generate_response(user_input)
                print(f"{response}\n")

            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again or type 'quit' to exit.\n")


# Example usage and demonstrations
def demo_basic_agent():
    """Run a basic agent with default settings."""
    agent = SimpleAgent()
    agent.run()


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


def demo_pirate_agent():
    """Run an agent with a pirate personality."""
    pirate_prompt = """You are a helpful AI assistant who speaks like a pirate.
Use pirate slang and sayings while still being helpful and accurate.
Start responses with 'Ahoy!' and use phrases like 'matey', 'arr', etc."""

    agent = SimpleAgent(system_prompt=pirate_prompt)
    agent.run()


def demo_single_response():
    """Demonstrate a single request-response (non-interactive)."""
    agent = SimpleAgent()

    # Example questions
    questions = [
        "What is Python?",
        "Explain what an AI agent is in one sentence.",
        "What's the difference between a list and a tuple in Python?"
    ]

    print("\n" + "="*60)
    print("Single Response Demo")
    print("="*60 + "\n")

    for question in questions:
        print(f"Question: {question}")
        response = agent.generate_response(question)
        print(f"Answer: {response}\n")
        print("-"*60 + "\n")


if __name__ == "__main__":
    # Run the basic interactive agent
    demo_basic_agent()

    # Uncomment to try other demos:
    # demo_custom_agent()
    # demo_pirate_agent()
    # demo_single_response()
