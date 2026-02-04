"""
Sequential Workflow — Microsoft Agent Framework
================================================

Builds a two-stage content pipeline with WorkflowBuilder.  A Writer agent
drafts a marketing tagline, then a Reviewer agent critiques it.  A terminal
executor collects the final output.

This is the first file in the tutorial that uses the workflow primitives
shared by files 04 and 05, so read the comments carefully — they explain
each builder method and the executor / yield_output pattern.

Graph topology:
    writer_agent  -->  reviewer_agent  -->  output_collector

Concepts covered:
    - WorkflowBuilder       : fluent builder for wiring a workflow graph
    - register_agent()      : register an agent via a no-arg factory function
    - register_executor()   : register a custom processing node
    - set_start_executor()  : mark the first node to receive user input
    - add_edge()            : unconditional edge between two nodes
    - @executor             : decorator that turns a function into a workflow node
    - WorkflowContext       : per-run context; yield_output() publishes the result
    - AgentExecutorRequest  : the input envelope passed to agent nodes
    - AgentExecutorResponse : the output envelope produced by agent nodes

Usage:
    python 03_sequential_workflow.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install -r requirements.txt
"""

import asyncio
import os
from typing import List

from dotenv import load_dotenv

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
# Agent factories
# ============================================================================
# register_agent() expects a no-arg callable that returns a ChatAgent.
# Using module-level factory functions (rather than lambdas) keeps the code
# readable and allows docstrings.


def _create_writer_agent():
    """Factory: a creative copywriter that produces a single tagline.

    Returns:
        A ChatAgent configured to output one concise marketing tagline.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="Writer",
        instructions=(
            "You are a creative marketing copywriter. "
            "When given a product description, write a single punchy marketing "
            "tagline (one sentence, max 15 words). "
            "Respond with ONLY the tagline — no preamble, no explanation."
        ),
    )


def _create_reviewer_agent():
    """Factory: a marketing director who critiques taglines.

    Returns:
        A ChatAgent that provides structured feedback on a tagline.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="Reviewer",
        instructions=(
            "You are a marketing director reviewing taglines. "
            "Given a tagline, provide exactly three bullet points: "
            "(1) what works, (2) what could be stronger, (3) one revised version. "
            "Be concise."
        ),
    )


# ============================================================================
# Terminal executor
# ============================================================================


@executor(id="output_collector")
async def output_collector(
    input_data: AgentExecutorResponse,
    ctx: WorkflowContext,
) -> None:
    """Terminal node: yield the Reviewer's feedback as the workflow output.

    This is the simplest possible executor.  It receives whatever the
    previous node produced and publishes it as the final result so the
    caller can retrieve it from events.get_outputs().

    Args:
        input_data: The AgentExecutorResponse from the Reviewer.
        ctx:        Workflow context; yield_output() marks this value as final.
    """
    await ctx.yield_output(input_data.text)


# ============================================================================
# Workflow construction
# ============================================================================


def _build_workflow():
    """Assemble the Writer -> Reviewer -> Collector pipeline.

    Returns:
        A compiled workflow ready for .run().
    """
    return (
        WorkflowBuilder()
        # 1. Register agents via their no-arg factories
        .register_agent(_create_writer_agent,  name="writer_agent")
        .register_agent(_create_reviewer_agent, name="reviewer_agent")
        # 2. Register the terminal executor
        #    The lambda wraps the already-decorated function; this is the
        #    pattern expected by register_executor().
        .register_executor(lambda: output_collector, name="output_collector")
        # 3. The Writer is the entry point — it will receive the user's input
        .set_start_executor("writer_agent")
        # 4. Wire the edges (unconditional: every message flows through)
        .add_edge("writer_agent",    "reviewer_agent")
        .add_edge("reviewer_agent",  "output_collector")
        # 5. Compile
        .build()
    )


# ============================================================================
# Demo
# ============================================================================


async def demo_sequential_workflow() -> None:
    """Run the Writer -> Reviewer pipeline on a fixed product prompt.

    Nothing interactive here — the prompt is baked in so the demo is fast
    and repeatable.  The printed output labels each stage so you can see
    the flow the workflow orchestrates behind the scenes.
    """
    _validate_api_key()

    print("\n" + "=" * 80)
    print("  DEMO: Sequential Workflow  (Writer  ->  Reviewer)")
    print("=" * 80)

    product_prompt = (
        "A lightweight, waterproof backpack designed for urban commuters "
        "who want style and function in one compact bag."
    )

    print(f"\n[Input] Product description:\n  {product_prompt}\n")
    print("-" * 80)
    print("  Pipeline:  Writer  -->  Reviewer  -->  Output\n")

    # Build the workflow graph
    workflow = _build_workflow()

    # Wrap the prompt in the request type the workflow expects
    request = AgentExecutorRequest(
        messages=[ChatMessage(Role.USER, text=product_prompt)]
    )

    print("[Stage 1] Writer is drafting a tagline …")
    # workflow.run() executes the entire graph; returns an events object
    events = await workflow.run(request)

    # Retrieve the value(s) yielded by the terminal executor
    outputs: List[str] = events.get_outputs()

    print("[Stage 2] Reviewer has provided feedback.\n")
    print("=" * 80)
    print("  WORKFLOW OUTPUT")
    print("=" * 80)
    for output in outputs:
        print(output)
    print()


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    asyncio.run(demo_sequential_workflow())
