#!/usr/bin/env python3
"""
Quick database connection test
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from taxonomy_v32 import TaxonomyConfig
import psycopg2

def test_db_connection():
    """Test database connection"""
    
    print("Testing Cultural Intelligence database connection...")
    
    try:
        config = TaxonomyConfig()
        db_url = config.config["supabase"]["url"]
        print(f"Database URL: {db_url}")
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT COUNT(*) FROM cultural_tracks")
        track_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cultural_artist_profiles") 
        artist_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cultural_label_profiles")
        label_count = cursor.fetchone()[0]
        
        print(f"✅ Database connection successful!")
        print(f"   Tracks: {track_count}")
        print(f"   Artists: {artist_count}")
        print(f"   Labels: {label_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_db_connection()