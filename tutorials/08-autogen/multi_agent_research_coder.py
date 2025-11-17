"""
Building a Multi-Agent Research & Coding Assistant with AutoGen.

Pipeline:
1) ResearchAgent: reads the user question and proposes a plan for `time_series.csv`.
2) CoderAgent: writes Python (pandas/matplotlib) to implement the plan.
3) Reviewer: checks the code and provides PASS/FAIL with reasons.

Note: Code execution is optional and OFF by default. Flip ENABLE_CODE_EXECUTION
below to True to run generated Python inside a local (non-Docker) sandbox.
"""

from __future__ import annotations

import os
from io import StringIO
from typing import Any, Iterable, Tuple

from dotenv import load_dotenv
from autogen import AssistantAgent, LLMConfig, UserProxyAgent

DEFAULT_MODEL = "gpt-4o-mini"
CSV_PATH = "time_series.csv"
USER_QUESTION = (
    "Find seasonality and anomalies in time_series.csv, summarize key stats, "
    "and recommend two follow-up analyses. Return concise bullets."
)
ENABLE_CODE_EXECUTION = False
WORK_DIR = "tutorials/08-autogen/tmp_run"


def build_llm_config() -> LLMConfig:
    """Return a deterministic-ish LLMConfig for the agents."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required.")

    return LLMConfig(
        {
            "model": DEFAULT_MODEL,
            "api_key": api_key,
            "temperature": 0.2,
            "max_tokens": 500,
        }
    )


def format_messages(messages: Iterable[dict[str, Any]]) -> Iterable[str]:
    """Convert AutoGen messages into readable strings."""
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            content = "\n".join(str(part) for part in content)
        speaker = message.get("name") or message.get("role")
        yield f"{speaker}: {content}"


def configure_agents(llm_config: LLMConfig) -> Tuple[AssistantAgent, AssistantAgent, AssistantAgent, UserProxyAgent]:
    """Instantiate Research, Coder, Reviewer, and the User proxy."""
    research = AssistantAgent(
        name="research_agent",
        system_message=(
            "You are a data research planner. Write short plans and call out assumptions. "
            "Do not write code. Identify columns to inspect and metrics to compute."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    coder = AssistantAgent(
        name="coder_agent",
        system_message=(
            "You are a cautious pandas/matplotlib coder. Write runnable Python code blocks. "
            "Never delete or overwrite files. Assume the CSV path is provided. "
            "Print key outputs (head, stats) and describe any plots in text."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    reviewer = AssistantAgent(
        name="reviewer_agent",
        system_message=(
            "You review code and findings. Check for correctness, safety, and whether the user "
            "question is answered. Respond with PASS or FAIL plus bullet reasons."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    user = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        description="Drives the conversation and prints messages.",
        code_execution_config={"work_dir": WORK_DIR, "use_docker": False},
    )

    return research, coder, reviewer, user


def run_step(sender: UserProxyAgent, recipient: AssistantAgent, message: str, max_turns: int = 3):
    """Run a chat step and return the RunResponse."""
    response = sender.run(
        recipient,
        message=message,
        max_turns=max_turns,
        clear_history=True,
        summary_method="last_msg",
    )
    response.process()
    return response


def transcript_to_text(messages: Iterable[dict[str, Any]]) -> str:
    """Flatten a list of message dicts into readable text."""
    return "\n".join(format_messages(messages))


def extract_python_code(text: str | None) -> str | None:
    """Pull the first ```python ... ``` block, if present."""
    if not text:
        return None
    lower = text.lower()
    start = lower.find("```python")
    if start == -1:
        return None
    end = lower.find("```", start + 3)
    if end == -1:
        return None
    # slice using original text to preserve casing
    return text[start + len("```python") : end].strip()


def execute_code_block(code: str, csv_path: str) -> Tuple[str, str]:
    """Execute generated code in a local sandbox and return stdout/stderr."""
    os.makedirs(WORK_DIR, exist_ok=True)
    stdout_buf, stderr_buf = StringIO(), StringIO()
    local_vars: dict[str, Any] = {"CSV_PATH": csv_path}
    try:
        compiled = compile(code, "<autogen-coder>", "exec")
        import contextlib

        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            exec(compiled, {}, local_vars)
    except Exception as exc:  # noqa: BLE001 - report all errors back
        stderr_buf.write(f"Execution error: {exc}")
    return stdout_buf.getvalue().strip(), stderr_buf.getvalue().strip()


def main() -> None:
    load_dotenv(override=True)
    llm_config = build_llm_config()
    research, coder, reviewer, user = configure_agents(llm_config)

    context: dict[str, Any] = {"plan": None, "code": None, "stdout": "", "stderr": ""}

    # Step 1: Research plan
    research_prompt = (
        f"Dataset path: {CSV_PATH}.\n"
        f"Question: {USER_QUESTION}\n"
        "Propose a short plan (bullets). List columns you expect and how to detect seasonality/anomalies."
    )
    research_result = run_step(user, research, research_prompt)
    context["plan"] = research_result.summary or transcript_to_text(research_result.messages)

    # Step 2: Coding based on the plan
    coder_prompt = (
        f"You will work on {CSV_PATH}.\n"
        "Here is the plan from the research agent:\n"
        f"{context['plan']}\n\n"
        "Write Python code using pandas (and matplotlib if needed) to implement the plan. "
        "Assume the file exists at CSV_PATH variable. Print outputs."
    )
    coder_result = run_step(user, coder, coder_prompt)
    coder_summary_text = coder_result.summary or transcript_to_text(coder_result.messages)
    context["code"] = extract_python_code(coder_summary_text) or coder_summary_text

    # Optional execution
    if ENABLE_CODE_EXECUTION and context["code"]:
        stdout, stderr = execute_code_block(str(context["code"]), CSV_PATH)
        context["stdout"], context["stderr"] = stdout, stderr

    # Step 3: Review the proposed code and findings
    reviewer_prompt = (
        "Review the proposed code and findings for safety and correctness.\n"
        "Rules: no file deletions, no network calls, stay in the current directory.\n"
        f"Plan:\n{context['plan']}\n\n"
        f"Code or reasoning to review:\n{context['code']}\n\n"
        f"Execution stdout:\n{context['stdout']}\n\n"
        f"Execution stderr:\n{context['stderr']}\n\n"
        "Respond with PASS or FAIL and list reasons."
    )
    reviewer_result = run_step(user, reviewer, reviewer_prompt, max_turns=2)

    # Print the full transcript for each step
    print("\n=== Research Agent Messages ===")
    for line in format_messages(research_result.messages):
        print(line)

    print("\n=== Coder Agent Messages ===")
    for line in format_messages(coder_result.messages):
        print(line)

    print("\n=== Reviewer Agent Messages ===")
    for line in format_messages(reviewer_result.messages):
        print(line)


if __name__ == "__main__":
    main()
