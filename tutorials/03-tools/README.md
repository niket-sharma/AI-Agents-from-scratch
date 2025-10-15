# Tutorial 03: Tool Integration - Making Agents Useful

Welcome to Tutorial 03! So far, our agents can converse and remember, but they can't actually DO anything in the real world. In this tutorial, we'll give your agent the ability to use tools like calculators, web search, file operations, and more.

## Learning Objectives

By the end of this tutorial, you will:
- Understand function calling with LLMs
- Implement a tool registry system
- Create custom tools for your agent
- Handle tool execution and errors
- Build agents that can use multiple tools
- Understand the tool use workflow

## Prerequisites

- Completed Tutorials 01 and 02
- Understanding of Python functions and decorators
- Basic knowledge of JSON schemas

## Time Required

Approximately 1 hour

## What You'll Build

An agent that can:
1. Understand when to use tools
2. Call appropriate tools with correct parameters
3. Process tool results
4. Chain multiple tool calls together
5. Handle tool errors gracefully

## Why Tools Matter

### Without Tools:
```
User: What's 1847 * 923?
Agent: I don't have a calculator, but I estimate it's around 1.7 million.
(Actual answer: 1,704,581)
```

### With Tools:
```
User: What's 1847 * 923?
Agent: [Uses calculator tool]
Agent: The answer is 1,704,581.
```

## Understanding Function Calling

Modern LLMs (GPT-4, Claude, etc.) support **function calling**, which allows them to:
1. Recognize when a tool is needed
2. Extract the right parameters
3. Format the tool call properly
4. Integrate results into their response

### Tool Definition Format

Tools are defined using JSON Schema:

```python
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, e.g. San Francisco"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
}
```

## Step 1: Creating Your First Tool

Let's start with a simple calculator:

```python
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

    return operations[operation](a, b)
```

### Tool Schema

```python
calculator_schema = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic math operations (add, subtract, multiply, divide)",
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
}
```

## Step 2: Building a Tool Registry

Create a system to manage multiple tools:

```python
class ToolRegistry:
    """Manages available tools for the agent."""

    def __init__(self):
        self.tools = {}
        self.schemas = []

    def register(self, name, function, schema):
        """Register a new tool."""
        self.tools[name] = {
            'function': function,
            'schema': schema
        }
        self.schemas.append(schema)

    def execute(self, name, **parameters):
        """Execute a tool by name with given parameters."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")

        tool_function = self.tools[name]['function']
        return tool_function(**parameters)

    def get_schemas(self):
        """Get all tool schemas for LLM."""
        return self.schemas

    def get_tool_names(self):
        """Get list of available tool names."""
        return list(self.tools.keys())
```

## Step 3: Agent with Tool Support

```python
class ToolAgent:
    """An agent that can use tools."""

    def __init__(self, model="gpt-3.5-turbo", system_prompt=None):
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.system_prompt = system_prompt or """You are a helpful AI assistant
with access to tools. Use them when needed to provide accurate information."""

        self.conversation_history = []
        self.tool_registry = ToolRegistry()

    def generate_response(self, user_message, max_tool_calls=5):
        """Generate response with tool support."""
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build messages
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
                tool_choice="auto"
            )

            response_message = response.choices[0].message

            # Check if LLM wants to use tools
            if not response_message.tool_calls:
                # No tool calls, return final response
                final_response = response_message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
                return final_response

            # Process tool calls
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Execute tool
                try:
                    result = self.tool_registry.execute(tool_name, **tool_args)
                    result_str = json.dumps(result)
                except Exception as e:
                    result_str = json.dumps({"error": str(e)})

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str
                })

            tool_calls_made += 1

        # Max tool calls reached
        return "I've reached the maximum number of tool calls. Please try a simpler request."
```

## Step 4: Common Tools

### Weather Tool

```python
def get_weather(location, unit="celsius"):
    """
    Get weather information (mock implementation).

    Args:
        location: City name
        unit: Temperature unit (celsius or fahrenheit)
    """
    # This is a mock - in real implementation, call a weather API
    mock_data = {
        "temperature": 22 if unit == "celsius" else 72,
        "condition": "Sunny",
        "humidity": 45,
        "location": location,
        "unit": unit
    }
    return mock_data

weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
}
```

### Web Search Tool

```python
import requests

def search_web(query, num_results=3):
    """
    Search the web for information.

    Args:
        query: Search query
        num_results: Number of results to return
    """
    # Mock implementation - use DuckDuckGo or Google API in production
    return {
        "query": query,
        "results": [
            {"title": f"Result {i+1}", "snippet": f"Information about {query}"}
            for i in range(num_results)
        ]
    }

search_schema = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for information",
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
```

### File Operations Tool

```python
import os

def read_file(filepath):
    """Read contents of a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(filepath, content):
    """Write content to a text file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"Written to {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

file_tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    }
]
```

## Step 5: Putting It All Together

```python
# Create agent
agent = ToolAgent()

# Register tools
agent.tool_registry.register("calculator", calculator, calculator_schema)
agent.tool_registry.register("get_weather", get_weather, weather_schema)
agent.tool_registry.register("search_web", search_web, search_schema)

# Use the agent
response = agent.generate_response("What's 1234 * 5678?")
print(response)  # Agent will use calculator

response = agent.generate_response("What's the weather in Paris?")
print(response)  # Agent will use weather tool
```

## Step 6: Error Handling

```python
class SafeToolRegistry(ToolRegistry):
    """Tool registry with enhanced error handling."""

    def execute(self, name, **parameters):
        """Execute tool with error handling."""
        if name not in self.tools:
            return {"error": f"Tool '{name}' not found"}

        try:
            result = self.tools[name]['function'](**parameters)
            return {"success": True, "result": result}
        except TypeError as e:
            return {"error": f"Invalid parameters: {e}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {e}"}
```

## Exercises

### Exercise 1: Create a Time Tool
Build a tool that returns the current time in different time zones.

### Exercise 2: Create a Unit Converter
Build a tool that converts between different units (length, weight, temperature).

### Exercise 3: API Integration
Integrate a real API (e.g., weather, news, or stocks).

### Exercise 4: Tool Chaining
Create a task that requires multiple tools in sequence.

## Best Practices

1. **Clear Descriptions**: Make tool descriptions explicit
2. **Input Validation**: Validate parameters before execution
3. **Error Messages**: Return helpful error messages
4. **Timeouts**: Set timeouts for long-running tools
5. **Logging**: Log all tool executions for debugging
6. **Security**: Validate and sanitize inputs
7. **Rate Limiting**: Respect API rate limits

## Common Patterns

### Pattern 1: Sequential Tool Use
```python
# User asks for weather and time in same query
# Agent uses weather tool, then time tool
```

### Pattern 2: Tool Results Processing
```python
# Agent uses search tool, then summarizes results
```

### Pattern 3: Conditional Tool Use
```python
# Agent decides which tool based on query type
```

## What's Next?

In [Tutorial 04: Planning and Reasoning](../04-planning/), you'll learn:
- Implement ReAct pattern
- Multi-step planning
- Goal-oriented agents
- Task decomposition

## Key Concepts Learned

- Function calling with LLMs
- Tool registry pattern
- Schema definitions
- Tool execution workflow
- Error handling for tools
- Multi-tool coordination

---

**Excellent work!** Your agent can now interact with the real world. Ready to add planning capabilities? Continue to Tutorial 04!
