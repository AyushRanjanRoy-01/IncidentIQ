"""LLM API cost tracking.

Tracks LLM API costs for cost optimization and budget management.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from app.utils.cost_tracker import LLMCostTracker, LLMProvider, cost_tracker


@dataclass
class LLMCostReport:
    """LLM cost report for a time period."""
    start_time: datetime
    end_time: datetime
    total_cost_usd: float
    total_requests: int
    total_tokens: int
    cost_by_provider: Dict[str, float]
    cost_by_model: Dict[str, float]
    metrics: List[Any] = field(default_factory=list)


class LLMCostService:
    """Service for tracking and reporting LLM costs.
    
    Provides cost tracking, reporting, and budget management
    for LLM API usage.
    """
    
    def __init__(self) -> None:
        """Initialize LLM cost service."""
        self.cost_tracker = cost_tracker
        self.budget_limit_usd: Optional[float] = None
        self.daily_budget_usd: Optional[float] = None
    
    def track_llm_call(
        self,
        provider: LLMProvider,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_id: Optional[str] = None,
    ) -> None:
        """Track an LLM API call.
        
        Args:
            provider: LLM provider
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            request_id: Optional request identifier
        """
        self.cost_tracker.track_call(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            request_id=request_id,
        )
        
        # Check budget limits
        self._check_budget_limits()
    
    def get_total_cost(self) -> float:
        """Get total cost tracked.
        
        Returns:
            Total cost in USD
        """
        return self.cost_tracker.get_total_cost()
    
    def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """Get cost for a specific day.
        
        Args:
            date: Date to check (default: today)
            
        Returns:
            Daily cost in USD
        """
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        daily_metrics = [
            m for m in self.cost_tracker.metrics
            if start_of_day <= m.timestamp < end_of_day
        ]
        
        return sum(m.cost_usd for m in daily_metrics)
    
    def generate_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> LLMCostReport:
        """Generate cost report for time period.
        
        Args:
            start_time: Report start time (default: beginning of tracking)
            end_time: Report end time (default: now)
            
        Returns:
            Cost report object
        """
        if end_time is None:
            end_time = datetime.now()
        
        if start_time is None:
            if self.cost_tracker.metrics:
                start_time = min(m.timestamp for m in self.cost_tracker.metrics)
            else:
                start_time = end_time
        
        period_metrics = [
            m for m in self.cost_tracker.metrics
            if start_time <= m.timestamp <= end_time
        ]
        
        total_cost = sum(m.cost_usd for m in period_metrics)
        total_requests = len(period_metrics)
        total_tokens = sum(m.total_tokens for m in period_metrics)
        
        cost_by_provider: Dict[str, float] = {}
        cost_by_model: Dict[str, float] = {}
        
        for metric in period_metrics:
            provider = metric.provider.value
            cost_by_provider[provider] = (
                cost_by_provider.get(provider, 0.0) + metric.cost_usd
            )
            
            model_key = f"{provider}:{metric.model}"
            cost_by_model[model_key] = (
                cost_by_model.get(model_key, 0.0) + metric.cost_usd
            )
        
        return LLMCostReport(
            start_time=start_time,
            end_time=end_time,
            total_cost_usd=total_cost,
            total_requests=total_requests,
            total_tokens=total_tokens,
            cost_by_provider=cost_by_provider,
            cost_by_model=cost_by_model,
            metrics=period_metrics,
        )
    
    def set_budget_limit(self, limit_usd: float) -> None:
        """Set total budget limit.
        
        Args:
            limit_usd: Budget limit in USD
        """
        self.budget_limit_usd = limit_usd
    
    def set_daily_budget(self, daily_limit_usd: float) -> None:
        """Set daily budget limit.
        
        Args:
            daily_limit_usd: Daily budget limit in USD
        """
        self.daily_budget_usd = daily_limit_usd
    
    def _check_budget_limits(self) -> None:
        """Check if budget limits are exceeded."""
        # TODO: Implement budget checking and alerting
        if self.budget_limit_usd:
            total_cost = self.get_total_cost()
            if total_cost >= self.budget_limit_usd:
                # TODO: Send alert or raise exception
                pass
        
        if self.daily_budget_usd:
            daily_cost = self.get_daily_cost()
            if daily_cost >= self.daily_budget_usd:
                # TODO: Send alert or raise exception
                pass


# Global LLM cost service instance
_llm_cost_service: Optional[LLMCostService] = None


def get_llm_cost_service() -> LLMCostService:
    """Get global LLM cost service instance.
    
    Returns:
        LLM cost service instance
    """
    global _llm_cost_service
    if _llm_cost_service is None:
        _llm_cost_service = LLMCostService()
    return _llm_cost_service

