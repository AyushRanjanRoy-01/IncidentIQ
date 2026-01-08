"""Event schema definitions.

Defines event schemas for Avro/JSON Schema validation
and type safety.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """Event type enumerations."""
    # Incident events
    INCIDENT_CREATED = "incident.created"
    INCIDENT_UPDATED = "incident.updated"
    INCIDENT_RESOLVED = "incident.resolved"
    INCIDENT_ESCALATED = "incident.escalated"
    
    # Alert events
    ALERT_CREATED = "alert.created"
    ALERT_CORRELATED = "alert.correlated"
    ALERT_RESOLVED = "alert.resolved"
    
    # Remediation events
    REMEDIATION_STARTED = "remediation.started"
    REMEDIATION_APPROVED = "remediation.approved"
    REMEDIATION_REJECTED = "remediation.rejected"
    REMEDIATION_EXECUTED = "remediation.executed"
    REMEDIATION_COMPLETED = "remediation.completed"
    REMEDIATION_FAILED = "remediation.failed"


class BaseEvent(BaseModel):
    """Base event schema."""
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_id: str
    source: str = "ai-sre-platform"
    version: str = "1.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentEvent(BaseEvent):
    """Incident-related event schema."""
    incident_id: str
    incident_status: str
    severity: Optional[str] = None
    service: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class AlertEvent(BaseEvent):
    """Alert-related event schema."""
    alert_id: str
    alert_severity: str
    metric_name: Optional[str] = None
    service: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class RemediationEvent(BaseEvent):
    """Remediation-related event schema."""
    remediation_id: str
    remediation_type: str
    incident_id: Optional[str] = None
    status: str
    action: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


def validate_event(event_data: Dict[str, Any]) -> BaseEvent:
    """Validate event data against schema.
    
    Args:
        event_data: Event data dictionary
        
    Returns:
        Validated event object
        
    Raises:
        ValueError: If event validation fails
    """
    event_type = EventType(event_data.get("event_type"))
    
    if event_type.value.startswith("incident."):
        return IncidentEvent(**event_data)
    elif event_type.value.startswith("alert."):
        return AlertEvent(**event_data)
    elif event_type.value.startswith("remediation."):
        return RemediationEvent(**event_data)
    else:
        return BaseEvent(**event_data)

