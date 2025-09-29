#!/usr/bin/env python3
"""
Check classifications in database
"""

from cultural_database_client import CulturalDatabaseClient

def check_classifications():
    client = CulturalDatabaseClient()
    try:
        # Check classification count
        response = client._make_request('GET', 'cultural_classifications?limit=3')
        classifications = response.json()
        print(f'Found {len(classifications)} classifications in database')
        
        if classifications:
            print('\nSample classifications:')
            for i, c in enumerate(classifications, 1):
                print(f'Classification {i}:')
                print(f'  Track ID: {c.get("track_id")}')
                print(f'  Artist: {c.get("artist", "Unknown")}')
                print(f'  Genre: {c.get("genre", "Unknown")}')
                print(f'  Overall Confidence: {c.get("overall_confidence", "N/A")}')
                print(f'  Genre Confidence: {c.get("genre_confidence", "N/A")}')
                print(f'  Needs Review: {c.get("needs_review", "N/A")}')
                print()
        else:
            print('No classifications found - all tracks are unclassified')
            
        # Also check track count
        track_response = client._make_request('GET', 'cultural_tracks?limit=1')
        tracks = track_response.json()
        if tracks:
            print(f'Total tracks in database: Found at least {len(tracks)} track(s)')
        
    except Exception as e:
        print(f'Error checking classifications: {e}')

if __name__ == "__main__":
    check_classifications()