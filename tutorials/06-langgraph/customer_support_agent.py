"""Enhanced LangGraph Tutorial: Customer Support Ticket Routing System

This tutorial demonstrates LangGraph's core strengths:
- Orchestration: Multiple specialized nodes working together
- Persistence: State tracking across conversation turns
- Branching: Conditional routing based on ticket properties

Example application: An intelligent customer support system that:
1. Analyzes incoming support requests
2. Routes tickets to appropriate handlers
3. Escalates urgent issues automatically
4. Maintains ticket state throughout the conversation
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Annotated, List, Literal, Optional, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph, add_messages


# ==================== DOMAIN MODELS ====================


class TicketCategory(str, Enum):
    """Support ticket categories."""

    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"


class TicketPriority(str, Enum):
    """Support ticket priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketState(TypedDict):
    """Current state of a support ticket."""

    ticket_id: str
    category: Optional[str]
    priority: Optional[str]
    summary: Optional[str]
    assigned_to: Optional[str]
    resolution: Optional[str]
    created_at: str


# ==================== LANGGRAPH STATE ====================


class SupportAgentState(TypedDict):
    """LangGraph state that tracks messages AND ticket metadata.

    This demonstrates how LangGraph can maintain complex state beyond
    just conversation history - perfect for workflows that need to
    track business logic.
    """

    messages: Annotated[List[BaseMessage], add_messages]
    ticket: TicketState  # Persistent ticket state


# ==================== TOOLS ====================


@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for solutions to common problems."""
    # Simulated knowledge base
    kb = {
        "password": "To reset your password:\n1. Go to login page\n2. Click 'Forgot Password'\n3. Check your email for reset link",
        "billing": "For billing inquiries:\n- Check your invoice in Account Settings\n- Payment methods can be updated under Billing\n- Contact billing@company.com for disputes",
        "slow": "Performance troubleshooting:\n1. Clear browser cache\n2. Check internet connection\n3. Try incognito mode\n4. Update your browser",
        "cancel": "To cancel your subscription:\n1. Go to Account Settings\n2. Select Subscription\n3. Click 'Cancel Subscription'\n4. Follow the confirmation steps",
    }

    query_lower = query.lower()
    for key, solution in kb.items():
        if key in query_lower:
            return solution

    return "No exact match found. Please describe your issue in more detail."


@tool
def check_account_status(user_id: str) -> str:
    """Check the status of a user account (simulated)."""
    # Simulated account database
    accounts = {
        "user123": {"status": "active", "plan": "premium", "expires": "2025-12-31"},
        "user456": {"status": "suspended", "plan": "basic", "reason": "payment_failed"},
    }

    account = accounts.get(user_id, {"status": "not_found"})
    return json.dumps(account, indent=2)


@tool
def create_escalation(ticket_id: str, reason: str) -> str:
    """Escalate a ticket to human support team."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"✓ Ticket {ticket_id} escalated at {timestamp}\nReason: {reason}\nA specialist will contact you within 2 hours."


# ==================== AGENT NODES ====================


def analyze_ticket_node(state: SupportAgentState) -> SupportAgentState:
    """First node: Analyze the user's request and classify the ticket.

    This demonstrates how nodes can:
    - Read from state (messages)
    - Update state (ticket metadata)
    - Use LLM for classification
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Get the latest user message
    last_message = state["messages"][-1]
    user_request = last_message.content if isinstance(last_message.content, str) else ""

    # Use LLM to classify the ticket
    analysis_prompt = f"""Analyze this support request and extract:
1. Category: technical, billing, account, or general
2. Priority: low, medium, high, or urgent
3. Brief summary (one line)

User request: {user_request}

Respond in JSON format:
{{"category": "...", "priority": "...", "summary": "..."}}
"""

    response = llm.invoke([HumanMessage(content=analysis_prompt)])

    try:
        analysis = json.loads(response.content)
        category = analysis.get("category", "general")
        priority = analysis.get("priority", "medium")
        summary = analysis.get("summary", user_request[:100])
    except:
        category = "general"
        priority = "medium"
        summary = user_request[:100]

    # Update ticket state
    updated_ticket = state["ticket"].copy()
    updated_ticket["category"] = category
    updated_ticket["priority"] = priority
    updated_ticket["summary"] = summary

    return {"ticket": updated_ticket}


def route_ticket_node(state: SupportAgentState) -> SupportAgentState:
    """Second node: Route ticket to appropriate handler based on category.

    This node demonstrates state-based decision making.
    """
    ticket = state["ticket"]
    category = ticket.get("category", "general")

    # Assign based on category
    handlers = {
        "technical": "Tech Support Team",
        "billing": "Billing Department",
        "account": "Account Services",
        "general": "General Support",
    }

    assigned_to = handlers.get(category, "General Support")

    updated_ticket = ticket.copy()
    updated_ticket["assigned_to"] = assigned_to

    # Add a system message about routing
    routing_msg = AIMessage(
        content=f"[System: Ticket routed to {assigned_to}]"
    )

    return {"ticket": updated_ticket, "messages": [routing_msg]}


def handle_support_node(state: SupportAgentState) -> SupportAgentState:
    """Third node: Actually handle the support request.

    This node uses tools and LLM to provide support.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    tools = [search_knowledge_base, check_account_status]
    llm_with_tools = llm.bind_tools(tools)

    ticket = state["ticket"]
    messages = state["messages"]

    # Create support context
    support_prompt = f"""You are a helpful customer support agent.

Ticket Info:
- Category: {ticket.get('category')}
- Priority: {ticket.get('priority')}
- Summary: {ticket.get('summary')}

You have access to:
- search_knowledge_base: Search for solutions
- check_account_status: Check user account details

Provide helpful, concise support. Use tools when appropriate."""

    # Build conversation with context
    conversation = [SystemMessage(content=support_prompt)] + messages[-3:]  # Last 3 messages

    response = llm_with_tools.invoke(conversation)

    # Handle tool calls if present
    if response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            if tool_call["name"] == "search_knowledge_base":
                result = search_knowledge_base.invoke(tool_call["args"])
                tool_results.append(f"Knowledge Base: {result}")
            elif tool_call["name"] == "check_account_status":
                result = check_account_status.invoke(tool_call["args"])
                tool_results.append(f"Account Status: {result}")

        # Create final response incorporating tool results
        final_prompt = f"""Based on these tool results, provide a clear answer to the user:

{chr(10).join(tool_results)}

Original request: {messages[-1].content}
"""
        final_response = llm.invoke([HumanMessage(content=final_prompt)])
        return {"messages": [final_response]}

    return {"messages": [response]}


def check_escalation_node(state: SupportAgentState) -> SupportAgentState:
    """Final node: Check if escalation is needed.

    This demonstrates conditional logic based on state.
    """
    ticket = state["ticket"]
    priority = ticket.get("priority", "medium")

    # Auto-escalate urgent tickets
    if priority == "urgent":
        escalation_msg = AIMessage(
            content=create_escalation.invoke({
                "ticket_id": ticket["ticket_id"],
                "reason": f"Urgent {ticket.get('category')} issue"
            })
        )
        updated_ticket = ticket.copy()
        updated_ticket["resolution"] = "escalated"
        return {"messages": [escalation_msg], "ticket": updated_ticket}

    # Mark as handled for non-urgent
    updated_ticket = ticket.copy()
    updated_ticket["resolution"] = "handled"
    return {"ticket": updated_ticket}


# ==================== ROUTING LOGIC ====================


def should_escalate(state: SupportAgentState) -> Literal["escalate", "complete"]:
    """Conditional edge: Decide if ticket needs escalation.

    This is where LangGraph shines - clean branching logic based on state.
    """
    priority = state["ticket"].get("priority", "medium")

    # Keywords that trigger escalation
    last_message = state["messages"][-1].content if state["messages"] else ""
    escalation_keywords = ["speak to manager", "lawsuit", "legal", "unacceptable"]

    if priority == "urgent" or any(kw in last_message.lower() for kw in escalation_keywords):
        return "escalate"

    return "complete"


# ==================== MAIN AGENT ====================


@dataclass
class CustomerSupportAgent:
    """LangGraph-powered customer support agent.

    This demonstrates the full power of LangGraph:
    - Multiple nodes for different stages
    - Conditional routing based on ticket properties
    - Persistent state across the conversation
    - Clean separation of concerns
    """

    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    graph: StateGraph = field(init=False)

    def __post_init__(self):
        load_dotenv(override=True)
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the support ticket workflow graph.

        Graph structure:
        START -> analyze -> route -> handle -> check_escalation -> [escalate|complete] -> END

        This workflow shows how LangGraph excels at orchestrating
        multi-step processes with conditional branching.
        """
        builder = StateGraph(SupportAgentState)

        # Add nodes for each stage
        builder.add_node("analyze", analyze_ticket_node)
        builder.add_node("route", route_ticket_node)
        builder.add_node("handle", handle_support_node)
        builder.add_node("check_escalation", check_escalation_node)

        # Define the workflow
        builder.add_edge(START, "analyze")
        builder.add_edge("analyze", "route")
        builder.add_edge("route", "handle")
        builder.add_edge("handle", "check_escalation")

        # Conditional ending - escalate or complete
        builder.add_conditional_edges(
            "check_escalation",
            should_escalate,
            {
                "escalate": END,  # Urgent tickets end after escalation
                "complete": END,  # Normal tickets end after handling
            }
        )

        return builder.compile()

    def handle_request(self, user_request: str, ticket_id: Optional[str] = None) -> dict:
        """Process a support request through the workflow.

        Returns:
            dict with 'response' and 'ticket' information
        """
        # Initialize ticket state
        if ticket_id is None:
            ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        initial_state = {
            "messages": [HumanMessage(content=user_request)],
            "ticket": {
                "ticket_id": ticket_id,
                "category": None,
                "priority": None,
                "summary": None,
                "assigned_to": None,
                "resolution": None,
                "created_at": datetime.now().isoformat(),
            }
        }

        # Run through the graph
        result = self.graph.invoke(initial_state)

        # Extract response
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        response = ai_messages[-1].content if ai_messages else "I'm here to help!"

        return {
            "response": response,
            "ticket": result["ticket"],
        }

    def print_ticket_info(self, ticket: TicketState):
        """Pretty print ticket information."""
        print("\n" + "="*60)
        print(f"Ticket ID: {ticket['ticket_id']}")
        print(f"Category: {ticket.get('category', 'N/A')}")
        print(f"Priority: {ticket.get('priority', 'N/A')}")
        print(f"Assigned To: {ticket.get('assigned_to', 'N/A')}")
        print(f"Summary: {ticket.get('summary', 'N/A')}")
        print(f"Status: {ticket.get('resolution', 'in_progress')}")
        print("="*60 + "\n")


# ==================== CLI INTERFACE ====================


def run_examples():
    """Run example scenarios to demonstrate the agent's capabilities."""
    agent = CustomerSupportAgent()

    examples = [
        {
            "name": "Low Priority - General Question",
            "request": "How do I change my email address?",
        },
        {
            "name": "Medium Priority - Technical Issue",
            "request": "The app is running really slow on my phone. What can I do?",
        },
        {
            "name": "High Priority - Billing Issue",
            "request": "I was charged twice this month! This is unacceptable.",
        },
        {
            "name": "Urgent - Account Access",
            "request": "URGENT: I can't access my account and I have an important presentation in 1 hour!",
        },
    ]

    print("\n*** CUSTOMER SUPPORT AGENT - EXAMPLE SCENARIOS ***")
    print("="*70)

    for i, example in enumerate(examples, 1):
        print(f"\n[Example {i}]: {example['name']}")
        print("-"*70)
        print(f"User: {example['request']}")
        print()

        result = agent.handle_request(example['request'])

        print(f"Agent: {result['response']}")
        agent.print_ticket_info(result['ticket'])

        if i < len(examples):
            print("\n" + "-"*70)


def run_interactive():
    """Run interactive chat mode."""
    agent = CustomerSupportAgent()

    print("\n*** CUSTOMER SUPPORT AGENT - INTERACTIVE MODE ***")
    print("="*70)
    print("Type your support request, or 'quit' to exit.")
    print()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSession ended.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit"}:
            print("Thank you for contacting support. Goodbye!")
            break

        result = agent.handle_request(user_input)

        print(f"\nAgent: {result['response']}")
        agent.print_ticket_info(result['ticket'])


def main():
    parser = argparse.ArgumentParser(
        description="LangGraph Customer Support Agent Tutorial"
    )
    parser.add_argument(
        "--mode",
        choices=["examples", "interactive"],
        default="examples",
        help="Run examples or interactive mode"
    )

    args = parser.parse_args()

    if args.mode == "examples":
        run_examples()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
