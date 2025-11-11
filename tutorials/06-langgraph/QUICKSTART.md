# LangGraph Tutorial - Quick Start Guide

**Goal:** Get hands-on with LangGraph in 15 minutes using a real-world example.

## Prerequisites

```bash
# Install dependencies
pip install langgraph langchain-openai langchain-core python-dotenv

# Set your API key in .env
echo "OPENAI_API_KEY=your-key-here" > .env
```

## Run the Examples (5 minutes)

### 1. Basic Agent (Simple)

```bash
python tutorials/06-langgraph/langgraph_agent.py --stream
```

**Try:**
- "What is 25 * 8?"
- "Calculate (100 / 5) + 3"

**What's happening:**
- LangGraph routes to calculator tool when needed
- Streams responses in real-time
- Maintains conversation state

### 2. Customer Support Agent (Advanced)

```bash
python tutorials/06-langgraph/customer_support_agent.py --mode examples
```

**Watch:**
- 4 different support scenarios
- How tickets are analyzed, routed, handled
- Automatic escalation for urgent issues

**Then try interactive:**

```bash
python tutorials/06-langgraph/customer_support_agent.py --mode interactive
```

**Test these scenarios:**
- "I forgot my password" (Low priority, knowledge base)
- "The app crashed 5 times today!" (Medium priority, technical)
- "URGENT: I need my account NOW!" (High priority, escalation)

## Understand the Code (5 minutes)

### Key Concepts

#### 1. State Definition

```python
class SupportAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]  # Conversation
    ticket: TicketState  # Your custom state!
```

**Takeaway:** State is more than just messages - track whatever you need!

#### 2. Node Functions

```python
def analyze_ticket_node(state: SupportAgentState) -> SupportAgentState:
    # Read from state
    user_message = state["messages"][-1].content

    # Do work
    category = classify(user_message)

    # Update state
    state["ticket"]["category"] = category
    return state
```

**Takeaway:** Nodes are pure functions: state in → state out

#### 3. Building the Graph

```python
graph = StateGraph(SupportAgentState)

# Add nodes
graph.add_node("analyze", analyze_ticket_node)
graph.add_node("route", route_ticket_node)

# Connect with edges
graph.add_edge("analyze", "route")

# Conditional edges
graph.add_conditional_edges(
    "route",
    lambda state: "escalate" if state["ticket"]["priority"] == "urgent" else "handle"
)
```

**Takeaway:** Graph = nodes + edges. Simple!

#### 4. Running the Graph

```python
result = graph.invoke({"messages": [HumanMessage("Help!")]})
print(result["ticket"]["category"])  # Access your state
```

**Takeaway:** Invoke with initial state, get final state back

## Modify the Code (5 minutes)

### Exercise 1: Add a New Ticket Category

**File:** `customer_support_agent.py`

**Find this:**
```python
class TicketCategory(str, Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"
```

**Add:**
```python
    FEATURE_REQUEST = "feature_request"
```

**Then update routing:**
```python
handlers = {
    "technical": "Tech Support Team",
    "billing": "Billing Department",
    "account": "Account Services",
    "general": "General Support",
    "feature_request": "Product Team",  # Add this
}
```

**Test:** "I want to request a dark mode feature"

### Exercise 2: Add More Knowledge Base Entries

**Find:**
```python
@tool
def search_knowledge_base(query: str) -> str:
    kb = {
        "password": "To reset your password...",
        # Add more here!
    }
```

**Add:**
```python
    kb = {
        "password": "To reset your password...",
        "export": "To export your data:\n1. Go to Settings\n2. Click 'Export Data'\n3. Choose format (CSV, JSON)\n4. Download",
        "delete": "To delete your account:\n1. Go to Settings\n2. Click 'Delete Account'\n3. Confirm via email\n4. Data deleted in 30 days",
    }
```

**Test:** "How do I export my data?"

### Exercise 3: Add Logging to See State Changes

**Add at the top of each node:**
```python
def analyze_ticket_node(state: SupportAgentState):
    print(f"\n[ANALYZE] Processing: {state['messages'][-1].content[:50]}...")

    # ... rest of the function

    print(f"[ANALYZE] Classified as: {state['ticket']['category']} / {state['ticket']['priority']}")
    return state
```

**Now run:** You'll see each stage execute!

## Visualize the Graph (Bonus)

**In Python:**
```python
from customer_support_agent import CustomerSupportAgent
agent = CustomerSupportAgent()

# Get the graph structure
print(agent.graph.get_graph().draw_ascii())
```

**Or with Mermaid (in Jupyter):**
```python
from IPython.display import Image, display
display(Image(agent.graph.get_graph().draw_mermaid_png()))
```

## Common Patterns

### Pattern 1: Conditional Routing

```python
def route_by_priority(state):
    if state["priority"] == "urgent":
        return "escalate"
    return "handle"

graph.add_conditional_edges("analyze", route_by_priority)
```

### Pattern 2: State Updates

```python
def update_node(state):
    # Create a copy, don't mutate
    new_state = state.copy()
    new_state["field"] = "new_value"
    return new_state
```

### Pattern 3: Tool Calling in Nodes

```python
def tool_node(state):
    llm_with_tools = llm.bind_tools([my_tool])
    response = llm_with_tools.invoke(state["messages"])

    if response.tool_calls:
        result = my_tool.invoke(response.tool_calls[0]["args"])
        state["messages"].append(AIMessage(content=result))

    return state
```

## Troubleshooting

### "ImportError: No module named langgraph"

```bash
pip install langgraph
```

### "OPENAI_API_KEY not found"

```bash
# Check .env file exists
cat .env

# Or set directly
export OPENAI_API_KEY="your-key"  # Linux/Mac
set OPENAI_API_KEY=your-key       # Windows
```

### "Graph seems to skip nodes"

- Check your edge definitions
- Make sure conditional edges return valid node names
- Add print statements to debug

### "State not persisting between turns"

- For multi-turn: You need to maintain state externally
- Use LangGraph's `MemorySaver` for automatic persistence
- Example in advanced exercises

## Next Steps

### Beginner
1. ✅ Run both examples
2. ✅ Add a new ticket category
3. ✅ Add more knowledge base entries
4. ⬜ Add timestamps to track processing time
5. ⬜ Add a counter for how many tickets of each category

### Intermediate
1. ⬜ Add sentiment analysis node
2. ⬜ Implement feedback collection
3. ⬜ Add parallel tool calls
4. ⬜ Create a second graph for follow-ups
5. ⬜ Add human-in-the-loop approval

### Advanced
1. ⬜ Implement MemorySaver checkpointing
2. ⬜ Build sub-graphs for specialized handling
3. ⬜ Add async node execution
4. ⬜ Create a web UI with streaming
5. ⬜ Deploy to production with monitoring

## Resources

- 📖 [Full Tutorial](README.md) - Comprehensive learning guide
- 🔍 [Comparison Guide](COMPARISON.md) - When to use LangGraph
- 🌐 [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- 💬 [LangChain Discord](https://discord.gg/langchain)

## Quick Reference Card

```python
# 1. Define State
class MyState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    my_field: str

# 2. Create Nodes
def my_node(state: MyState) -> MyState:
    # do work
    return {"my_field": "updated"}

# 3. Build Graph
from langgraph.graph import StateGraph, END
graph = StateGraph(MyState)
graph.add_node("my_node", my_node)
graph.add_edge(START, "my_node")
graph.add_edge("my_node", END)

# 4. Compile and Run
app = graph.compile()
result = app.invoke({"messages": [], "my_field": ""})
print(result["my_field"])
```

**That's it! You now understand LangGraph. Build something cool! 🚀**
