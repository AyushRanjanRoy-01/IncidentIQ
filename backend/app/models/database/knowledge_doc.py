"""Knowledge document database model."""

from sqlalchemy import Column, String, JSON, DateTime, Text, Float
from datetime import datetime
from app.models.database.base import TimestampedModel

class KnowledgeDocument(TimestampedModel):
    """Knowledge document in vector store."""
    __tablename__ = "knowledge_documents"
    
    doc_id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding_model = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)
