"""Database models package.

Importing this package registers every model with the shared ``Base.metadata``
so ``create_all`` / Alembic autogenerate can discover all tables.
"""

from app.models.database.alert import Alert
from app.models.database.base import Base, TimestampedModel
from app.models.database.incident import Incident
from app.models.database.knowledge_doc import KnowledgeChunk, KnowledgeDocument
from app.models.database.remediation_log import RemediationLog
from app.models.database.user import User

__all__ = [
    "Base",
    "TimestampedModel",
    "Alert",
    "Incident",
    "RemediationLog",
    "KnowledgeDocument",
    "KnowledgeChunk",
    "User",
]
