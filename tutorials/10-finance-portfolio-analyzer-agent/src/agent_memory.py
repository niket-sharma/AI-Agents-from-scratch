"""
Memory extension for FinanceAgent

This module adds Layer 5 (Memory) capabilities to the agent
"""

import os
import json
from typing import Dict, Any


class MemoryMixin:
    """Mixin class to add memory capabilities to the agent"""

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return self._create_empty_memory()
        return self._create_empty_memory()

    def _create_empty_memory(self) -> Dict[str, Any]:
        """Create empty memory structure"""
        return {
            "user_preferences": {},
            "portfolio_history": [],
            "important_facts": []
        }

    def _save_memory(self):
        """Save memory to JSON file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def get_memory_context(self) -> str:
        """Format memory for system prompt"""
        if not any([
            self.memory["user_preferences"],
            self.memory["important_facts"],
            self.memory["portfolio_history"]
        ]):
            return ""

        context = "\n\nREMEMBERED USER CONTEXT:\n"

        if self.memory["user_preferences"]:
            context += "\nUser Preferences:\n"
            for key, value in self.memory["user_preferences"].items():
                context += f"- {key}: {value}\n"

        if self.memory["important_facts"]:
            context += "\nImportant Facts:\n"
            for fact in self.memory["important_facts"]:
                context += f"- {fact}\n"

        return context

    def update_memory(self, key: str, value: Any):
        """
        Update a specific memory value

        Args:
            key: Memory key (from user_preferences)
            value: Value to store
        """
        self.memory["user_preferences"][key] = value
        self._save_memory()
        print(f"Memory updated: {key} = {value}")

    def add_important_fact(self, fact: str):
        """
        Add an important fact to memory

        Args:
            fact: Important fact to remember
        """
        if fact not in self.memory["important_facts"]:
            self.memory["important_facts"].append(fact)
            self._save_memory()
            print(f"Added to memory: {fact}")

    def view_memory(self) -> str:
        """Return formatted memory as string"""
        output = "=== AGENT MEMORY ===\n\n"

        output += "User Preferences:\n"
        if self.memory["user_preferences"]:
            for key, value in self.memory["user_preferences"].items():
                output += f"  {key}: {value}\n"
        else:
            output += "  (none)\n"

        output += "\nImportant Facts:\n"
        if self.memory["important_facts"]:
            for fact in self.memory["important_facts"]:
                output += f"  - {fact}\n"
        else:
            output += "  (none)\n"

        output += f"\nPortfolio History: {len(self.memory['portfolio_history'])} entries\n"

        return output

    def clear_memory(self):
        """Reset all memory"""
        self.memory = self._create_empty_memory()
        self._save_memory()
        print("Memory cleared.")

    def remove_memory_item(self, key: str):
        """
        Remove specific preference from memory

        Args:
            key: Preference key to remove
        """
        if key in self.memory["user_preferences"]:
            del self.memory["user_preferences"][key]
            self._save_memory()
            print(f"Removed from memory: {key}")
        else:
            print(f"Key not found in memory: {key}")

    def _extract_and_save_preferences(self, user_msg: str, assistant_msg: str):
        """
        Extract preferences from conversation and save to memory
        This is a simple keyword-based extraction.
        In production, you might use Claude's structured extraction.

        Args:
            user_msg: User's message
            assistant_msg: Assistant's response
        """
        user_lower = user_msg.lower()

        # Extract risk tolerance
        if "conservative" in user_lower:
            self.update_memory("risk_tolerance", "conservative")
        elif "aggressive" in user_lower:
            self.update_memory("risk_tolerance", "aggressive")
        elif "moderate" in user_lower:
            self.update_memory("risk_tolerance", "moderate")

        # Extract investment goals
        if "retirement" in user_lower:
            self.add_important_fact("User is focused on retirement planning")
        if "college" in user_lower or "education" in user_lower:
            self.add_important_fact("User is saving for education")
        if "house" in user_lower or "home" in user_lower:
            self.add_important_fact("User is saving for a home purchase")

        # Extract preferences
        if "avoid crypto" in user_lower or "no crypto" in user_lower:
            self.update_memory("avoid_crypto", True)
        if "esg" in user_lower or "sustainable" in user_lower:
            self.update_memory("prefer_esg", True)

    def chat_with_memory(self, message: str) -> str:
        """
        Full-featured chat with all capabilities (Layer 5)
        Includes Skills, Computer Use, and Memory

        Args:
            message: User's message

        Returns:
            Agent's response
        """
        # Build system prompt with memory context
        system_with_memory = self.system_prompt + self.get_memory_context()

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response from Claude with all features
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            system=system_with_memory,
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
                system=system_with_memory,
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

        # Extract and save preferences from this exchange
        self._extract_and_save_preferences(message, assistant_message)

        return assistant_message
