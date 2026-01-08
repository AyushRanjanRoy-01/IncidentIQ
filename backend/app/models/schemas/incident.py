"""Incident request/response schemas."""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class IncidentBase(BaseModel):
    """Base incident schema."""
    service: str
    incident_type: str
    status: str = "open"

class IncidentCreate(IncidentBase):
    """Schema for creating an incident."""
    alert_ids: List[str]

class IncidentResponse(IncidentBase):
    """Schema for incident response."""
    incident_id: str
    created_at: datetime
    rca_summary: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
