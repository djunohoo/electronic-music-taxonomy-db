#!/usr/bin/env python3
"""
Cultural Intelligence Dashboard - Real-Time Web Interface
========================================================
Stunning web dashboard for showcasing Cultural Intelligence System
Perfect for livestreaming and LAN access with real-time data visualization
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
import threading
from datetime import datetime, timedelta
from cultural_database_client import CulturalDatabaseClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with SocketIO for real-time updates
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cultural_intelligence_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database client
db_client = CulturalDatabaseClient()

class DashboardData:
    """Real-time data aggregator for dashboard."""
    
    def __init__(self):
        self.cache = {}
        self.last_update = None
        self.update_interval = 10  # seconds
        
    def get_collection_stats(self):
        """Get overall collection statistics."""
        try:
            stats = {
                'total_tracks': db_client.count_discovered_tracks(),
                'total_duplicates': db_client.count_duplicate_groups(),
                'total_artists': db_client.count_artist_profiles(),
                'total_labels': len(db_client.get_all_label_profiles()),
                'learned_patterns': db_client.count_learned_patterns(),
                'last_updated': datetime.now().isoformat()
            }
            
            # Calculate intelligence level (0-100 based on data richness)
            base_score = min(stats['total_tracks'] / 1000 * 30, 30)  # 30% for track volume
            pattern_score = min(stats['learned_patterns'] / 100 * 25, 25)  # 25% for patterns
            profile_score = min(stats['total_artists'] / 50 * 25, 25)  # 25% for profiles  
            quality_score = 20  # Base quality score
            
            stats['intelligence_level'] = int(base_score + pattern_score + profile_score + quality_score)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                'total_tracks': 0,
                'total_duplicates': 0,
                'total_artists': 0,
                'total_labels': 0,
                'learned_patterns': 0,
                'intelligence_level': 0,
                'last_updated': datetime.now().isoformat()
            }
    
    def get_genre_distribution(self):
        """Get genre distribution from classifications."""
        try:
            classifications = db_client.get_all_track_analyses()
            genre_counts = {}
            
            for track in classifications:
                genre = track.get('genre', 'Unknown')
                if genre and genre != 'Unknown':
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            # Convert to percentage
            total = sum(genre_counts.values()) if genre_counts else 1
            genre_distribution = []
            
            for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total) * 100
                genre_distribution.append({
                    'genre': genre,
                    'count': count,
                    'percentage': round(percentage, 1)
                })
            
            return genre_distribution[:10]  # Top 10 genres
            
        except Exception as e:
            logger.error(f"Error getting genre distribution: {e}")
            return []
    
    def get_recent_activity(self, limit=20):
        """Get recent scanning activity."""
        try:
            # Get recent tracks from cultural_tracks
            recent_tracks = db_client.get_all_discovered_tracks()
            
            # Sort by processed_at and take most recent
            if recent_tracks:
                sorted_tracks = sorted(recent_tracks, 
                                     key=lambda x: x.get('processed_at', ''), 
                                     reverse=True)[:limit]
                
                activity = []
                for track in sorted_tracks:
                    # Get classification for this track if available
                    classifications = db_client.get_all_track_analyses()
                    track_classification = next((c for c in classifications if c.get('track_id') == track['id']), None)
                    
                    activity.append({
                        'filename': track.get('filename', 'Unknown'),
                        'artist': track_classification.get('artist', 'Unknown') if track_classification else 'Unknown',
                        'genre': track_classification.get('genre', 'Unknown') if track_classification else 'Unknown',
                        'processed_at': track.get('processed_at', ''),
                        'file_size': track.get('file_size', 0)
                    })
                
                return activity
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def get_top_artists(self, limit=10):
        """Get top artists by track count."""
        try:
            artist_profiles = db_client.get_all_artist_profiles()
            
            # Sort by track count
            sorted_artists = sorted(artist_profiles, 
                                  key=lambda x: x.get('track_count', 0), 
                                  reverse=True)[:limit]
            
            top_artists = []
            for artist in sorted_artists:
                # Parse genre confidence if it's a string
                genre_confidence = artist.get('genre_confidence', {})
                if isinstance(genre_confidence, str):
                    try:
                        genre_confidence = json.loads(genre_confidence)
                    except:
                        genre_confidence = {}
                
                # Get primary genre
                primary_genre = 'Unknown'
                if genre_confidence:
                    primary_genre = max(genre_confidence.keys(), 
                                      key=lambda k: genre_confidence.get(k, 0))
                
                top_artists.append({
                    'name': artist.get('name', 'Unknown'),
                    'track_count': artist.get('track_count', 0),
                    'primary_genre': primary_genre,
                    'confidence': genre_confidence.get(primary_genre, 0) if isinstance(genre_confidence, dict) else 0
                })
            
            return top_artists
            
        except Exception as e:
            logger.error(f"Error getting top artists: {e}")
            return []
    
    def get_duplicate_analysis(self):
        """Get duplicate file analysis."""
        try:
            # Simple duplicate stats for now
            duplicate_count = db_client.count_duplicate_groups()
            total_tracks = db_client.count_discovered_tracks()
            
            duplicate_percentage = (duplicate_count / max(total_tracks, 1)) * 100
            
            return {
                'total_duplicates': duplicate_count,
                'duplicate_percentage': round(duplicate_percentage, 1),
                'space_saved': duplicate_count * 8.5,  # Estimate MB saved
                'efficiency_score': max(0, 100 - duplicate_percentage)
            }
            
        except Exception as e:
            logger.error(f"Error getting duplicate analysis: {e}")
            return {
                'total_duplicates': 0,
                'duplicate_percentage': 0,
                'space_saved': 0,
                'efficiency_score': 100
            }
    
    def get_intelligence_insights(self):
        """Get AI intelligence insights."""
        try:
            patterns = db_client.get_patterns()
            
            # Calculate pattern quality metrics
            high_confidence_patterns = [p for p in patterns if p.get('confidence', 0) > 0.8]
            pattern_coverage = len(patterns)
            pattern_quality = len(high_confidence_patterns) / max(len(patterns), 1) * 100
            
            # Learning progress
            total_samples = sum(p.get('sample_size', 0) for p in patterns)
            avg_confidence = sum(p.get('confidence', 0) for p in patterns) / max(len(patterns), 1)
            
            return {
                'total_patterns': len(patterns),
                'high_confidence_patterns': len(high_confidence_patterns),
                'pattern_quality': round(pattern_quality, 1),
                'learning_samples': total_samples,
                'avg_confidence': round(avg_confidence, 3),
                'intelligence_growth': min(total_samples / 1000 * 100, 100)
            }
            
        except Exception as e:
            logger.error(f"Error getting intelligence insights: {e}")
            return {
                'total_patterns': 0,
                'high_confidence_patterns': 0,
                'pattern_quality': 0,
                'learning_samples': 0,
                'avg_confidence': 0,
                'intelligence_growth': 0
            }
    
    def update_cache(self):
        """Update cached dashboard data."""
        try:
            self.cache = {
                'collection_stats': self.get_collection_stats(),
                'genre_distribution': self.get_genre_distribution(),
                'recent_activity': self.get_recent_activity(),
                'top_artists': self.get_top_artists(),
                'duplicate_analysis': self.get_duplicate_analysis(),
                'intelligence_insights': self.get_intelligence_insights()
            }
            self.last_update = datetime.now()
            
            # Emit to all connected clients
            socketio.emit('data_update', self.cache)
            
        except Exception as e:
            logger.error(f"Error updating cache: {e}")
    
    def get_data(self):
        """Get cached data or update if needed."""
        if (self.last_update is None or 
            datetime.now() - self.last_update > timedelta(seconds=self.update_interval)):
            self.update_cache()
        
        return self.cache

# Initialize dashboard data
dashboard_data = DashboardData()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_dashboard_data():
    """API endpoint for dashboard data."""
    return jsonify(dashboard_data.get_data())

@app.route('/api/stats')
def get_stats():
    """Quick stats endpoint."""
    return jsonify(dashboard_data.get_collection_stats())

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
            time.sleep(15)  # Update every 15 seconds
            dashboard_data.update_cache()
        except Exception as e:
            logger.error(f"Background updater error: {e}")

# Start background updater
update_thread = threading.Thread(target=background_updater, daemon=True)
update_thread.start()

if __name__ == '__main__':
    # Run on LAN-accessible IP for streaming
    logger.info("Starting Cultural Intelligence Dashboard...")
    logger.info("Access dashboard at: http://172.22.17.37:8083")
    logger.info("Perfect for livestreaming! 🎵✨")
    
    socketio.run(app, host='172.22.17.37', port=8083, debug=False)