#!/usr/bin/env python3
"""Seed the knowledge base with the sample runbooks and post-mortems.

Run from the repo root (uses the backend package + its configured database):

    backend/venv/Scripts/python scripts/seed_knowledge.py   # Windows
    backend/venv/bin/python scripts/seed_knowledge.py        # Linux/macOS
"""

import asyncio
import sys
from pathlib import Path

# Make the backend `app` package importable regardless of the current directory.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.db.postgres import AsyncSessionLocal, init_models  # noqa: E402
from app.services.knowledge_service import KnowledgeService  # noqa: E402

DATA_DIR = ROOT / "backend" / "data"


async def seed_knowledge_base() -> None:
    print("Seeding knowledge base...")
    await init_models()
    async with AsyncSessionLocal() as db:
        service = KnowledgeService(db)
        count = await service.index_directory(DATA_DIR)
        await db.commit()
        total_docs = await service.count()
    print(f"Indexed {count} document(s); knowledge base now holds {total_docs} document(s).")
    print("Knowledge base seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
