"""Knowledge base endpoints: semantic search + document listing."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.schemas.knowledge import (
    KnowledgeDocOut,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
)
from app.security.auth import require_viewer
from app.services.knowledge_service import KnowledgeService

router = APIRouter(tags=["knowledge"], prefix="/knowledge")


@router.post("/search", response_model=list[KnowledgeSearchResult])
async def search_knowledge(
    payload: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> list[KnowledgeSearchResult]:
    return await KnowledgeService(db).search(payload.query, top_k=payload.top_k)


@router.get("/documents", response_model=list[KnowledgeDocOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> list[KnowledgeDocOut]:
    docs = await KnowledgeService(db).list_documents()
    return [KnowledgeDocOut.model_validate(d) for d in docs]
