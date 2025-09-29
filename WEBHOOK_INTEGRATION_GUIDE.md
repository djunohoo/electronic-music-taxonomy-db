# 🔗 WEBHOOK INTEGRATION GUIDE
## Connecting Live DJ Stream Assistant to Main Taxonomy Database

---

## 🎯 **QUICK OVERVIEW**

This integration allows the **Live DJ Stream Assistant** to send real-time data back to your main **Electronic Music Taxonomy Database**, creating a feedback loop that:

- ✅ **Tracks real-world genre usage** in live streams
- ✅ **Analyzes audience engagement** by subgenre
- ✅ **Improves classification algorithms** with live data
- ✅ **Builds comprehensive analytics** for DJs and the scene

---

## 🛠️ **SETUP PROCESS**

### **1. Start the Webhook Server**

```bash
# In your main taxonomy database project
cd electronic-music-taxonomy-db
python stream_assistant_webhook.py
```

This starts a FastAPI server on `http://localhost:8000` that can receive webhook data.

### **2. Configure Stream Assistant**

In your Live Stream Assistant project, configure the webhook endpoint:

```python
WEBHOOK_BASE_URL = "http://your-domain.com:8000"  # Or localhost for testing
WEBHOOK_TIMEOUT = 5  # seconds
WEBHOOK_ENABLED = True
```

### **3. Send Data from Stream Assistant**

Use the webhook client to send data when events happen:

```python
from stream_webhook_client import StreamAssistantWebhookClient

# Initialize client
webhook_client = StreamAssistantWebhookClient("http://localhost:8000")

# When a new track is detected in rekordbox
track_data = {
    "artist": "LTJ Bukem",
    "title": "Music", 
    "classification": {
        "main_genre": "drum and bass",
        "subgenre": "liquid dnb",
        "confidence": 0.96,
        "characteristics": ["atmospheric", "jazzy", "melodic"]
    }
}

stream_info = {
    "twitch_username": "djunohoo",
    "stream_title": "Deep House Vibes",
    "viewer_count": 127
}

# Send to main database
webhook_client.send_track_classification(track_data, stream_info)
```

---

## 📡 **WEBHOOK ENDPOINTS**

### **Track Classification** `POST /api/webhook/track-classified`
Sent when a new track is detected and classified:

```json
{
  "timestamp": "2025-09-28T20:30:00Z",
  "dj_stream": {
    "twitch_username": "djunohoo",
    "stream_title": "Deep House Vibes",
    "viewer_count": 127,
    "platform": "twitch"
  },
  "track_data": {
    "artist": "LTJ Bukem",
    "title": "Music",
    "bpm": 174,
    "key": "A minor",
    "classification": {
      "main_genre": "drum and bass",
      "subgenre": "liquid dnb", 
      "confidence": 0.96,
      "characteristics": ["atmospheric", "jazzy", "melodic"]
    }
  },
  "session_id": "stream-session-uuid",
  "event_type": "track_start"
}
```

### **Chat Interaction** `POST /api/webhook/chat-interaction`
Sent when the bot posts to Twitch chat:

```json
{
  "timestamp": "2025-09-28T20:30:15Z",
  "dj_stream": { /* same as above */ },
  "chat_interaction": {
    "message_sent": "🌊 Liquid DnB detected! Notice those smooth jazz influences...",
    "engagement_type": "educational",
    "audience_reaction": "positive",
    "response_count": 8,
    "emoji_reactions": {"🌊": 5, "🔥": 3}
  },
  "session_id": "stream-session-uuid",
  "event_type": "chat_message"
}
```

### **Stream Stats** `POST /api/webhook/stream-stats`
General stream updates and session management:

```json
{
  "timestamp": "2025-09-28T20:45:00Z",
  "dj_stream": { /* updated viewer counts, etc */ },
  "session_id": "stream-session-uuid", 
  "event_type": "stream_update"  // or "stream_start", "stream_end"
}
```

---

## 🗄️ **DATABASE STORAGE**

The webhook system creates these tables in `stream_assistant_data.db`:

### **stream_sessions**
- Session metadata (DJ, title, duration, totals)
- Track count and interaction analytics
- Peak viewer counts

### **track_plays** 
- Individual track classifications
- BPM, key, confidence scores
- Real-time viewer counts when played

### **chat_interactions**
- Bot messages and audience responses
- Engagement type and reaction analysis
- Connection to specific tracks

### **genre_analytics**
- Aggregated genre performance data
- Popular characteristics by subgenre
- Engagement scores and play counts

---

## 📊 **ANALYTICS ENDPOINTS**

### **Genre Trends** `GET /api/analytics/genre-trends`
See which genres are popular in live streams:

```json
{
  "trends": [
    {
      "main_genre": "drum and bass",
      "subgenre": "liquid dnb",
      "total_plays": 47,
      "total_engagement": 156,
      "average_confidence": 0.94,
      "popular_characteristics": {
        "atmospheric": 23,
        "jazzy": 19,
        "melodic": 31
      }
    }
  ]
}
```

### **Session Summary** `GET /api/analytics/session-summary/{session_id}`
Comprehensive analysis of a single stream:

```json
{
  "session": {
    "dj_username": "djunohoo",
    "total_tracks": 24,
    "total_interactions": 67,
    "peak_viewers": 189
  },
  "genre_breakdown": [
    {"main_genre": "house", "subgenre": "deep house", "count": 8},
    {"main_genre": "breaks", "subgenre": "florida breaks", "count": 6}
  ],
  "interaction_stats": [
    {"type": "educational", "count": 23, "avg_response": 5.2},
    {"type": "hype", "count": 31, "avg_response": 8.7}
  ]
}
```

---

## 🧪 **TESTING THE INTEGRATION**

### **1. Run the Demo**
```bash
# Start webhook server in one terminal
python stream_assistant_webhook.py

# Run demo client in another terminal  
python stream_webhook_client_demo.py
```

This simulates a live stream session with track changes and chat interactions.

### **2. Check the Data**
```bash
# View stored data
sqlite3 stream_assistant_data.db
.tables
SELECT * FROM track_plays LIMIT 5;
SELECT * FROM genre_analytics;
```

### **3. Test Analytics**
```bash
curl http://localhost:8000/api/analytics/genre-trends
curl http://localhost:8000/api/analytics/session-summary/[session-id]
```

---

## 🚀 **DEPLOYMENT CONSIDERATIONS**

### **Production Setup**
- Deploy webhook server on cloud (AWS, Digital Ocean, etc.)
- Use HTTPS with SSL certificates
- Set up monitoring and alerting
- Configure proper logging and error handling

### **Security**
- Add API key authentication for webhook endpoints
- Validate payload signatures to prevent spoofing
- Rate limit webhook requests
- Use HTTPS for all communication

### **Scaling**
- Use PostgreSQL instead of SQLite for production
- Add Redis for caching and message queuing
- Implement webhook retry logic with exponential backoff
- Consider database sharding for high-volume streams

---

## 🎯 **WHAT THIS ENABLES**

### **For Your Taxonomy System**
- **Real-world validation** of genre classifications
- **Audience engagement data** by subgenre
- **Trend analysis** for electronic music evolution
- **Quality metrics** for classification confidence

### **For DJs**
- **Performance analytics** for their stream sessions
- **Audience engagement insights** by track/genre
- **Mixing technique feedback** based on chat reactions
- **Discovery of popular genres/characteristics**

### **For the Scene**
- **Electronic music education** at scale
- **Genre evolution tracking** in real-time
- **Community building** around shared knowledge
- **Data-driven insights** into scene preferences

---

## 🛠️ **IMPLEMENTATION TIMELINE**

1. **Week 1**: Basic webhook server + simple track classification
2. **Week 2**: Chat interaction tracking + basic analytics  
3. **Week 3**: Stream assistant integration + testing
4. **Week 4**: Production deployment + monitoring

---

**This webhook integration transforms your taxonomy system from a static classification tool into a living, breathing database that learns from real DJ performances and audience reactions!** 🎵📊

Ready to revolutionize electronic music analytics? 🚀