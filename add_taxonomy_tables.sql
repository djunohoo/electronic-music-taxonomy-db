-- =====================================================
-- CULTURAL INTELLIGENCE TAXONOMY SYSTEM - NEW TABLES
-- =====================================================
-- Add comprehensive taxonomy tables to existing MetaCrate database
-- Uses 'taxonomy_' prefix to avoid conflicts

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- CORE DISCOVERY TABLES
-- =====================================================

-- Raw file discovery and metadata
CREATE TABLE taxonomy_discovered_tracks (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_size BIGINT NOT NULL,
    file_modified TIMESTAMP WITH TIME ZONE,
    filename TEXT NOT NULL,
    folder_path TEXT NOT NULL,
    file_extension VARCHAR(10),
    raw_metadata JSONB, -- ALL metadata as JSON
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status VARCHAR(20) DEFAULT 'discovered'
);

-- Duplicate detection results
CREATE TABLE taxonomy_duplicate_groups (
    id BIGSERIAL PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,
    primary_track_id BIGINT REFERENCES taxonomy_discovered_tracks(id),
    duplicate_track_ids BIGINT[] NOT NULL,
    duplicate_count INTEGER NOT NULL,
    total_size_bytes BIGINT NOT NULL,
    space_waste_bytes BIGINT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INTELLIGENCE EXTRACTION TABLES
-- =====================================================

-- Track analysis from filenames, folders, metadata
CREATE TABLE taxonomy_track_analysis (
    id BIGSERIAL PRIMARY KEY,
    track_id BIGINT REFERENCES taxonomy_discovered_tracks(id),
    
    -- Filename extraction
    filename_artist TEXT,
    filename_track TEXT,
    filename_remix TEXT,
    filename_genre_hints TEXT[],
    
    -- Folder structure analysis
    folder_genre_hints TEXT[],
    folder_depth INTEGER,
    folder_structure TEXT[],
    
    -- Metadata extraction
    metadata_artist TEXT,
    metadata_title TEXT,
    metadata_album TEXT,
    metadata_genre TEXT,
    metadata_comment TEXT,
    metadata_label TEXT,
    metadata_year INTEGER,
    metadata_bpm INTEGER,
    metadata_key VARCHAR(10),
    metadata_duration INTEGER,
    
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INTELLIGENCE PROFILES
-- =====================================================

-- Artist intelligence profiles
CREATE TABLE taxonomy_artist_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL,
    
    -- Track statistics
    total_tracks INTEGER DEFAULT 0,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Genre probabilities (learned from collection)
    primary_genres JSONB, -- {"House": 0.8, "Deep House": 0.6}
    secondary_genres JSONB,
    
    -- Label associations
    labels_worked_with TEXT[],
    
    -- Intelligence confidence
    confidence_score DECIMAL(3,2),
    sample_size INTEGER,
    
    -- External data if found
    external_data JSONB
);

-- Label intelligence profiles  
CREATE TABLE taxonomy_label_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL,
    
    -- Release statistics
    total_releases INTEGER DEFAULT 0,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Genre specialization
    genre_specialization JSONB, -- {"Trance": 0.95, "Progressive": 0.7}
    
    -- Artist roster
    signed_artists TEXT[],
    
    -- Intelligence confidence
    confidence_score DECIMAL(3,2),
    sample_size INTEGER,
    
    -- External data
    external_data JSONB
);

-- =====================================================
-- PATTERN LEARNING SYSTEM
-- =====================================================

-- Discovered patterns for future classification
CREATE TABLE taxonomy_learned_patterns (
    id BIGSERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL, -- 'filename', 'folder', 'metadata'
    pattern_value TEXT NOT NULL,
    
    -- Genre associations
    genre VARCHAR(100),
    subgenre VARCHAR(100),
    
    -- Statistical confidence
    confidence DECIMAL(5,4) NOT NULL,
    sample_size INTEGER NOT NULL,
    success_rate DECIMAL(5,4),
    
    -- Pattern evolution
    first_discovered TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_reinforced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reinforcement_count INTEGER DEFAULT 1,
    
    UNIQUE(pattern_type, pattern_value, genre, subgenre)
);

-- =====================================================
-- FINAL CLASSIFICATIONS
-- =====================================================

-- Final taxonomy conclusions
CREATE TABLE taxonomy_track_classifications (
    id BIGSERIAL PRIMARY KEY,
    track_id BIGINT REFERENCES taxonomy_discovered_tracks(id),
    
    -- Final determinations
    artist TEXT,
    track_name TEXT,
    remix_info TEXT,
    label TEXT,
    
    -- Genre classification
    primary_genre TEXT,
    secondary_genre TEXT,
    subgenre TEXT,
    
    -- Confidence scores
    artist_confidence DECIMAL(3,2),
    genre_confidence DECIMAL(3,2),
    subgenre_confidence DECIMAL(3,2),
    overall_confidence DECIMAL(3,2),
    
    -- Classification sources
    classification_sources TEXT[], -- ['filename_pattern', 'artist_profile', 'folder_analysis']
    
    -- Quality flags
    needs_review BOOLEAN DEFAULT false,
    human_validated BOOLEAN DEFAULT false,
    validation_notes TEXT,
    
    classified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SYSTEM MONITORING
-- =====================================================

-- Scan session tracking
CREATE TABLE taxonomy_scan_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_uuid UUID DEFAULT gen_random_uuid(),
    
    -- Scan parameters
    scan_path TEXT NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    files_discovered INTEGER DEFAULT 0,
    files_analyzed INTEGER DEFAULT 0,
    files_classified INTEGER DEFAULT 0,
    duplicates_found INTEGER DEFAULT 0,
    patterns_learned INTEGER DEFAULT 0,
    
    -- Performance
    processing_time_seconds INTEGER,
    files_per_second DECIMAL(6,2),
    
    -- Status
    status VARCHAR(20) DEFAULT 'running', -- running, completed, failed
    error_message TEXT
);

-- Processing logs
CREATE TABLE taxonomy_processing_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT REFERENCES taxonomy_scan_sessions(id),
    log_level VARCHAR(10) NOT NULL, -- INFO, WARN, ERROR
    message TEXT NOT NULL,
    details JSONB,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- Discovery indexes
CREATE INDEX idx_taxonomy_discovered_tracks_hash ON taxonomy_discovered_tracks(file_hash);
CREATE INDEX idx_taxonomy_discovered_tracks_path ON taxonomy_discovered_tracks(file_path);
CREATE INDEX idx_taxonomy_discovered_tracks_status ON taxonomy_discovered_tracks(processing_status);

-- Analysis indexes
CREATE INDEX idx_taxonomy_track_analysis_track_id ON taxonomy_track_analysis(track_id);
CREATE INDEX idx_taxonomy_track_analysis_artist ON taxonomy_track_analysis(filename_artist);
CREATE INDEX idx_taxonomy_track_analysis_metadata_genre ON taxonomy_track_analysis(metadata_genre);

-- Profile indexes
CREATE INDEX idx_taxonomy_artist_profiles_name ON taxonomy_artist_profiles(normalized_name);
CREATE INDEX idx_taxonomy_label_profiles_name ON taxonomy_label_profiles(normalized_name);

-- Pattern indexes
CREATE INDEX idx_taxonomy_learned_patterns_type_value ON taxonomy_learned_patterns(pattern_type, pattern_value);
CREATE INDEX idx_taxonomy_learned_patterns_genre ON taxonomy_learned_patterns(genre);

-- Classification indexes
CREATE INDEX idx_taxonomy_track_classifications_track_id ON taxonomy_track_classifications(track_id);
CREATE INDEX idx_taxonomy_track_classifications_artist ON taxonomy_track_classifications(artist);
CREATE INDEX idx_taxonomy_track_classifications_genre ON taxonomy_track_classifications(primary_genre);

-- Session indexes
CREATE INDEX idx_taxonomy_scan_sessions_status ON taxonomy_scan_sessions(status);
CREATE INDEX idx_taxonomy_processing_logs_session ON taxonomy_processing_logs(session_id);

-- =====================================================
-- SEED DATA FOR BOOTSTRAP LEARNING
-- =====================================================

-- Seed initial patterns for bootstrap learning
INSERT INTO taxonomy_learned_patterns (pattern_type, pattern_value, genre, subgenre, confidence, sample_size, success_rate) VALUES
-- Filename patterns
('filename', '(Original Mix)', 'House', NULL, 0.75, 1000, 0.85),
('filename', '(Extended Mix)', 'Trance', NULL, 0.80, 800, 0.87),
('filename', '(Club Mix)', 'House', NULL, 0.70, 600, 0.82),
('filename', '(Radio Edit)', NULL, NULL, 0.60, 400, 0.75),
('filename', '(Dub Mix)', 'Techno', NULL, 0.65, 300, 0.78),

-- Folder patterns
('folder', 'House', 'House', NULL, 0.95, 5000, 0.96),
('folder', 'Deep House', 'House', 'Deep House', 0.90, 3000, 0.94),
('folder', 'Tech House', 'House', 'Tech House', 0.88, 2500, 0.92),
('folder', 'Trance', 'Trance', NULL, 0.93, 4000, 0.95),
('folder', 'Progressive', 'Trance', 'Progressive Trance', 0.85, 2000, 0.89),
('folder', 'Uplifting', 'Trance', 'Uplifting Trance', 0.87, 1800, 0.91),
('folder', 'Techno', 'Techno', NULL, 0.92, 3500, 0.94),
('folder', 'Minimal', 'Techno', 'Minimal Techno', 0.83, 1500, 0.87),
('folder', 'Breaks', 'Breakbeat', NULL, 0.89, 2200, 0.92),
('folder', 'Drum and Bass', 'Drum & Bass', NULL, 0.94, 2800, 0.96),
('folder', 'DNB', 'Drum & Bass', NULL, 0.91, 1200, 0.93),

-- Metadata patterns
('metadata', 'Trance', 'Trance', NULL, 0.88, 3000, 0.92),
('metadata', 'House', 'House', NULL, 0.86, 4000, 0.90),
('metadata', 'Techno', 'Techno', NULL, 0.87, 3200, 0.91),
('metadata', 'Electronic', NULL, NULL, 0.50, 8000, 0.65),
('metadata', 'Dance', NULL, NULL, 0.45, 6000, 0.60)
ON CONFLICT (pattern_type, pattern_value, genre, subgenre) DO NOTHING;

-- Seed known electronic music labels
INSERT INTO taxonomy_label_profiles (name, normalized_name, genre_specialization, confidence_score, sample_size) VALUES
('Anjunabeats', 'anjunabeats', '{"Trance": 0.95, "Progressive Trance": 0.88}', 0.95, 500),
('Defected Records', 'defected', '{"House": 0.92, "Deep House": 0.85}', 0.90, 800),
('Monstercat', 'monstercat', '{"Dubstep": 0.70, "Electronic": 0.60, "Future Bass": 0.65}', 0.75, 1200),
('Toolroom Records', 'toolroom', '{"Tech House": 0.88, "Techno": 0.75}', 0.85, 600),
('OWSLA', 'owsla', '{"Dubstep": 0.80, "Trap": 0.70, "Future Bass": 0.60}', 0.80, 400),
('Spinnin Records', 'spinnin', '{"Progressive House": 0.70, "Big Room": 0.75, "Future House": 0.65}', 0.75, 1000)
ON CONFLICT (name) DO NOTHING;

-- Seed known electronic music artists
INSERT INTO taxonomy_artist_profiles (name, normalized_name, primary_genres, confidence_score, sample_size) VALUES
('Deadmau5', 'deadmau5', '{"Progressive House": 0.85, "Electro House": 0.70}', 0.90, 150),
('Armin van Buuren', 'arminvanbuuren', '{"Trance": 0.95, "Uplifting Trance": 0.80}', 0.95, 200),
('Skrillex', 'skrillex', '{"Dubstep": 0.90, "Trap": 0.60}', 0.85, 100),
('Carl Cox', 'carlcox', '{"Techno": 0.92, "Tech House": 0.75}', 0.88, 180),
('Above & Beyond', 'aboveandbeyond', '{"Trance": 0.90, "Progressive Trance": 0.85}', 0.92, 160),
('Calvin Harris', 'calvinharris', '{"Progressive House": 0.75, "Future House": 0.60}', 0.70, 120)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- SUCCESS VERIFICATION
-- =====================================================

SELECT 
    'CULTURAL INTELLIGENCE TAXONOMY SYSTEM INSTALLED!' as status,
    COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_name LIKE 'taxonomy_%';

SELECT 'TAXONOMY SEED DATA LOADED' as status,
    (SELECT COUNT(*) FROM taxonomy_learned_patterns) as patterns,
    (SELECT COUNT(*) FROM taxonomy_label_profiles) as labels,
    (SELECT COUNT(*) FROM taxonomy_artist_profiles) as artists;