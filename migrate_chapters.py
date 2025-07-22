#!/usr/bin/env python3
"""
Migration script to add chapters column to existing stories table.
This preserves all existing data.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def migrate_database():
    """Add chapters column to stories table while preserving data."""

    # Get database path
    db_path = os.environ.get("DATABASE_PATH", "./data/snowmeth.db")
    database_url = f"sqlite+aiosqlite:///{db_path}"

    print(f"Migrating database at: {db_path}")

    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        # Check if chapters column already exists
        result = await conn.execute(text("PRAGMA table_info(stories);"))
        columns = result.fetchall()
        column_names = [col[1] for col in columns]

        if "chapters" not in column_names:
            print("Adding chapters column...")
            await conn.execute(
                text("ALTER TABLE stories ADD COLUMN chapters JSON DEFAULT '{}';")
            )
            print("✅ Chapters column added successfully!")
        else:
            print("✅ Chapters column already exists, no migration needed.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate_database())
