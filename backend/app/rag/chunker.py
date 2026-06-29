"""Document chunking for RAG ingestion.

Splits documents into overlapping word-windows. Markdown is chunked
section-by-section (using ``#`` headings) so each chunk stays topically coherent,
then long sections are further split with overlap to bound chunk size.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    content: str
    index: int
    meta: dict[str, Any] = field(default_factory=dict)


class DocumentChunker:
    """Splits documents into semantic chunks (word-based, with overlap)."""

    def __init__(self, chunk_size: int = 180, overlap: int = 40) -> None:
        """Args are measured in words (not tokens) to stay dependency-free."""
        self.chunk_size = chunk_size
        self.overlap = max(0, min(overlap, chunk_size - 1))

    def _split_words(self, text: str, base_index: int, meta: dict[str, Any]) -> list[Chunk]:
        words = text.split()
        if not words:
            return []
        if len(words) <= self.chunk_size:
            return [Chunk(content=text.strip(), index=base_index, meta=dict(meta))]
        chunks: list[Chunk] = []
        step = self.chunk_size - self.overlap
        idx = base_index
        for start in range(0, len(words), step):
            window = words[start : start + self.chunk_size]
            if not window:
                break
            chunks.append(Chunk(content=" ".join(window), index=idx, meta=dict(meta)))
            idx += 1
            if start + self.chunk_size >= len(words):
                break
        return chunks

    def chunk_text(self, text: str, meta: dict[str, Any] | None = None) -> list[Chunk]:
        return self._split_words(text, 0, meta or {})

    def chunk_markdown(self, markdown: str, meta: dict[str, Any] | None = None) -> list[Chunk]:
        """Chunk markdown by heading sections, preserving the section title."""
        meta = meta or {}
        lines = markdown.splitlines()
        sections: list[tuple[str, list[str]]] = []
        current_title = meta.get("title", "Document")
        current_body: list[str] = []
        heading_re = re.compile(r"^(#{1,6})\s+(.*)$")

        for line in lines:
            m = heading_re.match(line)
            if m:
                if current_body:
                    sections.append((current_title, current_body))
                current_title = m.group(2).strip()
                current_body = []
            else:
                current_body.append(line)
        if current_body:
            sections.append((current_title, current_body))

        chunks: list[Chunk] = []
        idx = 0
        for title, body in sections:
            body_text = "\n".join(body).strip()
            if not body_text:
                continue
            section_text = f"{title}\n{body_text}"
            section_meta = {**meta, "section": title}
            for chunk in self._split_words(section_text, idx, section_meta):
                chunks.append(chunk)
                idx += 1
        # Fallback: no headings found -> plain word chunks.
        if not chunks:
            return self.chunk_text(markdown, meta)
        return chunks
