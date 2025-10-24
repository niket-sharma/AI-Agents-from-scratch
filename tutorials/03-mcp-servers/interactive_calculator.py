# -*- coding: utf-8 -*-
"""
Interactive Calculator - Test MCP Tools Without MCP Protocol
=============================================================

This is a simplified version that you can interact with directly.
It uses the same logic as the MCP server but without the JSON-RPC protocol.

This is NOT an MCP server - it's a demo to help you understand the tools!
"""

import sys
import io

# Force UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class InteractiveCalculator:
    """Interactive calculator with the same tools as the MCP server."""

    def __init__(self):
        self.tools = {
            'add': {
                'description': 'Add two numbers together',
                'params': ['a', 'b']
            },
            'multiply': {
                'description': 'Multiply two numbers',
                'params': ['a', 'b']
            },
            'power': {
                'description': 'Raise a number to a power (a^b)',
                'params': ['base', 'exponent']
            }
        }

    def show_tools(self):
        """Display available tools."""
        print("\nAvailable Tools:")
        print("=" * 60)
        for name, info in self.tools.items():
            print(f"\n  {name}")
            print(f"    Description: {info['description']}")
            print(f"    Parameters: {', '.join(info['params'])}")
        print("\n" + "=" * 60)

    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        return f"The sum of {a} and {b} is {result}"

    def multiply(self, a, b):
        """Multiply two numbers."""
        result = a * b
        return f"The product of {a} and {b} is {result}"

    def power(self, base, exponent):
        """Raise a number to a power."""
        result = base ** exponent
        return f"{base} raised to the power of {exponent} is {result}"

    def call_tool(self, name, *args):
        """Call a tool with arguments."""
        if name == 'add':
            if len(args) != 2:
                return "Error: 'add' requires 2 numbers"
            return self.add(float(args[0]), float(args[1]))

        elif name == 'multiply':
            if len(args) != 2:
                return "Error: 'multiply' requires 2 numbers"
            return self.multiply(float(args[0]), float(args[1]))

        elif name == 'power':
            if len(args) != 2:
                return "Error: 'power' requires 2 numbers (base, exponent)"
            return self.power(float(args[0]), float(args[1]))

        else:
            return f"Error: Unknown tool '{name}'"

    def run(self):
        """Run the interactive calculator."""
        print("\n" + "=" * 60)
        print(" INTERACTIVE CALCULATOR ".center(60, "="))
        print("=" * 60)
        print("\nThis demonstrates the MCP calculator tools interactively.")
        print("You can actually use the tools without needing JSON-RPC!")
        print("\n" + "=" * 60)

        self.show_tools()

        print("\nHow to use:")
        print("  - Type: tool_name arg1 arg2")
        print("  - Example: add 10 5")
        print("  - Example: multiply 7 8")
        print("  - Example: power 2 10")
        print("\nCommands:")
        print("  - 'help' or 'tools' - Show available tools")
        print("  - 'quit' or 'exit' - Exit")
        print("\n" + "=" * 60)

        while True:
            try:
                print()
                user_input = input("Calculator> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!\n")
                    break

                if user_input.lower() in ['help', 'tools', '?']:
                    self.show_tools()
                    continue

                # Parse command
                parts = user_input.split()
                if len(parts) == 0:
                    continue

                tool_name = parts[0].lower()
                args = parts[1:]

                # Call the tool
                result = self.call_tool(tool_name, *args)
                print(f"\n  Result: {result}")

            except ValueError as e:
                print(f"\n  Error: Invalid number format. Please use numbers only.")
            except KeyboardInterrupt:
                print("\n\nGoodbye!\n")
                break
            except Exception as e:
                print(f"\n  Error: {e}")


def main():
    """Run the interactive calculator."""
    calc = InteractiveCalculator()
    calc.run()


if __name__ == "__main__":
    main()
