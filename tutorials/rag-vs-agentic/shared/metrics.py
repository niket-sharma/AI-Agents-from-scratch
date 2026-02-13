from __future__ import annotations

import re
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Optional


CITATION_RE = re.compile(r"\[([a-zA-Z0-9_\-]+)\|([a-zA-Z0-9_\-]+)\]")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def extract_citations(answer: str) -> List[Dict[str, str]]:
    found = []
    for doc, chunk_id in CITATION_RE.findall(answer or ""):
        found.append({"doc": doc, "chunk_id": chunk_id})
    return found


def parse_first_number(text: str) -> Optional[float]:
    match = NUMBER_RE.search(text or "")
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def evaluate_quality(
    answer: str,
    citations: List[Dict[str, str]],
    retrieved_chunk_ids: List[str],
    expected_numeric: Optional[float],
    tolerance: float,
    validator_status: Optional[str] = None,
    expected_keywords_any: Optional[List[str]] = None,
    expected_keywords_all: Optional[List[str]] = None,
    forbidden_keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    expected_keywords_any = expected_keywords_any or []
    expected_keywords_all = expected_keywords_all or []
    forbidden_keywords = forbidden_keywords or []

    has_citation = len(citations) > 0
    retrieved_set = set(retrieved_chunk_ids)
    cited_exist = all(c["chunk_id"] in retrieved_set for c in citations) if citations else False

    numeric_match = None
    extracted_numeric = parse_first_number(answer)
    if expected_numeric is not None:
        if extracted_numeric is None:
            numeric_match = False
        else:
            numeric_match = abs(extracted_numeric - expected_numeric) <= tolerance

    answer_lc = (answer or "").lower()
    keywords_any_match = None
    if expected_keywords_any:
        keywords_any_match = any(term.lower() in answer_lc for term in expected_keywords_any)

    keywords_all_match = None
    if expected_keywords_all:
        keywords_all_match = all(term.lower() in answer_lc for term in expected_keywords_all)

    forbidden_keywords_present = None
    if forbidden_keywords:
        forbidden_keywords_present = any(term.lower() in answer_lc for term in forbidden_keywords)

    textual_match = None
    textual_checks: List[bool] = []
    if keywords_any_match is not None:
        textual_checks.append(keywords_any_match)
    if keywords_all_match is not None:
        textual_checks.append(keywords_all_match)
    if forbidden_keywords_present is not None:
        textual_checks.append(not forbidden_keywords_present)
    if textual_checks:
        textual_match = all(textual_checks)

    validator_pass = validator_status in {None, "pass"}
    checks = [has_citation, cited_exist, validator_pass]
    if numeric_match is not None:
        checks.append(bool(numeric_match))

    task_correct_checks: List[bool] = []
    if numeric_match is not None:
        task_correct_checks.append(bool(numeric_match))
    if textual_match is not None:
        task_correct_checks.append(bool(textual_match))
    task_correct = all(task_correct_checks) if task_correct_checks else None

    score = sum(1 for c in checks if c) / len(checks) if checks else 0.0

    return {
        "has_citation": has_citation,
        "cited_documents_exist_in_retrieved": cited_exist,
        "expected_numeric": expected_numeric,
        "extracted_numeric": extracted_numeric,
        "numeric_match": numeric_match,
        "keywords_any_match": keywords_any_match,
        "keywords_all_match": keywords_all_match,
        "forbidden_keywords_present": forbidden_keywords_present,
        "textual_match": textual_match,
        "task_correct": task_correct,
        "validator_pass": validator_pass,
        "quality_proxy_score": round(score, 3),
    }


def summarize_runs(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(records)
    if not rows:
        return {}

    def _safe_avg(values: List[float]) -> float:
        return round(mean(values), 2) if values else 0.0

    def _safe_median(values: List[float]) -> float:
        return round(median(values), 2) if values else 0.0

    token_totals = [r["usage_totals"]["total_tokens"] for r in rows]
    prompt_totals = [r["usage_totals"]["prompt_tokens"] for r in rows]
    completion_totals = [r["usage_totals"]["completion_tokens"] for r in rows]
    latency = [r["latency_ms_total"] for r in rows]
    llm_calls = [r["num_llm_calls"] for r in rows]
    task_scores = [
        r.get("quality_checks", {}).get("task_correct")
        for r in rows
        if r.get("quality_checks", {}).get("task_correct") is not None
    ]

    failures = 0
    for row in rows:
        checks = row.get("quality_checks", {})
        no_citation = not checks.get("has_citation", False)
        validator_failed = not checks.get("validator_pass", True)
        if no_citation or validator_failed:
            failures += 1

    task_correct_count = sum(1 for x in task_scores if bool(x))
    tokens_per_correct_answer = (
        round(sum(token_totals) / task_correct_count, 2) if task_correct_count > 0 else None
    )

    return {
        "count": len(rows),
        "avg_total_tokens": _safe_avg(token_totals),
        "median_total_tokens": _safe_median(token_totals),
        "avg_prompt_tokens": _safe_avg(prompt_totals),
        "avg_completion_tokens": _safe_avg(completion_totals),
        "avg_latency_ms": _safe_avg(latency),
        "median_latency_ms": _safe_median(latency),
        "avg_llm_calls": _safe_avg(llm_calls),
        "failure_rate": round(failures / len(rows), 3),
        "task_accuracy": round(task_correct_count / len(task_scores), 3) if task_scores else None,
        "tokens_per_correct_answer": tokens_per_correct_answer,
        "avg_quality_proxy_score": round(
            mean([r.get("quality_checks", {}).get("quality_proxy_score", 0.0) for r in rows]),
            3,
        ),
    }
