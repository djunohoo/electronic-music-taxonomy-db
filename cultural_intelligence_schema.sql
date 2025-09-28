-- =====================================================
-- CULTURAL INTELLIGENCE SYSTEM v3.2 - DATABASE SCHEMA  
-- =====================================================
-- Self-hosted Supabase at 172.22.17.138
-- Complete electronic music taxonomy and intelligence system
-- 
-- PREREQUISITE: Database must exist! Run create_database.sql first
-- CONNECT TO: cultural_intelligence database before running this

-- Ensure we're connected to the right database
\c cultural_intelligence

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Core tracks table with complete metadata
CREATE TABLE IF NOT EXISTS tracks (
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_tracks_hash ON tracks (file_hash);
CREATE INDEX IF NOT EXISTS idx_tracks_path ON tracks (file_path);
CREATE INDEX IF NOT EXISTS idx_tracks_folder ON tracks (folder_path);
CREATE INDEX IF NOT EXISTS idx_tracks_processed ON tracks (processed_at);

-- Duplicate detection and management
CREATE TABLE IF NOT EXISTS duplicates (
    id BIGSERIAL PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,
    primary_track_id BIGINT REFERENCES tracks(id),
    duplicate_track_ids BIGINT[] NOT NULL,
    duplicate_count INTEGER NOT NULL,
    total_size_bytes BIGINT NOT NULL,
    space_waste_bytes BIGINT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for duplicates table
CREATE INDEX IF NOT EXISTS idx_duplicates_hash ON duplicates (file_hash);
CREATE INDEX IF NOT EXISTS idx_duplicates_primary ON duplicates (primary_track_id);

-- Classification results and intelligence
CREATE TABLE IF NOT EXISTS classifications (
    id BIGSERIAL PRIMARY KEY,
    track_id BIGINT REFERENCES tracks(id),
    
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
    classification_source VARCHAR(50), -- 'filename', 'metadata', 'pattern', 'audio'
    overall_confidence DECIMAL(3,2),
    needs_review BOOLEAN DEFAULT false,
    
    -- Learning and validation
    human_validated BOOLEAN DEFAULT false,
    validation_feedback TEXT,
    
    classified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for classifications table
CREATE INDEX IF NOT EXISTS idx_classifications_track ON classifications (track_id);
CREATE INDEX IF NOT EXISTS idx_classifications_artist ON classifications (artist);
CREATE INDEX IF NOT EXISTS idx_classifications_genre ON classifications (genre);
CREATE INDEX IF NOT EXISTS idx_classifications_label ON classifications (label);
CREATE INDEX IF NOT EXISTS idx_classifications_confidence ON classifications (overall_confidence);

-- Pattern learning and intelligence
CREATE TABLE IF NOT EXISTS patterns (
    id BIGSERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL, -- 'filename', 'folder', 'metadata', 'artist', 'label'
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_patterns_unique ON patterns (pattern_type, pattern_value, genre, subgenre);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns (pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns (confidence);

-- Artist intelligence and profiles
CREATE TABLE IF NOT EXISTS artist_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL, -- For matching variations
    
    -- Genre associations
    primary_genres TEXT[] DEFAULT '{}',
    secondary_genres TEXT[] DEFAULT '{}',
    genre_confidence JSONB, -- {'House': 0.8, 'Trance': 0.2}
    
    -- Statistics
    track_count INTEGER DEFAULT 0,
    labels_worked_with TEXT[] DEFAULT '{}',
    
    -- External information
    external_data JSONB, -- Wikipedia, Discogs, etc.
    
    -- Learning metadata
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for artist_profiles table
CREATE INDEX IF NOT EXISTS idx_artists_name ON artist_profiles (name);
CREATE INDEX IF NOT EXISTS idx_artists_normalized ON artist_profiles (normalized_name);
CREATE INDEX IF NOT EXISTS idx_artists_primary_genres ON artist_profiles USING GIN (primary_genres);

-- Label intelligence and profiles  
CREATE TABLE IF NOT EXISTS label_profiles (
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

-- Create indexes for label_profiles table
CREATE INDEX IF NOT EXISTS idx_labels_name ON label_profiles (name);
CREATE INDEX IF NOT EXISTS idx_labels_normalized ON label_profiles (normalized_name);
CREATE INDEX IF NOT EXISTS idx_labels_primary_genres ON label_profiles USING GIN (primary_genres);

-- Performance monitoring and statistics
CREATE TABLE IF NOT EXISTS processing_stats (
    id BIGSERIAL PRIMARY KEY,
    
    -- Processing run information
    run_id UUID NOT NULL,
    scan_path TEXT NOT NULL,
    
    -- Performance metrics
    files_scanned INTEGER NOT NULL,
    files_processed INTEGER NOT NULL,
    processing_time_seconds INTEGER NOT NULL,
    files_per_second DECIMAL(8,2) NOT NULL,
    
    -- Results summary
    duplicates_found INTEGER NOT NULL,
    classifications_made INTEGER NOT NULL,
    patterns_learned INTEGER NOT NULL,
    
    -- Quality metrics
    high_confidence_classifications INTEGER NOT NULL,
    needs_review_count INTEGER NOT NULL,
    
    -- System information
    processing_version VARCHAR(20) DEFAULT 'v3.2',
    system_config JSONB,
    
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for processing_stats table
CREATE INDEX IF NOT EXISTS idx_processing_stats_run ON processing_stats (run_id);
CREATE INDEX IF NOT EXISTS idx_processing_stats_completed ON processing_stats (completed_at);

-- MetaCrate integration and API access logs
CREATE TABLE IF NOT EXISTS api_requests (
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

-- Create indexes for api_requests table
CREATE INDEX IF NOT EXISTS idx_api_requests_hash ON api_requests (file_hash);
CREATE INDEX IF NOT EXISTS idx_api_requests_endpoint ON api_requests (endpoint);
CREATE INDEX IF NOT EXISTS idx_api_requests_requested ON api_requests (requested_at);

-- =====================================================
-- SEED DATA: Electronic Music Knowledge Base
-- =====================================================

-- Pre-populate with electronic music intelligence
INSERT INTO label_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Anjunabeats', 'anjunabeats', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.95, "Progressive House": 0.3}', '{"founded": 2000, "country": "UK"}'),
('Defected Records', 'defected', ARRAY['House', 'Deep House'], '{"House": 0.9, "Deep House": 0.8, "Tech House": 0.4}', '{"founded": 1999, "country": "UK"}'),
('Monstercat', 'monstercat', ARRAY['Electronic', 'Dubstep', 'Future Bass'], '{"Dubstep": 0.7, "Future Bass": 0.6, "Electronic": 0.9}', '{"founded": 2011, "country": "Canada"}'),
('Mau5trap', 'mau5trap', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.8, "Electro House": 0.6}', '{"founded": 2007, "owner": "Deadmau5"}'),
('Spinnin'' Records', 'spinnin', ARRAY['Big Room House', 'Progressive House', 'Future House'], '{"Big Room House": 0.8, "Progressive House": 0.6}', '{"founded": 1999, "country": "Netherlands"}'),
('OWSLA', 'owsla', ARRAY['Dubstep', 'Trap', 'Future Bass'], '{"Dubstep": 0.8, "Trap": 0.7, "Future Bass": 0.6}', '{"founded": 2011, "owner": "Skrillex"}'),
('Armada Music', 'armada', ARRAY['Trance', 'Progressive Trance', 'Uplifting Trance'], '{"Trance": 0.95, "Progressive Trance": 0.8}', '{"founded": 2003, "country": "Netherlands"}'),
('Ultra Music', 'ultra', ARRAY['Big Room House', 'Progressive House', 'Electro House'], '{"Big Room House": 0.7, "Progressive House": 0.6}', '{"founded": 1995, "country": "USA"}')
ON CONFLICT (name) DO NOTHING;

INSERT INTO artist_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Deadmau5', 'deadmau5', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.9, "Electro House": 0.7}', '{"real_name": "Joel Zimmerman", "country": "Canada"}'),
('Armin van Buuren', 'arminvanbuuren', ARRAY['Trance', 'Uplifting Trance'], '{"Trance": 0.95, "Uplifting Trance": 0.8}', '{"country": "Netherlands", "label": "Armada Music"}'),
('Martin Garrix', 'martingarrix', ARRAY['Big Room House', 'Future House'], '{"Big Room House": 0.8, "Future House": 0.7}', '{"real_name": "Martijn Garritsen", "country": "Netherlands"}'),
('Skrillex', 'skrillex', ARRAY['Dubstep', 'Trap'], '{"Dubstep": 0.9, "Trap": 0.6}', '{"real_name": "Sonny Moore", "label": "OWSLA"}'),
('Above & Beyond', 'aboveandbeyond', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.9, "Progressive Trance": 0.85}', '{"country": "UK", "label": "Anjunabeats"}'),
('Calvin Harris', 'calvinharris', ARRAY['Electro House', 'Big Room House'], '{"Electro House": 0.8, "Big Room House": 0.6}', '{"real_name": "Adam Wiles", "country": "Scotland"}'),
('Swedish House Mafia', 'swedishhousemafia', ARRAY['Progressive House', 'Big Room House'], '{"Progressive House": 0.8, "Big Room House": 0.7}', '{"country": "Sweden", "members": 3}'),
('Eric Prydz', 'ericprydz', ARRAY['Progressive House', 'Tech House'], '{"Progressive House": 0.9, "Tech House": 0.6}', '{"country": "Sweden", "aliases": ["Pryda", "Cirez D"]}')
ON CONFLICT (name) DO NOTHING;

INSERT INTO patterns (pattern_type, pattern_value, genre, subgenre, confidence, sample_size, success_rate) VALUES
('filename', '(Original Mix)', 'House', NULL, 0.7, 1000, 0.8),
('filename', '(Radio Edit)', NULL, NULL, 0.6, 500, 0.7),
('filename', '(Extended Mix)', 'Trance', NULL, 0.8, 300, 0.85),
('filename', '(Club Mix)', 'House', NULL, 0.75, 200, 0.8),
('folder', 'Trance', 'Trance', NULL, 0.95, 5000, 0.95),
('folder', 'House', 'House', NULL, 0.95, 5000, 0.95),
('folder', 'Techno', 'Techno', NULL, 0.95, 3000, 0.95),
('folder', 'Progressive', 'Progressive House', 'Progressive Trance', 0.8, 1000, 0.8),
('folder', 'Deep House', 'House', 'Deep House', 0.9, 800, 0.9),
('metadata', 'Trance', 'Trance', NULL, 0.9, 2000, 0.9),
('metadata', 'House', 'House', NULL, 0.9, 2000, 0.9),
('metadata', 'Electronic', 'Electronic', NULL, 0.6, 10000, 0.6)
ON CONFLICT (pattern_type, pattern_value, genre, subgenre) DO NOTHING;

-- =====================================================
-- VIEWS FOR EASY DATA ACCESS
-- =====================================================

-- Complete track information with classification
CREATE OR REPLACE VIEW track_intelligence AS
SELECT 
    t.id,
    t.file_path,
    t.file_hash,
    t.filename,
    t.folder_path,
    c.artist,
    c.track_name,
    c.remix_info,
    c.label,
    c.genre,
    c.subgenre,
    c.overall_confidence,
    c.bpm,
    c.musical_key,
    d.duplicate_count,
    CASE WHEN d.primary_track_id = t.id THEN true ELSE false END as is_primary_copy
FROM tracks t
LEFT JOIN classifications c ON t.id = c.track_id
LEFT JOIN duplicates d ON t.file_hash = d.file_hash;

-- Collection statistics summary
CREATE OR REPLACE VIEW collection_stats AS
SELECT 
    COUNT(*) as total_tracks,
    COUNT(DISTINCT file_hash) as unique_tracks,
    COUNT(*) - COUNT(DISTINCT file_hash) as duplicate_tracks,
    COUNT(DISTINCT artist) as unique_artists,
    COUNT(DISTINCT label) as unique_labels,
    COUNT(DISTINCT genre) as genres_identified,
    AVG(overall_confidence) as avg_confidence,
    SUM(file_size) as total_size_bytes
FROM track_intelligence;

-- Performance monitoring view
CREATE OR REPLACE VIEW system_performance AS
SELECT 
    DATE(completed_at) as date,
    COUNT(*) as runs_completed,
    SUM(files_processed) as total_files,
    AVG(files_per_second) as avg_performance,
    AVG(processing_time_seconds) as avg_runtime,
    SUM(duplicates_found) as total_duplicates,
    SUM(classifications_made) as total_classifications
FROM processing_stats
GROUP BY DATE(completed_at)
ORDER BY date DESC;

-- =====================================================
-- COMPLETE! Cultural Intelligence System v3.2 Ready
-- =====================================================