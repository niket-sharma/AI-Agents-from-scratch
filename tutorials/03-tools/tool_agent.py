"""
Tutorial 03: AI Agent with Tools
Demonstrates how to build agents that can use external tools and functions.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI


# ============================================================================
# Tool Functions
# ============================================================================

def calculator(operation, a, b):
    """
    Perform basic mathematical operations.

    Args:
        operation: One of 'add', 'subtract', 'multiply', 'divide'
        a: First number
        b: Second number

    Returns:
        Result of the operation
    """
    operations = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }

    if operation not in operations:
        return f"Error: Unknown operation '{operation}'"

    try:
        result = operations[operation](float(a), float(b))
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def get_current_time(timezone="UTC"):
    """
    Get the current time in a specified timezone.

    Args:
        timezone: Timezone name (e.g., 'UTC', 'EST', 'PST')

    Returns:
        Current time information
    """
    # Simplified - in production use pytz or zoneinfo
    current_time = datetime.now()
    return {
        "timezone": timezone,
        "time": current_time.strftime("%H:%M:%S"),
        "date": current_time.strftime("%Y-%m-%d"),
        "timestamp": current_time.isoformat()
    }


def get_weather(location, unit="celsius"):
    """
    Get weather information for a location (mock implementation).

    Args:
        location: City name
        unit: Temperature unit ('celsius' or 'fahrenheit')

    Returns:
        Weather data dictionary
    """
    # Mock data - in production, integrate with a real weather API
    mock_temperatures = {
        "celsius": {"New York": 18, "London": 12, "Tokyo": 22, "Paris": 15},
        "fahrenheit": {"New York": 64, "London": 54, "Tokyo": 72, "Paris": 59}
    }

    temp_dict = mock_temperatures.get(unit, mock_temperatures["celsius"])
    temperature = temp_dict.get(location, 20 if unit == "celsius" else 68)

    return {
        "location": location,
        "temperature": temperature,
        "unit": unit,
        "condition": "Partly cloudy",
        "humidity": 65,
        "wind_speed": 10
    }


def search_web(query, num_results=3):
    """
    Search the web for information (mock implementation).

    Args:
        query: Search query string
        num_results: Number of results to return

    Returns:
        List of search results
    """
    # Mock implementation - use DuckDuckGo, Google, or Brave API in production
    return {
        "query": query,
        "num_results": num_results,
        "results": [
            {
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is information about {query}. Lorem ipsum dolor sit amet..."
            }
            for i in range(num_results)
        ]
    }


# ============================================================================
# Tool Schemas (Function Definitions for OpenAI)
# ============================================================================

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform basic mathematical operations (add, subtract, multiply, divide)",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The mathematical operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time in a specified timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone name (e.g., 'UTC', 'EST', 'PST')",
                        "default": "UTC"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'New York', 'London', 'Tokyo')"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit",
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information on a given topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ============================================================================
# Tool Registry
# ============================================================================

class ToolRegistry:
    """
    Manages available tools for the agent.

    Provides methods to register tools, execute them, and get their schemas.
    """

    def __init__(self):
        """Initialize the tool registry."""
        self.tools = {}
        self.schemas = []

    def register(self, name, function, schema):
        """
        Register a new tool.

        Args:
            name: Tool name
            function: Callable function
            schema: OpenAI function schema
        """
        self.tools[name] = {
            'function': function,
            'schema': schema
        }
        self.schemas.append(schema)
        print(f"Registered tool: {name}")

    def execute(self, name, **parameters):
        """
        Execute a tool by name with given parameters.

        Args:
            name: Tool name
            **parameters: Tool parameters

        Returns:
            Tool execution result
        """
        if name not in self.tools:
            return {"error": f"Tool '{name}' not found"}

        try:
            tool_function = self.tools[name]['function']
            result = tool_function(**parameters)
            return result
        except TypeError as e:
            return {"error": f"Invalid parameters: {str(e)}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    def get_schemas(self):
        """Get all tool schemas for the LLM."""
        return self.schemas

    def get_tool_names(self):
        """Get list of available tool names."""
        return list(self.tools.keys())


# ============================================================================
# Tool Agent
# ============================================================================

class ToolAgent:
    """
    An AI agent that can use external tools.

    This agent can understand when to use tools, call them with appropriate
    parameters, and integrate the results into its responses.
    """

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
        """
        Initialize the tool agent.

        Args:
            model: OpenAI model to use
            system_prompt: System prompt for the agent
        """
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.system_prompt = system_prompt or """You are a helpful AI assistant with access to tools.
Use the available tools when they can help answer the user's question more accurately.
Always explain what tools you're using and why."""

        self.conversation_history = []
        self.tool_registry = ToolRegistry()
        self._setup_default_tools()

    def _setup_default_tools(self):
        """Register default tools."""
        # Map tool schemas to functions
        tool_functions = {
            "calculator": calculator,
            "get_current_time": get_current_time,
            "get_weather": get_weather,
            "search_web": search_web
        }

        for schema in TOOL_SCHEMAS:
            func_name = schema["function"]["name"]
            if func_name in tool_functions:
                self.tool_registry.register(
                    func_name,
                    tool_functions[func_name],
                    schema
                )

    def generate_response(self, user_message, max_tool_calls=5):
        """
        Generate a response with tool support.

        Args:
            user_message: User's input message
            max_tool_calls: Maximum number of tool iterations

        Returns:
            Agent's response string
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        tool_calls_made = 0

        while tool_calls_made < max_tool_calls:
            # Call LLM with tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_registry.get_schemas(),
                tool_choice="auto",
                temperature=0.7
            )

            response_message = response.choices[0].message

            # Check if LLM wants to use tools
            if not response_message.tool_calls:
                # No tool calls - return final response
                final_response = response_message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
                return final_response

            # LLM wants to use tools
            print(f"\n[Tool calls requested: {len(response_message.tool_calls)}]")

            # Add assistant message with tool calls to messages
            messages.append(response_message)

            # Execute each tool call
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"  - Calling {tool_name} with {tool_args}")

                # Execute the tool
                try:
                    result = self.tool_registry.execute(tool_name, **tool_args)
                    result_str = json.dumps(result)
                    print(f"    Result: {result_str[:100]}...")
                except Exception as e:
                    result_str = json.dumps({"error": str(e)})
                    print(f"    Error: {e}")

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str
                })

            tool_calls_made += 1

        # Max iterations reached
        return "I've reached the maximum number of tool calls. Please try rephrasing your request."

    def run(self):
        """Run interactive conversation loop."""
        print("\n" + "="*60)
        print("Tool Agent - Interactive Mode")
        print("="*60)
        print(f"Available tools: {', '.join(self.tool_registry.get_tool_names())}")
        print("\nCommands:")
        print("  - 'quit': Exit")
        print("  - 'tools': List available tools")
        print("="*60 + "\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Goodbye!\n")
                break

            if user_input.lower() == 'tools':
                print(f"\nAvailable tools: {', '.join(self.tool_registry.get_tool_names())}\n")
                continue

            if not user_input:
                continue

            try:
                response = self.generate_response(user_input)
                print(f"\nAgent: {response}\n")
            except Exception as e:
                print(f"\nError: {e}\n")


# ============================================================================
# Demonstrations
# ============================================================================

def demo_calculator():
    """Demonstrate calculator tool usage."""
    print("\n=== Demo: Calculator Tool ===\n")
    agent = ToolAgent()

    questions = [
        "What is 1234 multiplied by 5678?",
        "Calculate 100 divided by 7",
        "What's 2500 minus 873?"
    ]

    for question in questions:
        print(f"Q: {question}")
        response = agent.generate_response(question)
        print(f"A: {response}\n")


def demo_multiple_tools():
    """Demonstrate using multiple tools in one query."""
    print("\n=== Demo: Multiple Tools ===\n")
    agent = ToolAgent()

    # Question that requires multiple tools
    question = "What's the weather in Tokyo and what time is it there?"
    print(f"Q: {question}")
    response = agent.generate_response(question)
    print(f"A: {response}\n")


if __name__ == "__main__":
    # Run interactive agent
    agent = ToolAgent()
    agent.run()

    # Uncomment to run demos:
    # demo_calculator()
    # demo_multiple_tools()
