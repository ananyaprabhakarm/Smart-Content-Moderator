"""
Migration script to add user_email column to moderation_requests table.

This script adds the user_email field to support analytics tracking by user.
Run this script once to update your existing database schema.
"""

import sqlite3
import os

# Database file path
DB_PATH = "./moderation.db"

def migrate_database():
    """Add user_email column to moderation_requests table"""

    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        print("The column will be created automatically when you first run the application.")
        return

    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(moderation_requests)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'user_email' in columns:
            print("✓ Column 'user_email' already exists in moderation_requests table")
            conn.close()
            return

        # Add the new column
        print("Adding user_email column to moderation_requests table...")
        cursor.execute("""
            ALTER TABLE moderation_requests
            ADD COLUMN user_email VARCHAR(255)
        """)

        # Create index for better query performance
        print("Creating index on user_email column...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_requests_user_email
            ON moderation_requests(user_email)
        """)

        conn.commit()
        print("✓ Migration completed successfully!")
        print("  - Added user_email column")
        print("  - Created index on user_email for better performance")

        # Show table schema
        cursor.execute("PRAGMA table_info(moderation_requests)")
        columns = cursor.fetchall()
        print("\nUpdated schema for moderation_requests:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        conn.close()

    except sqlite3.Error as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add user_email to moderation_requests")
    print("=" * 60)
    migrate_database()
    print("\nMigration process completed.")
