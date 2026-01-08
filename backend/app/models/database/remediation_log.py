"""Remediation log database model."""

from sqlalchemy import Column, String, JSON, DateTime, Float, Integer
from datetime import datetime
from app.models.database.base import TimestampedModel

class RemediationLog(TimestampedModel):
    """Remediation action log."""
    __tablename__ = "remediation_logs"
    
    action_id = Column(String, primary_key=True)
    incident_id = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    executed_by = Column(String, nullable=True)
    executed_at = Column(DateTime, nullable=True)
