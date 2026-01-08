"""Alert request/response schemas."""

from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AlertBase(BaseModel):
    """Base alert schema."""
    service: str
    alert_type: str
    severity: str
    metric_name: str
    metric_value: float
    threshold: float
    labels: Dict[str, str]

class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    pass

class AlertResponse(AlertBase):
    """Schema for alert response."""
    alert_id: str
    timestamp: datetime
    status: str
    
    class Config:
        from_attributes = True
