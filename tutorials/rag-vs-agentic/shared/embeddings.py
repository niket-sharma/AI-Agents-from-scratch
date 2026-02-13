from __future__ import annotations

import math
import re
from collections import Counter
from typing import Counter as CounterType


TOKEN_RE = re.compile(r"[a-zA-Z0-9_.$]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def embed_text(text: str) -> CounterType[str]:
    return Counter(tokenize(text))


def cosine_similarity(a: CounterType[str], b: CounterType[str]) -> float:
    dot = 0.0
    for token, weight in a.items():
        dot += weight * b.get(token, 0)
    if dot == 0:
        return 0.0

    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
