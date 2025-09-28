#!/usr/bin/env python3
"""
Setup Training Tables for AI Learning System
===========================================
Creates the training queue and session tracking tables
"""

import json
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingTableSetup:
    """Setup training tables in Supabase."""
    
    def __init__(self, config_file: str = "taxonomy_config.json"):
        """Initialize with configuration."""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.base_url = f"{self.config['supabase']['url']}/rest/v1"
        self.headers = {
            "apikey": self.config["supabase"]["service_role_key"],
            "Authorization": f"Bearer {self.config['supabase']['service_role_key']}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def create_training_queue_table(self):
        """Create cultural_training_queue table using direct SQL."""
        create_sql = """
        CREATE TABLE IF NOT EXISTS cultural_training_queue (
            id SERIAL PRIMARY KEY,
            question_type VARCHAR(50) NOT NULL,
            priority INTEGER DEFAULT 5,
            status VARCHAR(20) DEFAULT 'pending',
            context_data JSONB,
            track_id INTEGER,
            file_path TEXT,
            uncertainty_score FLOAT DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT NOW(),
            assigned_at TIMESTAMP,
            completed_at TIMESTAMP,
            human_response JSONB,
            confidence_gained FLOAT
        );
        
        CREATE INDEX IF NOT EXISTS idx_training_queue_status ON cultural_training_queue(status);
        CREATE INDEX IF NOT EXISTS idx_training_queue_priority ON cultural_training_queue(priority DESC);
        CREATE INDEX IF NOT EXISTS idx_training_queue_created ON cultural_training_queue(created_at);
        """
        
        return self._execute_sql(create_sql)
    
    def create_training_sessions_table(self):
        """Create cultural_training_sessions table."""
        create_sql = """
        CREATE TABLE IF NOT EXISTS cultural_training_sessions (
            id SERIAL PRIMARY KEY,
            session_type VARCHAR(50) DEFAULT 'human_training',
            question_id INTEGER REFERENCES cultural_training_queue(id),
            user_id TEXT,
            question_text TEXT,
            human_response JSONB,
            response_time_ms INTEGER,
            confidence_before FLOAT,
            confidence_after FLOAT,
            accuracy_impact FLOAT,
            asked_at TIMESTAMP DEFAULT NOW(),
            answered_at TIMESTAMP,
            feedback_quality INTEGER DEFAULT 5,
            notes TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_training_sessions_asked ON cultural_training_sessions(asked_at);
        CREATE INDEX IF NOT EXISTS idx_training_sessions_type ON cultural_training_sessions(session_type);
        """
        
        return self._execute_sql(create_sql)
    
    def _execute_sql(self, sql: str) -> bool:
        """Execute SQL using Supabase SQL API."""
        try:
            # Use PostgREST SQL endpoint
            sql_url = f"{self.config['supabase']['url']}/rest/v1/rpc/exec_sql"
            
            # Try direct SQL execution
            response = requests.post(
                sql_url,
                headers=self.headers,
                json={"sql": sql}
            )
            
            if response.status_code == 200:
                logger.info("SQL executed successfully")
                return True
            else:
                logger.warning(f"SQL execution failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return False
    
    def populate_sample_training_data(self):
        """Add sample training questions."""
        sample_questions = [
            {
                "question_type": "genre_uncertainty",
                "priority": 10,
                "context_data": {
                    "genres": ["Progressive House", "Melodic Techno"],
                    "reason": "Emotional breakdown with techno drums",
                    "file_path": "/music/progressive/track_001.mp3",
                    "bpm": 128,
                    "key": "A minor"
                },
                "uncertainty_score": 0.75
            },
            {
                "question_type": "artist_profiling", 
                "priority": 8,
                "context_data": {
                    "artist": "Stephan Bodzin",
                    "uncertainty": "Progressive vs Melodic Techno classification",
                    "file_path": "/music/techno/bodzin_track.mp3",
                    "genre_distribution": {"Progressive": 60, "Melodic Techno": 40}
                },
                "uncertainty_score": 0.65
            },
            {
                "question_type": "tempo_analysis",
                "priority": 6,
                "context_data": {
                    "bpm_detected": 126,
                    "genres": ["Deep House", "Tech House"],
                    "reason": "BPM suggests tech house but groove feels deep",
                    "file_path": "/music/house/deep_tech_126.mp3"
                },
                "uncertainty_score": 0.55
            },
            {
                "question_type": "label_specialization",
                "priority": 7,
                "context_data": {
                    "label": "Anjunadeep",
                    "usual_genre": "Progressive House",
                    "this_track_genre": "Deep House",
                    "file_path": "/music/anjunadeep/track.mp3"
                },
                "uncertainty_score": 0.70
            }
        ]
        
        try:
            for question in sample_questions:
                response = requests.post(
                    f"{self.base_url}/cultural_training_queue",
                    headers=self.headers,
                    json=question
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Added training question: {question['question_type']}")
                else:
                    logger.warning(f"Failed to add question: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error populating sample data: {e}")
    
    def setup_all(self):
        """Setup all training tables and data."""
        logger.info("🎓 Setting up AI Training Queue System...")
        
        # Create tables
        logger.info("Creating training queue table...")
        self.create_training_queue_table()
        
        logger.info("Creating training sessions table...")
        self.create_training_sessions_table()
        
        # Add sample data
        logger.info("Adding sample training questions...")
        self.populate_sample_training_data()
        
        logger.info("✅ Training system setup complete!")
        logger.info("🚀 AI Training Zone is ready for human interaction!")

if __name__ == "__main__":
    setup = TrainingTableSetup()
    setup.setup_all()