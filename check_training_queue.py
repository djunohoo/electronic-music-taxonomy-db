#!/usr/bin/env python3
"""
Check if cultural_training_queue table exists and create sample data if needed.
"""

from cultural_database_client import CulturalDatabaseClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_setup_queue():
    """Check if cultural_training_queue exists and set it up if needed."""
    
    client = CulturalDatabaseClient()
    
    print("🔍 Checking cultural_training_queue table...")
    
    # Try to get training items from queue
    try:
        items = client.get_training_questions(limit=1)
        print(f"✅ cultural_training_queue table exists! Found {len(items)} items.")
        
        if len(items) == 0:
            print("📝 Table is empty, adding sample training items...")
            
            sample_items = [
                {
                    "question": "What genre is characterized by aggressive 4/4 beats at 140+ BPM?",
                    "options": ["Hardcore", "Ambient", "Jazz", "Folk"],
                    "correct_answer": "Hardcore",
                    "category": "genre_identification",
                    "difficulty": "medium",
                    "status": "pending"
                },
                {
                    "question": "Which electronic music style originated in Detroit in the 1980s?",
                    "options": ["House", "Techno", "Trance", "Dubstep"],
                    "correct_answer": "Techno", 
                    "category": "music_history",
                    "difficulty": "easy",
                    "status": "pending"
                },
                {
                    "question": "What BPM range is typical for classic House music?",
                    "options": ["90-100", "120-130", "140-150", "160-180"],
                    "correct_answer": "120-130",
                    "category": "technical_knowledge",
                    "difficulty": "medium", 
                    "status": "pending"
                }
            ]
            
            for item in sample_items:
                success = client.create_training_question(item)
                if success:
                    print(f"✅ Added: {item['question'][:50]}...")
                else:
                    print(f"❌ Failed to add: {item['question'][:50]}...")
        
        print(f"\n🎵 Hidden Voting Power System Ready!")
        print(f"🎛️ Users will be secretly scored based on response quality")
        print(f"⚡ RENEGADE MASTER achievement unlocks at max authority level")
        
    except Exception as e:
        print(f"❌ Error accessing cultural_training_queue: {e}")
        print(f"💡 The table might be named differently or not exist yet.")
        
        print(f"\n🔧 Suggested fixes:")
        print(f"1. Check if table is named 'cultural_training_queue' in database")
        print(f"2. Run database setup scripts to create the table")
        print(f"3. Verify Supabase connection and permissions")

if __name__ == "__main__":
    check_and_setup_queue()