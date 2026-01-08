"""Infrastructure cost tracking.

Tracks infrastructure costs for cloud resources to enable
cost optimization and FinOps practices.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class ResourceType(Enum):
    """Infrastructure resource types."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    MONITORING = "monitoring"


@dataclass
class InfrastructureCost:
    """Infrastructure cost record."""
    resource_type: ResourceType
    resource_id: str
    resource_name: str
    cost_usd: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    region: Optional[str] = None


class InfrastructureCostTracker:
    """Tracks infrastructure costs for cloud resources.
    
    Provides cost tracking and reporting for infrastructure
    resources to enable FinOps practices.
    """
    
    def __init__(self) -> None:
        """Initialize infrastructure cost tracker."""
        self.costs: List[InfrastructureCost] = []
        self.total_cost_usd = 0.0
    
    def track_cost(
        self,
        resource_type: ResourceType,
        resource_id: str,
        resource_name: str,
        cost_usd: float,
        tags: Optional[Dict[str, str]] = None,
        region: Optional[str] = None,
    ) -> None:
        """Track infrastructure cost.
        
        Args:
            resource_type: Type of resource
            resource_id: Unique resource identifier
            resource_name: Human-readable resource name
            cost_usd: Cost in USD
            tags: Optional resource tags
            region: Optional AWS/GCP region
        """
        cost_record = InfrastructureCost(
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            cost_usd=cost_usd,
            tags=tags or {},
            region=region,
        )
        
        self.costs.append(cost_record)
        self.total_cost_usd += cost_usd
    
    def get_total_cost(self) -> float:
        """Get total infrastructure cost.
        
        Returns:
            Total cost in USD
        """
        return self.total_cost_usd
    
    def get_cost_by_type(self) -> Dict[str, float]:
        """Get cost breakdown by resource type.
        
        Returns:
            Dictionary mapping resource type to total cost
        """
        breakdown: Dict[str, float] = {}
        for cost in self.costs:
            resource_type = cost.resource_type.value
            breakdown[resource_type] = (
                breakdown.get(resource_type, 0.0) + cost.cost_usd
            )
        return breakdown
    
    def get_cost_by_region(self) -> Dict[str, float]:
        """Get cost breakdown by region.
        
        Returns:
            Dictionary mapping region to total cost
        """
        breakdown: Dict[str, float] = {}
        for cost in self.costs:
            region = cost.region or "unknown"
            breakdown[region] = breakdown.get(region, 0.0) + cost.cost_usd
        return breakdown
    
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
        
        daily_costs = [
            c for c in self.costs
            if start_of_day <= c.timestamp < end_of_day
        ]
        
        return sum(c.cost_usd for c in daily_costs)
    
    def get_cost_by_tag(self, tag_key: str) -> Dict[str, float]:
        """Get cost breakdown by tag value.
        
        Args:
            tag_key: Tag key to group by
            
        Returns:
            Dictionary mapping tag value to total cost
        """
        breakdown: Dict[str, float] = {}
        for cost in self.costs:
            tag_value = cost.tags.get(tag_key, "untagged")
            breakdown[tag_value] = breakdown.get(tag_value, 0.0) + cost.cost_usd
        return breakdown
    
    def reset(self) -> None:
        """Reset all tracked costs."""
        self.costs.clear()
        self.total_cost_usd = 0.0


# Global infrastructure cost tracker instance
_infrastructure_cost_tracker: Optional[InfrastructureCostTracker] = None


def get_infrastructure_cost_tracker() -> InfrastructureCostTracker:
    """Get global infrastructure cost tracker instance.
    
    Returns:
        Infrastructure cost tracker instance
    """
    global _infrastructure_cost_tracker
    if _infrastructure_cost_tracker is None:
        _infrastructure_cost_tracker = InfrastructureCostTracker()
    return _infrastructure_cost_tracker

