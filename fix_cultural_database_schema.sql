-- Fix Cultural Intelligence Database Schema
-- Run this in Supabase SQL Editor or pgAdmin

BEGIN;

-- Add missing column to cultural_patterns table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'cultural_patterns' 
        AND column_name = 'reinforcement_count'
    ) THEN
        ALTER TABLE cultural_patterns 
        ADD COLUMN reinforcement_count INTEGER DEFAULT 1;
        
        UPDATE cultural_patterns 
        SET reinforcement_count = 1 
        WHERE reinforcement_count IS NULL;
        
        RAISE NOTICE 'Added reinforcement_count column to cultural_patterns';
    END IF;
END $$;

-- Create training questions table
CREATE TABLE IF NOT EXISTS cultural_training_questions (
    id SERIAL PRIMARY KEY,
    question_type VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    context_data JSONB DEFAULT '{}',
    uncertainty_score DECIMAL(3,2) DEFAULT 0.65,
    track_id INTEGER REFERENCES cultural_tracks(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    human_response JSONB
);

-- Create training sessions table
CREATE TABLE IF NOT EXISTS cultural_training_sessions (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES cultural_training_questions(id) ON DELETE SET NULL,
    question_type VARCHAR(100),
    question_text TEXT,
    human_response JSONB,
    response_text TEXT,
    answered_at TIMESTAMP DEFAULT NOW(),
    feedback_quality INTEGER DEFAULT 5 CHECK (feedback_quality >= 1 AND feedback_quality <= 10),
    response_time_ms INTEGER DEFAULT 2000
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_training_questions_status 
ON cultural_training_questions(status);

CREATE INDEX IF NOT EXISTS idx_training_questions_type 
ON cultural_training_questions(question_type);

CREATE INDEX IF NOT EXISTS idx_training_sessions_timestamp 
ON cultural_training_sessions(answered_at);

-- Insert sample training questions
INSERT INTO cultural_training_questions (question_type, question_text, context_data, uncertainty_score) VALUES
('genre_uncertainty', 
 'I''m analyzing a 128 BPM track with four-on-the-floor kicks and filtered house stabs. Could be House or Tech House. What''s your classification?',
 '{"genres": ["House", "Tech House"], "bpm": 128, "reason": "Similar rhythmic patterns, uncertain about sub-genre classification"}',
 0.75),

('artist_profiling', 
 'Artist ''Block & Crown'' has tracks across House (80%), Tech House (15%), Deep House (5%). What''s their primary specialty?',
 '{"artist": "Block & Crown", "genre_distribution": {"House": 80, "Tech House": 15, "Deep House": 5}}',
 0.60),

('tempo_analysis',
 'Track at 174 BPM with breakbeats and heavy bass. Could be Drum & Bass or Jungle. What classification do you recommend?',
 '{"bpm_detected": 174, "genres": ["Drum & Bass", "Jungle"], "reason": "High BPM with breakbeat pattern characteristics"}',
 0.70),

('label_specialization',
 'Label usually releases Trance, but this track seems like House. Should I trust the label pattern or the audio analysis?',
 '{"label": "Generic Label", "usual_genre": "Trance", "this_track_genre": "House"}',
 0.65),

('demo_question',
 'Help me learn! What genre would you classify an energetic 128 BPM track with four-on-the-floor kicks and synthesized leads?',
 '{"bpm": 128, "pattern": "four-on-the-floor", "elements": ["kicks", "synth leads"]}',
 0.65);

-- Enable RLS (Row Level Security) for the tables if needed
ALTER TABLE cultural_training_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cultural_training_sessions ENABLE ROW LEVEL SECURITY;

-- Create policies to allow full access (modify as needed for security)
CREATE POLICY "Allow full access to training questions" 
ON cultural_training_questions FOR ALL 
TO authenticated, anon
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow full access to training sessions" 
ON cultural_training_sessions FOR ALL 
TO authenticated, anon
USING (true) 
WITH CHECK (true);

COMMIT;

-- Verify the setup
SELECT 'Training Questions Created' as status, COUNT(*) as count FROM cultural_training_questions;
SELECT 'Training Sessions Table Ready' as status, 0 as count;
SELECT 'Schema Fix Complete' as status;