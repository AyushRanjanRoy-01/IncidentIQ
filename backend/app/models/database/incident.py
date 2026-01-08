"""Incident database model."""

from sqlalchemy import Column, String, JSON, DateTime, Integer, ForeignKey
from datetime import datetime
from app.models.database.base import TimestampedModel

class Incident(TimestampedModel):
    """Incident database model."""
    __tablename__ = "incidents"
    
    incident_id = Column(String, primary_key=True)
    service = Column(String, nullable=False, index=True)
    incident_type = Column(String, nullable=False)
    status = Column(String, default="open", nullable=False, index=True)
    rca_summary = Column(JSON, nullable=True)
    root_cause = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # TODO: Add relationships
