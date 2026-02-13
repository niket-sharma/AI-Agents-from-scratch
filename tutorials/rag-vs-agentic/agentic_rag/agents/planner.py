from __future__ import annotations

import json
from typing import Any, Dict

from shared.llm_client import LLMClient


class PlannerAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def plan(self, question: str) -> Dict[str, Any]:
        system = (
            "You are a planning agent for policy QA. Return strict JSON only. "
            "No markdown and no extra text."
        )
        user = (
            "Create a plan for answering this question.\n"
            f"Question: {question}\n\n"
            "JSON schema:\n"
            "{\n"
            '  "subquestions": ["..."],\n'
            '  "retrieval_queries": ["..."],\n'
            '  "target_docs": ["expense_policy"|"travel_policy"|"remote_work"|"procurement"|"faq"],\n'
            '  "needs_calculation": true/false,\n'
            '  "calculation_expression": "optional arithmetic expression",\n'
            '  "reasoning_notes": "short"\n'
            "}"
        )
        out = self.llm_client.call_llm(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            call_name="planner",
            temperature=0.0,
            max_tokens=500,
        )

        raw = out["text"]
        parsed: Dict[str, Any]
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            parsed = json.loads(raw[start : end + 1]) if start >= 0 and end > start else {}

        parsed.setdefault("subquestions", [question])
        parsed.setdefault("retrieval_queries", [question])
        parsed.setdefault("target_docs", [])
        parsed.setdefault("needs_calculation", False)
        parsed.setdefault("calculation_expression", "")
        parsed.setdefault("reasoning_notes", "")
        parsed["_llm"] = out
        return parsed
