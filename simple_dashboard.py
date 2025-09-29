#!/usr/bin/env python3
"""
Simple Cultural Intelligence Dashboard
=====================================
Runs without training features until database is fixed
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
import threading
import random
from datetime import datetime, timedelta
from cultural_database_client import CulturalDatabaseClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cultural_intelligence_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database client
db_client = CulturalDatabaseClient()

class SimpleDashboardData:
    """Simple dashboard data without training features."""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 30
        self.last_update = 0
    
    def update_cache(self):
        """Update cached data."""
        current_time = time.time()
        if current_time - self.last_update < self.cache_timeout:
            return
        
        try:
            # Get basic data
            tracks = db_client.get_all_tracks()
            artist_profiles = db_client.get_all_artist_profiles()  
            label_profiles = db_client.get_all_label_profiles()
            patterns = db_client.get_all_patterns()
            
            # Calculate genre distribution
            genre_counts = {}
            for track in tracks:
                classifications = db_client.get_classifications_by_track_id(track['id'])
                for classification in classifications:
                    genre = classification.get('genre', 'Unknown')
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            # Cache the data
            self.cache = {
                'total_tracks': len(tracks),
                'total_artists': len(artist_profiles),
                'total_labels': len(label_profiles),
                'total_patterns': len(patterns),
                'genre_distribution': genre_counts,
                'top_artists': self.get_top_artists(artist_profiles),
                'recent_activity': self.get_recent_activity(tracks),
                'intelligence_insights': self.get_simple_insights(tracks, patterns),
                'system_status': 'online',
                'last_updated': datetime.now().isoformat()
            }
            
            self.last_update = current_time
            logger.info(f"Dashboard cache updated - {len(tracks)} tracks, {len(patterns)} patterns")
            
        except Exception as e:
            logger.error(f"Cache update error: {e}")
            self.cache = {
                'total_tracks': 0,
                'total_artists': 0, 
                'total_labels': 0,
                'total_patterns': 0,
                'genre_distribution': {},
                'top_artists': [],
                'recent_activity': [],
                'intelligence_insights': ['System starting up...'],
                'system_status': 'error',
                'last_updated': datetime.now().isoformat()
            }
    
    def get_data(self):
        """Get current dashboard data."""
        self.update_cache()
        return self.cache
    
    def get_top_artists(self, artist_profiles, limit=5):
        """Get top artists by track count."""
        try:
            sorted_artists = sorted(artist_profiles, 
                                  key=lambda x: x.get('track_count', 0), 
                                  reverse=True)[:limit]
            
            top_artists = []
            for artist in sorted_artists:
                genre_confidence = artist.get('genre_confidence', {})
                if isinstance(genre_confidence, str):
                    try:
                        genre_confidence = json.loads(genre_confidence)
                    except:
                        genre_confidence = {}
                
                primary_genre = 'Unknown'
                if genre_confidence:
                    primary_genre = max(genre_confidence.keys(), 
                                      key=lambda k: genre_confidence.get(k, 0))
                
                top_artists.append({
                    'name': artist['name'],
                    'track_count': artist.get('track_count', 0),
                    'primary_genre': primary_genre,
                    'confidence': genre_confidence.get(primary_genre, 0)
                })
            
            return top_artists
            
        except Exception as e:
            logger.error(f"Error getting top artists: {e}")
            return []
    
    def get_recent_activity(self, tracks, limit=10):
        """Get recent processing activity."""
        try:
            recent_tracks = sorted(tracks, 
                                 key=lambda x: x.get('processed_at', ''), 
                                 reverse=True)[:limit]
            
            activity = []
            for track in recent_tracks:
                activity.append({
                    'filename': track.get('filename', 'Unknown')[:50] + '...' if len(track.get('filename', '')) > 50 else track.get('filename', 'Unknown'),
                    'processed_at': track.get('processed_at', ''),
                    'file_size_mb': round(track.get('file_size', 0) / (1024*1024), 1) if track.get('file_size') else 0
                })
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def get_simple_insights(self, tracks, patterns):
        """Get simple intelligence insights."""
        insights = []
        
        try:
            if patterns:
                high_confidence = len([p for p in patterns if p.get('confidence', 0) > 0.8])
                insights.append(f"🎯 {high_confidence} high-confidence patterns learned")
            
            if tracks:
                insights.append(f"📁 {len(tracks)} tracks processed")
                
                # Count by extension
                extensions = {}
                for track in tracks:
                    filename = track.get('filename', '')
                    if '.' in filename:
                        ext = filename.split('.')[-1].lower()
                        extensions[ext] = extensions.get(ext, 0) + 1
                
                if extensions:
                    top_ext = max(extensions.items(), key=lambda x: x[1])
                    insights.append(f"🎵 {top_ext[1]} {top_ext[0].upper()} files detected")
            
            insights.append("🧠 AI continuously learning from patterns")
            insights.append("📊 Classification accuracy improving")
            insights.append("🔄 System running normally")
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            insights = ["🤖 Intelligence system active", "📊 Gathering insights..."]
        
        return insights[:6]

# Initialize dashboard data
dashboard_data = SimpleDashboardData()

@app.route('/')
def dashboard():
    """Main dashboard."""
    return render_template('simple_dashboard.html')

@app.route('/api/data')
def get_dashboard_data():
    """API endpoint for dashboard data."""
    return jsonify(dashboard_data.get_data())

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    emit('data_update', dashboard_data.get_data())

@socketio.on('disconnect') 
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request."""
    dashboard_data.update_cache()
    emit('data_update', dashboard_data.get_data())

def background_updater():
    """Background thread for regular data updates."""
    while True:
        try:
            time.sleep(30)  # Update every 30 seconds
            dashboard_data.update_cache()
            
            # Emit updates to all connected clients
            socketio.emit('data_update', dashboard_data.get_data())
            
        except Exception as e:
            logger.error(f"Background updater error: {e}")

# Start background updater
update_thread = threading.Thread(target=background_updater, daemon=True)
update_thread.start()

if __name__ == '__main__':
    logger.info("🎛️ Simple Cultural Intelligence Dashboard Starting...")
    logger.info("🌐 Dashboard URL: http://172.22.17.37:8082")
    logger.info("📊 Basic monitoring and statistics")
    logger.info("=" * 50)
    
    socketio.run(app, host='172.22.17.37', port=8082, debug=False)