"""
Enhanced data loading with hierarchical genres, BPM ranges, energy levels, 
keywords, mixing compatibility, and label associations.
"""
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import (
    Genre, Characteristic, AudioFeature, Timeline, GenreKeyword, 
    RecordLabel, LabelAssociation, MixingCompatibility
)
from typing import List, Dict, Tuple

class EnhancedDataLoader:
    """Enhanced data loader with comprehensive genre taxonomy features."""
    
    def __init__(self):
        pass
    
    def load_enhanced_genres(self):
        """Load genres with enhanced taxonomy features."""
        db: Session = next(get_db())
        try:
            enhanced_genres = [
                {
                    'name': 'House',
                    'description': 'Four-on-the-floor dance music originating in Chicago',
                    'energy_level': 7,
                    'bpm_min': 118,
                    'bpm_max': 135,
                    'bpm_typical': 125,
                    'origin_year': 1981,
                    'origin_location': 'Chicago, USA'
                },
                {
                    'name': 'Deep House',
                    'description': 'Soulful, jazz-influenced house with deeper basslines',
                    'energy_level': 6,
                    'bpm_min': 120,
                    'bpm_max': 125,
                    'bpm_typical': 122,
                    'origin_year': 1985,
                    'origin_location': 'Chicago, USA'
                },
                {
                    'name': 'Tech House',
                    'description': 'Fusion of house and techno with minimal, techy elements',
                    'energy_level': 8,
                    'bpm_min': 125,
                    'bpm_max': 130,
                    'bpm_typical': 128,
                    'origin_year': 1995,
                    'origin_location': 'London, UK'
                },
                {
                    'name': 'Techno',
                    'description': 'Electronic dance music with futuristic, mechanical sounds',
                    'energy_level': 9,
                    'bpm_min': 120,
                    'bpm_max': 150,
                    'bpm_typical': 130,
                    'origin_year': 1985,
                    'origin_location': 'Detroit, USA'
                },
                {
                    'name': 'Minimal Techno',
                    'description': 'Stripped-down techno with repetitive, hypnotic elements',
                    'energy_level': 7,
                    'bpm_min': 125,
                    'bpm_max': 135,
                    'bpm_typical': 130,
                    'origin_year': 1992,
                    'origin_location': 'Germany'
                },
                {
                    'name': 'Trance',
                    'description': 'Hypnotic electronic music with emotional buildups',
                    'energy_level': 8,
                    'bpm_min': 125,
                    'bpm_max': 150,
                    'bpm_typical': 138,
                    'origin_year': 1990,
                    'origin_location': 'Germany'
                },
                {
                    'name': 'Breakbeat',
                    'description': 'Electronic music featuring syncopated drum patterns and broken rhythms - THE FOUNDATION!',
                    'energy_level': 8,
                    'bpm_min': 120,
                    'bpm_max': 180,
                    'bpm_typical': 140,
                    'origin_year': 1990,
                    'origin_location': 'UK'
                },
                {
                    'name': 'Drum and Bass',
                    'description': 'Fast breakbeats with heavy bass and sub-bass lines',
                    'energy_level': 9,
                    'bpm_min': 160,
                    'bpm_max': 180,
                    'bpm_typical': 174,
                    'origin_year': 1992,
                    'origin_location': 'UK'
                },
                {
                    'name': 'Jungle',
                    'description': 'The original breakbeat hardcore that birthed drum and bass',
                    'energy_level': 10,
                    'bpm_min': 150,
                    'bpm_max': 190,
                    'bpm_typical': 170,
                    'origin_year': 1991,
                    'origin_location': 'London, UK'
                },
                {
                    'name': 'Big Beat',
                    'description': 'Fat beats and heavy basslines - Chemical Brothers style!',
                    'energy_level': 8,
                    'bpm_min': 120,
                    'bpm_max': 140,
                    'bpm_typical': 130,
                    'origin_year': 1995,
                    'origin_location': 'UK'
                },
                {
                    'name': 'Nu-Skool Breaks',
                    'description': 'Modern breakbeat with crisp production and heavy bass',
                    'energy_level': 8,
                    'bpm_min': 125,
                    'bpm_max': 140,
                    'bpm_typical': 132,
                    'origin_year': 1998,
                    'origin_location': 'UK/USA'
                },
                {
                    'name': 'Dubstep',
                    'description': 'Syncopated drum patterns with prominent sub-bass frequencies',
                    'energy_level': 9,
                    'bpm_min': 130,
                    'bpm_max': 145,
                    'bpm_typical': 140,
                    'origin_year': 2002,
                    'origin_location': 'South London, UK'
                }
            ]
            
            loaded_count = 0
            for genre_data in enhanced_genres:
                existing = db.query(Genre).filter(Genre.name == genre_data['name']).first()
                if not existing:
                    genre = Genre(
                        name=genre_data['name'],
                        slug=self._create_slug(genre_data['name']),
                        description=genre_data['description'],
                        energy_level=genre_data['energy_level'],
                        bpm_min=genre_data['bpm_min'],
                        bpm_max=genre_data['bpm_max'],
                        bpm_typical=genre_data['bpm_typical'],
                        origin_year=genre_data['origin_year'],
                        origin_location=genre_data['origin_location']
                    )
                    db.add(genre)
                    loaded_count += 1
            
            db.commit()
            print(f"Loaded {loaded_count} enhanced genres")
        finally:
            db.close()
    
    def _create_slug(self, name: str) -> str:
        """Create URL-friendly slug from genre name."""
        return name.lower().replace(' ', '-').replace('&', 'and')
    
    def load_all_enhanced_data(self):
        """Load all enhanced data features."""
        print("Loading enhanced genre taxonomy data...")
        self.load_enhanced_genres()
        print("Enhanced data loading complete!")

if __name__ == "__main__":
    loader = EnhancedDataLoader()
    loader.load_all_enhanced_data()