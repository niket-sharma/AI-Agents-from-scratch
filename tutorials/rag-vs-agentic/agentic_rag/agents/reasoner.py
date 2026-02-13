from __future__ import annotations

import json
from typing import Any, Dict, List

from shared.llm_client import LLMClient
from shared.schemas import RetrievedChunk


class ReasonerAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def reason(
        self,
        question: str,
        plan: Dict[str, Any],
        retrieved: List[RetrievedChunk],
        tool_result: str | None = None,
    ) -> Dict[str, Any]:
        excerpts = []
        for item in retrieved:
            excerpts.append(
                f"[{item.chunk.doc_name}|{item.chunk.chunk_id}] "
                f"section={item.chunk.section}\n{item.chunk.text}"
            )

        system = "You are a policy reasoner. Return strict JSON only."
        user = (
            f"Question: {question}\n\n"
            f"Plan: {json.dumps({k: v for k, v in plan.items() if not k.startswith('_')})}\n\n"
            f"Tool result: {tool_result or 'none'}\n\n"
            "Retrieved excerpts:\n"
            + "\n\n".join(excerpts)
            + "\n\nReturn JSON with schema:\n"
            "{\n"
            '  "draft_answer": "...",\n'
            '  "claims": [{"text": "...", "citation_ids": ["chunk_id"]}],\n'
            '  "needs_calculation": true/false,\n'
            '  "calculation_expression": "optional",\n'
            '  "missing_context": "optional short note"\n'
            "}"
        )

        out = self.llm_client.call_llm(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            call_name="reasoner",
            temperature=0.0,
            max_tokens=700,
        )

        raw = out["text"]
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            parsed = json.loads(raw[start : end + 1]) if start >= 0 and end > start else {}

        parsed.setdefault("draft_answer", raw)
        parsed.setdefault("claims", [])
        parsed.setdefault("needs_calculation", False)
        parsed.setdefault("calculation_expression", "")
        parsed.setdefault("missing_context", "")
        parsed["_llm"] = out
        return parsed
