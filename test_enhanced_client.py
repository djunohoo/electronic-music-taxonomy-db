#!/usr/bin/env python3
"""
Test the enhanced database client functionality
"""

from cultural_database_client import CulturalDatabaseClient
import json

def test_enhanced_client():
    try:
        print('Testing enhanced database client...')
        client = CulturalDatabaseClient()
        
        # Test the enhanced low-confidence track method
        print('\nTesting get_low_confidence_tracks_for_training()...')
        tracks = client.get_low_confidence_tracks_for_training(3)
        print(f'Found {len(tracks)} tracks')
        
        for i, track in enumerate(tracks, 1):
            print(f'\nTrack {i}:')
            print(f'  Title: {track.get("title", "Unknown")}')
            print(f'  Artist: {track.get("artist", "Unknown")}')
            print(f'  Confidence: {track.get("overall_confidence", 0):.2f}')
            print(f'  Impact Score: {track.get("missing_analysis", {}).get("impact_score", 0)}')
            print(f'  Question Type: {track.get("missing_analysis", {}).get("question_type", "unknown")}')
            print(f'  Priority Field: {track.get("missing_analysis", {}).get("priority_field", "unknown")}')
        
        # Test the enhanced training questions
        print('\n\nTesting get_training_questions()...')
        questions = client.get_training_questions(2)
        print(f'Generated {len(questions)} training questions')
        
        for i, q in enumerate(questions, 1):
            print(f'\nQuestion {i}:')
            print(f'  Question: {q.get("question", "No question")}')
            print(f'  Priority: {q.get("priority", 0)}')
            print(f'  Impact: {q.get("context", {}).get("impact_explanation", "No explanation")}')
            
        print('\n✅ Database client test completed successfully')
        
    except Exception as e:
        print(f'❌ Error testing database client: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_client()