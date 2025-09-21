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
                    'name': 'Progressive Trance',
                    'description': 'Longer format trance with gradual buildups and breakdowns',
                    'energy_level': 9,
                    'bpm_min': 130,
                    'bpm_max': 140,
                    'bpm_typical': 135,
                    'origin_year': 1993,
                    'origin_location': 'UK'
                },
                {
                    'name': 'Drum and Bass',
                    'description': 'Fast breakbeats with heavy bass lines',
                    'energy_level': 9,
                    'bpm_min': 160,
                    'bpm_max': 180,
                    'bpm_typical': 174,
                    'origin_year': 1992,
                    'origin_location': 'London, UK'
                },
                {
                    'name': 'Liquid Drum and Bass',
                    'description': 'Smooth, jazzy drum and bass with melodic elements',
                    'energy_level': 7,
                    'bpm_min': 170,
                    'bpm_max': 180,
                    'bpm_typical': 174,
                    'origin_year': 1996,
                    'origin_location': 'London, UK'
                },
                {
                    'name': 'Dubstep',
                    'description': 'Bass-heavy electronic music with syncopated rhythms',
                    'energy_level': 8,
                    'bpm_min': 135,
                    'bpm_max': 145,
                    'bpm_typical': 140,
                    'origin_year': 2002,
                    'origin_location': 'London, UK'
                },
                {
                    'name': 'Ambient',
                    'description': 'Atmospheric, textural electronic music',
                    'energy_level': 3,
                    'bpm_min': 60,
                    'bpm_max': 90,
                    'bpm_typical': 75,
                    'origin_year': 1978,
                    'origin_location': 'UK'
                },
                {
                    'name': 'Breakbeat',
                    'description': 'Electronic music featuring broken rhythm patterns',
                    'energy_level': 8,
                    'bpm_min': 130,
                    'bpm_max': 150,
                    'bpm_typical': 140,
                    'origin_year': 1990,
                    'origin_location': 'UK'
                }
            ]
            
            loaded_count = 0\n            for genre_data in enhanced_genres:\n                existing = db.query(Genre).filter(Genre.name == genre_data['name']).first()\n                if not existing:\n                    genre = Genre(\n                        name=genre_data['name'],\n                        slug=self._create_slug(genre_data['name']),\n                        description=genre_data['description'],\n                        energy_level=genre_data['energy_level'],\n                        bpm_min=genre_data['bpm_min'],\n                        bpm_max=genre_data['bpm_max'],\n                        bpm_typical=genre_data['bpm_typical'],\n                        origin_year=genre_data['origin_year'],\n                        origin_location=genre_data['origin_location']\n                    )\n                    db.add(genre)\n                    loaded_count += 1\n            \n            db.commit()\n            print(f\"Loaded {loaded_count} enhanced genres\")\n        finally:\n            db.close()\n    \n    def create_genre_hierarchy(self):\n        \"\"\"Create parent-child relationships between genres.\"\"\"\n        db: Session = next(get_db())\n        try:\n            # Define hierarchical relationships\n            hierarchies = [\n                ('House', 'Deep House'),\n                ('House', 'Tech House'),\n                ('Techno', 'Minimal Techno'),\n                ('Trance', 'Progressive Trance'),\n                ('Drum and Bass', 'Liquid Drum and Bass'),\n            ]\n            \n            created_count = 0\n            for parent_name, child_name in hierarchies:\n                parent = db.query(Genre).filter(Genre.name == parent_name).first()\n                child = db.query(Genre).filter(Genre.name == child_name).first()\n                \n                if parent and child and child not in parent.subgenres:\n                    parent.subgenres.append(child)\n                    created_count += 1\n            \n            db.commit()\n            print(f\"Created {created_count} genre hierarchy relationships\")\n        finally:\n            db.close()\n    \n    def load_genre_keywords(self):\n        \"\"\"Load keywords and aliases for genre detection.\"\"\"\n        db: Session = next(get_db())\n        try:\n            keywords_data = {\n                'House': [\n                    {'keyword': 'house music', 'type': 'alias', 'weight': 1.0},\n                    {'keyword': 'four on the floor', 'type': 'descriptor', 'weight': 0.9},\n                    {'keyword': 'disco house', 'type': 'tag', 'weight': 0.8},\n                    {'keyword': 'soulful house', 'type': 'tag', 'weight': 0.8},\n                    {'keyword': 'jackin house', 'type': 'tag', 'weight': 0.7}\n                ],\n                'Deep House': [\n                    {'keyword': 'deep', 'type': 'descriptor', 'weight': 0.9},\n                    {'keyword': 'soulful', 'type': 'descriptor', 'weight': 0.8},\n                    {'keyword': 'jazzy house', 'type': 'tag', 'weight': 0.7}\n                ],\n                'Tech House': [\n                    {'keyword': 'tech house', 'type': 'alias', 'weight': 1.0},\n                    {'keyword': 'techy', 'type': 'descriptor', 'weight': 0.8},\n                    {'keyword': 'minimal house', 'type': 'tag', 'weight': 0.7}\n                ],\n                'Techno': [\n                    {'keyword': 'techno', 'type': 'alias', 'weight': 1.0},\n                    {'keyword': 'detroit techno', 'type': 'tag', 'weight': 0.9},\n                    {'keyword': 'industrial', 'type': 'descriptor', 'weight': 0.7},\n                    {'keyword': 'hard techno', 'type': 'tag', 'weight': 0.8}\n                ],\n                'Trance': [\n                    {'keyword': 'trance', 'type': 'alias', 'weight': 1.0},\n                    {'keyword': 'uplifting', 'type': 'descriptor', 'weight': 0.8},\n                    {'keyword': 'euphoric', 'type': 'descriptor', 'weight': 0.8},\n                    {'keyword': 'psychedelic trance', 'type': 'tag', 'weight': 0.7},\n                    {'keyword': 'psytrance', 'type': 'alias', 'weight': 0.7}\n                ],\n                'Drum and Bass': [\n                    {'keyword': 'dnb', 'type': 'alias', 'weight': 1.0},\n                    {'keyword': 'jungle', 'type': 'tag', 'weight': 0.9},\n                    {'keyword': 'breakbeat', 'type': 'descriptor', 'weight': 0.8},\n                    {'keyword': 'bass music', 'type': 'tag', 'weight': 0.7}\n                ],\n                'Dubstep': [\n                    {'keyword': 'dubstep', 'type': 'alias', 'weight': 1.0},\n                    {'keyword': 'wobble', 'type': 'descriptor', 'weight': 0.8},\n                    {'keyword': 'bass drop', 'type': 'descriptor', 'weight': 0.7},\n                    {'keyword': 'brostep', 'type': 'tag', 'weight': 0.6}\n                ],\n                'Ambient': [\n                    {'keyword': 'ambient', 'type': 'alias', 'weight': 1.0},\n                    {'keyword': 'atmospheric', 'type': 'descriptor', 'weight': 0.8},\n                    {'keyword': 'soundscape', 'type': 'descriptor', 'weight': 0.7},\n                    {'keyword': 'dark ambient', 'type': 'tag', 'weight': 0.7}\n                ]\n            }\n            \n            loaded_count = 0\n            for genre_name, keywords in keywords_data.items():\n                genre = db.query(Genre).filter(Genre.name == genre_name).first()\n                if genre:\n                    for keyword_data in keywords:\n                        existing = db.query(GenreKeyword).filter(\n                            GenreKeyword.genre_id == genre.id,\n                            GenreKeyword.keyword == keyword_data['keyword']\n                        ).first()\n                        \n                        if not existing:\n                            keyword = GenreKeyword(\n                                genre_id=genre.id,\n                                keyword=keyword_data['keyword'],\n                                keyword_type=keyword_data['type'],\n                                weight=keyword_data['weight']\n                            )\n                            db.add(keyword)\n                            loaded_count += 1\n            \n            db.commit()\n            print(f\"Loaded {loaded_count} genre keywords\")\n        finally:\n            db.close()\n    \n    def load_record_labels(self):\n        \"\"\"Load record labels and their genre associations.\"\"\"\n        db: Session = next(get_db())\n        try:\n            labels_data = [\n                {\n                    'name': 'Defected Records',\n                    'founded_year': 1999,\n                    'country': 'UK',\n                    'website': 'https://defected.com',\n                    'description': 'Leading house music label',\n                    'genres': [('House', 0.9), ('Deep House', 0.8), ('Tech House', 0.7)]\n                },\n                {\n                    'name': 'Ostgut Ton',\n                    'founded_year': 2005,\n                    'country': 'Germany',\n                    'description': 'Berghain/Panorama Bar label',\n                    'genres': [('Techno', 0.9), ('Minimal Techno', 0.8)]\n                },\n                {\n                    'name': 'Anjunabeats',\n                    'founded_year': 2000,\n                    'country': 'UK',\n                    'website': 'https://anjunabeats.com',\n                    'description': 'Progressive and trance label',\n                    'genres': [('Trance', 0.9), ('Progressive Trance', 0.9)]\n                },\n                {\n                    'name': 'Hospital Records',\n                    'founded_year': 1996,\n                    'country': 'UK',\n                    'website': 'https://hospitalrecords.com',\n                    'description': 'Premier drum and bass label',\n                    'genres': [('Drum and Bass', 0.9), ('Liquid Drum and Bass', 0.8)]\n                },\n                {\n                    'name': 'Warp Records',\n                    'founded_year': 1989,\n                    'country': 'UK',\n                    'website': 'https://warp.net',\n                    'description': 'Electronic and experimental music',\n                    'genres': [('Ambient', 0.7), ('Breakbeat', 0.6)]\n                }\n            ]\n            \n            loaded_count = 0\n            for label_data in labels_data:\n                existing = db.query(RecordLabel).filter(RecordLabel.name == label_data['name']).first()\n                if not existing:\n                    label = RecordLabel(\n                        name=label_data['name'],\n                        founded_year=label_data['founded_year'],\n                        country=label_data['country'],\n                        website=label_data.get('website'),\n                        description=label_data['description']\n                    )\n                    db.add(label)\n                    db.flush()  # Get the ID\n                    \n                    # Add genre associations\n                    for genre_name, strength in label_data['genres']:\n                        genre = db.query(Genre).filter(Genre.name == genre_name).first()\n                        if genre:\n                            association = LabelAssociation(\n                                genre_id=genre.id,\n                                label_id=label.id,\n                                association_strength=strength\n                            )\n                            db.add(association)\n                    \n                    loaded_count += 1\n            \n            db.commit()\n            print(f\"Loaded {loaded_count} record labels with associations\")\n        finally:\n            db.close()\n    \n    def calculate_mixing_compatibility(self):\n        \"\"\"Calculate and store mixing compatibility between genres.\"\"\"\n        db: Session = next(get_db())\n        try:\n            genres = db.query(Genre).all()\n            compatibility_count = 0\n            \n            for i, genre1 in enumerate(genres):\n                for genre2 in genres[i+1:]:  # Avoid duplicates\n                    # Check if compatibility already exists\n                    existing = db.query(MixingCompatibility).filter(\n                        ((MixingCompatibility.genre1_id == genre1.id) & (MixingCompatibility.genre2_id == genre2.id)) |\n                        ((MixingCompatibility.genre1_id == genre2.id) & (MixingCompatibility.genre2_id == genre1.id))\n                    ).first()\n                    \n                    if not existing:\n                        compatibility = self._calculate_genre_compatibility(genre1, genre2)\n                        \n                        mixing_comp = MixingCompatibility(\n                            genre1_id=genre1.id,\n                            genre2_id=genre2.id,\n                            compatibility_score=compatibility['overall'],\n                            bpm_compatibility=compatibility['bpm'],\n                            energy_compatibility=compatibility['energy']\n                        )\n                        db.add(mixing_comp)\n                        compatibility_count += 1\n            \n            db.commit()\n            print(f\"Calculated {compatibility_count} mixing compatibilities\")\n        finally:\n            db.close()\n    \n    def _calculate_genre_compatibility(self, genre1: Genre, genre2: Genre) -> Dict[str, float]:\n        \"\"\"Calculate compatibility scores between two genres.\"\"\"\n        # BPM compatibility (closer BPMs = higher compatibility)\n        bpm_compatibility = 0.0\n        if genre1.bpm_typical and genre2.bpm_typical:\n            bpm_diff = abs(genre1.bpm_typical - genre2.bpm_typical)\n            # Normalize to 0-1 scale (0 diff = 1.0, 50+ diff = 0.0)\n            bpm_compatibility = max(0.0, 1.0 - (bpm_diff / 50.0))\n        \n        # Energy compatibility (similar energy levels mix better)\n        energy_compatibility = 0.0\n        if genre1.energy_level and genre2.energy_level:\n            energy_diff = abs(genre1.energy_level - genre2.energy_level)\n            # Normalize to 0-1 scale (0 diff = 1.0, 5+ diff = 0.0)\n            energy_compatibility = max(0.0, 1.0 - (energy_diff / 5.0))\n        \n        # Overall compatibility (average of individual scores)\n        overall = (bmp_compatibility + energy_compatibility) / 2.0\n        \n        return {\n            'overall': overall,\n            'bpm': bpm_compatibility,\n            'energy': energy_compatibility\n        }\n    \n    def _create_slug(self, name: str) -> str:\n        \"\"\"Create URL-friendly slug from genre name.\"\"\"\n        return name.lower().replace(' ', '-').replace('&', 'and')\n    \n    def load_all_enhanced_data(self):\n        \"\"\"Load all enhanced data features.\"\"\"\n        print(\"Loading enhanced genre taxonomy data...\")\n        \n        self.load_enhanced_genres()\n        self.create_genre_hierarchy()\n        self.load_genre_keywords()\n        self.load_record_labels()\n        self.calculate_mixing_compatibility()\n        \n        print(\"Enhanced data loading complete!\")\n\nif __name__ == \"__main__\":\n    loader = EnhancedDataLoader()\n    loader.load_all_enhanced_data()