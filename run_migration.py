#!/usr/bin/env python3
"""
Database Migration Script
Executes SQL migration to change foreign key constraint to CASCADE
"""
import os
import sys
import psycopg2
from psycopg2 import sql

def run_migration():
    """Execute SQL migration script"""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print("Usage: railway run python run_migration.py")
        sys.exit(1)

    # Read SQL migration file
    migration_file = "migrations/migrate_cascade.sql"
    try:
        with open(migration_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Migration file not found: {migration_file}")
        sys.exit(1)

    print(f"📄 Loading migration script: {migration_file}")
    print(f"🔗 Connecting to database...")

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("✅ Connected to database")
        print("🚀 Executing migration...\n")

        # Execute migration
        cursor.execute(sql_script)

        print("\n✅ Migration completed successfully!")
        print("\n📊 Verification:")
        print("=" * 60)

        # Verify the change
        cursor.execute("""
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.referential_constraints rc
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_name = 'send_history'
                AND kcu.column_name = 'company_id';
        """)

        result = cursor.fetchone()
        if result:
            constraint_name, table_name, column_name, delete_rule = result
            print(f"Constraint Name: {constraint_name}")
            print(f"Table Name: {table_name}")
            print(f"Column Name: {column_name}")
            print(f"Delete Rule: {delete_rule}")

            if delete_rule == "CASCADE":
                print("\n✅ Foreign key constraint successfully changed to CASCADE!")
            else:
                print(f"\n⚠️  Warning: Delete rule is '{delete_rule}', expected 'CASCADE'")
        else:
            print("❌ Could not verify constraint")

        print("=" * 60)

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"\n❌ Database error occurred:")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error occurred:")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Database Migration Tool")
    print("=" * 60)
    run_migration()
