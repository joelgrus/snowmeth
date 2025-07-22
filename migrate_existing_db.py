#!/usr/bin/env python3
"""
Safe migration script to add chapters column to existing database.
This works by directly modifying the SQLite database structure.
"""

import sqlite3
import os
import shutil
from datetime import datetime


def migrate_database(db_path):
    """Add chapters column to existing database safely."""

    # Create backup first (in a writable location)
    backup_filename = f"snowmeth_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = f"./{backup_filename}"
    print(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if chapters column already exists
        cursor.execute("PRAGMA table_info(stories);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if "chapters" in column_names:
            print("✅ Chapters column already exists, no migration needed.")
            return True

        print("Adding chapters column...")

        # Add the chapters column with default empty JSON
        cursor.execute("ALTER TABLE stories ADD COLUMN chapters TEXT DEFAULT '{}';")

        # Update all existing rows to have empty chapters object
        cursor.execute("UPDATE stories SET chapters = '{}' WHERE chapters IS NULL;")

        conn.commit()
        print("✅ Migration completed successfully!")
        print(f"✅ Backup saved as: {backup_path}")

        # Verify the migration worked
        cursor.execute("SELECT COUNT(*) FROM stories WHERE chapters IS NOT NULL;")
        count = cursor.fetchone()[0]
        print(f"✅ Verified: {count} stories now have chapters field")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Restoring from backup...")
        conn.close()
        shutil.copy2(backup_path, db_path)
        print("✅ Database restored from backup")
        return False

    finally:
        conn.close()


def main():
    # Check different possible database locations
    possible_paths = [
        "./data/snowmeth.db",
        "/app/data/snowmeth.db",
        os.environ.get("DATABASE_PATH", "./data/snowmeth.db"),
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break

    if not db_path:
        print("❌ Could not find database file")
        print("Checked paths:", possible_paths)
        return False

    print(f"Found database: {db_path}")

    # Check permissions
    if not os.access(db_path, os.W_OK):
        print(f"❌ No write permission to {db_path}")
        print("You may need to run: sudo chown $USER:$USER data/snowmeth.db")
        return False

    return migrate_database(db_path)


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Migration complete! You can now use chapter functionality.")
    else:
        print("\n💥 Migration failed. Check the error messages above.")
