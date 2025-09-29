-- Create the cultural_training_questions table
CREATE TABLE IF NOT EXISTS cultural_training_questions (
    id SERIAL PRIMARY KEY,
    track_id INTEGER,
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    options JSONB,
    confidence_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert sample training questions based on music library with low confidence
INSERT INTO cultural_training_questions (track_id, question, correct_answer, options, confidence_score, status)
VALUES 
(1, 'What genre is this track with low confidence score?', 'House', '["House", "Techno", "Trance", "Ambient"]', 0.3, 'pending'),
(2, 'Identify the primary genre of this music track', 'Techno', '["Techno", "House", "Drum & Bass", "Dubstep"]', 0.4, 'pending'),
(3, 'What electronic music genre does this track belong to?', 'Trance', '["Trance", "Progressive", "Ambient", "House"]', 0.2, 'pending'),
(4, 'Classify this electronic music track', 'Ambient', '["Ambient", "Downtempo", "Chillout", "Trance"]', 0.5, 'pending'),
(5, 'What genre classification fits this track?', 'Drum & Bass', '["Drum & Bass", "Jungle", "Breakbeat", "Dubstep"]', 0.35, 'pending'),
(6, 'Identify the musical style of this track', 'Progressive House', '["Progressive House", "Deep House", "Tech House", "Electro House"]', 0.45, 'pending'),
(7, 'What is the primary genre of this electronic track?', 'Dubstep', '["Dubstep", "Trap", "Future Bass", "Drum & Bass"]', 0.25, 'pending'),
(8, 'Classify this music according to electronic genres', 'Deep House', '["Deep House", "Tech House", "Progressive House", "Minimal"]', 0.4, 'pending'),
(9, 'What genre best describes this electronic music?', 'Minimal Techno', '["Minimal Techno", "Detroit Techno", "Hard Techno", "Tech House"]', 0.3, 'pending'),
(10, 'Identify the electronic music subgenre', 'Future Bass', '["Future Bass", "Trap", "Dubstep", "Electro"]', 0.35, 'pending');