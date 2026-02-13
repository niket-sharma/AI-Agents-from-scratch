from __future__ import annotations

from pathlib import Path
from typing import List

from shared.schemas import Chunk


def _split_text(text: str, max_chars: int) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    buffer = ""

    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
        if len(candidate) <= max_chars:
            buffer = candidate
        else:
            if buffer:
                chunks.append(buffer)
            if len(paragraph) <= max_chars:
                buffer = paragraph
            else:
                for i in range(0, len(paragraph), max_chars):
                    chunks.append(paragraph[i : i + max_chars])
                buffer = ""

    if buffer:
        chunks.append(buffer)
    return chunks


def chunk_markdown(doc_name: str, text: str, max_chars: int = 650) -> List[Chunk]:
    lines = text.splitlines()
    sections: List[tuple[str, str]] = []
    current_heading = "Overview"
    current_body: List[str] = []

    for line in lines:
        if line.startswith("#"):
            if current_body:
                sections.append((current_heading, "\n".join(current_body).strip()))
                current_body = []
            current_heading = line.lstrip("#").strip()
        else:
            current_body.append(line)

    if current_body:
        sections.append((current_heading, "\n".join(current_body).strip()))

    chunks: List[Chunk] = []
    idx = 0
    for section_name, body in sections:
        for piece in _split_text(body, max_chars=max_chars):
            idx += 1
            chunks.append(
                Chunk(
                    chunk_id=f"{doc_name}_chunk_{idx}",
                    doc_name=doc_name,
                    section=section_name,
                    text=piece,
                )
            )
    return chunks


def load_policy_chunks(data_dir: Path, max_chars: int = 650) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    for path in sorted((data_dir / "policies").glob("*.md")):
        doc_name = path.stem
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(chunk_markdown(doc_name=doc_name, text=text, max_chars=max_chars))
    return all_chunks
