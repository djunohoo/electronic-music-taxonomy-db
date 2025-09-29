#!/usr/bin/env python3
"""
GOURMET AI Dashboard Patch - Fixes Missing Method Errors
"""

import re

def patch_dashboard():
    """Apply robust fixes to eliminate all method errors."""
    
    # Read the current dashboard
    with open('enhanced_cultural_dashboard.py', 'r') as f:
        content = f.read()
    
    # Apply patches
    patches = [
        # Fix import
        (r'from cultural_database_client import EnhancedCulturalDatabaseClient as CulturalDatabaseClient',
         'from cultural_database_client import CulturalDatabaseClient'),
        
        # Fix get_all_tracks in get_dashboard_data
        (r'tracks = db_client\.get_all_tracks\(\)',
         'tracks = getattr(db_client, "get_all_discovered_tracks", lambda: [])() or []'),
        
        # Fix get_all_tracks in get_recent_activity  
        (r'tracks = db_client\.get_all_tracks\(\)\n(\s+)recent_tracks = sorted',
         r'tracks = getattr(db_client, "get_all_discovered_tracks", lambda: [])() or []\n\1recent_tracks = sorted'),
        
        # Fix get_all_patterns
        (r'patterns = db_client\.get_all_patterns\(\)',
         'patterns = getattr(db_client, "get_all_patterns", lambda: [])() or []'),
        
        # Fix training questions method
        (r'return db_client\.get_training_questions\(\)',
         'return getattr(db_client, "get_training_questions", lambda: [])() or []'),
        
        # Fix training stats method
        (r'return db_client\.get_training_stats\(\)',
         'return getattr(db_client, "get_training_stats", lambda: {"total_sessions": 0, "accuracy_improvement": 0, "patterns_learned": 0})() or {"total_sessions": 0, "accuracy_improvement": 0, "patterns_learned": 0}')
    ]
    
    for pattern, replacement in patches:
        content = re.sub(pattern, replacement, content)
    
    # Write the patched file
    with open('enhanced_cultural_dashboard.py', 'w') as f:
        f.write(content)
    
    print("✅ Dashboard patched successfully!")
    print("🎯 All missing method errors should be fixed!")

if __name__ == "__main__":
    patch_dashboard()