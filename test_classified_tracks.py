#!/usr/bin/env python3
"""
Test with specific tracks that have classifications
"""

from cultural_database_client import CulturalDatabaseClient

def test_with_classified_tracks():
    client = CulturalDatabaseClient()
    try:
        print('Testing with tracks that have classifications...')
        
        # Get tracks that have corresponding classifications
        classified_tracks = client.get_low_confidence_tracks_for_training(5)
        
        print(f'Found {len(classified_tracks)} tracks')
        
        # Let's also test by manually getting tracks with known IDs
        response = client._make_request('GET', 'cultural_tracks?id=in.(185,186,187)&select=id,filename,file_path,raw_metadata,folder_path')
        specific_tracks = response.json()
        
        print(f'\nFound {len(specific_tracks)} specific tracks with known classifications')
        
        for track in specific_tracks:
            print(f'\nTrack ID {track["id"]}:')
            print(f'  Filename: {track.get("filename", "Unknown")}')
            
            # Get classification for this track
            class_response = client._make_request('GET', f'cultural_classifications?track_id=eq.{track["id"]}')
            classifications = class_response.json()
            
            if classifications:
                c = classifications[0]
                print(f'  Artist: {c.get("artist", "Unknown")}')
                print(f'  Genre: {c.get("genre", "Unknown")}')
                print(f'  Overall Confidence: {c.get("overall_confidence", 0)}')
                print(f'  Genre Confidence: {c.get("genre_confidence", 0)}')
                print(f'  Needs Review: {c.get("needs_review", False)}')
                
                # Test our impact analysis function directly
                missing_analysis = client._analyze_missing_information_impact(track, c, track.get('raw_metadata', {}))
                print(f'  Impact Score: {missing_analysis["impact_score"]}')
                print(f'  Question Type: {missing_analysis["question_type"]}')
                print(f'  Priority Field: {missing_analysis["priority_field"]}')
                print(f'  Explanation: {missing_analysis["explanation"]}')
            else:
                print('  No classification found')
                
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_classified_tracks()