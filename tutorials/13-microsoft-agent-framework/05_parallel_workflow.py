"""
Parallel Workflow (Fan-Out / Fan-In) — Microsoft Agent Framework
=================================================================

Dispatches a single product description to three expert agents that run
concurrently, then collects their outputs and feeds them to an aggregator
agent that synthesises a unified report.

Graph topology:
                        +--> market_analyst  --+
    dispatcher  --------+--> tech_reviewer  ---+--> combine_insights --> aggregator --> output_finalizer
                        +--> legal_advisor  --+

The fan-in edge collects all three expert outputs into a single list; the
combine_insights executor merges them into one prompt before handing off to
the aggregator agent.

Wall-clock time is dominated by the slowest single expert, not the sum of
all three — that is the fan-out / fan-in advantage.

Concepts covered:
    - add_fan_out_edges(source, [targets])  : replicate input to N nodes
    - add_fan_in_edges([sources], target)   : wait for all N, then forward
    - Parallel agent execution              : the framework runs the experts
      concurrently inside a single workflow.run() call
    - Dispatcher executor                   : a lightweight @executor that
      re-emits the input so fan-out edges have a single source node

Usage:
    python 05_parallel_workflow.py

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
# Expert agent factories  (run in parallel)
# ============================================================================


def _create_market_analyst():
    """Factory: evaluates market positioning and audience fit.

    Returns:
        A ChatAgent focused on market strategy.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="MarketAnalyst",
        instructions=(
            "You are a senior market analyst. Given a product description, "
            "provide a focused analysis of 3-5 bullet points covering: "
            "target audience, competitive positioning, and market timing. "
            "Be specific and actionable."
        ),
    )


def _create_technical_reviewer():
    """Factory: assesses technical feasibility and implementation risk.

    Returns:
        A ChatAgent focused on the tech stack and scalability.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="TechnicalReviewer",
        instructions=(
            "You are a senior technical reviewer. Given a product description, "
            "provide a focused technical assessment of 3-5 bullet points covering: "
            "feasibility, technology-stack considerations, scalability, and "
            "implementation risk."
        ),
    )


def _create_legal_advisor():
    """Factory: flags compliance and regulatory concerns.

    Returns:
        A ChatAgent focused on legal and regulatory review.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="LegalAdvisor",
        instructions=(
            "You are a legal and compliance advisor. Given a product description, "
            "provide a focused compliance review of 3-5 bullet points covering: "
            "regulatory requirements, data-privacy implications, liability "
            "considerations, and intellectual-property concerns."
        ),
    )


# ============================================================================
# Aggregator agent factory  (runs after fan-in)
# ============================================================================


def _create_aggregator():
    """Factory: synthesises all expert outputs into one coherent report.

    The instructions explicitly name the three expert domains so the LLM
    structures its output with matching headers.

    Returns:
        A ChatAgent that merges expert inputs into a unified report.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="Aggregator",
        instructions=(
            "You are a product-launch coordinator. You will receive analysis "
            "from three experts: a Market Analyst, a Technical Reviewer, and a "
            "Legal Advisor. Synthesise their findings into a single coherent "
            "product-launch readiness report. Use a clear header for each "
            "expert's domain, then end with a 2-3 sentence Executive Summary."
        ),
    )


# ============================================================================
# Executors
# ============================================================================


@executor(id="dispatcher")
async def dispatcher(
    input_data: AgentExecutorRequest,
    ctx: WorkflowContext[AgentExecutorRequest],
) -> None:
    """Entry-point executor: re-emits the user's input for fan-out.

    add_fan_out_edges() needs a single source node.  The dispatcher is that
    node.  It receives the initial AgentExecutorRequest and forwards it
    unchanged; the framework then replicates the message to every fan-out
    target.

    Args:
        input_data: The original user request.
        ctx:        Workflow context; send_message() pushes to downstream edges.
    """
    await ctx.send_message(input_data)


# ---------------------------------------------------------------------------
# Fan-in combiner
# ---------------------------------------------------------------------------
# Fan-in collects each expert's AgentExecutorResponse into a list.  A ChatAgent
# can't consume that list directly, so this executor joins the texts into a
# single prompt and forwards it as an AgentExecutorRequest to the aggregator.

_EXPERT_LABELS = ["Market Analyst", "Technical Reviewer", "Legal Advisor"]


@executor(id="combine_insights")
async def combine_insights(
    inputs: list[AgentExecutorResponse],
    ctx: WorkflowContext[AgentExecutorRequest],
) -> None:
    """Merge the three expert outputs into one prompt for the aggregator.

    Args:
        inputs: List of AgentExecutorResponse objects, one per expert,
                collected by the fan-in edge.
        ctx:    Workflow context; send_message() forwards to the next node.
    """
    sections: List[str] = []
    for label, resp in zip(_EXPERT_LABELS, inputs):
        sections.append(f"--- {label} ---\n{resp.text}")

    combined_prompt = "\n\n".join(sections)
    await ctx.send_message(
        AgentExecutorRequest(
            messages=[ChatMessage(Role.USER, text=combined_prompt)]
        )
    )


@executor(id="output_finalizer")
async def output_finalizer(
    input_data: AgentExecutorResponse,
    ctx: WorkflowContext[str],
) -> None:
    """Terminal node: publishes the aggregator's report as the workflow output.

    Args:
        input_data: The Aggregator's synthesised report.
        ctx:        Workflow context; yield_output() marks this as the final result.
    """
    await ctx.yield_output(input_data.text)


# ============================================================================
# Workflow construction
# ============================================================================

# Shared list — used in both fan_out and fan_in so the expert names stay in sync
_EXPERT_NAMES: List[str] = ["market_analyst", "tech_reviewer", "legal_advisor"]


def _build_workflow():
    """Assemble the fan-out / fan-in product-launch analysis graph.

    Returns:
        A compiled workflow ready for .run().
    """
    return (
        WorkflowBuilder()
        # --- dispatcher (entry point) ---
        .register_executor(lambda: dispatcher,       name="dispatcher")
        # --- three parallel experts ---
        .register_agent(_create_market_analyst,      name="market_analyst")
        .register_agent(_create_technical_reviewer,  name="tech_reviewer")
        .register_agent(_create_legal_advisor,       name="legal_advisor")
        # --- fan-in combiner + aggregator + terminal ---
        .register_executor(lambda: combine_insights, name="combine_insights")
        .register_agent(_create_aggregator,          name="aggregator")
        .register_executor(lambda: output_finalizer, name="output_finalizer")
        # --- entry point ---
        .set_start_executor("dispatcher")
        # --- fan-out: dispatcher sends to all three experts in parallel ---
        .add_fan_out_edges("dispatcher", _EXPERT_NAMES)
        # --- fan-in: wait for all three, then collect into combine_insights ---
        #   Fan-in passes a list[AgentExecutorResponse] to the target.
        #   combine_insights merges them and forwards as a single request.
        .add_fan_in_edges(_EXPERT_NAMES, "combine_insights")
        # --- combine_insights -> aggregator -> terminal ---
        .add_edge("combine_insights", "aggregator")
        .add_edge("aggregator",       "output_finalizer")
        # --- compile ---
        .build()
    )


# ============================================================================
# Demo
# ============================================================================


async def demo_parallel_analysis() -> None:
    """Run the full fan-out / fan-in analysis on a sample product.

    The three experts execute concurrently.  The aggregator waits for all
    three before synthesising.  Total wall-clock time ≈ max(expert latencies),
    not the sum.
    """
    _validate_api_key()

    print("\n" + "=" * 80)
    print("  DEMO: Parallel Product-Launch Analysis  (Fan-Out / Fan-In)")
    print("=" * 80)

    product_description = (
        "SmartBrew Pro: An AI-powered smart coffee maker that learns your "
        "taste preferences over time. Connects to a mobile app, integrates "
        "with voice assistants, and can auto-order coffee beans via a "
        "partnered subscription service. Target price: $249."
    )

    print(f"\n[Input] Product description:\n  {product_description}\n")
    print("-" * 80)
    print("  Pipeline:")
    print("    dispatcher  -->  [ MarketAnalyst | TechReviewer | LegalAdvisor ]  (parallel)")
    print("                -->  combine_insights  -->  Aggregator  -->  Final Report\n")

    workflow = _build_workflow()
    request  = AgentExecutorRequest(
        messages=[ChatMessage(Role.USER, text=product_description)]
    )

    print("[Running] Dispatching to 3 experts in parallel …")
    events  = await workflow.run(request)
    outputs: List[str] = events.get_outputs()

    print("[Complete] Aggregator has synthesised all expert inputs.\n")
    print("=" * 80)
    print("  PRODUCT-LAUNCH READINESS REPORT")
    print("=" * 80)
    for output in outputs:
        print(output)
    print()


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    asyncio.run(demo_parallel_analysis())
