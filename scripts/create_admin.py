#!/usr/bin/env python3
"""Create (or update) a real user — use this in production instead of demo seeding.

    backend/venv/bin/python scripts/create_admin.py --username alice \
        --password 's3cret' --role admin --email alice@corp.com

If --password is omitted you'll be prompted (input hidden).
"""

import argparse
import asyncio
import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.db.postgres import AsyncSessionLocal, init_models  # noqa: E402
from app.models.database.user import User  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.security.auth import hash_password  # noqa: E402


async def upsert_user(username: str, password: str, role: str, email: str, full_name: str) -> None:
    await init_models()
    async with AsyncSessionLocal() as db:
        user = await db.get(User, username)
        if user is None:
            user = User(username=username)
            db.add(user)
            action = "Created"
        else:
            action = "Updated"
        user.hashed_password = hash_password(password)
        user.role = role
        user.email = email or user.email or ""
        user.full_name = full_name or user.full_name or username
        user.disabled = False
        await db.commit()
    print(f"{action} user '{username}' with role '{role}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update an IncidentIQ user.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password")
    parser.add_argument("--role", default=UserRole.ADMIN.value,
                        choices=[r.value for r in UserRole])
    parser.add_argument("--email", default="")
    parser.add_argument("--full-name", default="")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Password: ")
    if len(password) < 6:
        parser.error("password must be at least 6 characters")

    asyncio.run(upsert_user(args.username, password, args.role, args.email, args.full_name))


if __name__ == "__main__":
    main()
