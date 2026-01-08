"""Custom exceptions for the application."""

class AIEREException(Exception):
    """Base exception for AI-SRE platform."""
    
    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        """Initialize exception."""
        self.message = message
        self.code = code
        super().__init__(self.message)

class AlertNotFoundError(AIEREException):
    """Raised when an alert is not found."""
    
    def __init__(self, alert_id: str) -> None:
        super().__init__(f"Alert {alert_id} not found", "ALERT_NOT_FOUND")

class IncidentNotFoundError(AIEREException):
    """Raised when an incident is not found."""
    
    def __init__(self, incident_id: str) -> None:
        super().__init__(f"Incident {incident_id} not found", "INCIDENT_NOT_FOUND")

class RemediationFailedError(AIEREException):
    """Raised when remediation action fails."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, "REMEDIATION_FAILED")

class AgentExecutionError(AIEREException):
    """Raised when agent execution fails."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, "AGENT_EXECUTION_ERROR")

class VectorStoreError(AIEREException):
    """Raised when vector store operations fail."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, "VECTOR_STORE_ERROR")
