-- GOURMET AI ENHANCEMENT: Advanced Pattern Learning Schema
-- Add sophisticated reinforcement learning columns to cultural_patterns table

-- Add reinforcement learning columns
ALTER TABLE cultural_patterns ADD COLUMN IF NOT EXISTS reinforcement_count INTEGER DEFAULT 1;
ALTER TABLE cultural_patterns ADD COLUMN IF NOT EXISTS sample_size INTEGER DEFAULT 1;
ALTER TABLE cultural_patterns ADD COLUMN IF NOT EXISTS learning_rate FLOAT DEFAULT 0.1;
ALTER TABLE cultural_patterns ADD COLUMN IF NOT EXISTS last_reinforced TIMESTAMP DEFAULT NOW();
ALTER TABLE cultural_patterns ADD COLUMN IF NOT EXISTS pattern_strength FLOAT DEFAULT 0.0;

-- Create index for performance on reinforcement queries
CREATE INDEX IF NOT EXISTS idx_cultural_patterns_reinforcement ON cultural_patterns(reinforcement_count, confidence);
CREATE INDEX IF NOT EXISTS idx_cultural_patterns_strength ON cultural_patterns(pattern_strength DESC);

-- Update existing records to have proper defaults
UPDATE cultural_patterns SET 
    reinforcement_count = 1,
    sample_size = 1,
    learning_rate = 0.1,
    last_reinforced = NOW(),
    pattern_strength = COALESCE(confidence, 0.5)
WHERE reinforcement_count IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN cultural_patterns.reinforcement_count IS 'Number of times this pattern has been reinforced (higher = more reliable)';
COMMENT ON COLUMN cultural_patterns.sample_size IS 'Total number of examples used to train this pattern';
COMMENT ON COLUMN cultural_patterns.learning_rate IS 'Adaptive learning rate (decreases as pattern becomes more established)';
COMMENT ON COLUMN cultural_patterns.last_reinforced IS 'Last time this pattern was reinforced during training';
COMMENT ON COLUMN cultural_patterns.pattern_strength IS 'Overall strength score combining confidence and reinforcement count';