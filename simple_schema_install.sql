-- =====================================================
-- SIMPLE SCHEMA INSTALLATION - NO NEW DATABASE NEEDED
-- =====================================================
-- Use this if you want to skip creating a new database
-- Just creates tables in your existing Supabase database

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Core tracks table with complete metadata
CREATE TABLE IF NOT EXISTS cultural_tracks (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    file_hash VARCHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    file_modified TIMESTAMP WITH TIME ZONE,
    
    -- Raw metadata (complete extraction)
    raw_metadata JSONB,
    
    -- Parsed file information
    filename TEXT NOT NULL,
    folder_path TEXT NOT NULL,
    file_extension VARCHAR(10),
    
    -- Processing information
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_version VARCHAR(20) DEFAULT 'v3.2'
);

-- Create indexes for tracks table
CREATE UNIQUE INDEX IF NOT EXISTS idx_cultural_tracks_hash ON cultural_tracks (file_hash);
CREATE INDEX IF NOT EXISTS idx_cultural_tracks_path ON cultural_tracks (file_path);
CREATE INDEX IF NOT EXISTS idx_cultural_tracks_folder ON cultural_tracks (folder_path);
CREATE INDEX IF NOT EXISTS idx_cultural_tracks_processed ON cultural_tracks (processed_at);

-- Duplicate detection and management
CREATE TABLE IF NOT EXISTS cultural_duplicates (
    id BIGSERIAL PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,
    primary_track_id BIGINT REFERENCES cultural_tracks(id),
    duplicate_track_ids BIGINT[] NOT NULL,
    duplicate_count INTEGER NOT NULL,
    total_size_bytes BIGINT NOT NULL,
    space_waste_bytes BIGINT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for duplicates table
CREATE INDEX IF NOT EXISTS idx_cultural_duplicates_hash ON cultural_duplicates (file_hash);
CREATE INDEX IF NOT EXISTS idx_cultural_duplicates_primary ON cultural_duplicates (primary_track_id);

-- Classification results and intelligence
CREATE TABLE IF NOT EXISTS cultural_classifications (
    id BIGSERIAL PRIMARY KEY,
    track_id BIGINT REFERENCES cultural_tracks(id),
    
    -- Extracted information
    artist TEXT,
    track_name TEXT,
    remix_info TEXT,
    label TEXT,
    catalog_number TEXT,
    
    -- Genre classification
    genre TEXT,
    subgenre TEXT,
    genre_confidence DECIMAL(3,2),
    subgenre_confidence DECIMAL(3,2),
    
    -- Technical information
    bpm INTEGER,
    musical_key VARCHAR(10),
    duration_seconds INTEGER,
    
    -- Classification source and confidence
    classification_source VARCHAR(50),
    overall_confidence DECIMAL(3,2),
    needs_review BOOLEAN DEFAULT false,
    
    -- Learning and validation
    human_validated BOOLEAN DEFAULT false,
    validation_feedback TEXT,
    
    classified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for classifications table
CREATE INDEX IF NOT EXISTS idx_cultural_classifications_track ON cultural_classifications (track_id);
CREATE INDEX IF NOT EXISTS idx_cultural_classifications_artist ON cultural_classifications (artist);
CREATE INDEX IF NOT EXISTS idx_cultural_classifications_genre ON cultural_classifications (genre);
CREATE INDEX IF NOT EXISTS idx_cultural_classifications_label ON cultural_classifications (label);

-- Pattern learning and intelligence
CREATE TABLE IF NOT EXISTS cultural_patterns (
    id BIGSERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_value TEXT NOT NULL,
    
    -- Genre associations
    genre VARCHAR(100),
    subgenre VARCHAR(100),
    confidence DECIMAL(3,2) NOT NULL,
    
    -- Statistical backing
    sample_size INTEGER NOT NULL,
    success_rate DECIMAL(3,2),
    
    -- Learning metadata
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for patterns table
CREATE UNIQUE INDEX IF NOT EXISTS idx_cultural_patterns_unique ON cultural_patterns (pattern_type, pattern_value, genre, subgenre);
CREATE INDEX IF NOT EXISTS idx_cultural_patterns_type ON cultural_patterns (pattern_type);

-- Artist intelligence and profiles
CREATE TABLE IF NOT EXISTS cultural_artist_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL,
    
    -- Genre associations
    primary_genres TEXT[] DEFAULT '{}',
    secondary_genres TEXT[] DEFAULT '{}',
    genre_confidence JSONB,
    
    -- Statistics
    track_count INTEGER DEFAULT 0,
    labels_worked_with TEXT[] DEFAULT '{}',
    
    -- External information
    external_data JSONB,
    
    -- Learning metadata
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Label intelligence and profiles  
CREATE TABLE IF NOT EXISTS cultural_label_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL,
    
    -- Genre specialization
    primary_genres TEXT[] DEFAULT '{}',
    genre_confidence JSONB,
    
    -- Statistics
    release_count INTEGER DEFAULT 0,
    artists_signed TEXT[] DEFAULT '{}',
    
    -- External information
    external_data JSONB,
    
    -- Learning metadata
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API access logs
CREATE TABLE IF NOT EXISTS cultural_api_requests (
    id BIGSERIAL PRIMARY KEY,
    
    -- Request information
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_path TEXT,
    
    -- Request details
    file_hash VARCHAR(64),
    file_path TEXT,
    
    -- Response information
    response_time_ms INTEGER,
    status_code INTEGER,
    classification_returned JSONB,
    
    -- Metadata
    client_ip INET,
    user_agent TEXT,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SEED DATA: Electronic Music Knowledge Base
-- =====================================================

-- Pre-populate with electronic music intelligence
INSERT INTO cultural_label_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Anjunabeats', 'anjunabeats', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.95, "Progressive House": 0.3}', '{"founded": 2000, "country": "UK"}'),
('Defected Records', 'defected', ARRAY['House', 'Deep House'], '{"House": 0.9, "Deep House": 0.8}', '{"founded": 1999, "country": "UK"}'),
('Monstercat', 'monstercat', ARRAY['Electronic', 'Dubstep', 'Future Bass'], '{"Dubstep": 0.7, "Electronic": 0.9}', '{"founded": 2011, "country": "Canada"}'),
('Mau5trap', 'mau5trap', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.8}', '{"founded": 2007, "owner": "Deadmau5"}')
ON CONFLICT (name) DO NOTHING;

INSERT INTO cultural_artist_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Deadmau5', 'deadmau5', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.9}', '{"real_name": "Joel Zimmerman", "country": "Canada"}'),
('Armin van Buuren', 'arminvanbuuren', ARRAY['Trance', 'Uplifting Trance'], '{"Trance": 0.95}', '{"country": "Netherlands", "label": "Armada Music"}'),
('Skrillex', 'skrillex', ARRAY['Dubstep', 'Trap'], '{"Dubstep": 0.9}', '{"real_name": "Sonny Moore", "label": "OWSLA"}'),
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
-- VERIFICATION QUERIES
-- =====================================================

-- Check what was created
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename LIKE 'cultural_%'
ORDER BY tablename;

-- Check seeded data
SELECT 'Labels' as type, COUNT(*) as count FROM cultural_label_profiles
UNION ALL
SELECT 'Artists' as type, COUNT(*) as count FROM cultural_artist_profiles
UNION ALL
SELECT 'Patterns' as type, COUNT(*) as count FROM cultural_patterns;

-- Success message
SELECT '🎵 Cultural Intelligence System v3.2 - Database Ready! 🚀' as status;