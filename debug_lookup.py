#!/usr/bin/env python3
"""
Debug the classification lookup in the main method
"""

from cultural_database_client import CulturalDatabaseClient

def debug_classification_lookup():
    client = CulturalDatabaseClient()
    try:
        # Simulate the exact same process as the main method
        tracks = [{'id': 185, 'filename': 'test.mp3'}]
        track_ids = [str(track['id']) for track in tracks]
        
        print(f'Looking up classifications for track IDs: {track_ids}')
        
        classifications_response = client._make_request('GET', 
            f'cultural_classifications?track_id=in.({",".join(track_ids)})&select=track_id,overall_confidence,genre_confidence,genre,artist,track_name,needs_review,human_validated')
        classifications_data = classifications_response.json() or []
        
        print(f'Raw classifications response: {classifications_data}')
        
        # Build the lookup dict like the main method does
        classifications = {c['track_id']: c for c in classifications_data}
        print(f'Classifications lookup dict: {classifications}')
        
        # Test the lookup
        track_id = 185
        classification = classifications.get(track_id, None)
        print(f'Classification for track {track_id}: {classification}')
        
        # Test the analysis
        track_data = {'id': 185}
        metadata = {}
        result = client._analyze_missing_information_impact(track_data, classification, metadata)
        print(f'Impact analysis result: {result}')
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_classification_lookup()