"""
Example: Customer Support Agent

A practical example of an AI agent for customer support that can:
- Answer common questions
- Look up order information
- Check product availability
- Handle refund requests
- Escalate to human support when needed
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI


# ============================================================================
# Mock Database and Tools
# ============================================================================

# Mock customer database
CUSTOMERS = {
    "customer123": {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "tier": "premium",
        "join_date": "2023-01-15"
    },
    "customer456": {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "tier": "standard",
        "join_date": "2023-06-20"
    }
}

# Mock orders database
ORDERS = {
    "ORD-001": {
        "customer_id": "customer123",
        "items": ["Laptop Stand", "USB-C Cable"],
        "total": 89.99,
        "status": "delivered",
        "order_date": "2024-01-10",
        "tracking": "TRACK123456"
    },
    "ORD-002": {
        "customer_id": "customer456",
        "items": ["Wireless Mouse"],
        "total": 29.99,
        "status": "shipped",
        "order_date": "2024-01-18",
        "tracking": "TRACK789012"
    }
}

# Mock product database
PRODUCTS = {
    "laptop-stand": {
        "name": "Ergonomic Laptop Stand",
        "price": 49.99,
        "in_stock": True,
        "quantity": 50
    },
    "usb-c-cable": {
        "name": "USB-C Cable 2m",
        "price": 19.99,
        "in_stock": True,
        "quantity": 200
    },
    "wireless-mouse": {
        "name": "Wireless Mouse",
        "price": 29.99,
        "in_stock": False,
        "quantity": 0,
        "restock_date": "2024-02-01"
    }
}


def lookup_order(order_id):
    """
    Look up order information by order ID.

    Args:
        order_id: Order identifier

    Returns:
        Order details or error message
    """
    if order_id in ORDERS:
        order = ORDERS[order_id]
        customer = CUSTOMERS.get(order["customer_id"], {})
        return {
            "success": True,
            "order_id": order_id,
            "customer_name": customer.get("name", "Unknown"),
            "items": order["items"],
            "total": order["total"],
            "status": order["status"],
            "order_date": order["order_date"],
            "tracking": order.get("tracking", "N/A")
        }
    else:
        return {
            "success": False,
            "error": f"Order {order_id} not found. Please check the order ID."
        }


def check_product_availability(product_name):
    """
    Check if a product is available and get details.

    Args:
        product_name: Name or slug of the product

    Returns:
        Product availability information
    """
    # Convert to slug format
    slug = product_name.lower().replace(" ", "-")

    if slug in PRODUCTS:
        product = PRODUCTS[slug]
        result = {
            "success": True,
            "product": product["name"],
            "price": product["price"],
            "in_stock": product["in_stock"],
        }

        if not product["in_stock"]:
            result["message"] = f"Currently out of stock. Expected restock: {product.get('restock_date', 'Unknown')}"
            result["quantity"] = 0
        else:
            result["quantity"] = product["quantity"]
            result["message"] = "Available for immediate purchase"

        return result
    else:
        return {
            "success": False,
            "error": f"Product '{product_name}' not found in our catalog."
        }


def process_refund_request(order_id, reason):
    """
    Process a refund request for an order.

    Args:
        order_id: Order identifier
        reason: Reason for refund

    Returns:
        Refund request status
    """
    if order_id not in ORDERS:
        return {
            "success": False,
            "error": f"Order {order_id} not found."
        }

    order = ORDERS[order_id]
    order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
    days_since_order = (datetime.now() - order_date).days

    # Check if within refund window (30 days)
    if days_since_order > 30:
        return {
            "success": False,
            "error": "Refund request outside 30-day window. Please contact support for exceptions.",
            "escalate": True
        }

    # Auto-approve for delivered orders within window
    if order["status"] == "delivered":
        return {
            "success": True,
            "message": f"Refund approved for order {order_id}",
            "amount": order["total"],
            "refund_id": f"REF-{order_id}",
            "estimated_days": "5-7 business days",
            "reason": reason
        }
    else:
        return {
            "success": True,
            "message": f"Order {order_id} will be cancelled and refunded",
            "amount": order["total"],
            "status": "cancellation_in_progress"
        }


def get_shipping_status(tracking_number):
    """
    Get shipping status for a tracking number.

    Args:
        tracking_number: Tracking number

    Returns:
        Shipping status information
    """
    # Mock tracking data
    mock_status = {
        "TRACK123456": {
            "status": "delivered",
            "location": "Customer's address",
            "delivered_date": "2024-01-15",
            "carrier": "FedEx"
        },
        "TRACK789012": {
            "status": "in_transit",
            "location": "Distribution center - New York",
            "estimated_delivery": "2024-01-22",
            "carrier": "UPS"
        }
    }

    if tracking_number in mock_status:
        return {
            "success": True,
            "tracking_number": tracking_number,
            **mock_status[tracking_number]
        }
    else:
        return {
            "success": False,
            "error": f"Tracking number {tracking_number} not found."
        }


def escalate_to_human(reason, customer_info=None):
    """
    Escalate the conversation to human support.

    Args:
        reason: Reason for escalation
        customer_info: Optional customer information

    Returns:
        Escalation confirmation
    """
    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
        "success": True,
        "message": "Your request has been escalated to our human support team.",
        "ticket_id": ticket_id,
        "estimated_response": "within 2 hours",
        "reason": reason
    }


# ============================================================================
# Tool Schemas
# ============================================================================

SUPPORT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Look up order information using order ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID (format: ORD-XXX)"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_product_availability",
            "description": "Check if a product is in stock and get pricing",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Product name or slug"
                    }
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund_request",
            "description": "Process a customer refund request",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to refund"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for refund"
                    }
                },
                "required": ["order_id", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_shipping_status",
            "description": "Get current shipping status using tracking number",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_number": {
                        "type": "string",
                        "description": "Tracking number"
                    }
                },
                "required": ["tracking_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate complex issues to human support agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    },
                    "customer_info": {
                        "type": "string",
                        "description": "Optional customer information"
                    }
                }
            }
        }
    }
]


# ============================================================================
# Customer Support Agent
# ============================================================================

class CustomerSupportAgent:
    """
    A customer support AI agent with specialized tools and knowledge.
    """

    def __init__(self):
        """Initialize the customer support agent."""
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"

        self.system_prompt = """You are a helpful customer support agent for TechShop.

Your role:
- Assist customers with order inquiries
- Check product availability
- Process refund requests (within policy)
- Track shipments
- Escalate complex issues to human support

Guidelines:
- Be friendly, professional, and empathetic
- Use the available tools to look up accurate information
- For refunds, check our 30-day policy
- Always confirm order IDs and tracking numbers before looking them up
- Escalate to human support for: complaints, technical issues, policy exceptions
- Never make up information - use tools or admit you don't know

Company policies:
- 30-day refund policy on all products
- Free shipping on orders over $50
- Premium members get priority support
"""

        self.conversation_history = []
        self.tools = {
            "lookup_order": lookup_order,
            "check_product_availability": check_product_availability,
            "process_refund_request": process_refund_request,
            "get_shipping_status": get_shipping_status,
            "escalate_to_human": escalate_to_human
        }

    def handle_message(self, user_message):
        """
        Handle a customer message with tool support.

        Args:
            user_message: Customer's message

        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        # Call LLM with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=SUPPORT_TOOLS,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # Process tool calls if any
        if response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Execute tool
                result = self.tools[tool_name](**tool_args)

                # Add result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Get final response
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            response_text = final_response.choices[0].message.content
        else:
            response_text = response_message.content

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })

        return response_text

    def run(self):
        """Run interactive customer support session."""
        print("\n" + "="*60)
        print("TechShop Customer Support")
        print("="*60)
        print("Hello! I'm your AI support assistant.")
        print("How can I help you today?")
        print("\nType 'quit' to end the chat.")
        print("="*60 + "\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nAgent: Thank you for contacting TechShop! Have a great day!\n")
                break

            if not user_input:
                continue

            try:
                response = self.handle_message(user_input)
                print(f"\nAgent: {response}\n")
            except Exception as e:
                print(f"\nError: {e}")
                print("I apologize for the technical difficulty. Let me escalate this to our team.\n")


# ============================================================================
# Demo Scenarios
# ============================================================================

def demo_order_lookup():
    """Demo: Looking up order information."""
    print("\n=== Demo: Order Lookup ===\n")
    agent = CustomerSupportAgent()

    queries = [
        "Hi, I want to check on my order ORD-001",
        "Where is my package?",
    ]

    for query in queries:
        print(f"Customer: {query}")
        response = agent.handle_message(query)
        print(f"Agent: {response}\n")


def demo_refund_request():
    """Demo: Processing refund request."""
    print("\n=== Demo: Refund Request ===\n")
    agent = CustomerSupportAgent()

    queries = [
        "I need to return my order ORD-001. The product doesn't fit my needs.",
    ]

    for query in queries:
        print(f"Customer: {query}")
        response = agent.handle_message(query)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    # Run interactive support
    agent = CustomerSupportAgent()
    agent.run()

    # Uncomment to run demos:
    # demo_order_lookup()
    # demo_refund_request()
