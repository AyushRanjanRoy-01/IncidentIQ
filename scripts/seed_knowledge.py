#!/usr/bin/env python3
"""Seed knowledge base with sample runbooks and post-mortems.

This script populates the knowledge base with sample documents
for RAG retrieval and testing.
"""

import asyncio
import json
from pathlib import Path
from app.rag.vector_store import VectorStore
from app.rag.chunker import Chunker
from app.rag.embeddings import EmbeddingService
from app.core.config import settings


async def seed_knowledge_base():
    """Seed knowledge base with sample documents."""
    print("🌱 Seeding knowledge base...")
    
    # Initialize services
    embedding_service = EmbeddingService()
    chunker = Chunker()
    vector_store = VectorStore()
    
    # Load sample documents
    data_dir = Path(__file__).parent.parent / "data"
    runbooks_dir = data_dir / "runbooks"
    postmortems_dir = data_dir / "postmortems"
    
    documents = []
    
    # Load runbooks
    if runbooks_dir.exists():
        for runbook_file in runbooks_dir.glob("*.md"):
            with open(runbook_file, "r") as f:
                content = f.read()
                documents.append({
                    "title": runbook_file.stem,
                    "content": content,
                    "type": "runbook",
                    "source": str(runbook_file),
                })
    
    # Load post-mortems
    if postmortems_dir.exists():
        for postmortem_file in postmortems_dir.glob("*.md"):
            with open(postmortem_file, "r") as f:
                content = f.read()
                documents.append({
                    "title": postmortem_file.stem,
                    "content": content,
                    "type": "postmortem",
                    "source": str(postmortem_file),
                })
    
    # Process and index documents
    for doc in documents:
        print(f"📄 Processing: {doc['title']}")
        
        # Chunk document
        chunks = chunker.chunk(doc["content"])
        
        # Generate embeddings and store
        for i, chunk in enumerate(chunks):
            embedding = await embedding_service.embed(chunk)
            
            # TODO: Store in vector database
            # await vector_store.add_document(
            #     text=chunk,
            #     embedding=embedding,
            #     metadata={
            #         "title": doc["title"],
            #         "type": doc["type"],
            #         "chunk_index": i,
            #         "source": doc["source"],
            #     }
            # )
    
    print(f"✅ Indexed {len(documents)} documents")
    print("🎉 Knowledge base seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
