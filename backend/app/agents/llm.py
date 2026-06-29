"""LLM provider abstraction for the agent pipeline.

``get_llm_provider()`` returns an OpenAI-backed provider when an API key is
configured, otherwise a deterministic mock provider so the platform runs fully
offline. The RCA agent gates real LLM calls on ``provider.available`` and falls
back to a deterministic, runbook-grounded synthesis when no LLM is present.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class LLMResult:
    content: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


def _extract_json(text: str) -> dict:
    """Best-effort parse of a JSON object from an LLM response."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return {}


class LLMProvider(ABC):
    name: str = "base"
    available: bool = False

    @abstractmethod
    def complete(self, system: str, user: str) -> LLMResult: ...

    def complete_json(self, system: str, user: str) -> tuple[dict, LLMResult]:
        result = self.complete(system, user)
        return _extract_json(result.content), result


class MockLLMProvider(LLMProvider):
    """No-op provider used when no LLM is configured (offline mode)."""

    name = "mock"
    available = False

    def complete(self, system: str, user: str) -> LLMResult:
        return LLMResult(content="{}", model="mock", provider="mock")


class OpenAILLMProvider(LLMProvider):
    """OpenAI Chat Completions backend (lazy-imports the openai SDK)."""

    name = "openai"
    available = True

    def __init__(self, model: str, api_key: str, base_url: str = "") -> None:
        from openai import OpenAI  # lazy import; optional at runtime

        self.model = model
        kwargs: dict = {"api_key": api_key, "timeout": settings.llm_timeout_seconds}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = OpenAI(**kwargs)

    def complete(self, system: str, user: str) -> LLMResult:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        common = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
        }
        try:
            resp = self._client.chat.completions.create(
                response_format={"type": "json_object"}, **common
            )
        except Exception as exc:
            # Some OpenAI-compatible servers reject response_format; retry plain.
            logger.warning("llm.json_mode_unavailable", error=str(exc))
            resp = self._client.chat.completions.create(**common)

        usage = getattr(resp, "usage", None)
        return LLMResult(
            content=resp.choices[0].message.content or "",
            model=self.model,
            provider="openai",
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
        )


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider singleton."""
    provider = settings.llm_provider
    if provider == "mock":
        logger.info("llm.provider", provider="mock", reason="configured")
        return MockLLMProvider()
    if provider in ("auto", "openai") and settings.openai_ready:
        try:
            logger.info("llm.provider", provider="openai", model=settings.llm_model)
            return OpenAILLMProvider(
                model=settings.llm_model,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.warning("llm.openai_init_failed", error=str(exc), fallback="mock")
    if provider == "openai":
        logger.warning("llm.openai_unconfigured", fallback="mock")
    logger.info("llm.provider", provider="mock", reason="no api key")
    return MockLLMProvider()
