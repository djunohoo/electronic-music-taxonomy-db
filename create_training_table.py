#!/usr/bin/env python3
"""Quick script to create the missing cultural_training_questions table"""
import os
import requests
import json

# Use hardcoded database config for quick fix
database_url = "http://172.22.17.138:8000"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF5b21lZ3didmhxcGhvamppYXEiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcwNzYxNTg0NSwiZXhwIjoyMDIzMTkxODQ1fQ.I0XzYSfLq1zQBH7r9TKfHYZcjxHwBUFz9_zZwYNvK8k"

# Create the training questions table
create_table_sql = """
CREATE TABLE IF NOT EXISTS cultural_training_questions (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES music_library(id),
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    options JSONB,
    confidence_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert some sample training questions
INSERT INTO cultural_training_questions (track_id, question, correct_answer, options, confidence_score, status)
SELECT 
    ml.id,
    'What genre is this track "' || ml.title || '" by ' || ml.artist || '?',
    COALESCE(ml.primary_genre, 'Unknown'),
    jsonb_build_array(
        COALESCE(ml.primary_genre, 'Unknown'),
        CASE WHEN ml.primary_genre != 'House' THEN 'House' ELSE 'Techno' END,
        CASE WHEN ml.primary_genre != 'Trance' THEN 'Trance' ELSE 'Ambient' END,
        CASE WHEN ml.primary_genre != 'Drum & Bass' THEN 'Drum & Bass' ELSE 'Dubstep' END
    ),
    COALESCE(ml.confidence_score, 0.5),
    'pending'
FROM music_library ml 
WHERE ml.confidence_score < 0.7 
ORDER BY ml.confidence_score ASC 
LIMIT 50
ON CONFLICT DO NOTHING;
"""

# Execute via Supabase REST API
headers = {
    'apikey': api_key,
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Use PostgREST rpc endpoint for raw SQL
rpc_url = f"{database_url}/rest/v1/rpc/execute_sql"

try:
    response = requests.post(
        rpc_url,
        headers=headers,
        json={'sql': create_table_sql}
    )
    
    if response.status_code == 200:
        print("✅ Training questions table created successfully!")
    else:
        print(f"❌ Failed to create table: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try alternative approach - direct SQL execution
        print("\nTrying alternative approach...")
        
        # Split into individual statements
        statements = [s.strip() for s in create_table_sql.split(';') if s.strip()]
        
        for i, stmt in enumerate(statements):
            if not stmt:
                continue
                
            print(f"Executing statement {i+1}...")
            try:
                resp = requests.post(
                    rpc_url,
                    headers=headers,
                    json={'sql': stmt}
                )
                if resp.status_code == 200:
                    print(f"✅ Statement {i+1} executed")
                else:
                    print(f"❌ Statement {i+1} failed: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"❌ Statement {i+1} error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying manual table creation...")
    
    # Try creating table via direct POST to the table endpoint
    table_url = f"{database_url}/rest/v1/cultural_training_questions"
    
    # This will create the table if it doesn't exist when we try to query it
    response = requests.get(table_url, headers=headers)
    print(f"Table check response: {response.status_code}")