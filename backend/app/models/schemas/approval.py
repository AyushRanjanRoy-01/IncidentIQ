"""Approval request/response schemas."""

from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class ApprovalRequestCreate(BaseModel):
    """Schema for creating approval request."""
    action_id: str
    action_description: str
    rca_summary: str
    confidence: float

class ApprovalRequestResponse(BaseModel):
    """Schema for approval request response."""
    request_id: str
    action_id: str
    status: str
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
