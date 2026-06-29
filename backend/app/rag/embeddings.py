"""Embedding generation for semantic search.

Two backends:

* ``LocalHashingEmbedder`` (default) — a deterministic, dependency-light hashing
  embedder (bag-of-tokens hashed into a fixed-dim L2-normalised vector). It needs
  no network or model download, so RAG works fully offline and in CI. It captures
  lexical overlap well enough to retrieve the right runbook for an alert.
* ``OpenAIEmbedder`` — real semantic embeddings via the OpenAI API (used when
  ``EMBEDDING_PROVIDER=openai`` and a key is configured).

Index and query must use the same embedder; ``get_embedder()`` returns a cached
singleton chosen from settings.
"""

from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from typing import Protocol

import numpy as np
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class Embedder(Protocol):
    """Minimal embedder interface."""

    dim: int
    name: str

    def embed(self, text: str) -> list[float]: ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class LocalHashingEmbedder:
    """Deterministic hashing embedder (offline, no dependencies beyond numpy)."""

    name = "local-hashing"

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = _tokenize(text)
        if not tokens:
            return vec
        for tok in tokens:
            digest = hashlib.md5(tok.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % self.dim
            sign = 1.0 if digest[4] & 1 else -1.0
            vec[idx] += sign
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def embed(self, text: str) -> list[float]:
        return self._vector(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class OpenAIEmbedder:
    """OpenAI embeddings backend (lazy-imports the openai SDK)."""

    name = "openai"

    def __init__(self, model: str, api_key: str, base_url: str = "") -> None:
        from openai import OpenAI  # lazy import; optional at runtime

        self.model = model
        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = OpenAI(**kwargs)
        # text-embedding-3-small -> 1536 dims; recorded for bookkeeping only.
        self.dim = 1536

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]


@lru_cache
def get_embedder() -> Embedder:
    """Return the configured embedder singleton."""
    if settings.embedding_provider == "openai" and settings.openai_ready:
        try:
            logger.info("embeddings.openai", model=settings.openai_embedding_model)
            return OpenAIEmbedder(
                model=settings.openai_embedding_model,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.warning("embeddings.openai_failed", error=str(exc), fallback="local")
    return LocalHashingEmbedder(dim=settings.embedding_dim)


# Backwards-compatible alias for the original scaffold name.
EmbeddingGenerator = LocalHashingEmbedder
