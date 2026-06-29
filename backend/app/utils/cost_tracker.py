"""LLM cost tracking utilities.

Tracks and calculates costs for LLM API calls to enable
cost-aware decision making and budget management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"


@dataclass
class LLMCostMetrics:
    """LLM cost metrics for a single call."""

    provider: LLMProvider
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str | None = None


class LLMCostTracker:
    """Tracks LLM API costs for cost optimization.

    Calculates costs based on provider pricing and token usage.
    Supports cost tracking, budgeting, and cost-aware routing.
    """

    # Pricing per 1M tokens (as of 2024, update as needed)
    PRICING: dict[str, dict[str, dict[str, float]]] = {
        "openai": {
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        },
        "anthropic": {
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
        },
    }

    def __init__(self) -> None:
        """Initialize cost tracker."""
        self.metrics: list[LLMCostMetrics] = []
        self.total_cost_usd = 0.0

    def calculate_cost(
        self,
        provider: LLMProvider,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost for LLM API call.

        Args:
            provider: LLM provider
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        provider_name = provider.value
        if provider_name not in self.PRICING:
            # TODO: Log warning for unknown provider
            return 0.0

        if model not in self.PRICING[provider_name]:
            # TODO: Log warning for unknown model, use default pricing
            return 0.0

        pricing = self.PRICING[provider_name][model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def track_call(
        self,
        provider: LLMProvider,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_id: str | None = None,
    ) -> LLMCostMetrics:
        """Track an LLM API call and calculate cost.

        Args:
            provider: LLM provider
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            request_id: Optional request identifier

        Returns:
            Cost metrics object
        """
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)

        metrics = LLMCostMetrics(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            request_id=request_id,
        )

        self.metrics.append(metrics)
        self.total_cost_usd += cost

        return metrics

    def get_total_cost(self) -> float:
        """Get total cost tracked.

        Returns:
            Total cost in USD
        """
        return self.total_cost_usd

    def get_cost_by_provider(self) -> dict[str, float]:
        """Get cost breakdown by provider.

        Returns:
            Dictionary mapping provider to total cost
        """
        breakdown: dict[str, float] = {}
        for metric in self.metrics:
            provider = metric.provider.value
            breakdown[provider] = breakdown.get(provider, 0.0) + metric.cost_usd
        return breakdown

    def get_cost_by_model(self) -> dict[str, float]:
        """Get cost breakdown by model.

        Returns:
            Dictionary mapping model to total cost
        """
        breakdown: dict[str, float] = {}
        for metric in self.metrics:
            model_key = f"{metric.provider.value}:{metric.model}"
            breakdown[model_key] = breakdown.get(model_key, 0.0) + metric.cost_usd
        return breakdown

    def reset(self) -> None:
        """Reset all tracked costs."""
        self.metrics.clear()
        self.total_cost_usd = 0.0


# Global cost tracker instance
cost_tracker = LLMCostTracker()
