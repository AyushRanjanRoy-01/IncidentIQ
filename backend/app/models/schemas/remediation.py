"""Remediation request/response schemas."""

from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class RemediationActionBase(BaseModel):
    """Base remediation action schema."""
    action_type: str
    description: str
    confidence: float

class RemediationActionCreate(RemediationActionBase):
    """Schema for creating remediation action."""
    incident_id: str
    parameters: Dict[str, Any]

class RemediationActionResponse(RemediationActionBase):
    """Schema for remediation action response."""
    action_id: str
    status: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
