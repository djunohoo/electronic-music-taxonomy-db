#!/usr/bin/env python3
"""
CULTURAL INTELLIGENCE SYSTEM - EXISTING DATABASE INSTALLER
=========================================================
Installs Cultural Intelligence tables into your existing MetaCrate database.
Uses 'cultural_' prefixed table names to avoid conflicts.

Run this ONCE to install the system.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from taxonomy_v32 import DatabaseSchema, TaxonomyConfig
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)

def main():
    """Install Cultural Intelligence System into existing database"""
    
    print("🎵 CULTURAL INTELLIGENCE SYSTEM v3.2 - DATABASE INSTALLER")
    print("=" * 60)
    
    # Initialize configuration
    config = TaxonomyConfig()
    schema = DatabaseSchema()
    
    db_url = config.config["supabase"]["url"]
    print(f"📡 Connecting to: {db_url}")
    
    if not db_url or db_url == "your-database-url-here":
        print("❌ Database URL not configured!")
        print("Using default: postgresql://postgres:BvbMRx6lqbbRK5e@172.22.17.138:5432/postgres")
        db_url = "postgresql://postgres:BvbMRx6lqbbRK5e@172.22.17.138:5432/postgres"
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        conn.autocommit = True  # Important for CREATE statements
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Connected to database")
        
        # Execute schema installation
        print("🔧 Installing Cultural Intelligence schema...")
        cursor.execute(schema.schema_sql)
        print("✅ Schema installed successfully")
        
        # Verify installation
        print("🔍 Verifying installation...")
        cursor.execute("""
            SELECT COUNT(*) as table_count
            FROM information_schema.tables 
            WHERE table_name LIKE 'cultural_%'
        """)
        result = cursor.fetchone()
        table_count = result['table_count']
        
        print(f"✅ Found {table_count} Cultural Intelligence tables")
        
        # Check seed data
        cursor.execute("SELECT COUNT(*) as count FROM cultural_label_profiles")
        labels = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM cultural_artist_profiles") 
        artists = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM cultural_patterns")
        patterns = cursor.fetchone()['count']
        
        print(f"✅ Seed data loaded:")
        print(f"   - {labels} label profiles")
        print(f"   - {artists} artist profiles") 
        print(f"   - {patterns} classification patterns")
        
        print("\n" + "=" * 60)
        print("🎉 CULTURAL INTELLIGENCE SYSTEM READY!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run scanner: python cultural_intelligence_system.py --scan /path/to/music")
        print("2. Start API: python cultural_intelligence_system.py --api") 
        print("3. Launch dashboard: python cultural_intelligence_system.py --dashboard")
        print()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Installation error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()