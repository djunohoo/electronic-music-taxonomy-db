#!/usr/bin/env python3
"""
Test the enhanced training system with genre/subgenre questions and button options
"""

from cultural_database_client import CulturalDatabaseClient
import json

def test_enhanced_training_system():
    try:
        print('Testing Enhanced Training System with Genre/Subgenre Questions...')
        client = CulturalDatabaseClient()
        
        # Test getting known genres
        print('\n1. Testing Known Genres:')
        genres = client._get_known_genres()
        print(f'Found {len(genres)} known genres:')
        for genre in genres[:10]:  # Show first 10
            print(f'  - {genre}')
        if len(genres) > 10:
            print(f'  ... and {len(genres) - 10} more')
        
        # Test getting subgenres for House
        print('\n2. Testing Subgenres for House:')
        house_subgenres = client._get_known_subgenres('House')
        print(f'Found {len(house_subgenres)} House subgenres:')
        for subgenre in house_subgenres:
            print(f'  - {subgenre}')
        
        # Test enhanced training questions
        print('\n3. Testing Enhanced Training Questions:')
        questions = client.get_training_questions(2)
        print(f'Generated {len(questions)} enhanced training questions')
        
        for i, q in enumerate(questions, 1):
            print(f'\nQuestion {i}:')
            question_data = q.get('question', {})
            print(f'  Text: {question_data.get("question", "No question")}')
            print(f'  Type: {question_data.get("type", "unknown")}')
            print(f'  Options: {len(question_data.get("options", []))} button options')
            print(f'  Allow Custom: {question_data.get("allow_custom", False)}')
            print(f'  Follow-up: {question_data.get("follow_up", "None")}')
            print(f'  Priority: {q.get("priority", 0)}')
            
            # Show some options if available
            options = question_data.get('options', [])
            if options:
                print(f'  Sample Options: {", ".join(options[:5])}{"..." if len(options) > 5 else ""}')
        
        # Test subgenre follow-up question generation
        print('\n4. Testing Subgenre Follow-up:')
        sample_track = {
            'id': 123,
            'title': 'Test Track',
            'artist': 'Test Artist'
        }
        
        followup = client.generate_subgenre_followup_question(sample_track, 'House')
        print(f'Follow-up Question: {followup.get("question", "No question")}')
        print(f'Follow-up Type: {followup.get("type", "unknown")}')
        print(f'Follow-up Options: {len(followup.get("options", []))} options')
        print(f'Sample Subgenre Options: {", ".join(followup.get("options", [])[:5])}')
        
        print('\n✅ Enhanced training system test completed successfully!')
        
    except Exception as e:
        print(f'❌ Error testing enhanced training system: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_training_system()