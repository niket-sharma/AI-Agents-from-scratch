"""
Finance Portfolio Analyzer Agent

This module implements a progressive AI agent that demonstrates:
- Layer 1: Basic conversation
- Layer 2: Skills integration
- Layer 3: Computer use for file operations
- Layer 4: MCP server integration for real-time data
- Layer 5: Memory for persistent context
"""

import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from anthropic.types.beta import BetaMessageParam
from agent_memory import MemoryMixin


class FinanceAgent(MemoryMixin):
    """AI Agent for personal finance portfolio analysis"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Finance Agent

        Args:
            api_key: Anthropic API key (if not provided, loads from ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt = "You are a helpful financial advisor assistant with expertise in portfolio analysis, investment strategies, and personal finance."
        self.memory_file = "agent_memory.json"
        self.memory: Dict[str, Any] = self._load_memory()

    def chat(self, message: str) -> str:
        """
        Basic chat with the agent (Layer 1)

        Args:
            message: User's message

        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response from Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.conversation_history
        )

        # Extract assistant's response
        assistant_message = response.content[0].text

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def reset(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared.")

    def get_history_length(self) -> int:
        """Get the number of messages in conversation history"""
        return len(self.conversation_history)

    def chat_with_skills(self, message: str) -> str:
        """
        Chat with Skills enabled (Layer 2)

        Args:
            message: User's message

        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response from Claude with Skills
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.conversation_history,
            betas=["skills-2025-01-31"],
            tools=[{"type": "code_execution"}],
            skill_ids=["portfolio-analysis", "excel-reporting"]
        )

        # Handle tool use loop
        while response.stop_reason == "tool_use":
            # Extract tool uses
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # Code execution happens automatically
                    # We'll get the result in the next response
                    pass

            # Add assistant message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            # Continue conversation to get final response
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.conversation_history,
                betas=["skills-2025-01-31"],
                tools=[{"type": "code_execution"}],
                skill_ids=["portfolio-analysis", "excel-reporting"]
            )

        # Extract final response
        assistant_message = ""
        for block in response.content:
            if hasattr(block, "text"):
                assistant_message += block.text

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def chat_with_computer(self, message: str) -> str:
        """
        Chat with Computer Use enabled (Layer 3)
        Enables file operations on /mnt/user-data/

        Args:
            message: User's message

        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response from Claude with Computer Use
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,  # Higher for computer use
            system=self.system_prompt,
            messages=self.conversation_history,
            betas=["skills-2025-01-31", "computer-use-2024-10-22"],
            tools=[
                {"type": "code_execution"},
                {
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": 1024,
                    "display_height_px": 768,
                    "display_number": 1
                }
            ],
            skill_ids=["portfolio-analysis", "excel-reporting"]
        )

        # Handle tool use loop
        while response.stop_reason == "tool_use":
            # Add assistant message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            # Continue conversation
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                system=self.system_prompt,
                messages=self.conversation_history,
                betas=["skills-2025-01-31", "computer-use-2024-10-22"],
                tools=[
                    {"type": "code_execution"},
                    {
                        "type": "computer_20241022",
                        "name": "computer",
                        "display_width_px": 1024,
                        "display_height_px": 768,
                        "display_number": 1
                    }
                ],
                skill_ids=["portfolio-analysis", "excel-reporting"]
            )

        # Extract final response
        assistant_message = ""
        for block in response.content:
            if hasattr(block, "text"):
                assistant_message += block.text

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message
