"""Custom exceptions for the application.

Each domain exception carries an application ``code`` and an HTTP ``status_code``
so the API layer can translate them into consistent JSON error responses via a
single exception handler (see ``app.main``).
"""

from __future__ import annotations


class IncidentIQError(Exception):
    """Base exception for the IncidentIQ platform."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(
        self, message: str, *, code: str | None = None, status_code: int | None = None
    ) -> None:
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(IncidentIQError):
    """Generic 404."""

    status_code = 404
    code = "NOT_FOUND"


class AlertNotFoundError(NotFoundError):
    code = "ALERT_NOT_FOUND"

    def __init__(self, alert_id: str) -> None:
        super().__init__(f"Alert {alert_id} not found")


class IncidentNotFoundError(NotFoundError):
    code = "INCIDENT_NOT_FOUND"

    def __init__(self, incident_id: str) -> None:
        super().__init__(f"Incident {incident_id} not found")


class RemediationNotFoundError(NotFoundError):
    code = "REMEDIATION_NOT_FOUND"

    def __init__(self, remediation_id: str) -> None:
        super().__init__(f"Remediation {remediation_id} not found")


class ValidationError(IncidentIQError):
    status_code = 422
    code = "VALIDATION_ERROR"


class ConflictError(IncidentIQError):
    """State transition not allowed (e.g. approving an already-approved fix)."""

    status_code = 409
    code = "CONFLICT"


class AuthenticationError(IncidentIQError):
    status_code = 401
    code = "AUTHENTICATION_ERROR"


class AuthorizationError(IncidentIQError):
    status_code = 403
    code = "AUTHORIZATION_ERROR"


class RateLimitError(IncidentIQError):
    status_code = 429
    code = "RATE_LIMITED"


class RemediationFailedError(IncidentIQError):
    code = "REMEDIATION_FAILED"


class AgentExecutionError(IncidentIQError):
    code = "AGENT_EXECUTION_ERROR"


class VectorStoreError(IncidentIQError):
    code = "VECTOR_STORE_ERROR"


class IntegrationError(IncidentIQError):
    code = "INTEGRATION_ERROR"
    status_code = 502


# Backwards-compatible alias (the original scaffold used this name).
AIEREException = IncidentIQError
