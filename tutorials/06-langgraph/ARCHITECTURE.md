# Customer Support Agent - Architecture Deep Dive

## System Overview

The Customer Support Agent demonstrates LangGraph's strengths through a realistic multi-stage workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Customer Support Agent                        │
│                                                                   │
│  Input: "URGENT: Can't access my account!"                      │
│  Output: Escalation ticket + Support response                    │
│  State: Full ticket metadata tracked throughout                  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Architecture

### Complete Flow Diagram

```
                        ┌─────────────┐
                        │   START     │
                        └──────┬──────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   ANALYZE NODE       │
                    │                      │
                    │  • Extract content   │
                    │  • Classify category │
                    │  • Determine priority│
                    │  • Generate summary  │
                    └──────────┬───────────┘
                               │
                State Updated: │
                - category: "account"
                - priority: "urgent"
                - summary: "Account access issue"
                               │
                               ▼
                    ┌──────────────────────┐
                    │    ROUTE NODE        │
                    │                      │
                    │  • Map category      │
                    │    to handler        │
                    │  • Assign team       │
                    └──────────┬───────────┘
                               │
                State Updated: │
                - assigned_to: "Account Services"
                               │
                               ▼
                    ┌──────────────────────┐
                    │   HANDLE NODE        │
                    │                      │
                    │  • Search knowledge  │
                    │  • Check account     │
                    │  • Generate solution │
                    └──────────┬───────────┘
                               │
                State Updated: │
                - messages: [solution added]
                               │
                               ▼
                    ┌──────────────────────┐
                    │ CHECK_ESCALATION     │
                    │       NODE           │
                    │                      │
                    │  • Check priority    │
                    │  • Scan for keywords │
                    └──────────┬───────────┘
                               │
                               ▼
                        ┌──────────┐
                        │ ROUTING  │
                        │ DECISION │
                        └─────┬────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │  ESCALATE    │    │  COMPLETE    │
            │   (urgent)   │    │  (normal)    │
            └──────┬───────┘    └──────┬───────┘
                   │                   │
                   └─────────┬─────────┘
                             │
                             ▼
                        ┌────────┐
                        │  END   │
                        └────────┘
                             │
                Final State: │
                - resolution: "escalated" | "handled"
                - Full ticket metadata
                - Complete message history
```

## State Evolution

### State Structure

```python
SupportAgentState = {
    "messages": [
        HumanMessage("URGENT: Can't access my account!"),
        AIMessage("[System: Ticket routed to Account Services]"),
        AIMessage("I understand this is urgent..."),
    ],
    "ticket": {
        "ticket_id": "TKT-20251108192000",
        "category": "account",
        "priority": "urgent",
        "summary": "Account access issue",
        "assigned_to": "Account Services",
        "resolution": "escalated",
        "created_at": "2025-11-08T19:20:00"
    }
}
```

### State Transitions

#### After ANALYZE Node

```python
{
    "messages": [HumanMessage(...)],
    "ticket": {
        "ticket_id": "TKT-20251108192000",
        "category": "account",        # ✅ NEW
        "priority": "urgent",         # ✅ NEW
        "summary": "Account access",  # ✅ NEW
        "assigned_to": None,
        "resolution": None,
        "created_at": "2025-11-08T19:20:00"
    }
}
```

#### After ROUTE Node

```python
{
    "messages": [
        HumanMessage(...),
        AIMessage("[System: Ticket routed to Account Services]")  # ✅ NEW
    ],
    "ticket": {
        "ticket_id": "TKT-20251108192000",
        "category": "account",
        "priority": "urgent",
        "summary": "Account access",
        "assigned_to": "Account Services",  # ✅ NEW
        "resolution": None,
        "created_at": "2025-11-08T19:20:00"
    }
}
```

#### After HANDLE Node

```python
{
    "messages": [
        HumanMessage(...),
        AIMessage("[System: Ticket routed to Account Services]"),
        AIMessage("I understand this is urgent. I've checked your account...")  # ✅ NEW
    ],
    "ticket": {
        # ... same as before
    }
}
```

#### After CHECK_ESCALATION Node

```python
{
    "messages": [
        # ... previous messages
        AIMessage("✓ Ticket TKT-... escalated at ...")  # ✅ NEW
    ],
    "ticket": {
        # ...
        "resolution": "escalated",  # ✅ NEW
        # ...
    }
}
```

## Node Deep Dive

### 1. ANALYZE Node

**Purpose:** Extract and classify the support request

**Input:**
```python
{
    "messages": [HumanMessage("I forgot my password")],
    "ticket": {/* empty fields */}
}
```

**Processing:**
```python
def analyze_ticket_node(state):
    # 1. Extract user request
    user_request = state["messages"][-1].content

    # 2. Use LLM to classify
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    analysis = llm.invoke(f"Classify this support request: {user_request}")

    # 3. Parse classification
    parsed = json.loads(analysis.content)

    # 4. Update ticket state
    state["ticket"]["category"] = parsed["category"]
    state["ticket"]["priority"] = parsed["priority"]
    state["ticket"]["summary"] = parsed["summary"]

    return state
```

**Output:**
```python
{
    "messages": [HumanMessage("I forgot my password")],
    "ticket": {
        "category": "account",
        "priority": "low",
        "summary": "Password reset request"
    }
}
```

**Key Insight:** This node is **pure** - same input always produces same output (for deterministic LLM settings).

### 2. ROUTE Node

**Purpose:** Assign ticket to appropriate team

**Input:** State with classified ticket

**Processing:**
```python
def route_ticket_node(state):
    category = state["ticket"]["category"]

    # Simple mapping
    handlers = {
        "technical": "Tech Support Team",
        "billing": "Billing Department",
        "account": "Account Services",
        "general": "General Support",
    }

    assigned_to = handlers.get(category, "General Support")

    # Update state
    state["ticket"]["assigned_to"] = assigned_to

    # Add system message
    routing_msg = AIMessage(content=f"[System: Routed to {assigned_to}]")
    state["messages"].append(routing_msg)

    return state
```

**Output:** State with assignment and routing notification

**Key Insight:** This node is **deterministic** - no LLM, pure logic. Easy to test!

### 3. HANDLE Node

**Purpose:** Actually resolve the support request

**Input:** State with routed ticket

**Processing:**
```python
def handle_support_node(state):
    llm = ChatOpenAI()
    tools = [search_knowledge_base, check_account_status]
    llm_with_tools = llm.bind_tools(tools)

    # 1. Build context from state
    ticket = state["ticket"]
    context = f"""
    Category: {ticket['category']}
    Priority: {ticket['priority']}
    Summary: {ticket['summary']}
    """

    # 2. Get LLM response with tools
    response = llm_with_tools.invoke(
        [SystemMessage(context)] + state["messages"][-3:]
    )

    # 3. Execute tool calls if present
    if response.tool_calls:
        for tc in response.tool_calls:
            tool_result = execute_tool(tc)
            # Use result to generate final response
            final_response = llm.invoke(
                f"Based on this data: {tool_result}, answer the user"
            )
            state["messages"].append(final_response)
    else:
        state["messages"].append(response)

    return state
```

**Output:** State with solution added to messages

**Key Insight:** This is where the **actual work** happens. Tools are contextual.

### 4. CHECK_ESCALATION Node

**Purpose:** Determine if human intervention needed

**Input:** State after handling

**Processing:**
```python
def check_escalation_node(state):
    priority = state["ticket"]["priority"]

    if priority == "urgent":
        # Auto-escalate urgent tickets
        escalation = create_escalation(
            state["ticket"]["ticket_id"],
            f"Urgent {state['ticket']['category']} issue"
        )
        state["messages"].append(AIMessage(escalation))
        state["ticket"]["resolution"] = "escalated"
    else:
        state["ticket"]["resolution"] = "handled"

    return state
```

**Output:** State with resolution status

**Key Insight:** Business rules determine the path forward.

## Conditional Routing Logic

### The Decision Function

```python
def should_escalate(state: SupportAgentState) -> Literal["escalate", "complete"]:
    """
    This is where LangGraph shines - clean branching based on state!
    """

    # Check 1: Priority level
    if state["ticket"]["priority"] == "urgent":
        return "escalate"

    # Check 2: Escalation keywords in latest message
    last_msg = state["messages"][-1].content.lower()
    escalation_keywords = [
        "speak to manager",
        "lawsuit",
        "legal",
        "unacceptable",
        "horrible service"
    ]

    if any(keyword in last_msg for keyword in escalation_keywords):
        return "escalate"

    # Default: mark as complete
    return "complete"
```

### Routing Paths

```
Priority = "urgent"        → ESCALATE
Priority = "high"          → COMPLETE
Priority = "medium"        → COMPLETE
Priority = "low"           → COMPLETE

Keywords detected         → ESCALATE
No keywords               → COMPLETE
```

## Tool Integration

### Available Tools

#### 1. search_knowledge_base

```python
@tool
def search_knowledge_base(query: str) -> str:
    """Search KB for solutions to common problems."""

    kb = {
        "password": "Reset steps: ...",
        "billing": "Billing info: ...",
        "slow": "Performance tips: ...",
    }

    # Simple keyword matching
    for key, solution in kb.items():
        if key in query.lower():
            return solution

    return "No match found"
```

**When used:** User request contains common keywords

#### 2. check_account_status

```python
@tool
def check_account_status(user_id: str) -> str:
    """Check user account details (simulated)."""

    accounts = {
        "user123": {"status": "active", "plan": "premium"},
        "user456": {"status": "suspended", "reason": "payment_failed"},
    }

    return json.dumps(accounts.get(user_id, {"status": "not_found"}))
```

**When used:** Need to verify account information

#### 3. create_escalation

```python
@tool
def create_escalation(ticket_id: str, reason: str) -> str:
    """Escalate ticket to human team."""

    return f"""
    ✓ Ticket {ticket_id} escalated
    Reason: {reason}
    A specialist will contact you within 2 hours.
    """
```

**When used:** Urgent priority or escalation keywords detected

## Example Execution Trace

### Scenario: Urgent Account Access Issue

**Input:**
```
"URGENT: I can't access my account and I have a presentation in 1 hour!"
```

**Execution Trace:**

```
[START]
  │
  ▼
[ANALYZE NODE]
  • Received: "URGENT: I can't access my account..."
  • LLM Classification:
    - category: "account"
    - priority: "urgent"
    - summary: "Urgent account access issue"
  • State Updated ✓
  │
  ▼
[ROUTE NODE]
  • Category: "account"
  • Assigned to: "Account Services"
  • Added routing message ✓
  │
  ▼
[HANDLE NODE]
  • Context: account, urgent
  • Tools available: search_kb, check_account
  • LLM decision: Search KB for "account access"
  • KB Result: "To regain access: 1. Reset password..."
  • Generated response with solution ✓
  │
  ▼
[CHECK_ESCALATION NODE]
  • Priority check: "urgent" → ESCALATE
  • Created escalation ticket
  • Resolution: "escalated" ✓
  │
  ▼
[CONDITIONAL ROUTING]
  • Decision: should_escalate(state)
  • Result: "escalate" (due to urgent priority)
  │
  ▼
[END]
  • Final State:
    - messages: [user msg, routing, solution, escalation]
    - ticket.resolution: "escalated"
    - ticket.category: "account"
    - ticket.priority: "urgent"
```

## Performance Characteristics

### Time Complexity

```
Node             | Typical Duration | Bottleneck
-----------------+------------------+-----------------
ANALYZE          | 1-2s             | LLM inference
ROUTE            | <50ms            | Dictionary lookup
HANDLE           | 1-3s             | LLM + tools
CHECK_ESCALATION | <100ms           | Simple logic
ROUTING DECISION | <10ms            | Conditional check

Total: ~2-5 seconds per ticket
```

### Space Complexity

```
Component        | Memory Usage
-----------------+------------------
State            | ~1-5 KB per ticket
Messages         | ~500 bytes per message
LLM Context      | ~2-4K tokens
Total            | ~10-20 KB per ticket
```

## Testing Strategy

### Unit Testing Nodes

```python
def test_analyze_node():
    # Arrange
    initial_state = {
        "messages": [HumanMessage("I forgot my password")],
        "ticket": {"category": None, "priority": None}
    }

    # Act
    result = analyze_ticket_node(initial_state)

    # Assert
    assert result["ticket"]["category"] == "account"
    assert result["ticket"]["priority"] == "low"

def test_routing_decision():
    # Test urgent → escalate
    urgent_state = {"ticket": {"priority": "urgent"}}
    assert should_escalate(urgent_state) == "escalate"

    # Test normal → complete
    normal_state = {"ticket": {"priority": "medium"}}
    assert should_escalate(normal_state) == "complete"
```

### Integration Testing

```python
def test_full_workflow():
    agent = CustomerSupportAgent()

    result = agent.handle_request("URGENT: Can't login!")

    assert result["ticket"]["priority"] == "urgent"
    assert result["ticket"]["resolution"] == "escalated"
    assert "escalated" in result["response"].lower()
```

## Extending the Architecture

### Adding a New Node: Sentiment Analysis

```python
# 1. Define node
def sentiment_analysis_node(state):
    analyzer = SentimentAnalyzer()
    last_msg = state["messages"][-1].content
    sentiment = analyzer.analyze(last_msg)

    # Boost priority if very negative
    if sentiment < -0.7 and state["ticket"]["priority"] == "medium":
        state["ticket"]["priority"] = "high"

    return state

# 2. Add to graph
graph.add_node("sentiment", sentiment_analysis_node)
graph.add_edge("analyze", "sentiment")  # Insert between analyze and route
graph.add_edge("sentiment", "route")
```

### Adding Parallel Processing

```python
# Create parallel branches
graph.add_node("check_kb", search_kb_node)
graph.add_node("check_account", account_node)

# Both run in parallel from "route"
graph.add_edge("route", "check_kb")
graph.add_edge("route", "check_account")

# Merge results at "handle"
graph.add_edge("check_kb", "handle")
graph.add_edge("check_account", "handle")
```

## Summary

This architecture demonstrates:

✅ **Clear separation of concerns** - Each node has one job
✅ **Testable components** - Nodes can be unit tested
✅ **Visible state transitions** - Track ticket evolution
✅ **Flexible routing** - Easy to add branches
✅ **Production-ready patterns** - Error handling, logging, tools

**This is why LangGraph excels for complex workflows!**
