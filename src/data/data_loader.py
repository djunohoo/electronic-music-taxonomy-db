"""
Data loading and management utilities.
"""
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Genre, Characteristic, AudioFeature, Timeline
from src.data.scraper import WikipediaGenreScraper, GenreCharacteristicsExtractor
from typing import List, Dict

class DataLoader:
    """Load and manage data for the taxonomy database."""
    
    def __init__(self):
        self.scraper = WikipediaGenreScraper()
        self.characteristics_extractor = GenreCharacteristicsExtractor()
    
    def load_wikipedia_data(self) -> Dict[str, int]:
        """Load genre data from Wikipedia."""
        print("Scraping Wikipedia for electronic music genres...")
        genres_data = self.scraper.scrape_genre_list()
        
        db: Session = next(get_db())
        try:
            loaded_count = 0
            updated_count = 0
            
            for genre_data in genres_data:
                # Check if genre already exists
                existing = db.query(Genre).filter(Genre.name == genre_data.name).first()
                
                if existing:
                    # Update existing genre
                    if genre_data.description and not existing.description:
                        existing.description = genre_data.description
                    if genre_data.wikipedia_url and not existing.wikipedia_url:
                        existing.wikipedia_url = genre_data.wikipedia_url
                    if genre_data.origin_year and not existing.origin_year:
                        existing.origin_year = genre_data.origin_year
                    if genre_data.origin_location and not existing.origin_location:
                        existing.origin_location = genre_data.origin_location
                    updated_count += 1
                else:
                    # Create new genre
                    genre = Genre(
                        name=genre_data.name,
                        slug=self._create_slug(genre_data.name),
                        description=genre_data.description,
                        wikipedia_url=genre_data.wikipedia_url,
                        origin_year=genre_data.origin_year,
                        origin_location=genre_data.origin_location
                    )
                    db.add(genre)
                    loaded_count += 1
            
            db.commit()
            return {
                'loaded': loaded_count,
                'updated': updated_count,
                'total_scraped': len(genres_data)
            }
        finally:
            db.close()
    
    def load_sample_characteristics(self):
        """Load sample characteristics for genres."""
        db: Session = next(get_db())
        try:
            # Sample characteristics for popular genres
            sample_data = {
                'House': [
                    {'type': 'tempo', 'name': 'BPM Range', 'value': '120-130', 'description': 'Typical house tempo range'},
                    {'type': 'rhythm', 'name': '4/4 Beat', 'description': 'Four-on-the-floor kick drum pattern'},
                    {'type': 'instruments', 'name': 'Roland TR-808/909', 'description': 'Classic drum machines'},
                    {'type': 'style', 'name': 'Repetitive Groove', 'description': 'Hypnotic, danceable rhythms'}
                ],
                'Techno': [
                    {'type': 'tempo', 'name': 'BPM Range', 'value': '120-150', 'description': 'Wide tempo range'},
                    {'type': 'sound', 'name': 'Industrial', 'description': 'Mechanical, futuristic sounds'},
                    {'type': 'instruments', 'name': 'Synthesizers', 'description': 'Heavy use of analog and digital synths'},
                    {'type': 'production', 'name': 'Minimalism', 'description': 'Stripped-down, functional approach'}
                ],
                'Trance': [
                    {'type': 'tempo', 'name': 'BPM Range', 'value': '125-150', 'description': 'Progressive build-ups'},
                    {'type': 'melody', 'name': 'Uplifting', 'description': 'Emotional, soaring melodies'},
                    {'type': 'structure', 'name': 'Build and Drop', 'description': 'Tension and release patterns'},
                    {'type': 'effects', 'name': 'Reverb and Delay', 'description': 'Spacious, atmospheric production'}
                ]
            }
            
            loaded_count = 0
            for genre_name, characteristics in sample_data.items():
                genre = db.query(Genre).filter(Genre.name == genre_name).first()
                if genre:
                    for char_data in characteristics:
                        # Check if characteristic already exists
                        existing = db.query(Characteristic).filter(
                            Characteristic.genre_id == genre.id,
                            Characteristic.name == char_data['name']
                        ).first()
                        
                        if not existing:
                            characteristic = Characteristic(
                                genre_id=genre.id,
                                characteristic_type=char_data['type'],
                                name=char_data['name'],
                                description=char_data.get('description'),
                                value=char_data.get('value')
                            )
                            db.add(characteristic)
                            loaded_count += 1
            
            db.commit()
            print(f"Loaded {loaded_count} sample characteristics")
        finally:
            db.close()
    
    def load_sample_audio_features(self):
        """Load sample audio features for genres."""
        db: Session = next(get_db())
        try:
            sample_features = {
                'House': {
                    'bpm_min': 118, 'bpm_max': 135, 'bpm_typical': 125,
                    'time_signature': '4/4',
                    'typical_instruments': 'TR-808, TR-909, bass synthesizer, piano, vocal samples',
                    'production_techniques': 'Side-chain compression, swing quantization, reverb'
                },
                'Techno': {
                    'bpm_min': 120, 'bpm_max': 150, 'bpm_typical': 130,
                    'time_signature': '4/4',
                    'typical_instruments': 'TB-303, TR-808, TR-909, analog synthesizers',
                    'production_techniques': 'Acid sequences, distortion, industrial samples'
                },
                'Trance': {
                    'bpm_min': 125, 'bpm_max': 150, 'bpm_typical': 138,
                    'time_signature': '4/4',
                    'typical_instruments': 'Supersaw leads, arpeggiated sequences, vocal pads',
                    'production_techniques': 'Build-ups, breakdowns, reverb tails, gates'
                },
                'Drum and Bass': {
                    'bpm_min': 160, 'bpm_max': 180, 'bpm_typical': 174,
                    'time_signature': '4/4',
                    'typical_instruments': 'Amen break, reese bass, breakbeats',
                    'production_techniques': 'Time-stretching, chopping, heavy compression'
                }
            }
            
            loaded_count = 0
            for genre_name, features in sample_features.items():
                genre = db.query(Genre).filter(Genre.name == genre_name).first()
                if genre:
                    existing = db.query(AudioFeature).filter(AudioFeature.genre_id == genre.id).first()
                    if not existing:
                        audio_feature = AudioFeature(
                            genre_id=genre.id,
                            **features
                        )
                        db.add(audio_feature)
                        loaded_count += 1
            
            db.commit()
            print(f"Loaded {loaded_count} sample audio features")
        finally:
            db.close()
    
    def load_sample_timeline(self):
        """Load sample timeline events."""
        db: Session = next(get_db())
        try:
            timeline_events = [
                {
                    'genre': 'House', 'year': 1981, 'event_type': 'emergence',
                    'description': 'House music emerges in Chicago clubs',
                    'location': 'Chicago, USA',
                    'key_artists': 'Frankie Knuckles, Ron Hardy'
                },
                {
                    'genre': 'Techno', 'year': 1985, 'event_type': 'emergence',
                    'description': 'Detroit techno develops with futuristic sound',
                    'location': 'Detroit, USA',
                    'key_artists': 'Juan Atkins, Derrick May, Kevin Saunderson'
                },
                {
                    'genre': 'Trance', 'year': 1990, 'event_type': 'emergence',
                    'description': 'Trance music develops in Germany',
                    'location': 'Germany',
                    'key_artists': 'Klaus Schulze, Kraftwerk influence'
                },
                {
                    'genre': 'Drum and Bass', 'year': 1992, 'event_type': 'emergence',
                    'description': 'Drum and bass evolves from breakbeat hardcore',
                    'location': 'London, UK',
                    'key_artists': 'LTJ Bukem, Goldie, Roni Size'
                }
            ]
            
            loaded_count = 0
            for event_data in timeline_events:
                genre = db.query(Genre).filter(Genre.name == event_data['genre']).first()
                if genre:
                    existing = db.query(Timeline).filter(
                        Timeline.genre_id == genre.id,
                        Timeline.year == event_data['year']
                    ).first()
                    
                    if not existing:
                        timeline = Timeline(
                            genre_id=genre.id,
                            year=event_data['year'],
                            event_type=event_data['event_type'],
                            description=event_data['description'],
                            location=event_data['location'],
                            key_artists=event_data['key_artists']
                        )
                        db.add(timeline)
                        loaded_count += 1
            
            db.commit()
            print(f"Loaded {loaded_count} timeline events")
        finally:
            db.close()
    
    def _create_slug(self, name: str) -> str:
        """Create URL-friendly slug from genre name."""
        return name.lower().replace(' ', '-').replace('&', 'and')
    
    def initialize_sample_data(self):
        """Initialize the database with sample data."""
        print("Initializing sample data...")
        
        # Load basic genres first
        basic_genres = [
            {'name': 'House', 'description': 'Four-on-the-floor dance music originating in Chicago'},
            {'name': 'Techno', 'description': 'Electronic dance music with futuristic, mechanical sounds'},
            {'name': 'Trance', 'description': 'Hypnotic electronic music with emotional buildups'},
            {'name': 'Drum and Bass', 'description': 'Fast breakbeats with heavy bass lines'},
            {'name': 'Ambient', 'description': 'Atmospheric, textural electronic music'},
            {'name': 'Dubstep', 'description': 'Bass-heavy electronic music with syncopated rhythms'}
        ]
        
        db: Session = next(get_db())
        try:
            for genre_data in basic_genres:
                existing = db.query(Genre).filter(Genre.name == genre_data['name']).first()
                if not existing:
                    genre = Genre(
                        name=genre_data['name'],
                        slug=self._create_slug(genre_data['name']),
                        description=genre_data['description']
                    )
                    db.add(genre)
            
            db.commit()
            print("Basic genres loaded")
        finally:
            db.close()
        
        # Load additional data
        self.load_sample_characteristics()
        self.load_sample_audio_features()
        self.load_sample_timeline()
        
        print("Sample data initialization complete!")

if __name__ == "__main__":
    loader = DataLoader()
    loader.initialize_sample_data()
    
    # Optionally load Wikipedia data
    print("\nWould you like to load data from Wikipedia? (y/n)")
    response = input().strip().lower()
    if response == 'y':
        result = loader.load_wikipedia_data()
        print(f"Wikipedia data loaded: {result}")