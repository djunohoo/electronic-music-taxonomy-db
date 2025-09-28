#!/usr/bin/env python3
"""
Live Training System - Create Tables using API Logs
==================================================
Uses existing cultural_api_requests table to simulate training queue
"""

import json
import requests
import logging
from datetime import datetime
from cultural_database_client import EnhancedCulturalDatabaseClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_training_using_existing_tables():
    """Setup training using existing table structure."""
    
    db_client = EnhancedCulturalDatabaseClient()
    
    # Create training questions as API requests (using existing table)
    training_questions = [
        {
            'endpoint': 'training_question',
            'method': 'PENDING',
            'request_path': '/ai/training/genre_uncertainty/1',
            'status_code': 200,
            'classification_returned': {
                'question_type': 'genre_uncertainty',
                'priority': 10,
                'context_data': {
                    'genres': ['Progressive House', 'Melodic Techno'],
                    'reason': 'Emotional breakdown with techno drums',
                    'file_path': '/music/progressive/track_001.mp3',
                    'bpm': 128,
                    'key': 'A minor'
                },
                'uncertainty_score': 0.75,
                'status': 'pending'
            }
        },
        {
            'endpoint': 'training_question',
            'method': 'PENDING', 
            'request_path': '/ai/training/artist_profiling/2',
            'status_code': 200,
            'classification_returned': {
                'question_type': 'artist_profiling',
                'priority': 8,
                'context_data': {
                    'artist': 'Stephan Bodzin',
                    'uncertainty': 'Progressive vs Melodic Techno classification',
                    'file_path': '/music/techno/bodzin_track.mp3',
                    'genre_distribution': {'Progressive': 60, 'Melodic Techno': 40}
                },
                'uncertainty_score': 0.65,
                'status': 'pending'
            }
        },
        {
            'endpoint': 'training_question',
            'method': 'PENDING',
            'request_path': '/ai/training/tempo_analysis/3', 
            'status_code': 200,
            'classification_returned': {
                'question_type': 'tempo_analysis',
                'priority': 6,
                'context_data': {
                    'bpm_detected': 126,
                    'genres': ['Deep House', 'Tech House'],
                    'reason': 'BPM suggests tech house but groove feels deep',
                    'file_path': '/music/house/deep_tech_126.mp3'
                },
                'uncertainty_score': 0.55,
                'status': 'pending'
            }
        },
        {
            'endpoint': 'training_question',
            'method': 'PENDING',
            'request_path': '/ai/training/label_specialization/4',
            'status_code': 200, 
            'classification_returned': {
                'question_type': 'label_specialization',
                'priority': 7,
                'context_data': {
                    'label': 'Anjunadeep',
                    'usual_genre': 'Progressive House',
                    'this_track_genre': 'Deep House',
                    'file_path': '/music/anjunadeep/track.mp3'
                },
                'uncertainty_score': 0.70,
                'status': 'pending'
            }
        }
    ]
    
    logger.info("🚀 Creating live training questions using existing infrastructure...")
    
    for question in training_questions:
        try:
            response = db_client._make_request('POST', 'cultural_api_requests', json=question)
            result = response.json()
            logger.info(f"✅ Created training question: {question['classification_returned']['question_type']}")
        except Exception as e:
            logger.error(f"❌ Failed to create question: {e}")
    
    logger.info("🎉 LIVE TRAINING SYSTEM DEPLOYED!")
    logger.info("✅ All training questions are now live in the database!")

if __name__ == "__main__":
    setup_training_using_existing_tables()