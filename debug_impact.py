#!/usr/bin/env python3
"""
Debug the impact analysis logic
"""

from cultural_database_client import CulturalDatabaseClient

def debug_impact_analysis():
    client = CulturalDatabaseClient()
    
    # Test track 185 which should have good classification
    track_data = {
        'id': 185,
        'filename': '01 Los Pueblos (Pablo Fierro Remix).mp3'
    }
    
    classification_data = {
        'track_id': 185,
        'artist': 'Pino Arduini, Javier Bollag, Pablo Fierro',
        'genre': 'House',
        'overall_confidence': 0.9,
        'genre_confidence': 0.85,
        'needs_review': False,
        'human_validated': False
    }
    
    metadata = {}
    
    print('Debugging impact analysis for track 185...')
    print(f'Track data: {track_data}')
    print(f'Classification data: {classification_data}')
    print(f'Classification bool check: {bool(classification_data)}')
    print(f'Classification length: {len(classification_data)}')
    
    result = client._analyze_missing_information_impact(track_data, classification_data, metadata)
    print(f'Impact analysis result: {result}')

if __name__ == "__main__":
    debug_impact_analysis()