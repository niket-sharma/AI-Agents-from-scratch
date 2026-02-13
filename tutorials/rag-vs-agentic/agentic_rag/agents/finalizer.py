from __future__ import annotations

from typing import Any, Dict, List

from shared.llm_client import LLMClient


class FinalizerAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def finalize(
        self,
        question: str,
        draft_answer: str,
        claims: List[Dict[str, Any]],
        validator_issues: List[str],
    ) -> Dict[str, Any]:
        system = (
            "You produce concise policy answers with explicit citations in format [doc|chunk_id]. "
            "Do not invent facts and keep output clean for end users."
        )
        user = (
            f"Question: {question}\n\n"
            f"Draft answer: {draft_answer}\n\n"
            f"Claims: {claims}\n\n"
            f"Validator issues: {validator_issues}\n\n"
            "Return final answer text only."
        )

        out = self.llm_client.call_llm(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            call_name="finalizer",
            temperature=0.0,
            max_tokens=500,
        )
        return {"text": out["text"], "_llm": out}
