from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Chunk:
    chunk_id: str
    doc_name: str
    section: str
    text: str


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


@dataclass
class LLMUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class LLMCallRecord:
    call_name: str
    model: str
    latency_ms: int
    usage: LLMUsage
    prompt_preview: str


@dataclass
class BenchmarkQuestion:
    query_id: str
    query_text: str
    expected_numeric: Optional[float] = None
    tolerance: float = 0.01
    expected_keywords_any: List[str] = field(default_factory=list)
    expected_keywords_all: List[str] = field(default_factory=list)
    forbidden_keywords: List[str] = field(default_factory=list)


@dataclass
class RunResult:
    query_id: str
    query_text: str
    workflow_type: str
    num_llm_calls: int
    llm_calls: List[LLMCallRecord] = field(default_factory=list)
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms_total: int = 0
    citations_used: List[Dict[str, str]] = field(default_factory=list)
    retrieved_chunk_ids: List[str] = field(default_factory=list)
    final_answer: str = ""
    validator_status: Optional[str] = None
    validator_notes: Optional[str] = None
    quality_checks: Dict[str, Any] = field(default_factory=dict)

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "workflow_type": self.workflow_type,
            "num_llm_calls": self.num_llm_calls,
            "llm_calls": [
                {
                    "call_name": c.call_name,
                    "model": c.model,
                    "latency_ms": c.latency_ms,
                    "usage": {
                        "prompt_tokens": c.usage.prompt_tokens,
                        "completion_tokens": c.usage.completion_tokens,
                        "total_tokens": c.usage.total_tokens,
                    },
                    "prompt_preview": c.prompt_preview,
                }
                for c in self.llm_calls
            ],
            "usage_totals": {
                "prompt_tokens": self.total_prompt_tokens,
                "completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_tokens,
            },
            "latency_ms_total": self.latency_ms_total,
            "citations_used": self.citations_used,
            "retrieved_chunk_ids": self.retrieved_chunk_ids,
            "final_answer": self.final_answer,
            "validator_status": self.validator_status,
            "validator_notes": self.validator_notes,
            "quality_checks": self.quality_checks,
        }
