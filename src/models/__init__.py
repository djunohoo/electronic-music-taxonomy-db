"""
Database models for the Electronic Music Taxonomy Database.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped

Base = declarative_base()

# Association table for many-to-many relationship between genres
genre_relationships = Table(
    'genre_relationships',
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('genres.id'), primary_key=True),
    Column('child_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

# Association table for genre compatibility (mixing)
genre_compatibility = Table(
    'genre_compatibility',
    Base.metadata,
    Column('genre1_id', Integer, ForeignKey('genres.id'), primary_key=True),
    Column('genre2_id', Integer, ForeignKey('genres.id'), primary_key=True),
    Column('compatibility_score', Float, default=0.0)  # 0.0 to 1.0 compatibility
)

# Association table for related genres (similarity)
genre_similarity = Table(
    'genre_similarity',
    Base.metadata,
    Column('genre1_id', Integer, ForeignKey('genres.id'), primary_key=True),
    Column('genre2_id', Integer, ForeignKey('genres.id'), primary_key=True),
    Column('similarity_score', Float, default=0.0)  # 0.0 to 1.0 similarity
)

class Genre(Base):
    """Primary genre classification model."""
    __tablename__ = 'genres'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = Column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = Column(Text)
    wikipedia_url: Mapped[Optional[str]] = Column(String(500))
    origin_year: Mapped[Optional[int]] = Column(Integer)
    origin_location: Mapped[Optional[str]] = Column(String(200))
    
    # Enhanced taxonomy features
    energy_level: Mapped[Optional[int]] = Column(Integer)  # 1-10 scale
    bpm_min: Mapped[Optional[int]] = Column(Integer)
    bpm_max: Mapped[Optional[int]] = Column(Integer)
    bpm_typical: Mapped[Optional[int]] = Column(Integer)
    
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    characteristics: Mapped[List["Characteristic"]] = relationship("Characteristic", back_populates="genre")
    audio_features: Mapped[List["AudioFeature"]] = relationship("AudioFeature", back_populates="genre")
    keywords: Mapped[List["GenreKeyword"]] = relationship("GenreKeyword", back_populates="genre")
    label_associations: Mapped[List["LabelAssociation"]] = relationship("LabelAssociation", back_populates="genre")
    
    # Self-referential many-to-many for subgenres
    subgenres: Mapped[List["Genre"]] = relationship(
        "Genre",
        secondary=genre_relationships,
        primaryjoin=id == genre_relationships.c.parent_id,
        secondaryjoin=id == genre_relationships.c.child_id,
        back_populates="parent_genres"
    )
    
    parent_genres: Mapped[List["Genre"]] = relationship(
        "Genre",
        secondary=genre_relationships,
        primaryjoin=id == genre_relationships.c.child_id,
        secondaryjoin=id == genre_relationships.c.parent_id,
        back_populates="subgenres"
    )
    
    # Mixing compatibility relationships
    compatible_genres: Mapped[List["Genre"]] = relationship(
        "Genre",
        secondary=genre_compatibility,
        primaryjoin=id == genre_compatibility.c.genre1_id,
        secondaryjoin=id == genre_compatibility.c.genre2_id,
        back_populates="compatible_with"
    )
    
    compatible_with: Mapped[List["Genre"]] = relationship(
        "Genre",
        secondary=genre_compatibility,
        primaryjoin=id == genre_compatibility.c.genre2_id,
        secondaryjoin=id == genre_compatibility.c.genre1_id,
        back_populates="compatible_genres"
    )
    
    # Similar genres relationships
    similar_genres: Mapped[List["Genre"]] = relationship(
        "Genre",
        secondary=genre_similarity,
        primaryjoin=id == genre_similarity.c.genre1_id,
        secondaryjoin=id == genre_similarity.c.genre2_id,
        back_populates="similar_to"
    )
    
    similar_to: Mapped[List["Genre"]] = relationship(
        "Genre",
        secondary=genre_similarity,
        primaryjoin=id == genre_similarity.c.genre2_id,
        secondaryjoin=id == genre_similarity.c.genre1_id,
        back_populates="similar_genres"
    )
    
    def __repr__(self) -> str:
        return f"<Genre(name='{self.name}', year={self.origin_year})>"

class Characteristic(Base):
    """Genre characteristics and identifying features."""
    __tablename__ = 'characteristics'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    genre_id: Mapped[int] = Column(Integer, ForeignKey('genres.id'), nullable=False)
    characteristic_type: Mapped[str] = Column(String(50), nullable=False)  # 'tempo', 'instruments', 'style', etc.
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    value: Mapped[Optional[str]] = Column(String(200))  # For numeric or specific values
    
    # Relationships
    genre: Mapped["Genre"] = relationship("Genre", back_populates="characteristics")
    
    def __repr__(self) -> str:
        return f"<Characteristic(genre='{self.genre.name}', type='{self.characteristic_type}', name='{self.name}')>"

class AudioFeature(Base):
    """Audio analysis features for genre identification."""
    __tablename__ = 'audio_features'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    genre_id: Mapped[int] = Column(Integer, ForeignKey('genres.id'), nullable=False)
    
    # Tempo and rhythm features
    bpm_min: Mapped[Optional[float]] = Column(Float)
    bpm_max: Mapped[Optional[float]] = Column(Float)
    bpm_typical: Mapped[Optional[float]] = Column(Float)
    time_signature: Mapped[Optional[str]] = Column(String(10))
    
    # Harmonic features
    key_preferences: Mapped[Optional[str]] = Column(String(100))  # Common keys
    chord_progressions: Mapped[Optional[str]] = Column(Text)  # Typical progressions
    
    # Spectral features
    frequency_range: Mapped[Optional[str]] = Column(String(50))
    dominant_frequencies: Mapped[Optional[str]] = Column(String(200))
    
    # Timbre and texture
    typical_instruments: Mapped[Optional[str]] = Column(Text)
    production_techniques: Mapped[Optional[str]] = Column(Text)
    
    # Relationships
    genre: Mapped["Genre"] = relationship("Genre", back_populates="audio_features")
    
    def __repr__(self) -> str:
        return f"<AudioFeature(genre='{self.genre.name}', bpm={self.bpm_typical})>"

class Timeline(Base):
    """Historical timeline of genre development."""
    __tablename__ = 'timeline'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    genre_id: Mapped[int] = Column(Integer, ForeignKey('genres.id'), nullable=False)
    year: Mapped[int] = Column(Integer, nullable=False)
    event_type: Mapped[str] = Column(String(50), nullable=False)  # 'emergence', 'peak', 'evolution', etc.
    description: Mapped[str] = Column(Text, nullable=False)
    location: Mapped[Optional[str]] = Column(String(200))
    key_artists: Mapped[Optional[str]] = Column(Text)
    influential_tracks: Mapped[Optional[str]] = Column(Text)
    
    # Relationships
    genre: Mapped["Genre"] = relationship("Genre")
    
    def __repr__(self) -> str:
        return f"<Timeline(genre='{self.genre.name}', year={self.year}, event='{self.event_type}')>"

class GenreKeyword(Base):
    """Keywords and aliases for genre detection."""
    __tablename__ = 'genre_keywords'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    genre_id: Mapped[int] = Column(Integer, ForeignKey('genres.id'), nullable=False)
    keyword: Mapped[str] = Column(String(100), nullable=False)
    keyword_type: Mapped[str] = Column(String(20), nullable=False)  # 'alias', 'tag', 'descriptor'
    weight: Mapped[float] = Column(Float, default=1.0)  # Importance weight for detection
    
    # Relationships
    genre: Mapped["Genre"] = relationship("Genre", back_populates="keywords")
    
    def __repr__(self) -> str:
        return f"<GenreKeyword(genre='{self.genre.name}', keyword='{self.keyword}', type='{self.keyword_type}')>"

class RecordLabel(Base):
    """Record labels and their information."""
    __tablename__ = 'record_labels'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(200), nullable=False, unique=True)
    founded_year: Mapped[Optional[int]] = Column(Integer)
    country: Mapped[Optional[str]] = Column(String(100))
    website: Mapped[Optional[str]] = Column(String(500))
    description: Mapped[Optional[str]] = Column(Text)
    
    # Relationships
    genre_associations: Mapped[List["LabelAssociation"]] = relationship("LabelAssociation", back_populates="label")
    
    def __repr__(self) -> str:
        return f"<RecordLabel(name='{self.name}', country='{self.country}')>"

class LabelAssociation(Base):
    """Association between record labels and genres."""
    __tablename__ = 'label_associations'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    genre_id: Mapped[int] = Column(Integer, ForeignKey('genres.id'), nullable=False)
    label_id: Mapped[int] = Column(Integer, ForeignKey('record_labels.id'), nullable=False)
    association_strength: Mapped[float] = Column(Float, default=1.0)  # 0.0 to 1.0
    notes: Mapped[Optional[str]] = Column(Text)
    
    # Relationships
    genre: Mapped["Genre"] = relationship("Genre", back_populates="label_associations")
    label: Mapped["RecordLabel"] = relationship("RecordLabel", back_populates="genre_associations")
    
    def __repr__(self) -> str:
        return f"<LabelAssociation(genre='{self.genre.name}', label='{self.label.name}', strength={self.association_strength})>"

class MixingCompatibility(Base):
    """Detailed mixing compatibility between genres."""
    __tablename__ = 'mixing_compatibility'
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    genre1_id: Mapped[int] = Column(Integer, ForeignKey('genres.id'), nullable=False)
    genre2_id: Mapped[int] = Column(Integer, ForeignKey('genres.id'), nullable=False)
    compatibility_score: Mapped[float] = Column(Float, nullable=False)  # 0.0 to 1.0
    bpm_compatibility: Mapped[Optional[float]] = Column(Float)  # BPM mixing compatibility
    key_compatibility: Mapped[Optional[float]] = Column(Float)  # Harmonic compatibility
    energy_compatibility: Mapped[Optional[float]] = Column(Float)  # Energy level compatibility
    notes: Mapped[Optional[str]] = Column(Text)
    
    # Relationships
    genre1: Mapped["Genre"] = relationship("Genre", foreign_keys=[genre1_id])
    genre2: Mapped["Genre"] = relationship("Genre", foreign_keys=[genre2_id])
    
    def __repr__(self) -> str:
        return f"<MixingCompatibility('{self.genre1.name}' <-> '{self.genre2.name}', score={self.compatibility_score})>"