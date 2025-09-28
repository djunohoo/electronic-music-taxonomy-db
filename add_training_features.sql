-- =====================================================
-- AI TRAINING ZONE - Interactive Learning Features
-- =====================================================
-- Add this to your existing cultural intelligence database

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

-- Performance indexes
CREATE INDEX idx_training_sessions_status ON cultural_training_sessions(status);
CREATE INDEX idx_training_sessions_asked ON cultural_training_sessions(asked_at);
CREATE INDEX idx_training_queue_priority ON cultural_training_queue(priority DESC, created_at);
CREATE INDEX idx_training_queue_status ON cultural_training_queue(status);

-- Seed some example training scenarios for demonstration
INSERT INTO cultural_training_queue (question_type, uncertainty_score, context_data, priority) VALUES
('genre_uncertainty', 0.65, '{"genres": ["House", "Techno"], "bpm": 128, "reason": "BPM suggests House but percussion patterns indicate Techno"}', 1),
('artist_profiling', 0.70, '{"artist": "Unknown Artist", "track_count": 12, "genre_distribution": {"House": 6, "Trance": 4, "Techno": 2}}', 2),
('label_specialization', 0.75, '{"label": "New Label", "usual_genre": "Trance", "this_track_genre": "House", "confidence_drop": 0.3}', 1);

-- Success verification
SELECT 
    'AI TRAINING ZONE READY!' as status,
    (SELECT COUNT(*) FROM cultural_training_queue WHERE status = 'pending') as pending_questions;