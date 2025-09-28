-- Cultural Intelligence Training System Tables
-- Execute this SQL in your Supabase SQL Editor

-- Training Queue Table
CREATE TABLE IF NOT EXISTS cultural_training_queue (
    id SERIAL PRIMARY KEY,
    question_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    context_data JSONB,
    track_id INTEGER,
    file_path TEXT,
    uncertainty_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT NOW(),
    assigned_at TIMESTAMP,
    completed_at TIMESTAMP,
    human_response JSONB,
    confidence_gained FLOAT
);

-- Training Sessions Table  
CREATE TABLE IF NOT EXISTS cultural_training_sessions (
    id SERIAL PRIMARY KEY,
    session_type VARCHAR(50) DEFAULT 'human_training',
    question_id INTEGER REFERENCES cultural_training_queue(id),
    user_id TEXT,
    question_text TEXT,
    human_response JSONB,
    response_time_ms INTEGER,
    confidence_before FLOAT,
    confidence_after FLOAT,
    accuracy_impact FLOAT,
    asked_at TIMESTAMP DEFAULT NOW(),
    answered_at TIMESTAMP,
    feedback_quality INTEGER DEFAULT 5,
    notes TEXT
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_training_queue_status ON cultural_training_queue(status);
CREATE INDEX IF NOT EXISTS idx_training_queue_priority ON cultural_training_queue(priority DESC);
CREATE INDEX IF NOT EXISTS idx_training_queue_created ON cultural_training_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_training_sessions_asked ON cultural_training_sessions(asked_at);
CREATE INDEX IF NOT EXISTS idx_training_sessions_type ON cultural_training_sessions(session_type);

-- Insert Sample Training Questions
INSERT INTO cultural_training_queue (question_type, priority, context_data, uncertainty_score) VALUES
('genre_uncertainty', 10, '{"genres": ["Progressive House", "Melodic Techno"], "reason": "Emotional breakdown with techno drums", "file_path": "/music/progressive/track_001.mp3", "bpm": 128, "key": "A minor"}', 0.75),
('artist_profiling', 8, '{"artist": "Stephan Bodzin", "uncertainty": "Progressive vs Melodic Techno classification", "file_path": "/music/techno/bodzin_track.mp3", "genre_distribution": {"Progressive": 60, "Melodic Techno": 40}}', 0.65),
('tempo_analysis', 6, '{"bpm_detected": 126, "genres": ["Deep House", "Tech House"], "reason": "BPM suggests tech house but groove feels deep", "file_path": "/music/house/deep_tech_126.mp3"}', 0.55),
('label_specialization', 7, '{"label": "Anjunadeep", "usual_genre": "Progressive House", "this_track_genre": "Deep House", "file_path": "/music/anjunadeep/track.mp3"}', 0.70),
('pattern_recognition', 9, '{"pattern": "four-on-the-floor", "tempo": 128, "genres": ["House", "Techno"], "reason": "Classic pattern but unclear subgenre", "file_path": "/music/electronic/pattern_test.mp3"}', 0.60),
('energy_classification', 5, '{"energy_level": "high", "bpm": 140, "genres": ["Trance", "Hard Techno"], "reason": "High energy but style unclear", "file_path": "/music/high_energy/track.mp3"}', 0.68);