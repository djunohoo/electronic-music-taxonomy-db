#!/usr/bin/env python3
"""
Fix Cultural Intelligence Database Issues
===========================================
Fixes database schema and handles Unicode/duplicate errors
"""

import json
import requests
import logging
from cultural_database_client import CulturalDatabaseClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix missing database columns and constraints."""
    
    try:
        # Load configuration
        with open('taxonomy_config.json', 'r') as f:
            config = json.load(f)
        
        base_url = f"{config['supabase']['url']}/rest/v1/rpc"
        headers = {
            "apikey": config["supabase"]["service_role_key"],
            "Authorization": f"Bearer {config['supabase']['service_role_key']}",
            "Content-Type": "application/json"
        }
        
        # SQL to add missing reinforcement_count column
        add_column_sql = """
            DO $$
            BEGIN
                -- Add reinforcement_count column if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'cultural_patterns' 
                    AND column_name = 'reinforcement_count'
                ) THEN
                    ALTER TABLE cultural_patterns 
                    ADD COLUMN reinforcement_count INTEGER DEFAULT 1;
                    
                    -- Update existing records
                    UPDATE cultural_patterns 
                    SET reinforcement_count = 1 
                    WHERE reinforcement_count IS NULL;
                    
                    RAISE NOTICE 'Added reinforcement_count column to cultural_patterns';
                ELSE
                    RAISE NOTICE 'reinforcement_count column already exists';
                END IF;
                
                -- Ensure training tables exist
                CREATE TABLE IF NOT EXISTS cultural_training_questions (
                    id SERIAL PRIMARY KEY,
                    question_type VARCHAR(100) NOT NULL,
                    question_text TEXT NOT NULL,
                    context_data JSONB DEFAULT '{}',
                    uncertainty_score DECIMAL(3,2) DEFAULT 0.65,
                    track_id INTEGER REFERENCES cultural_tracks(id),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    human_response JSONB
                );
                
                CREATE TABLE IF NOT EXISTS cultural_training_sessions (
                    id SERIAL PRIMARY KEY,
                    question_id INTEGER REFERENCES cultural_training_questions(id),
                    question_type VARCHAR(100),
                    question_text TEXT,
                    human_response JSONB,
                    response_text TEXT,
                    answered_at TIMESTAMP DEFAULT NOW(),
                    feedback_quality INTEGER DEFAULT 5,
                    response_time_ms INTEGER DEFAULT 2000
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_training_questions_status 
                ON cultural_training_questions(status);
                
                CREATE INDEX IF NOT EXISTS idx_training_questions_type 
                ON cultural_training_questions(question_type);
                
                CREATE INDEX IF NOT EXISTS idx_training_sessions_timestamp 
                ON cultural_training_sessions(answered_at);
                
                RAISE NOTICE 'Database schema fixes completed successfully';
            END $$;
        """
        
        # Execute the SQL
        response = requests.post(
            f"{config['supabase']['url']}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"sql": add_column_sql}
        )
        
        if response.status_code == 200:
            logger.info("✅ Database schema fixed successfully!")
        else:
            logger.error(f"❌ Schema fix failed: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Error fixing database schema: {e}")

def clean_duplicate_tracks():
    """Clean up duplicate tracks to resolve conflict errors."""
    
    try:
        db_client = CulturalDatabaseClient()
        
        # Get all tracks
        tracks = db_client.get_all_tracks()
        
        # Find duplicates by file_path
        seen_paths = set()
        duplicates = []
        
        for track in tracks:
            file_path = track.get('file_path', '')
            if file_path in seen_paths:
                duplicates.append(track)
            else:
                seen_paths.add(file_path)
        
        logger.info(f"Found {len(duplicates)} duplicate tracks")
        
        # Delete duplicates (keep the first one)
        deleted_count = 0
        for duplicate in duplicates:
            try:
                success = db_client.delete_track(duplicate['id'])
                if success:
                    deleted_count += 1
                    logger.info(f"Deleted duplicate: {duplicate.get('filename', 'unknown')}")
            except Exception as e:
                logger.warning(f"Failed to delete duplicate {duplicate['id']}: {e}")
        
        logger.info(f"✅ Cleaned up {deleted_count} duplicate tracks")
        
    except Exception as e:
        logger.error(f"❌ Error cleaning duplicates: {e}")

def create_sample_training_questions():
    """Create sample training questions for testing."""
    
    try:
        db_client = CulturalDatabaseClient()
        
        sample_questions = [
            {
                "question_type": "genre_uncertainty",
                "question_text": "I'm analyzing a 128 BPM track with four-on-the-floor kicks and filtered house stabs. Could be House or Tech House. What's your classification?",
                "context_data": {
                    "genres": ["House", "Tech House"],
                    "bpm": 128,
                    "reason": "Similar rhythmic patterns, uncertain about sub-genre classification"
                },
                "uncertainty_score": 0.75
            },
            {
                "question_type": "artist_profiling", 
                "question_text": "Artist 'Block & Crown' has tracks across House (80%), Tech House (15%), Deep House (5%). What's their primary specialty?",
                "context_data": {
                    "artist": "Block & Crown",
                    "genre_distribution": {"House": 80, "Tech House": 15, "Deep House": 5}
                },
                "uncertainty_score": 0.60
            },
            {
                "question_type": "tempo_analysis",
                "question_text": "Track at 174 BPM with breakbeats and heavy bass. Could be Drum & Bass or Jungle. What classification do you recommend?",
                "context_data": {
                    "bpm_detected": 174,
                    "genres": ["Drum & Bass", "Jungle"],
                    "reason": "High BPM with breakbeat pattern characteristics"
                },
                "uncertainty_score": 0.70
            }
        ]
        
        created_count = 0
        for question in sample_questions:
            success = db_client.create_training_question(question)
            if success:
                created_count += 1
        
        logger.info(f"✅ Created {created_count} sample training questions")
        
    except Exception as e:
        logger.error(f"❌ Error creating sample questions: {e}")

def main():
    """Main fix routine."""
    logger.info("🔧 Starting Cultural Intelligence Database Fixes...")
    
    # 1. Fix database schema
    logger.info("1️⃣ Fixing database schema...")
    fix_database_schema()
    
    # 2. Clean duplicates
    logger.info("2️⃣ Cleaning duplicate tracks...")
    clean_duplicate_tracks()
    
    # 3. Create sample training questions
    logger.info("3️⃣ Creating sample training questions...")
    create_sample_training_questions()
    
    logger.info("✅ Database fixes completed!")
    logger.info("🎯 Dashboard should now work properly")
    logger.info("🚀 Try running: python enhanced_cultural_dashboard.py")

if __name__ == "__main__":
    main()