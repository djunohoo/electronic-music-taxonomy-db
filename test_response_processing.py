#!/usr/bin/env python3
"""
Test response processing and follow-up question generation
"""

from cultural_database_client import CulturalDatabaseClient
import json

def test_response_processing():
    try:
        print('Testing Response Processing and Follow-up Questions...')
        client = CulturalDatabaseClient()
        
        # Simulate a genre selection response
        print('\n1. Testing Genre Selection Response:')
        
        # Mock response data for a genre selection
        response_data = {
            'original_context': {
                'track_data': {
                    'id': 123,
                    'title': 'Test House Track',
                    'artist': 'Test Artist'
                },
                'impact_score': 75
            },
            'question_context': {
                'stage': 'genre',
                'requires_subgenre': True
            },
            'response': 'House'
        }
        
        followup = client.process_training_response('test_question_123', response_data)
        
        if followup:
            print('Generated follow-up question:')
            followup_q = followup.get('question', {})
            print(f'  Question: {followup_q.get("question", "No question")}')
            print(f'  Type: {followup_q.get("type", "unknown")}')
            print(f'  Options: {len(followup_q.get("options", []))} subgenre options')
            print(f'  Parent Genre: {followup_q.get("context", {}).get("parent_genre", "unknown")}')
            
            # Show subgenre options
            options = followup_q.get('options', [])
            if options:
                print(f'  Subgenre Options: {", ".join(options)}')
        else:
            print('No follow-up question generated')
        
        # Test subgenre completion
        print('\n2. Testing Subgenre Completion:')
        
        subgenre_response = {
            'original_context': {
                'track_data': {
                    'id': 123,
                    'title': 'Test House Track',
                    'artist': 'Test Artist'
                }
            },
            'question_context': {
                'stage': 'subgenre',
                'parent_genre': 'House'
            },
            'response': 'Deep House'
        }
        
        completion_result = client.process_training_response('test_subgenre_123', subgenre_response)
        
        if completion_result is None:
            print('✅ Subgenre completion processed - no further follow-up needed')
        else:
            print(f'Unexpected follow-up: {completion_result}')
        
        # Test manual classification with track that needs genre classification
        print('\n3. Testing Classification-Needed Questions:')
        
        # Find tracks that actually need classification (no existing classification)
        unclassified_tracks = []
        tracks_response = client._make_request('GET', 'cultural_tracks?limit=10')
        tracks = tracks_response.json() or []
        
        for track in tracks:
            # Check if this track has a classification
            class_response = client._make_request('GET', f'cultural_classifications?track_id=eq.{track["id"]}')
            classifications = class_response.json()
            
            if not classifications:  # No classification exists
                unclassified_tracks.append(track)
                break  # Just need one for testing
        
        if unclassified_tracks:
            track = unclassified_tracks[0]
            print(f'Found unclassified track: {track.get("filename", "Unknown")}')
            
            # Generate a classification question for this track
            formatted_track = {
                'id': track['id'],
                'title': track.get('filename', 'Unknown').replace('.mp3', '').replace('.wav', '').replace('.flac', ''),
                'artist': 'Unknown',
                'missing_analysis': {
                    'question_type': 'classification_needed',
                    'priority_field': 'genre'
                }
            }
            
            question_data = client._generate_targeted_question(formatted_track, 'classification_needed', 'genre')
            print(f'Classification Question: {question_data.get("question")}')
            print(f'Available Genre Options: {len(question_data.get("options", []))} options')
            print(f'First 5 options: {", ".join(question_data.get("options", [])[:5])}')
            
        else:
            print('No unclassified tracks found for testing')
        
        print('\n✅ Response processing test completed successfully!')
        
    except Exception as e:
        print(f'❌ Error testing response processing: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_response_processing()