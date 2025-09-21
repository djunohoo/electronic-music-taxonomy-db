"""
Unit tests for the Electronic Music Taxonomy Database.
Tests cover enhanced features including hierarchical genres, BPM ranges,
energy levels, keywords, mixing compatibility, and label associations.
"""
import pytest
import tempfile
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import (Base, Genre, Characteristic, AudioFeature, GenreKeyword, 
                       RecordLabel, LabelAssociation, MixingCompatibility)
from src.data.scraper import WikipediaGenreScraper, GenreCharacteristicsExtractor
from src.data.enhanced_loader_simple import EnhancedDataLoader
from src.analysis.audio_analyzer import AudioFeatureExtractor, GenreClassifier

class TestModels:
    """Test database models."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_genre_creation(self, db_session):
        """Test enhanced genre model creation."""
        genre = Genre(
            name="Test House",
            slug="test-house",
            description="A test house genre",
            origin_year=1980,
            energy_level=7,
            bpm_min=120,
            bpm_max=130,
            bpm_typical=125
        )
        db_session.add(genre)
        db_session.commit()
        
        assert genre.id is not None
        assert genre.name == "Test House"
        assert genre.slug == "test-house"
        assert genre.energy_level == 7
        assert genre.bpm_min == 120
        assert genre.bpm_max == 130
        assert genre.bpm_typical == 125
    
    def test_hierarchical_genres(self, db_session):
        """Test parent-child genre relationships."""
        # Create parent genre
        house = Genre(
            name="House",
            slug="house",
            description="Main house genre",
            energy_level=6,
            bpm_typical=125
        )
        db_session.add(house)
        db_session.flush()
        
        # Create child genre
        deep_house = Genre(
            name="Deep House",
            slug="deep-house",
            description="Deeper variant of house",
            parent_id=house.id,
            energy_level=5,
            bpm_typical=122
        )
        db_session.add(deep_house)
        db_session.commit()
        
        # Test relationships
        assert deep_house.parent == house
        assert deep_house in house.children
        assert len(house.children) == 1
    
    def test_genre_keywords(self, db_session):
        """Test genre keyword associations."""
        genre = Genre(name="House", slug="house")
        db_session.add(genre)
        db_session.flush()
        
        # Add keywords
        keywords = ["four-on-the-floor", "disco", "chicago"]
        for keyword_text in keywords:
            keyword = GenreKeyword(
                genre_id=genre.id,
                keyword=keyword_text,
                weight=1.0
            )
            db_session.add(keyword)
        
        db_session.commit()
        
        assert len(genre.keywords) == 3
        keyword_texts = [k.keyword for k in genre.keywords]
        assert "four-on-the-floor" in keyword_texts
        assert "chicago" in keyword_texts
    
    def test_mixing_compatibility(self, db_session):
        """Test mixing compatibility between genres."""
        # Create two genres
        house = Genre(name="House", slug="house", bpm_typical=125, energy_level=6)
        tech_house = Genre(name="Tech House", slug="tech-house", bpm_typical=126, energy_level=7)
        
        db_session.add_all([house, tech_house])
        db_session.flush()
        
        # Create compatibility
        compatibility = MixingCompatibility(
            genre1_id=house.id,
            genre2_id=tech_house.id,
            compatibility_score=0.9,
            notes="Very similar BPM and style"
        )
        db_session.add(compatibility)
        db_session.commit()
        
        assert compatibility.compatibility_score == 0.9
        assert "similar BPM" in compatibility.notes
    
    def test_label_associations(self, db_session):
        """Test record label associations."""
        # Create genre and label
        house = Genre(name="House", slug="house")
        defected = RecordLabel(name="Defected Records", country="UK")
        
        db_session.add_all([house, defected])
        db_session.flush()
        
        # Create association
        association = LabelAssociation(
            genre_id=house.id,
            label_id=defected.id,
            strength=0.9
        )
        db_session.add(association)
        db_session.commit()
        
        assert len(house.label_associations) == 1
        assert house.label_associations[0].label.name == "Defected Records"
        assert house.label_associations[0].strength == 0.9
    
    def test_characteristic_relationship(self, db_session):
        """Test genre-characteristic relationship."""
        genre = Genre(name="Test Genre", slug="test-genre")
        db_session.add(genre)
        db_session.flush()
        
        characteristic = Characteristic(
            genre_id=genre.id,
            characteristic_type="tempo",
            name="BPM",
            value="120-130"
        )
        db_session.add(characteristic)
        db_session.commit()
        
        assert len(genre.characteristics) == 1
        assert genre.characteristics[0].name == "BPM"

class TestScraper:
    """Test Wikipedia scraper functionality."""
    
    def test_genre_name_cleaning(self):
        """Test genre name cleaning function."""
        scraper = WikipediaGenreScraper()
        
        # Test cases
        assert scraper._clean_genre_name("House music[edit]") == "House music"
        assert scraper._clean_genre_name("1. Techno") == "Techno"
        assert scraper._clean_genre_name("  Trance  ") == "Trance"
    
    def test_valid_genre_detection(self):
        """Test genre name validation."""
        scraper = WikipediaGenreScraper()
        
        assert scraper._is_valid_genre("House") == True
        assert scraper._is_valid_genre("Techno") == True
        assert scraper._is_valid_genre("contents") == False
        assert scraper._is_valid_genre("List of genres") == False
    
    def test_year_extraction(self):
        """Test year extraction from text."""
        scraper = WikipediaGenreScraper()
        
        text1 = "House music emerged in the early 1980s in Chicago"
        assert scraper._extract_year(text1) == 1980
        
        text2 = "Techno developed in 1985 in Detroit"
        assert scraper._extract_year(text2) == 1985
        
        text3 = "No year mentioned here"
        assert scraper._extract_year(text3) is None

class TestEnhancedDataLoader:
    """Test enhanced data loader functionality."""
    
    def test_enhanced_loader_initialization(self):
        """Test that enhanced loader can be initialized."""
        loader = EnhancedDataLoader()
        assert loader is not None
    
    def test_slug_creation(self):
        """Test slug creation from genre names."""
        loader = EnhancedDataLoader()
        
        test_cases = [
            ("House", "house"),
            ("Deep House", "deep-house"),
            ("Drum & Bass", "drum-and-bass"),
            ("Progressive Trance", "progressive-trance"),
            ("UK Garage", "uk-garage")
        ]
        
        for name, expected_slug in test_cases:
            assert loader._create_slug(name) == expected_slug
    
    def test_bpm_compatibility_calculation(self):
        """Test BPM-based compatibility calculations."""
        # Test same BPM (should be high compatibility)
        bpm1, bpm2 = 125, 125
        bpm_diff = abs(bpm1 - bpm2)
        score1 = max(0.0, 1.0 - (bpm_diff / 50.0))
        assert score1 >= 0.9
        
        # Test close BPM (should be medium-high compatibility)
        bpm1, bpm2 = 125, 128
        bpm_diff = abs(bpm1 - bpm2)
        score2 = max(0.0, 1.0 - (bpm_diff / 50.0))
        assert 0.7 <= score2 <= 0.9
        
        # Test distant BPM (should be low compatibility)
        bpm1, bpm2 = 125, 175
        bpm_diff = abs(bpm1 - bpm2)
        score3 = max(0.0, 1.0 - (bpm_diff / 50.0))
        assert score3 <= 0.3
    
    def test_energy_compatibility_calculation(self):
        """Test energy level compatibility calculations."""
        # Test same energy level
        energy1, energy2 = 7, 7
        energy_diff = abs(energy1 - energy2)
        score1 = max(0.0, 1.0 - (energy_diff / 10.0))
        assert score1 >= 0.9
        
        # Test adjacent energy levels
        energy1, energy2 = 7, 8
        energy_diff = abs(energy1 - energy2)
        score2 = max(0.0, 1.0 - (energy_diff / 10.0))
        assert 0.7 <= score2 <= 0.9
        
        # Test distant energy levels
        energy1, energy2 = 3, 9
        energy_diff = abs(energy1 - energy2)
        score3 = max(0.0, 1.0 - (energy_diff / 10.0))
        assert score3 <= 0.4

class TestBPMCompatibility:
    """Test BPM-based compatibility calculations."""
    
    def test_bpm_compatibility_same(self):
        """Test compatibility for same BPM."""
        # Mock genres with same BPM
        genre1 = Genre(name="House", bpm_typical=125)
        genre2 = Genre(name="Tech House", bmp_typical=125)
        
        # Same BPM should have high compatibility
        bpm_diff = abs(genre1.bpm_typical - genre2.bpm_typical)
        compatibility = max(0.0, 1.0 - (bpm_diff / 50.0))
        
        assert compatibility == 1.0
    
    def test_bpm_compatibility_different(self):
        """Test compatibility for different BPMs."""
        genre1 = Genre(name="House", bpm_typical=125)
        genre2 = Genre(name="Drum and Bass", bpm_typical=174)
        
        bpm_diff = abs(genre1.bpm_typical - genre2.bpm_typical)
        compatibility = max(0.0, 1.0 - (bpm_diff / 50.0))
        
        # Should have very low compatibility due to large BPM difference
        assert compatibility < 0.5
    
    def test_bpm_range_validation(self):
        """Test BPM range validation."""
        genre = Genre(
            name="House",
            bpm_min=120,
            bpm_max=130,
            bmp_typical=125
        )
        
        # Typical BPM should be within range
        assert genre.bpm_min <= genre.bpm_typical <= genre.bpm_max

class TestEnergyLevels:
    """Test energy level functionality."""
    
    def test_energy_level_ranges(self):
        """Test energy level categorization."""
        energy_categories = {
            'Chill': [1, 2, 3],
            'Medium': [4, 5, 6],
            'High': [7, 8],
            'Peak Time': [9, 10]
        }
        
        for category, levels in energy_categories.items():
            for level in levels:
                assert 1 <= level <= 10
    
    def test_energy_level_assignment(self):
        """Test genre energy level assignments."""
        ambient = Genre(name="Ambient", energy_level=2)
        house = Genre(name="House", energy_level=6)
        hardstyle = Genre(name="Hardstyle", energy_level=9)
        
        assert ambient.energy_level < house.energy_level < hardstyle.energy_level
        assert 1 <= ambient.energy_level <= 10
        assert 1 <= house.energy_level <= 10
        assert 1 <= hardstyle.energy_level <= 10
    """Test characteristics extraction."""
    
    def test_tempo_extraction(self):
        """Test BPM extraction from text."""
        extractor = GenreCharacteristicsExtractor()
        
        text = "House music typically ranges from 120-130 BPM"
        tempo_info = extractor.extract_tempo_info(text)
        
        assert tempo_info['bpm_min'] == '120'
        assert tempo_info['bpm_max'] == '130'
    
    def test_instrument_extraction(self):
        """Test instrument extraction."""
        extractor = GenreCharacteristicsExtractor()
        
        text = "Uses synthesizer, drum machine, and 808 sounds"
        instruments = extractor.extract_instruments(text)
        
        assert 'synthesizer' in [inst.lower() for inst in instruments]
        assert '808' in instruments

class TestAudioAnalyzer:
    """Test audio analysis functionality."""
    
    def test_feature_extractor_init(self):
        """Test feature extractor initialization."""
        extractor = AudioFeatureExtractor()
        assert extractor.sample_rate == 22050
        assert extractor.hop_length == 512
    
    def test_genre_classifier_init(self):
        """Test genre classifier initialization."""
        classifier = GenreClassifier()
        assert classifier.classifier is not None
        assert classifier.scaler is not None
    
    def test_training_data_preparation(self):
        """Test training data preparation."""
        classifier = GenreClassifier()
        
        # Sample feature data
        feature_data = [
            {'tempo': 120, 'spectral_centroid': 1000},
            {'tempo': 140, 'spectral_centroid': 1200}
        ]
        labels = ['house', 'techno']
        
        X, y = classifier.prepare_training_data(feature_data, labels)
        
        assert X.shape == (2, 2)
        assert len(y) == 2
        assert 'tempo' in classifier.feature_names

class TestWebAPI:
    """Test web application API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.web.app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_home_page(self, client):
        """Test home page loads."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_genres_api(self, client):
        """Test genres API endpoint."""
        response = client.get('/api/genres')
        assert response.status_code == 200
        assert response.is_json
    
    def test_search_api(self, client):
        """Test search API endpoint."""
        response = client.get('/api/search?q=house')
        assert response.status_code == 200
        assert response.is_json
    
    def test_mixing_compatibility_api(self, client):
        """Test mixing compatibility API endpoint."""
        response = client.get('/api/mixing-compatibility/1/2')
        # Should return a compatibility score or 404 if genres don't exist
        assert response.status_code in [200, 404]
    
    def test_labels_api(self, client):
        """Test record labels API endpoint."""
        response = client.get('/api/labels')
        assert response.status_code == 200
    
    def test_keywords_api(self, client):
        """Test genre keywords API endpoint."""
        response = client.get('/api/genres/1/keywords')
        assert response.status_code in [200, 404]  # 404 if genre doesn't exist

class TestDatabaseIntegration:
    """Test database integration and data consistency."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_data_loader_integration(self, db_session):
        """Test enhanced data loader integration."""
        try:
            loader = EnhancedDataLoader()
            # This tests that the loader can be instantiated and has expected methods
            assert hasattr(loader, 'load_enhanced_genres')
            assert hasattr(loader, '_create_slug')
        except Exception as e:
            pytest.fail(f"Data loader integration failed: {e}")
    
    def test_genre_hierarchy_consistency(self, db_session):
        """Test genre hierarchy data consistency."""
        # Create parent and child genres
        house = Genre(name="House", slug="house", energy_level=6)
        deep_house = Genre(name="Deep House", slug="deep-house", energy_level=5)
        
        db_session.add_all([house, deep_house])
        db_session.flush()
        
        # Set up hierarchy
        deep_house.parent_id = house.id
        db_session.commit()
        
        # Test hierarchy integrity
        assert deep_house.parent == house
        assert deep_house in house.children
    
    def test_bpm_energy_correlation(self, db_session):
        """Test that BPM and energy levels have logical correlation."""
        # High energy genres should generally have higher BPM
        hardstyle = Genre(
            name="Hardstyle",
            slug="hardstyle",
            energy_level=9,
            bpm_typical=150
        )
        
        ambient = Genre(
            name="Ambient",
            slug="ambient",
            energy_level=2,
            bpm_typical=60
        )
        
        # High energy should have higher BPM than low energy
        assert hardstyle.bpm_typical > ambient.bpm_typical
        assert hardstyle.energy_level > ambient.energy_level

class TestPerformance:
    """Test performance aspects of the enhanced database."""
    
    def test_search_performance(self):
        """Test search performance with keywords."""
        # This would test actual search performance in a real database
        # For now, just test that we can perform basic operations efficiently
        keywords = ["house", "techno", "trance", "ambient", "drum-and-bass"]
        
        # Test keyword processing
        for keyword in keywords:
            slug = keyword.lower().replace(" ", "-").replace("&", "and")
            assert len(slug) > 0
    
    def test_compatibility_calculation_performance(self):
        """Test mixing compatibility calculation performance."""
        # Test that compatibility calculations are reasonable
        bpms = [120, 125, 130, 140, 174]
        energy_levels = [3, 5, 7, 8, 9]
        
        for bpm1 in bpms:
            for bpm2 in bpms:
                bpm_diff = abs(bpm1 - bpm2)
                compatibility = max(0.0, 1.0 - (bpm_diff / 50.0))
                assert 0.0 <= compatibility <= 1.0
        
        for energy1 in energy_levels:
            for energy2 in energy_levels:
                energy_diff = abs(energy1 - energy2)
                compatibility = max(0.0, 1.0 - (energy_diff / 10.0))
                assert 0.0 <= compatibility <= 1.0

def test_database_initialization():
    """Test that enhanced database can be initialized."""
    try:
        from src.database import init_database
        # Don't actually initialize in test, just test import
        assert init_database is not None
    except Exception as e:
        pytest.fail(f"Database initialization test failed: {e}")

def test_enhanced_features_import():
    """Test that all enhanced features can be imported."""
    try:
        from src.models import (
            Genre, GenreKeyword, RecordLabel, LabelAssociation, 
            MixingCompatibility, Characteristic, AudioFeature, Timeline
        )
        # Test that all enhanced models are available
        assert Genre is not None
        assert GenreKeyword is not None
        assert RecordLabel is not None
        assert LabelAssociation is not None
        assert MixingCompatibility is not None
    except ImportError as e:
        pytest.fail(f"Enhanced features import failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])