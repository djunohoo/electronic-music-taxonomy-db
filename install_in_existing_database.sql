-- =====================================================
-- CULTURAL INTELLIGENCE SYSTEM - EXISTING DATABASE VERSION
-- =====================================================
-- Run this in your current MetaCrate database
-- Uses prefixed table names to avoid conflicts

-- Enable extensions first
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Core tracks table
CREATE TABLE cultural_tracks (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_size BIGINT NOT NULL,
    file_modified TIMESTAMP WITH TIME ZONE,
    raw_metadata JSONB,
    filename TEXT NOT NULL,
    folder_path TEXT NOT NULL,
    file_extension VARCHAR(10),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_version VARCHAR(20) DEFAULT 'v3.2'
);

-- Duplicate detection
CREATE TABLE cultural_duplicates (
    id BIGSERIAL PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,
    primary_track_id BIGINT REFERENCES cultural_tracks(id),
    duplicate_track_ids BIGINT[] NOT NULL,
    duplicate_count INTEGER NOT NULL,
    total_size_bytes BIGINT NOT NULL,
    space_waste_bytes BIGINT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Classifications
CREATE TABLE cultural_classifications (
    id BIGSERIAL PRIMARY KEY,
    track_id BIGINT REFERENCES cultural_tracks(id),
    artist TEXT,
    track_name TEXT,
    remix_info TEXT,
    label TEXT,
    catalog_number TEXT,
    genre TEXT,
    subgenre TEXT,
    genre_confidence DECIMAL(3,2),
    subgenre_confidence DECIMAL(3,2),
    bpm INTEGER,
    musical_key VARCHAR(10),
    duration_seconds INTEGER,
    classification_source VARCHAR(50),
    overall_confidence DECIMAL(3,2),
    needs_review BOOLEAN DEFAULT false,
    human_validated BOOLEAN DEFAULT false,
    validation_feedback TEXT,
    classified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Patterns
CREATE TABLE cultural_patterns (
    id BIGSERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_value TEXT NOT NULL,
    genre VARCHAR(100),
    subgenre VARCHAR(100),
    confidence DECIMAL(3,2) NOT NULL,
    sample_size INTEGER NOT NULL,
    success_rate DECIMAL(3,2),
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(pattern_type, pattern_value, genre, subgenre)
);

-- Artist profiles
CREATE TABLE cultural_artist_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL,
    primary_genres TEXT[] DEFAULT '{}',
    secondary_genres TEXT[] DEFAULT '{}',
    genre_confidence JSONB,
    track_count INTEGER DEFAULT 0,
    labels_worked_with TEXT[] DEFAULT '{}',
    external_data JSONB,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Label profiles
CREATE TABLE cultural_label_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL,
    primary_genres TEXT[] DEFAULT '{}',
    genre_confidence JSONB,
    release_count INTEGER DEFAULT 0,
    artists_signed TEXT[] DEFAULT '{}',
    external_data JSONB,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API logs
CREATE TABLE cultural_api_requests (
    id BIGSERIAL PRIMARY KEY,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_path TEXT,
    file_hash VARCHAR(64),
    file_path TEXT,
    response_time_ms INTEGER,
    status_code INTEGER,
    classification_returned JSONB,
    client_ip INET,
    user_agent TEXT,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_cultural_tracks_hash ON cultural_tracks(file_hash);
CREATE INDEX idx_cultural_tracks_path ON cultural_tracks(file_path);
CREATE INDEX idx_cultural_duplicates_hash ON cultural_duplicates(file_hash);
CREATE INDEX idx_cultural_classifications_track ON cultural_classifications(track_id);
CREATE INDEX idx_cultural_classifications_artist ON cultural_classifications(artist);
CREATE INDEX idx_cultural_classifications_genre ON cultural_classifications(genre);

-- Seed electronic music data
INSERT INTO cultural_label_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Anjunabeats', 'anjunabeats', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.95}', '{"founded": 2000, "country": "UK"}'),
('Defected Records', 'defected', ARRAY['House', 'Deep House'], '{"House": 0.9, "Deep House": 0.8}', '{"founded": 1999, "country": "UK"}'),
('Monstercat', 'monstercat', ARRAY['Electronic', 'Dubstep'], '{"Dubstep": 0.7, "Electronic": 0.9}', '{"founded": 2011, "country": "Canada"}'),
('Mau5trap', 'mau5trap', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.8}', '{"founded": 2007, "owner": "Deadmau5"}')
ON CONFLICT (name) DO NOTHING;

INSERT INTO cultural_artist_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Deadmau5', 'deadmau5', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.9}', '{"real_name": "Joel Zimmerman", "country": "Canada"}'),
('Armin van Buuren', 'arminvanbuuren', ARRAY['Trance', 'Uplifting Trance'], '{"Trance": 0.95}', '{"country": "Netherlands"}'),
('Skrillex', 'skrillex', ARRAY['Dubstep', 'Trap'], '{"Dubstep": 0.9}', '{"real_name": "Sonny Moore"}'),
('Above & Beyond', 'aboveandbeyond', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.9}', '{"country": "UK", "label": "Anjunabeats"}')
ON CONFLICT (name) DO NOTHING;

INSERT INTO cultural_patterns (pattern_type, pattern_value, genre, subgenre, confidence, sample_size, success_rate) VALUES
('filename', '(Original Mix)', 'House', NULL, 0.7, 1000, 0.8),
('filename', '(Extended Mix)', 'Trance', NULL, 0.8, 300, 0.85),
('folder', 'Trance', 'Trance', NULL, 0.95, 5000, 0.95),
('folder', 'House', 'House', NULL, 0.95, 5000, 0.95),
('metadata', 'Trance', 'Trance', NULL, 0.9, 2000, 0.9),
('metadata', 'House', 'House', NULL, 0.9, 2000, 0.9)
ON CONFLICT (pattern_type, pattern_value, genre, subgenre) DO NOTHING;

-- =====================================================
-- AI TRAINING ZONE - Interactive Learning Features
-- =====================================================

-- Training sessions for human feedback
CREATE TABLE cultural_training_sessions (
    id BIGSERIAL PRIMARY KEY,
    question_type VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    context_data JSONB NOT NULL,
    track_id BIGINT REFERENCES cultural_tracks(id),
    file_path TEXT,
    filename TEXT,
    current_classification JSONB,
    confidence_level DECIMAL(3,2),
    human_response JSONB,
    response_text TEXT,
    processing_time_seconds INTEGER,
    accuracy_improvement DECIMAL(3,2),
    session_ip INET,
    asked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    answered_at TIMESTAMP WITH TIME ZONE,
    applied_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Training queue for pending questions
CREATE TABLE cultural_training_queue (
    id BIGSERIAL PRIMARY KEY,
    priority INTEGER DEFAULT 1,
    question_type VARCHAR(50) NOT NULL,
    track_id BIGINT REFERENCES cultural_tracks(id),
    uncertainty_score DECIMAL(3,2),
    context_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Training indexes
CREATE INDEX idx_training_sessions_status ON cultural_training_sessions(status);
CREATE INDEX idx_training_sessions_asked ON cultural_training_sessions(asked_at);
CREATE INDEX idx_training_queue_priority ON cultural_training_queue(priority DESC, created_at);
CREATE INDEX idx_training_queue_status ON cultural_training_queue(status);

-- Seed example training scenarios for livestream demonstration
INSERT INTO cultural_training_queue (question_type, uncertainty_score, context_data, priority) VALUES
('genre_uncertainty', 0.65, '{"genres": ["House", "Techno"], "bpm": 128, "reason": "BPM suggests House but percussion patterns indicate Techno"}', 1),
('artist_profiling', 0.70, '{"artist": "Unknown Artist", "track_count": 12, "genre_distribution": {"House": 6, "Trance": 4, "Techno": 2}}', 2),
('label_specialization', 0.75, '{"label": "New Label", "usual_genre": "Trance", "this_track_genre": "House", "confidence_drop": 0.3}', 1);

-- Success verification
SELECT 
    'CULTURAL INTELLIGENCE SYSTEM WITH AI TRAINING INSTALLED!' as status,
    COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_name LIKE 'cultural_%';

SELECT 'SEEDED DATA READY' as status,
    (SELECT COUNT(*) FROM cultural_label_profiles) as labels,
    (SELECT COUNT(*) FROM cultural_artist_profiles) as artists,
    (SELECT COUNT(*) FROM cultural_patterns) as patterns,
    (SELECT COUNT(*) FROM cultural_training_queue WHERE status = 'pending') as pending_questions;