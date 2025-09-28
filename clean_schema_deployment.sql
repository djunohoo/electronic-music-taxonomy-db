-- =====================================================
-- CULTURAL INTELLIGENCE SYSTEM v3.2 - CLEAN SCHEMA
-- =====================================================
-- Run this AFTER creating the cultural_intelligence database
-- Make sure you're connected to: cultural_intelligence database

-- Verify we're in the right database
SELECT current_database() as database_name, current_user as user_name;

-- Core tracks table with complete metadata
CREATE TABLE tracks (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
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

-- Duplicate detection and management
CREATE TABLE duplicates (
    id BIGSERIAL PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL REFERENCES tracks(file_hash),
    primary_track_id BIGINT NOT NULL REFERENCES tracks(id),
    duplicate_track_ids BIGINT[] NOT NULL,
    duplicate_count INTEGER NOT NULL,
    total_size_bytes BIGINT NOT NULL,
    space_waste_bytes BIGINT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Classification results and intelligence
CREATE TABLE classifications (
    id BIGSERIAL PRIMARY KEY,
    track_id BIGINT NOT NULL REFERENCES tracks(id),
    
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

-- Pattern learning and intelligence
CREATE TABLE patterns (
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
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(pattern_type, pattern_value, genre, subgenre)
);

-- Artist intelligence and profiles
CREATE TABLE artist_profiles (
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
CREATE TABLE label_profiles (
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

-- MetaCrate API access logs
CREATE TABLE api_requests (
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
-- PERFORMANCE INDEXES
-- =====================================================

-- Tracks indexes
CREATE INDEX idx_tracks_hash ON tracks(file_hash);
CREATE INDEX idx_tracks_path ON tracks(file_path);
CREATE INDEX idx_tracks_folder ON tracks(folder_path);
CREATE INDEX idx_tracks_processed ON tracks(processed_at);

-- Duplicates indexes
CREATE INDEX idx_duplicates_hash ON duplicates(file_hash);
CREATE INDEX idx_duplicates_primary ON duplicates(primary_track_id);

-- Classifications indexes
CREATE INDEX idx_classifications_track ON classifications(track_id);
CREATE INDEX idx_classifications_artist ON classifications(artist);
CREATE INDEX idx_classifications_genre ON classifications(genre);
CREATE INDEX idx_classifications_label ON classifications(label);
CREATE INDEX idx_classifications_confidence ON classifications(overall_confidence);

-- Patterns indexes
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON patterns(confidence);

-- Artist profiles indexes
CREATE INDEX idx_artists_name ON artist_profiles(name);
CREATE INDEX idx_artists_normalized ON artist_profiles(normalized_name);

-- Label profiles indexes  
CREATE INDEX idx_labels_name ON label_profiles(name);
CREATE INDEX idx_labels_normalized ON label_profiles(normalized_name);

-- API requests indexes
CREATE INDEX idx_api_requests_hash ON api_requests(file_hash);
CREATE INDEX idx_api_requests_endpoint ON api_requests(endpoint);
CREATE INDEX idx_api_requests_requested ON api_requests(requested_at);

-- =====================================================
-- SEED DATA: Electronic Music Knowledge Base
-- =====================================================

-- Pre-populate with electronic music intelligence
INSERT INTO label_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Anjunabeats', 'anjunabeats', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.95, "Progressive House": 0.3}', '{"founded": 2000, "country": "UK"}'),
('Defected Records', 'defected', ARRAY['House', 'Deep House'], '{"House": 0.9, "Deep House": 0.8}', '{"founded": 1999, "country": "UK"}'),
('Monstercat', 'monstercat', ARRAY['Electronic', 'Dubstep', 'Future Bass'], '{"Dubstep": 0.7, "Electronic": 0.9}', '{"founded": 2011, "country": "Canada"}'),
('Mau5trap', 'mau5trap', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.8}', '{"founded": 2007, "owner": "Deadmau5"}'),
('Armada Music', 'armada', ARRAY['Trance', 'Progressive Trance', 'Uplifting Trance'], '{"Trance": 0.95}', '{"founded": 2003, "country": "Netherlands"}'),
('Ultra Music', 'ultra', ARRAY['Big Room House', 'Progressive House'], '{"Big Room House": 0.7}', '{"founded": 1995, "country": "USA"}');

INSERT INTO artist_profiles (name, normalized_name, primary_genres, genre_confidence, external_data) VALUES
('Deadmau5', 'deadmau5', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.9}', '{"real_name": "Joel Zimmerman", "country": "Canada"}'),
('Armin van Buuren', 'arminvanbuuren', ARRAY['Trance', 'Uplifting Trance'], '{"Trance": 0.95}', '{"country": "Netherlands", "label": "Armada Music"}'),
('Skrillex', 'skrillex', ARRAY['Dubstep', 'Trap'], '{"Dubstep": 0.9}', '{"real_name": "Sonny Moore", "label": "OWSLA"}'),
('Above & Beyond', 'aboveandbeyond', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.9}', '{"country": "UK", "label": "Anjunabeats"}'),
('Martin Garrix', 'martingarrix', ARRAY['Big Room House', 'Future House'], '{"Big Room House": 0.8}', '{"real_name": "Martijn Garritsen", "country": "Netherlands"}'),
('Calvin Harris', 'calvinharris', ARRAY['Electro House', 'Big Room House'], '{"Electro House": 0.8}', '{"real_name": "Adam Wiles", "country": "Scotland"}');

INSERT INTO patterns (pattern_type, pattern_value, genre, subgenre, confidence, sample_size, success_rate) VALUES
('filename', '(Original Mix)', 'House', NULL, 0.7, 1000, 0.8),
('filename', '(Extended Mix)', 'Trance', NULL, 0.8, 300, 0.85),
('filename', '(Radio Edit)', NULL, NULL, 0.6, 500, 0.7),
('folder', 'Trance', 'Trance', NULL, 0.95, 5000, 0.95),
('folder', 'House', 'House', NULL, 0.95, 5000, 0.95),
('folder', 'Techno', 'Techno', NULL, 0.95, 3000, 0.95),
('metadata', 'Trance', 'Trance', NULL, 0.9, 2000, 0.9),
('metadata', 'House', 'House', NULL, 0.9, 2000, 0.9),
('metadata', 'Electronic', 'Electronic', NULL, 0.6, 10000, 0.6);

-- =====================================================
-- VERIFICATION & SUCCESS
-- =====================================================

-- Verify tables created
SELECT 
    'TABLES CREATED' as status,
    COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';

-- Verify seeded data
SELECT 'SEEDED DATA' as status,
    (SELECT COUNT(*) FROM label_profiles) as labels,
    (SELECT COUNT(*) FROM artist_profiles) as artists,
    (SELECT COUNT(*) FROM patterns) as patterns;

-- Success message
SELECT '🎵 CULTURAL INTELLIGENCE SYSTEM v3.2 - CLEAN DATABASE READY! 🚀' as final_status;