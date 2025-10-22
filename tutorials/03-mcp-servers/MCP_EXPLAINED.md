# MCP Explained: From Concept to Implementation

## What Problem Does MCP Solve?

### Before MCP
```
You: "Claude, what files are in my Documents folder?"
Claude: "I can't access your local files. I only work with text you paste."

You: "Can you check my database?"
Claude: "I don't have access to your database."

You: "Run this calculation for me..."
Claude: "I can do basic math, but can't access your custom tools."
```

### After MCP
```
You: "Claude, what files are in my Documents folder?"
Claude: *uses file-explorer MCP server* "You have 23 files. Here are the most recent..."

You: "Can you check my database?"
Claude: *uses database MCP server* "I found 142 records matching your criteria..."

You: "Calculate using my custom formula..."
Claude: *uses your custom MCP server* "Result: 42.7"
```

**MCP lets AI access YOUR tools and data, securely!**

---

## Core Concept: Client-Server Model

```
┌─────────────────────────────────────────────┐
│           YOUR AI ASSISTANT                 │
│          (MCP Client - Claude)              │
│                                             │
│  "I need to check files"  ──────┐          │
│  "I need to get weather"  ──────┤          │
│  "I need to calculate"    ──────┤          │
└─────────────────────────────────┼───────────┘
                                  │
                    MCP Protocol  │
                    (stdio/HTTP)  │
                                  │
        ┌─────────────────────────┼─────────────┐
        │                         │             │
┌───────▼────────┐    ┌──────────▼─────┐  ┌───▼──────┐
│ File Explorer  │    │ Weather Server │  │Calculator│
│  MCP Server    │    │   MCP Server   │  │  Server  │
│                │    │                │  │          │
│ • list files   │    │ • get weather  │  │ • add    │
│ • read file    │    │ • forecast     │  │ • multiply│
│ • file info    │    │ • compare      │  │ • power  │
└────────────────┘    └────────────────┘  └──────────┘
```

---

## MCP vs Other Approaches

### Traditional Function Calling
```python
# AI generates this
{"function": "get_weather", "args": {"city": "NYC"}}

# You have to manually route it
if function == "get_weather":
    result = weather_api.get(args["city"])
```
**Problem**: You need to implement routing, validation, error handling for every function.

### With MCP
```python
# You define once in MCP server
@server.call_tool()
async def call_tool(name, arguments):
    if name == "get_weather":
        return get_weather(arguments["city"])

# MCP handles: routing, validation, error handling, transport
```
**Benefit**: Standardized protocol, works with any MCP client (Claude, your code, etc.)

---

## The Two Building Blocks: Tools & Resources

### Tools = Functions (AI Can Call)

Think of tools as **API endpoints** the AI can hit.

```python
# Example: Weather tool
Tool(
    name="get_weather",
    description="Get current weather for a city",
    inputSchema={
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        }
    }
)

# When AI calls it:
AI: "Get weather for Tokyo"
Server executes: get_weather(city="Tokyo")
Returns: {"temp": 72, "condition": "Sunny"}
```

**Use tools for:**
- ✅ Actions (save, delete, update)
- ✅ Calculations (compute, analyze)
- ✅ API calls (fetch data, search)

### Resources = Data (AI Can Read)

Think of resources as **files** or **database records** the AI can access.

```python
# Example: File resource
Resource(
    uri="file:///Users/you/document.txt",
    name="document.txt",
    description="My important document",
    mimeType="text/plain"
)

# When AI accesses it:
AI: "Read document.txt"
Server returns: <file contents>
```

**Use resources for:**
- ✅ Files (documents, configs, logs)
- ✅ Database records
- ✅ Live data streams
- ✅ API responses (as data)

---

## Request Flow: Step-by-Step

Let's trace what happens when you ask Claude to "Add 10 and 5" using our calculator MCP server.

### Step 1: User Request
```
You: "Claude, add 10 and 5"
```

### Step 2: Claude Decides to Use MCP
```
Claude's reasoning:
"The user wants to add numbers. I have access to a calculator
MCP server with an 'add' tool. I'll use that."
```

### Step 3: Claude Lists Available Tools
```
MCP Request: list_tools()

MCP Response:
[
  {
    "name": "add",
    "description": "Add two numbers",
    "inputSchema": {
      "properties": {
        "a": {"type": "number"},
        "b": {"type": "number"}
      }
    }
  }
]
```

### Step 4: Claude Calls the Tool
```
MCP Request: call_tool("add", {"a": 10, "b": 5})

Your server executes:
def call_tool(name, arguments):
    if name == "add":
        result = arguments["a"] + arguments["b"]  # 10 + 5 = 15
        return [TextContent(text=f"The sum is {result}")]

MCP Response:
[{"type": "text", "text": "The sum is 15"}]
```

### Step 5: Claude Responds to You
```
Claude: "The sum of 10 and 5 is 15."
```

---

## The Three Communication Patterns

### 1. stdio (Standard Input/Output)
**What it is**: Server runs as a child process, communicates via stdin/stdout

```
Claude Desktop
     │
     ├─ spawns ──> python calculator_server.py
     │                    │
     │                    │ stdin/stdout
     │                    │
     └─ talks to ─────────┘
```

**Used by**: Claude Desktop, local applications

**Pros**:
- ✅ Simple
- ✅ No network setup
- ✅ Secure (local only)

**Cons**:
- ❌ Local only
- ❌ One client at a time

### 2. HTTP (Server-Sent Events)
**What it is**: Server runs as HTTP server, clients connect via HTTP

```
Multiple Clients
     │
     ├─ HTTP request ──> MCP Server :8080
     │                          │
     └─ SSE stream ─────────────┘
```

**Used by**: Remote servers, multiple clients

**Pros**:
- ✅ Remote access
- ✅ Multiple clients
- ✅ Scalable

**Cons**:
- ❌ More complex
- ❌ Security considerations

### 3. Custom Transport
**What it is**: Build your own (WebSocket, gRPC, etc.)

**Used by**: Advanced use cases

---

## Building a Mental Model

### MCP is like a Restaurant

```
┌─────────────────────────────────────────┐
│         CUSTOMER (AI Assistant)         │
│   "I'd like the weather please"         │
└────────────────┬────────────────────────┘
                 │
                 │ Orders from menu
                 ▼
┌────────────────────────────────────────────┐
│         MENU (MCP Server)                  │
│                                            │
│  Available Dishes (Tools):                 │
│  • get_weather ................. $tool     │
│  • get_forecast ................ $tool     │
│  • compare_weather ............. $tool     │
│                                            │
│  Available Ingredients (Resources):        │
│  • weather_data.json                       │
│  • cities.txt                              │
└────────────────┬───────────────────────────┘
                 │
                 │ Prepares order
                 ▼
┌─────────────────────────────────────────┐
│       KITCHEN (Your Code)               │
│   Executes: get_weather("NYC")          │
│   Returns: {"temp": 72, ...}            │
└─────────────────────────────────────────┘
```

**Key Points:**
- **Menu** = List of tools/resources (what's available)
- **Order** = Tool call (what AI wants)
- **Kitchen** = Your implementation (how it works)
- **Dish** = Result (what AI gets back)

---

## Security Model

### What MCP Protects

1. **Local-first**: Servers run on YOUR machine
2. **Explicit approval**: You choose which servers to connect
3. **Sandboxing**: Each server is isolated
4. **No internet by default**: Unless YOU configure it

### What You Control

```python
# Example: File server with security
@server.read_resource()
async def read_resource(uri):
    file_path = Path(uri.replace("file:///", ""))

    # Security check!
    if not str(file_path).startswith(str(self.root_dir)):
        raise ValueError("Access denied: file outside root directory")

    return open(file_path).read()
```

**You decide:**
- ✅ Which directories AI can access
- ✅ Which operations are allowed
- ✅ What data is exposed
- ✅ Rate limits, validation, logging

---

## Real-World Example: Research Assistant

Let's build a mental model of a research assistant using MCP:

### The Setup
```
Claude Desktop
    │
    ├── File Explorer MCP Server (read papers)
    ├── Web Search MCP Server (find new papers)
    ├── Database MCP Server (store findings)
    └── Email MCP Server (send summaries)
```

### The Workflow
```
You: "Research recent papers on AI agents and summarize them"

Claude:
1. Uses Web Search MCP: "Find papers on AI agents"
   → Gets list of papers

2. Uses File Explorer MCP: "Read downloaded papers"
   → Reads paper contents

3. Analyzes and summarizes (using its own intelligence)

4. Uses Database MCP: "Save summary to database"
   → Stores findings

5. Uses Email MCP: "Send summary to user"
   → Sends email

Response: "I've researched 15 papers, saved summaries to your
          database, and emailed you the findings."
```

**Each MCP server is a specialized tool!**

---

## Common Patterns

### Pattern 1: API Wrapper
Wrap external APIs as MCP tools

```python
@server.call_tool()
async def call_tool(name, arguments):
    if name == "search_github":
        # Call GitHub API
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": arguments["query"]}
        )
        return [TextContent(text=response.json())]
```

### Pattern 2: Database Access
Expose database queries

```python
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_users",
            description="Query user database",
            inputSchema={"type": "object", ...}
        )
    ]
```

### Pattern 3: File Operations
Provide file system access

```python
@server.list_resources()
async def list_resources():
    return [
        Resource(uri=f"file:///{file}", ...)
        for file in Path(".").glob("*.txt")
    ]
```

---

## When to Use MCP

### ✅ Use MCP When:
- You want to give AI access to local tools
- You need standardized tool integration
- You want to work with multiple AI assistants
- You're building reusable components

### ❌ Don't Use MCP When:
- Simple one-off script (direct API call is easier)
- No need for standardization
- Building a web app (use REST API instead)

---

## Comparison Table

| Feature | Function Calling | MCP | LangChain Tools |
|---------|-----------------|-----|-----------------|
| Standardized | ❌ | ✅ | ⚠️ (LangChain-specific) |
| Works with Claude Desktop | ❌ | ✅ | ❌ |
| Local tools | ✅ | ✅ | ✅ |
| Remote tools | ✅ | ✅ | ✅ |
| Reusable | ⚠️ | ✅ | ⚠️ |
| Learning curve | Low | Medium | Medium-High |

---

## Summary: The Big Picture

```
MCP = Standardized way for AI to use YOUR tools

1. You build MCP servers (like our examples)
2. AI discovers available tools/resources
3. AI calls tools when needed
4. You control what AI can access
5. Everything runs locally and securely

Result: AI with superpowers, under YOUR control!
```

---

## Next Steps

1. **Understand**: Read this document
2. **See it work**: Run the examples
3. **Modify**: Change the calculator server
4. **Build**: Create your own MCP server
5. **Deploy**: Connect to Claude Desktop

**You now understand MCP! Start building! 🚀**
