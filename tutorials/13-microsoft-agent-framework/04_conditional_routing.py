"""
Conditional Routing — Microsoft Agent Framework
================================================

Builds a workflow with conditional edges that route messages to different
downstream nodes based on a runtime classification.  A spam-detection agent
classifies an incoming email using a Pydantic structured output; the workflow
then takes one of two branches:

    spam_detector  --[is_spam]-->     spam_handler     -->  spam_output
                   --[not spam]-->    email_assistant  -->  legit_output

Concepts covered:
    - Pydantic BaseModel as response_format   : forces the LLM to return
      valid JSON matching a schema; no free-text parsing needed.
    - model_validate_json()                   : parse the agent's JSON text
      into a typed Python object.
    - Edge conditions (predicate functions)   : a callable(response) -> bool
      attached to add_edge() that gates the transition.
    - Branching topology                      : exactly one edge out of the
      detector fires for any given input.

Usage:
    python 04_conditional_routing.py

    By default this runs the "not spam" branch.  Uncomment demo_spam() in
    the __main__ block to exercise the spam branch.

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install -r requirements.txt
"""

import asyncio
import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

from agent_framework import (
    AgentExecutorRequest,
    AgentExecutorResponse,
    ChatMessage,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.openai import OpenAIChatClient

# ============================================================================
# Environment
# ============================================================================

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"


# ============================================================================
# Helpers
# ============================================================================


def _validate_api_key() -> None:
    """Exit with a helpful message when OPENAI_API_KEY is missing.

    Raises:
        SystemExit: If the key is not set in the environment.
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        print("  1. Create a .env file with  OPENAI_API_KEY=sk-...")
        print("  2. Or export it in your shell.")
        raise SystemExit(1)


# ============================================================================
# Structured-output schema
# ============================================================================


class SpamClassification(BaseModel):
    """Schema the spam-detector agent is forced to return.

    Passing this as response_format tells the LLM to emit JSON that
    exactly matches these fields — no free-text preamble allowed.

    Attributes:
        is_spam:    True when the email is classified as spam.
        confidence: 0.0–1.0 classification confidence score.
        reason:     Short human-readable explanation of the decision.
    """

    is_spam:    bool
    confidence: float
    reason:     str


# ============================================================================
# Sample emails
# ============================================================================

# Default input — a legitimate work email that should take the "not spam" path.
NOT_SPAM_EMAIL = (
    "Subject: Project Update\n\n"
    "Hi Sarah,\n\n"
    "Just wanted to let you know that the Q3 report is almost ready. "
    "I should have it to you by end of day Thursday. "
    "Let me know if you need any specific sections highlighted.\n\n"
    "Thanks,\nAlex"
)

# Swap this in (via demo_spam()) to exercise the spam branch.
SPAM_EMAIL = (
    "Subject: You Won a FREE iPhone!!!\n\n"
    "Congratulations!!! You have been selected as the lucky winner of a "
    "brand new iPhone 15 Pro. Click the link below immediately to claim "
    "your prize: http://totally-legit-prize.example.com/claim?id=94837\n\n"
    "Act fast — this offer expires in 24 hours!!!"
)


# ============================================================================
# Agent factories
# ============================================================================


def _create_spam_detector():
    """Factory: classifier agent with a forced Pydantic response_format.

    default_options={"response_format": SpamClassification} is the key:
    it instructs the framework (and the underlying LLM) to return only
    valid JSON matching SpamClassification.  No post-processing regex needed.

    Returns:
        A ChatAgent that always returns SpamClassification-shaped JSON.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="SpamDetector",
        instructions=(
            "You are an email spam classifier. Analyze the given email and "
            "determine whether it is spam or legitimate. "
            "Return your answer as structured JSON only — no other text."
        ),
        default_options={"response_format": SpamClassification},
    )


def _create_spam_handler():
    """Factory: agent that produces a spam-flagging notice.

    Returns:
        A ChatAgent that acknowledges the spam flag.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="SpamHandler",
        instructions=(
            "You are a spam-handling system. The email you receive has been "
            "classified as spam. Generate a short notice (2-3 sentences) "
            "informing the user that the email has been flagged and moved to spam."
        ),
    )


def _create_email_assistant():
    """Factory: agent that drafts a reply to a legitimate email.

    Returns:
        A ChatAgent that writes a polite, professional reply.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="EmailAssistant",
        instructions=(
            "You are an email assistant. Draft a polite, professional reply "
            "to the email you receive. Acknowledge the message and respond "
            "appropriately. Keep the reply to 2-4 sentences."
        ),
    )


# ============================================================================
# Edge-condition predicates
# ============================================================================
# Each predicate receives the upstream node's AgentExecutorResponse, parses
# the structured JSON, and returns a bool.  The workflow fires exactly the
# edge whose predicate returns True.


def _is_spam(response: AgentExecutorResponse) -> bool:
    """Route to spam_handler when the detector flagged the email.

    Args:
        response: The spam_detector's output (JSON text).

    Returns:
        True if the parsed SpamClassification.is_spam is True.
    """
    classification = SpamClassification.model_validate_json(response.text)
    return classification.is_spam


def _is_not_spam(response: AgentExecutorResponse) -> bool:
    """Route to email_assistant when the detector cleared the email.

    Args:
        response: The spam_detector's output (JSON text).

    Returns:
        True if the parsed SpamClassification.is_spam is False.
    """
    return not _is_spam(response)


# ============================================================================
# Terminal executors
# ============================================================================


@executor(id="spam_output")
async def spam_output(
    input_data: AgentExecutorResponse,
    ctx: WorkflowContext,
) -> None:
    """Terminal node for the spam branch.

    Args:
        input_data: SpamHandler's notice text.
        ctx:        Workflow context; yield_output() publishes the final result.
    """
    await ctx.yield_output(f"[SPAM DETECTED]\n{input_data.text}")


@executor(id="legit_output")
async def legit_output(
    input_data: AgentExecutorResponse,
    ctx: WorkflowContext,
) -> None:
    """Terminal node for the legitimate branch.

    Args:
        input_data: EmailAssistant's drafted reply.
        ctx:        Workflow context; yield_output() publishes the final result.
    """
    await ctx.yield_output(f"[REPLY DRAFTED]\n{input_data.text}")


# ============================================================================
# Workflow construction
# ============================================================================


def _build_workflow():
    """Assemble the conditional-routing email-triage graph.

    Graph:
                        +--> spam_handler     --> spam_output
    spam_detector --+
                    +-->  email_assistant    --> legit_output

    Returns:
        A compiled workflow ready for .run().
    """
    return (
        WorkflowBuilder()
        # --- agents ---
        .register_agent(_create_spam_detector,    name="spam_detector")
        .register_agent(_create_spam_handler,     name="spam_handler")
        .register_agent(_create_email_assistant,  name="email_assistant")
        # --- terminal executors ---
        .register_executor(lambda: spam_output,  name="spam_output")
        .register_executor(lambda: legit_output, name="legit_output")
        # --- entry point ---
        .set_start_executor("spam_detector")
        # --- conditional edges out of the detector ---
        #   Exactly one of _is_spam / _is_not_spam will be True,
        #   so exactly one downstream branch executes.
        .add_edge("spam_detector",    "spam_handler",    condition=_is_spam)
        .add_edge("spam_detector",    "email_assistant", condition=_is_not_spam)
        # --- unconditional edges to terminal nodes ---
        .add_edge("spam_handler",     "spam_output")
        .add_edge("email_assistant",  "legit_output")
        # --- compile ---
        .build()
    )


# ============================================================================
# Shared runner
# ============================================================================


async def _run_triage(email_text: str, label: str) -> None:
    """Execute the triage workflow on the given email and print results.

    Args:
        email_text: Raw email string to classify and route.
        label:      Short label ("Legitimate" or "Spam") for the print header.
    """
    print(f"\n[Input] {label} email:\n")
    for line in email_text.splitlines():
        print(f"  {line}")

    print(f"\n{'-' * 80}")
    print("  spam_detector  -->  [conditional]  -->  handler  -->  output\n")

    workflow = _build_workflow()
    request  = AgentExecutorRequest(
        messages=[ChatMessage(Role.USER, text=email_text)]
    )

    events  = await workflow.run(request)
    outputs: List[str] = events.get_outputs()

    print("=" * 80)
    print("  WORKFLOW OUTPUT")
    print("=" * 80)
    for output in outputs:
        print(output)
    print()


# ============================================================================
# Demos
# ============================================================================


async def demo_not_spam() -> None:
    """Run the triage workflow with the default legitimate email."""
    _validate_api_key()
    print("\n" + "=" * 80)
    print("  DEMO: Conditional Routing — Legitimate Email")
    print("=" * 80)
    await _run_triage(NOT_SPAM_EMAIL, "Legitimate")


async def demo_spam() -> None:
    """Run the triage workflow with the spam email sample."""
    _validate_api_key()
    print("\n" + "=" * 80)
    print("  DEMO: Conditional Routing — Spam Email")
    print("=" * 80)
    await _run_triage(SPAM_EMAIL, "Spam")


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    # Default: the legitimate email (exercises the "not spam" branch).
    # Uncomment demo_spam() to test the spam branch.

    asyncio.run(demo_not_spam())

    # asyncio.run(demo_spam())
