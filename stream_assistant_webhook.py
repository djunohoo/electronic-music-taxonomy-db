#!/usr/bin/env python3
"""
Live DJ Stream Assistant - Webhook Integration
Receives real-time track classification and chat interaction data
from the live stream assistant and integrates with main taxonomy database
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DJ Stream Assistant Webhook", version="1.0.0")

# Pydantic models for webhook payloads
class StreamInfo(BaseModel):
    twitch_username: str
    stream_title: str
    viewer_count: int
    platform: str = "twitch"

class TrackClassification(BaseModel):
    main_genre: str
    subgenre: Optional[str]
    confidence: float
    characteristics: List[str]
    bpm: Optional[int]
    key: Optional[str]

class TrackData(BaseModel):
    artist: str
    title: str
    album: Optional[str] = None
    label: Optional[str] = None
    year: Optional[int] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    classification: TrackClassification
    file_path: Optional[str] = None

class ChatInteraction(BaseModel):
    message_sent: str
    engagement_type: str  # educational, hype, technical, interactive
    audience_reaction: str  # positive, neutral, negative
    response_count: int = 0
    emoji_reactions: Dict[str, int] = {}

class StreamWebhookPayload(BaseModel):
    timestamp: datetime
    dj_stream: StreamInfo
    track_data: TrackData
    chat_interaction: Optional[ChatInteraction] = None
    session_id: str
    event_type: str  # track_start, track_end, chat_message, etc.

# Database functions
def init_webhook_database():
    """Initialize webhook tracking database"""
    conn = sqlite3.connect('stream_assistant_data.db')
    cursor = conn.cursor()
    
    # Create tables for webhook data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stream_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            dj_username TEXT,
            stream_title TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            total_tracks INTEGER DEFAULT 0,
            total_interactions INTEGER DEFAULT 0,
            peak_viewers INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS track_plays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            artist TEXT,
            title TEXT,
            main_genre TEXT,
            subgenre TEXT,
            bpm INTEGER,
            key_signature TEXT,
            classification_confidence REAL,
            characteristics TEXT,  -- JSON array
            play_timestamp TIMESTAMP,
            viewer_count INTEGER,
            chat_engagement INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES stream_sessions (session_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            track_id INTEGER,
            message_content TEXT,
            engagement_type TEXT,
            audience_reaction TEXT,
            response_count INTEGER,
            emoji_reactions TEXT,  -- JSON
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES stream_sessions (session_id),
            FOREIGN KEY (track_id) REFERENCES track_plays (id)
        )
    ''')
    
    # Genre analytics table for taxonomy insights
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genre_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_genre TEXT,
            subgenre TEXT,
            total_plays INTEGER DEFAULT 1,
            total_engagement INTEGER DEFAULT 0,
            average_confidence REAL,
            popular_characteristics TEXT,  -- JSON
            last_played TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def update_genre_analytics(track_data: TrackData, engagement_score: int = 0):
    """Update genre analytics based on track play data"""
    conn = sqlite3.connect('stream_assistant_data.db')
    cursor = conn.cursor()
    
    # Check if genre combo exists
    cursor.execute('''
        SELECT id, total_plays, total_engagement, average_confidence, popular_characteristics
        FROM genre_analytics 
        WHERE main_genre = ? AND subgenre = ?
    ''', (track_data.classification.main_genre, track_data.classification.subgenre))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        new_total_plays = existing[1] + 1
        new_total_engagement = existing[2] + engagement_score
        new_avg_confidence = (existing[3] * existing[1] + track_data.classification.confidence) / new_total_plays
        
        # Merge characteristics
        existing_chars = json.loads(existing[4]) if existing[4] else {}
        for char in track_data.classification.characteristics:
            existing_chars[char] = existing_chars.get(char, 0) + 1
        
        cursor.execute('''
            UPDATE genre_analytics 
            SET total_plays = ?, total_engagement = ?, average_confidence = ?, 
                popular_characteristics = ?, last_played = ?, updated_at = ?
            WHERE id = ?
        ''', (new_total_plays, new_total_engagement, new_avg_confidence,
              json.dumps(existing_chars), datetime.now(), datetime.now(), existing[0]))
    else:
        # Create new record
        chars_dict = {char: 1 for char in track_data.classification.characteristics}
        cursor.execute('''
            INSERT INTO genre_analytics 
            (main_genre, subgenre, total_plays, total_engagement, average_confidence, 
             popular_characteristics, last_played)
            VALUES (?, ?, 1, ?, ?, ?, ?)
        ''', (track_data.classification.main_genre, track_data.classification.subgenre,
              engagement_score, track_data.classification.confidence,
              json.dumps(chars_dict), datetime.now()))
    
    conn.commit()
    conn.close()

# Webhook endpoints
@app.post("/api/webhook/track-classified")
async def track_classified(payload: StreamWebhookPayload, background_tasks: BackgroundTasks):
    """
    Receive track classification data from live stream assistant
    """
    try:
        logger.info(f"Track classified: {payload.track_data.artist} - {payload.track_data.title}")
        
        # Store track play data
        conn = sqlite3.connect('stream_assistant_data.db')
        cursor = conn.cursor()
        
        # Ensure session exists
        cursor.execute('''
            INSERT OR IGNORE INTO stream_sessions 
            (session_id, dj_username, stream_title, start_time)
            VALUES (?, ?, ?, ?)
        ''', (payload.session_id, payload.dj_stream.twitch_username,
              payload.dj_stream.stream_title, payload.timestamp))
        
        # Insert track play
        cursor.execute('''
            INSERT INTO track_plays 
            (session_id, artist, title, main_genre, subgenre, bpm, key_signature,
             classification_confidence, characteristics, play_timestamp, viewer_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (payload.session_id, payload.track_data.artist, payload.track_data.title,
              payload.track_data.classification.main_genre, 
              payload.track_data.classification.subgenre,
              payload.track_data.bpm, payload.track_data.key,
              payload.track_data.classification.confidence,
              json.dumps(payload.track_data.classification.characteristics),
              payload.timestamp, payload.dj_stream.viewer_count))
        
        # Update session stats
        cursor.execute('''
            UPDATE stream_sessions 
            SET total_tracks = total_tracks + 1,
                peak_viewers = MAX(peak_viewers, ?)
            WHERE session_id = ?
        ''', (payload.dj_stream.viewer_count, payload.session_id))
        
        conn.commit()
        conn.close()
        
        # Update analytics in background
        background_tasks.add_task(update_genre_analytics, payload.track_data)
        
        return {"status": "success", "message": "Track classification recorded"}
        
    except Exception as e:
        logger.error(f"Error processing track classification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/chat-interaction")
async def chat_interaction(payload: StreamWebhookPayload):
    """
    Receive chat interaction data from Twitch bot
    """
    try:
        if not payload.chat_interaction:
            raise HTTPException(status_code=400, detail="Chat interaction data required")
        
        logger.info(f"Chat interaction: {payload.chat_interaction.engagement_type}")
        
        conn = sqlite3.connect('stream_assistant_data.db')
        cursor = conn.cursor()
        
        # Get latest track for this session
        cursor.execute('''
            SELECT id FROM track_plays 
            WHERE session_id = ? 
            ORDER BY play_timestamp DESC LIMIT 1
        ''', (payload.session_id,))
        
        track_result = cursor.fetchone()
        track_id = track_result[0] if track_result else None
        
        # Insert chat interaction
        cursor.execute('''
            INSERT INTO chat_interactions 
            (session_id, track_id, message_content, engagement_type, audience_reaction,
             response_count, emoji_reactions, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (payload.session_id, track_id, payload.chat_interaction.message_sent,
              payload.chat_interaction.engagement_type, 
              payload.chat_interaction.audience_reaction,
              payload.chat_interaction.response_count,
              json.dumps(payload.chat_interaction.emoji_reactions),
              payload.timestamp))
        
        # Update session interaction count
        cursor.execute('''
            UPDATE stream_sessions 
            SET total_interactions = total_interactions + 1
            WHERE session_id = ?
        ''', (payload.session_id,))
        
        # Calculate engagement score for analytics
        engagement_score = payload.chat_interaction.response_count
        if payload.chat_interaction.audience_reaction == "positive":
            engagement_score += 5
        elif payload.chat_interaction.audience_reaction == "negative":
            engagement_score -= 2
        
        # Update genre analytics with engagement
        if track_id:
            cursor.execute('''
                SELECT main_genre, subgenre FROM track_plays WHERE id = ?
            ''', (track_id,))
            genre_data = cursor.fetchone()
            if genre_data:
                cursor.execute('''
                    UPDATE genre_analytics 
                    SET total_engagement = total_engagement + ?
                    WHERE main_genre = ? AND subgenre = ?
                ''', (engagement_score, genre_data[0], genre_data[1]))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Chat interaction recorded"}
        
    except Exception as e:
        logger.error(f"Error processing chat interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/stream-stats")
async def stream_stats(payload: StreamWebhookPayload):
    """
    Receive general stream statistics and session updates
    """
    try:
        logger.info(f"Stream stats update for session: {payload.session_id}")
        
        conn = sqlite3.connect('stream_assistant_data.db')
        cursor = conn.cursor()
        
        # Update session with latest stats
        cursor.execute('''
            UPDATE stream_sessions 
            SET peak_viewers = MAX(peak_viewers, ?),
                stream_title = ?
            WHERE session_id = ?
        ''', (payload.dj_stream.viewer_count, payload.dj_stream.stream_title, payload.session_id))
        
        # If this is a session end event
        if payload.event_type == "stream_end":
            cursor.execute('''
                UPDATE stream_sessions 
                SET end_time = ?
                WHERE session_id = ?
            ''', (payload.timestamp, payload.session_id))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Stream stats updated"}
        
    except Exception as e:
        logger.error(f"Error processing stream stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/api/analytics/genre-trends")
async def get_genre_trends(limit: int = 20):
    """
    Get trending genres based on play count and engagement
    """
    conn = sqlite3.connect('stream_assistant_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT main_genre, subgenre, total_plays, total_engagement, 
               average_confidence, popular_characteristics, last_played
        FROM genre_analytics 
        ORDER BY (total_plays + total_engagement) DESC 
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    trends = []
    for row in results:
        trends.append({
            "main_genre": row[0],
            "subgenre": row[1],
            "total_plays": row[2],
            "total_engagement": row[3],
            "average_confidence": row[4],
            "popular_characteristics": json.loads(row[5]) if row[5] else {},
            "last_played": row[6]
        })
    
    return {"trends": trends}

@app.get("/api/analytics/session-summary/{session_id}")
async def get_session_summary(session_id: str):
    """
    Get comprehensive summary of a stream session
    """
    conn = sqlite3.connect('stream_assistant_data.db')
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute('''
        SELECT * FROM stream_sessions WHERE session_id = ?
    ''', (session_id,))
    session = cursor.fetchone()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get track breakdown
    cursor.execute('''
        SELECT main_genre, subgenre, COUNT(*) as count
        FROM track_plays 
        WHERE session_id = ?
        GROUP BY main_genre, subgenre
        ORDER BY count DESC
    ''', (session_id,))
    genre_breakdown = cursor.fetchall()
    
    # Get interaction stats
    cursor.execute('''
        SELECT engagement_type, COUNT(*) as count, AVG(response_count) as avg_response
        FROM chat_interactions 
        WHERE session_id = ?
        GROUP BY engagement_type
    ''', (session_id,))
    interaction_stats = cursor.fetchall()
    
    conn.close()
    
    return {
        "session": {
            "session_id": session[1],
            "dj_username": session[2],
            "stream_title": session[3],
            "duration": session[5] - session[4] if session[5] else None,
            "total_tracks": session[6],
            "total_interactions": session[7],
            "peak_viewers": session[8]
        },
        "genre_breakdown": [
            {"main_genre": row[0], "subgenre": row[1], "count": row[2]}
            for row in genre_breakdown
        ],
        "interaction_stats": [
            {"type": row[0], "count": row[1], "avg_response": row[2]}
            for row in interaction_stats
        ]
    }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_webhook_database()
    logger.info("Webhook database initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)