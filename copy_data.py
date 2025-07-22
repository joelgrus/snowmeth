#!/usr/bin/env python3
"""
Copy data from old database to new database with chapters field.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def copy_data():
    """Copy all story data from old database to new database."""
    
    # Connect to both databases
    old_db_url = f"sqlite+aiosqlite:///data/snowmeth.db"
    new_db_url = f"sqlite+aiosqlite:///test_migration.db"
    
    old_engine = create_async_engine(old_db_url)
    new_engine = create_async_engine(new_db_url)
    
    print("Copying story data from old database to new database...")
    
    async with old_engine.begin() as old_conn:
        async with new_engine.begin() as new_conn:
            # Get all stories from old database
            result = await old_conn.execute(text("SELECT * FROM stories"))
            stories = result.fetchall()
            
            print(f"Found {len(stories)} stories to copy")
            
            # Insert each story into new database
            for story in stories:
                await new_conn.execute(text("""
                    INSERT INTO stories (story_id, slug, story_idea, current_step, created_at, updated_at, steps, chapters)
                    VALUES (:story_id, :slug, :story_idea, :current_step, :created_at, :updated_at, :steps, '{}')
                """), {
                    'story_id': story[0],
                    'slug': story[1], 
                    'story_idea': story[2],
                    'current_step': story[3],
                    'created_at': story[4],
                    'updated_at': story[5],
                    'steps': story[6]
                })
                print(f"✅ Copied story: {story[1]}")
    
    await old_engine.dispose()
    await new_engine.dispose()
    
    print("✅ Data migration complete!")
    print("Now you can replace the old database with:")
    print("  mv data/snowmeth.db data/snowmeth_backup.db")
    print("  mv test_migration.db data/snowmeth.db")

if __name__ == "__main__":
    asyncio.run(copy_data())