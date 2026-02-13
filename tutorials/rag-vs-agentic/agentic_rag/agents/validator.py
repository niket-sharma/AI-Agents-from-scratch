from __future__ import annotations

import json
from typing import Any, Dict, List

from shared.llm_client import LLMClient
from shared.schemas import RetrievedChunk


class ValidatorAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def validate(
        self,
        question: str,
        draft_answer: str,
        claims: List[Dict[str, Any]],
        retrieved: List[RetrievedChunk],
    ) -> Dict[str, Any]:
        context = []
        for item in retrieved:
            context.append(f"{item.chunk.chunk_id}: {item.chunk.text}")

        system = "You are a strict validator. Return strict JSON only."
        user = (
            f"Question: {question}\n\n"
            f"Draft answer: {draft_answer}\n\n"
            f"Claims JSON: {json.dumps(claims)}\n\n"
            "Retrieved context:\n"
            + "\n\n".join(context)
            + "\n\nReturn JSON schema:\n"
            "{\n"
            '  "status": "pass" | "needs_more_context",\n'
            '  "issues": ["..."],\n'
            '  "refined_query": "optional retrieval query"\n'
            "}"
        )

        out = self.llm_client.call_llm(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            call_name="validator",
            temperature=0.0,
            max_tokens=350,
        )

        raw = out["text"]
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            parsed = json.loads(raw[start : end + 1]) if start >= 0 and end > start else {}

        parsed.setdefault("status", "pass")
        parsed.setdefault("issues", [])
        parsed.setdefault("refined_query", "")
        parsed["_llm"] = out
        return parsed
