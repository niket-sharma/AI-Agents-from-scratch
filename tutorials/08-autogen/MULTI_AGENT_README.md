# Building a Multi-Agent Research & Coding Assistant with AutoGen

A guided outline to build a practical research + coding assistant using AutoGen/AG2. You will wire three collaborating agents (ResearchAgent, CoderAgent, Reviewer) and orchestrate them end-to-end on a sample dataset (`time_series.csv`).

## Prereqs & Setup
- Python 3.11+ and `pip install -r requirements.txt` (AutoGen is included).
- Set `OPENAI_API_KEY` in `.env` (or export it).
- Place `time_series.csv` in the project root (or adjust the path in the orchestration script).
- Familiarity: basic Python, pandas, and how to read CSVs.

## Minimal 2-agent example
Goal: show the smallest working multi-agent chat.
- Agents: `AssistantAgent` (analysis) + `UserProxyAgent` (driver).
- Flow: user proxy sends a research question; assistant replies with a short plan + answer.
- Key APIs: `LLMConfig`, `AssistantAgent`, `UserProxyAgent.run`, `RunResponse.process()`.
- Deliverable: a 40–50 line script you can run before scaling up.

## System design: ResearchAgent + CoderAgent + Reviewer
- **ResearchAgent**: reads the problem context, drafts an analysis plan, and proposes code tasks.
- **CoderAgent**: writes executable Python (pandas, matplotlib) to implement the plan.
- **Reviewer**: sanity-checks outputs and catches unsafe file operations or hallucinations.
- Message flow: Research -> Coder -> Reviewer -> final report. Optionally loop if Reviewer requests fixes.
- State: pass along the latest code, stderr/stdout snippets, and a short summary at each hop.

## Implementing agents
- Configure `LLMConfig` (model, temperature, max_tokens) for deterministic runs.
- Define system prompts:
  - ResearchAgent: “produce plans, cite assumptions, avoid code.”
  - CoderAgent: “write runnable Python; prefer pure pandas; print sample outputs; never delete files.”
  - Reviewer: “check for correctness, safety, and alignment with the request; respond with PASS/FAIL + reasons.”
- Enable/disable code execution: keep `human_input_mode="NEVER"` for automation; optionally allow code execution via `code_execution_config`.
- Optional: register lightweight tools (e.g., schema inspection for the CSV) if desired.

## Orchestrating a full run on `time_series.csv`
- Input: a user question, e.g., “Find seasonality and anomaly points in `time_series.csv`; produce a short text summary and suggest two follow-up analyses.”
- Pipeline outline:
  1) ResearchAgent reads the request and emits a plan + intended columns/aggregations.
  2) CoderAgent generates Python to load `time_series.csv`, do EDA (stats, plots, anomalies), and print findings.
  3) Execute code (locally or via the user proxy), capture stdout/stderr.
  4) Reviewer inspects outputs/errors and either approves or asks CoderAgent for fixes.
  5) Return a final summary + recommended code snippet to the user.
- Implementation sketch:
  - Use `UserProxyAgent.run` with a scripted loop to append outputs/errors into the next message.
  - Maintain a small context dict: `{"plan": ..., "code": ..., "stdout": ..., "stderr": ...}`.
  - Limit `max_turns` to prevent runaway loops.

## Guardrails & debugging
- Safety prompts: forbid deletion/mutation outside the tutorial directory; require confirmation before writing files.
- Execution sandbox: set `code_execution_config={"work_dir": "tutorials/08-autogen/tmp", "use_docker": False}` (or True if Docker available).
- Determinism: lower `temperature`, cap `max_tokens`, and log all messages to a file.
- Debug tips: inspect `RunResponse.messages`, print intermediate summaries, and surface any stderr back to the Reviewer.

## Extensions & exercises
1) Add a **DataInspector tool** that lists columns/dtypes before coding.
2) Add a **PlotReviewer** agent that only checks plot descriptions (no code changes).
3) Swap models (e.g., `FAST_MODEL` for quick passes, higher-accuracy model for final review).
4) Add retry logic: on Reviewer FAIL, loop CoderAgent with the Reviewer’s notes once.
5) Persist reports: have Reviewer write `report.md` with the final summary + code block.
6) Turn this into a CLI: accept `--question` and `--csv path` flags to run the pipeline end-to-end.
