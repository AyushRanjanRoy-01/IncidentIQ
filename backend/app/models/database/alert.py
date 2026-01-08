"""Alert database model."""

from sqlalchemy import Column, String, Float, JSON, DateTime, Integer
from datetime import datetime
from app.models.database.base import TimestampedModel

class Alert(TimestampedModel):
    """Alert database model."""
    __tablename__ = "alerts"
    
    alert_id = Column(String, primary_key=True)
    service = Column(String, nullable=False, index=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    labels = Column(JSON, nullable=True)
    status = Column(String, default="open", nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # TODO: Add relationship to incidents table
