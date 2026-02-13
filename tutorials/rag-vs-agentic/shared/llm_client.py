from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from shared.schemas import LLMCallRecord, LLMUsage


class LLMClient:
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0) -> None:
        load_dotenv(override=True)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for benchmarks.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def call_llm(
        self,
        messages: List[Dict[str, str]],
        call_name: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 700,
    ) -> Dict[str, Any]:
        active_model = model or self.model
        active_temp = self.temperature if temperature is None else temperature

        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=active_model,
            messages=messages,
            temperature=active_temp,
            max_tokens=max_tokens,
        )
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        usage_obj = response.usage
        usage = LLMUsage(
            prompt_tokens=getattr(usage_obj, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage_obj, "completion_tokens", 0) or 0,
            total_tokens=getattr(usage_obj, "total_tokens", 0) or 0,
        )
        text = response.choices[0].message.content or ""

        record = LLMCallRecord(
            call_name=call_name,
            model=active_model,
            latency_ms=elapsed_ms,
            usage=usage,
            prompt_preview=(messages[-1].get("content", "")[:180] if messages else ""),
        )
        return {
            "text": text.strip(),
            "usage": usage,
            "latency_ms": elapsed_ms,
            "record": record,
        }
