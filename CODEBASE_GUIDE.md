# Codebase Learning Guide: Understanding the Agent Framework

## 🎯 Overview

This codebase has **two main parts**:

1. **`src/`** - Reusable agent framework (the library)
2. **`tutorials/`** - Step-by-step lessons that teach you how to use and build the framework

**Key Insight:** The tutorials **teach you** how the `src/` code works by building similar functionality from scratch!

---

## 📁 Project Structure Explained

```
AI-Agents-from-scratch/
│
├── src/                        # ⭐ THE FRAMEWORK (reusable components)
│   ├── agent/                  # Core agent classes
│   │   ├── base.py            # BaseAgent - foundation for all agents
│   │   ├── chat.py            # ChatAgent - conversational agent
│   │   └── __init__.py        # Public API exports
│   │
│   ├── memory/                 # Memory systems for context
│   │   ├── base.py            # BaseMemory - abstract interface
│   │   ├── buffer.py          # ConversationBufferMemory - simple storage
│   │   ├── token_window.py    # TokenWindowMemory - token-limited storage
│   │   └── __init__.py
│   │
│   ├── planning/               # Planning and reasoning
│   │   ├── react.py           # ReAct pattern implementation
│   │   ├── task_decomposition.py  # Task breakdown logic
│   │   └── __init__.py
│   │
│   ├── tools/                  # Tool integration
│   │   ├── base.py            # BaseTool - tool interface
│   │   ├── calculator.py      # Example tool implementation
│   │   └── __init__.py
│   │
│   └── utils/                  # Helper utilities
│       ├── logging.py         # Logging setup
│       ├── messages.py        # Message data structures
│       └── __init__.py
│
├── tutorials/                  # 📚 LEARNING PATH (teaches the framework)
│   ├── 01-basics/             # Learn: What is an agent?
│   ├── 02-memory/             # Learn: How memory works
│   ├── 03-tools/              # Learn: Tool integration
│   ├── 04-planning/           # Learn: ReAct and planning
│   ├── 05-advanced/           # Learn: Advanced patterns
│   └── 06-langgraph/          # Learn: LangGraph (alternative approach)
│
├── examples/                   # 🚀 REAL-WORLD APPS (using the framework)
├── tests/                      # 🧪 UNIT TESTS
└── docs/                       # 📖 CONCEPTUAL DOCUMENTATION
```

---

## 🔍 Deep Dive: The `src/` Framework

### 1. **`src/agent/` - Core Agent Classes**

#### `base.py` - BaseAgent

**Purpose:** The foundation class that all agents inherit from.

**What it does:**
- Manages OpenAI API connection
- Handles memory (conversation history)
- Builds messages for the LLM
- Provides `complete()` method for getting responses

**Key Code:**
```python
class BaseAgent:
    def __init__(self, system_prompt, model="gpt-4o-mini", memory=None, tools=None):
        self.system_prompt = system_prompt
        self.model = model
        self.memory = memory or ConversationBufferMemory()
        self.tools = tools or []
        self.client = OpenAI()

    def _build_messages(self, user_prompt: str) -> List[dict]:
        # System prompt + Memory + User prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory.get_context())
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def complete(self, prompt: str) -> str:
        # Call OpenAI API and update memory
        messages = self._build_messages(prompt)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        content = response.choices[0].message.content
        self.memory.add(Message("user", prompt))
        self.memory.add(Message("assistant", content))
        return content
```

**When to use:** Base class for building custom agents.

**Tutorial connection:** Tutorial 01 teaches you how to build this from scratch!

---

#### `chat.py` - ChatAgent

**Purpose:** Specialized agent for interactive conversations.

**What it does:**
- Extends BaseAgent
- Adds conversation-specific features
- Handles chat loops

**Tutorial connection:** Tutorial 01 and 02 build towards this.

---

### 2. **`src/memory/` - Memory Systems**

#### `base.py` - BaseMemory

**Purpose:** Abstract base class defining the memory interface.

**Key Code:**
```python
class BaseMemory(ABC):
    def __init__(self):
        self._messages: List[Message] = []

    def add(self, message: Message) -> None:
        """Add a message to memory"""
        self._messages.append(message)

    @abstractmethod
    def get_context(self) -> List[Message]:
        """Return messages to send to the model"""
        # Subclasses implement different strategies
```

**Why it's abstract:** Different memory types retrieve context differently.

---

#### `buffer.py` - ConversationBufferMemory

**Purpose:** Simplest memory - stores all messages.

**Key Code:**
```python
class ConversationBufferMemory(BaseMemory):
    def get_context(self) -> List[Message]:
        """Return all stored messages"""
        return self._messages
```

**Pros:** Simple, complete history
**Cons:** Can exceed token limits

---

#### `token_window.py` - TokenWindowMemory

**Purpose:** Smart memory that limits by token count.

**Key Code:**
```python
class TokenWindowMemory(BaseMemory):
    def __init__(self, max_tokens: int = 2000):
        super().__init__()
        self.max_tokens = max_tokens

    def get_context(self) -> List[Message]:
        """Return recent messages within token limit"""
        # Start from most recent, count backwards
        # Stop when token limit is reached
```

**Pros:** Won't exceed token limits
**Cons:** May lose older context

**Tutorial connection:** Tutorial 02 teaches memory systems in depth!

---

### 3. **`src/planning/` - Planning & Reasoning**

#### `react.py` - ReActPlanner

**Purpose:** Implements the ReAct (Reasoning + Acting) pattern.

**What is ReAct?**
A loop where the agent:
1. **Thinks** - Reasons about what to do
2. **Acts** - Calls a tool
3. **Observes** - Sees the result
4. **Repeats** - Until task is complete

**Key Code:**
```python
class ReActPlanner:
    def __init__(self, tools, max_steps=5):
        self.tools = {tool.name: tool for tool in tools}
        self.max_steps = max_steps

    def run(self, question: str, agent: BaseAgent):
        steps = []
        for i in range(self.max_steps):
            # 1. Get thought from agent
            prompt = self._format_prompt(question, steps)
            response = agent.complete(prompt)
            step = self._parse_step(response)

            # 2. Execute action (tool call)
            if step.action in self.tools:
                result = self.tools[step.action].run(step.action_input)
                step.observation = result.content

            steps.append(step)

            # 3. Check if done
            if step.final_answer:
                return step.final_answer

        return steps[-1].observation
```

**ThoughtStep structure:**
```python
@dataclass
class ThoughtStep:
    thought: str              # "I need to calculate 2+2"
    action: Optional[str]     # "calculator"
    action_input: Optional[str]  # "2+2"
    observation: Optional[str]   # "4"
    final_answer: Optional[str]  # "The answer is 4"
```

**Tutorial connection:** Tutorial 04 teaches ReAct in detail!

---

#### `task_decomposition.py` - Task Breakdown

**Purpose:** Break complex tasks into subtasks.

**Tutorial connection:** Tutorial 04 and 05 cover this.

---

### 4. **`src/tools/` - Tool System**

#### `base.py` - BaseTool

**Purpose:** Interface that all tools must implement.

**Key Code:**
```python
@dataclass
class ToolResult:
    content: str              # Human-readable result
    data: Optional[Dict] = None  # Structured data

class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, input_text: str) -> ToolResult:
        """Execute the tool"""
```

**Design pattern:** Template Method - subclasses implement `run()`.

---

#### `calculator.py` - Example Tool

**Purpose:** Shows how to implement a tool.

**Tutorial connection:** Tutorial 03A teaches tool creation!

---

### 5. **`src/utils/` - Utilities**

#### `messages.py` - Message Data Structures

**Purpose:** Standardized message format.

**Key Code:**
```python
class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    role: str
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}
```

---

## 📚 How Tutorials Connect to `src/`

### Learning Path & Codebase Mapping

| Tutorial | What You Learn | `src/` Components Used | Build Your Own Version? |
|----------|----------------|------------------------|-------------------------|
| **01-basics/** | Agent fundamentals | `agent/base.py` | ✅ Yes - build from scratch |
| **02-memory/** | Memory systems | `memory/base.py`, `memory/buffer.py` | ✅ Yes - build memory classes |
| **03-tools/** | Tool integration | `tools/base.py`, `tools/calculator.py` | ✅ Yes - create custom tools |
| **04-planning/** | ReAct pattern | `planning/react.py` | ✅ Yes - implement ReAct |
| **05-advanced/** | RAG, multi-agent | All of `src/` | 🔄 Use the framework |
| **06-langgraph/** | Alternative approach | None (uses LangGraph) | 🆕 Learn different framework |

---

## 🚀 Step-by-Step Learning Plan

### **Phase 1: Understand the Basics (Week 1)**

**Goal:** Learn what agents are and how they work.

1. **Read conceptual docs:**
   ```bash
   docs/concepts.md          # What is an agent?
   docs/architecture.md      # System design
   ```

2. **Tutorial 01 - Basics:**
   ```bash
   cd tutorials/01-basics
   cat README.md            # Read the tutorial
   python simple_agent.py   # Run the example
   ```

   **What you'll learn:**
   - How to call OpenAI API
   - Build a basic agent class
   - Prompt-response loop

   **Compare with framework:**
   ```bash
   # Your tutorial code
   tutorials/01-basics/simple_agent.py

   # vs Framework code
   src/agent/base.py
   ```

   **Key insight:** The tutorial version is simplified; the framework adds error handling, logging, etc.

3. **Experiment:**
   - Modify the system prompt
   - Change temperature
   - Add conversation loop

---

### **Phase 2: Add Memory (Week 1-2)**

**Goal:** Understand how agents remember context.

1. **Tutorial 02 - Memory:**
   ```bash
   cd tutorials/02-memory
   python memory_agent.py
   ```

   **What you'll learn:**
   - Why memory matters
   - Different memory strategies
   - Token management

2. **Study framework implementation:**
   ```python
   # Read these in order:
   src/memory/base.py         # Interface
   src/memory/buffer.py       # Simple implementation
   src/memory/token_window.py # Smart implementation
   ```

3. **Hands-on exercise:**
   ```python
   # Create your own memory type
   from src.memory import BaseMemory

   class SummaryMemory(BaseMemory):
       """Keep only summaries of old conversations"""
       def get_context(self):
           # Your implementation here
   ```

---

### **Phase 3: Tool Integration (Week 2)**

**Goal:** Enable agents to use external tools.

1. **Tutorial 03A - Tools:**
   ```bash
   cd tutorials/03-tools
   python tool_agent.py
   ```

   **What you'll learn:**
   - OpenAI function calling
   - Tool schemas
   - Error handling

2. **Study framework:**
   ```python
   src/tools/base.py          # Tool interface
   src/tools/calculator.py    # Example implementation
   ```

3. **Create custom tool:**
   ```python
   from src.tools import BaseTool, ToolResult

   class WeatherTool(BaseTool):
       name = "get_weather"
       description = "Get current weather for a location"

       def run(self, input_text: str) -> ToolResult:
           # Call weather API
           return ToolResult(content=f"Weather for {input_text}: Sunny, 72°F")
   ```

4. **Use in agent:**
   ```python
   from src.agent import BaseAgent
   from your_tools import WeatherTool

   agent = BaseAgent(
       system_prompt="You are a helpful assistant",
       tools=[WeatherTool()]
   )
   ```

---

### **Phase 4: Planning & Reasoning (Week 3)**

**Goal:** Build agents that can plan multi-step tasks.

1. **Tutorial 04 - Planning:**
   ```bash
   cd tutorials/04-planning
   python react_agent.py
   ```

   **What you'll learn:**
   - ReAct pattern
   - Multi-step reasoning
   - Tool chaining

2. **Study ReAct implementation:**
   ```python
   src/planning/react.py
   ```

   **Key sections:**
   - `_format_prompt()` - How prompts are built
   - `_parse_step()` - Parsing agent responses
   - `run()` - The main loop

3. **Experiment:**
   ```python
   from src.agent import BaseAgent
   from src.planning import ReActPlanner
   from src.tools import CalculatorTool

   agent = BaseAgent(system_prompt="You are a problem solver")
   planner = ReActPlanner(tools=[CalculatorTool()], max_steps=5)

   answer, steps = planner.run(
       question="What is (25 * 4) + (100 / 5)?",
       agent=agent
   )

   # Inspect the reasoning steps
   for i, step in enumerate(steps):
       print(f"Step {i+1}:")
       print(f"  Thought: {step.thought}")
       print(f"  Action: {step.action}")
       print(f"  Observation: {step.observation}")
   ```

---

### **Phase 5: Advanced Patterns (Week 4)**

**Goal:** Master production-ready patterns.

1. **Tutorial 05 - Advanced:**
   ```bash
   cd tutorials/05-advanced
   python rag_agent.py        # RAG pattern
   python multi_agent.py      # Multi-agent
   ```

2. **Now you use the framework:**
   ```python
   from src.agent import BaseAgent
   from src.memory import TokenWindowMemory
   from src.planning import ReActPlanner
   from src.tools import CalculatorTool, YourCustomTool

   # Build a complex agent using all components
   agent = BaseAgent(
       system_prompt="You are an expert assistant",
       memory=TokenWindowMemory(max_tokens=2000),
       tools=[CalculatorTool(), YourCustomTool()]
   )

   planner = ReActPlanner(tools=agent.tools)
   answer, steps = planner.run("Complex task here", agent)
   ```

---

### **Phase 6: Alternative Approach - LangGraph (Week 4-5)**

**Goal:** Learn when to use orchestration frameworks.

1. **Tutorial 06 - LangGraph:**
   ```bash
   cd tutorials/06-langgraph
   cat QUICKSTART.md
   python customer_support_agent.py --mode examples
   ```

2. **Compare approaches:**
   - `src/` approach: Build everything yourself
   - LangGraph approach: Use orchestration framework

3. **Decision guide:**
   - Use `src/` when: Learning, custom logic, simple workflows
   - Use LangGraph when: Complex workflows, branching, persistence

---

## 🎓 Understanding the Architecture

### How Components Work Together

```
┌─────────────────────────────────────────────────┐
│                   YOUR APP                      │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              BaseAgent                          │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ System Prompt│  │    Memory    │           │
│  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐           │
│  │    Tools     │  │  LLM Client  │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
         │                  │                │
         ▼                  ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Tool System  │  │Memory System │  │  Planning    │
│              │  │              │  │              │
│ - BaseTool   │  │ - BaseMemory │  │ - ReAct      │
│ - Calculator │  │ - Buffer     │  │ - TaskDecomp │
│ - Custom...  │  │ - TokenWin   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Example: A Complete Agent Interaction

```python
# 1. Create an agent with all components
from src.agent import BaseAgent
from src.memory import TokenWindowMemory
from src.tools import CalculatorTool
from src.planning import ReActPlanner

agent = BaseAgent(
    system_prompt="You are a math tutor",
    memory=TokenWindowMemory(max_tokens=2000),
    tools=[CalculatorTool()]
)

planner = ReActPlanner(tools=agent.tools)

# 2. User asks a question
question = "If I have 5 apples and buy 3 more, then eat 2, how many do I have?"

# 3. The flow:
# ┌─────────────────┐
# │ User Question   │
# └────────┬────────┘
#          ▼
# ┌─────────────────┐
# │ ReActPlanner    │ ← Coordinates the process
# └────────┬────────┘
#          │
#          ├─→ Format prompt with tools
#          │
#          ▼
# ┌─────────────────┐
# │ BaseAgent       │ ← Calls LLM
# │ .complete()     │
# └────────┬────────┘
#          │
#          ├─→ _build_messages()
#          │   ├─→ System prompt
#          │   ├─→ Memory.get_context()
#          │   └─→ User question
#          │
#          ▼
# ┌─────────────────┐
# │ OpenAI API      │
# └────────┬────────┘
#          │
#          ▼ (Returns: "Thought: I need to calculate 5+3-2...")
#          │
# ┌─────────────────┐
# │ ReActPlanner    │ ← Parses response
# │ ._parse_step()  │
# └────────┬────────┘
#          │
#          ▼ (Identified action: "calculator")
#          │
# ┌─────────────────┐
# │ CalculatorTool  │ ← Executes tool
# │ .run("5+3-2")   │
# └────────┬────────┘
#          │
#          ▼ (Returns: "6")
#          │
# ┌─────────────────┐
# │ ReActPlanner    │ ← Continues loop
# └────────┬────────┘
#          │
#          ▼ (Next iteration with observation...)
#          │
# ┌─────────────────┐
# │ Final Answer    │ → "You have 6 apples"
# └─────────────────┘
```

---

## 📋 Quick Reference: Key Concepts

### Agent Lifecycle

```python
# 1. Initialization
agent = BaseAgent(system_prompt="...", memory=..., tools=...)

# 2. Receive user input
user_input = "Tell me about AI"

# 3. Build context
messages = agent._build_messages(user_input)
# → [system_message, *memory_messages, user_message]

# 4. Call LLM
response = agent.complete(user_input)

# 5. Update memory
agent.memory.add(Message("user", user_input))
agent.memory.add(Message("assistant", response))

# 6. Return response
return response
```

### Memory Strategies

| Memory Type | Use When | Pros | Cons |
|-------------|----------|------|------|
| **Buffer** | Short conversations | Simple, complete history | Token limits |
| **TokenWindow** | Longer conversations | Automatic pruning | May lose context |
| **Summary** | Very long conversations | Compact | Loses details |

### Tool Execution Flow

```python
# 1. Agent decides to use tool
# LLM returns: {"name": "calculator", "arguments": {"expression": "2+2"}}

# 2. Tool is called
tool = tools["calculator"]
result = tool.run("2+2")
# → ToolResult(content="4", data={"result": 4})

# 3. Result goes back to agent
# Agent sees: "Observation: 4"

# 4. Agent formulates final answer
# "The answer is 4"
```

---

## ❓ FAQ

### Q: Should I learn `src/` or just use the tutorials?

**A:** Both! Here's the path:
1. **Do tutorials** - Learn concepts by building from scratch
2. **Study `src/`** - See production-quality implementations
3. **Use `src/`** - Build your own apps using the framework

### Q: Can I use the `src/` code in my projects?

**A:** Yes! That's what it's for. The framework is designed to be:
- Reusable
- Extendable
- Production-ready (with some additions)

### Q: How is this different from LangChain?

**A:**
- **This framework:** Educational, minimal, transparent
- **LangChain:** Production, feature-rich, complex

**Use this to learn**, then decide if you need LangChain's features.

### Q: Which tutorial teaches which `src/` component?

See the table in "How Tutorials Connect to `src/`" above.

### Q: Can I mix `src/` components with LangGraph?

**A:** Not directly. They're different approaches:
- `src/` = Build your own orchestration
- LangGraph = Use framework orchestration

Choose one approach per project.

---

## 🎯 Next Steps

### 1. **Beginners (Week 1-2)**
```bash
# Start here
tutorials/01-basics/README.md
tutorials/02-memory/README.md

# Then compare with:
src/agent/base.py
src/memory/buffer.py
```

### 2. **Intermediate (Week 2-3)**
```bash
# Build on fundamentals
tutorials/03-tools/README.md
tutorials/04-planning/README.md

# Study implementation:
src/tools/base.py
src/planning/react.py
```

### 3. **Advanced (Week 3-4)**
```bash
# Master complex patterns
tutorials/05-advanced/README.md
tutorials/06-langgraph/QUICKSTART.md

# Use the framework:
examples/customer_support_agent.py
```

### 4. **Build Your Own**
```python
from src.agent import BaseAgent
from src.memory import TokenWindowMemory
from src.planning import ReActPlanner
from src.tools import BaseTool, ToolResult

# Create custom tool
class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"
    def run(self, input_text: str) -> ToolResult:
        # Your logic here
        return ToolResult(content="Result")

# Build your agent
agent = BaseAgent(
    system_prompt="Custom system prompt",
    memory=TokenWindowMemory(),
    tools=[MyTool()]
)

# Add planning if needed
planner = ReActPlanner(tools=agent.tools)
answer, steps = planner.run("Your question", agent)
```

---

## 📚 Summary

**The Codebase Has Two Roles:**

1. **Teaching Tool** (via tutorials)
   - Learn by building from scratch
   - Understand fundamentals
   - See how things work

2. **Production Framework** (via `src/`)
   - Reusable components
   - Best practices
   - Build real applications

**Learning Strategy:**
1. ✅ Do tutorials to understand concepts
2. ✅ Study `src/` to see production code
3. ✅ Use `src/` to build your own agents

**Start Now:**
```bash
cd tutorials/01-basics
cat README.md
python simple_agent.py
```

Happy learning! 🚀
