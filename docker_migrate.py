#!/usr/bin/env python3
"""
Docker-friendly migration script.
Run this inside the Docker container to migrate the database.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def migrate_database():
    """Add chapters column to existing database using SQLAlchemy."""

    # Get database path from environment or default
    db_path = os.environ.get("DATABASE_PATH", "/app/data/snowmeth.db")
    database_url = f"sqlite+aiosqlite:///{db_path}"

    print(f"Migrating database: {db_path}")

    engine = create_async_engine(database_url, echo=False)

    try:
        async with engine.begin() as conn:
            # Check if chapters column already exists
            result = await conn.execute(text("PRAGMA table_info(stories);"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]

            if "chapters" in column_names:
                print("✅ Chapters column already exists, no migration needed.")
                return True

            print("Adding chapters column...")

            # Add the chapters column
            await conn.execute(
                text("ALTER TABLE stories ADD COLUMN chapters JSON DEFAULT '{}';")
            )

            # Update all existing rows to have empty chapters object
            await conn.execute(
                text("UPDATE stories SET chapters = '{}' WHERE chapters IS NULL;")
            )

            print("✅ Migration completed successfully!")

            # Verify the migration worked
            result = await conn.execute(
                text("SELECT COUNT(*) FROM stories WHERE chapters IS NOT NULL;")
            )
            count = result.fetchone()[0]
            print(f"✅ Verified: {count} stories now have chapters field")

            return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(migrate_database())
    if success:
        print(
            "\n🎉 Migration complete! Restart the API server to use chapter functionality."
        )
    else:
        print("\n💥 Migration failed. Check the error messages above.")
