#!/usr/bin/env python3
"""
Enhanced Cultural Intelligence Dashboard with AI Training Zone
=============================================================
Interactive web dashboard with real-time AI training for livestreaming
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
import threading
import random
from datetime import datetime, timedelta
from cultural_database_client import EnhancedCulturalDatabaseClient as CulturalDatabaseClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with SocketIO for real-time updates
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cultural_intelligence_training_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database client
db_client = CulturalDatabaseClient()

class EnhancedDashboardData:
    """Enhanced real-time data aggregator with AI training features."""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 30  # seconds
        self.last_update = 0
        self.current_question = None
    
    def update_cache(self):
        """Update cached data."""
        current_time = time.time()
        if current_time - self.last_update < self.cache_timeout:
            return
        
        try:
            # Get all data
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
                'top_artists': self.get_top_artists(),
                'recent_activity': self.get_recent_activity(),
                'intelligence_insights': self.get_intelligence_insights(),
                'pending_questions': self.get_pending_training_questions(),
                'training_stats': self.get_training_stats(),
                'current_question': self.generate_ai_question(),
                'last_updated': datetime.now().isoformat()
            }
            
            self.last_update = current_time
            logger.info("Dashboard cache updated")
            
        except Exception as e:
            logger.error(f"Cache update error: {e}")
    
    def get_data(self):
        """Get current dashboard data."""
        self.update_cache()
        return self.cache
    
    def get_top_artists(self, limit=5):
        """Get top artists by track count."""
        try:
            artist_profiles = db_client.get_all_artist_profiles()
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
    
    def get_recent_activity(self, limit=10):
        """Get recent processing activity."""
        try:
            tracks = db_client.get_all_tracks()
            recent_tracks = sorted(tracks, 
                                 key=lambda x: x.get('processed_at', ''), 
                                 reverse=True)[:limit]
            
            activity = []
            for track in recent_tracks:
                activity.append({
                    'filename': track.get('filename', 'Unknown'),
                    'processed_at': track.get('processed_at', ''),
                    'file_size_mb': round(track.get('file_size', 0) / (1024*1024), 1)
                })
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def get_intelligence_insights(self):
        """Get intelligence insights and learning progress."""
        insights = []
        
        try:
            patterns = db_client.get_all_patterns()
            if patterns:
                high_confidence = len([p for p in patterns if p.get('confidence', 0) > 0.8])
                insights.append(f"🎯 {high_confidence} high-confidence patterns learned")
            
            artists = db_client.get_all_artist_profiles()
            profiled = len([a for a in artists if a.get('track_count', 0) >= 5])
            if profiled > 0:
                insights.append(f"👨‍🎤 {profiled} artists profiled with 5+ tracks")
            
            labels = db_client.get_all_label_profiles()
            specialized = len([l for l in labels if l.get('release_count', 0) >= 10])
            if specialized > 0:
                insights.append(f"🏷️ {specialized} labels with specialized profiles")
            
            # Training progress
            training_stats = self.get_training_stats()
            if training_stats['total_sessions'] > 0:
                insights.append(f"🎓 {training_stats['total_sessions']} human training sessions")
            
            insights.append("🧠 AI continuously learning from patterns")
            insights.append("📈 Classification accuracy improving")
            
        except Exception as e:
            logger.error(f"Error getting intelligence insights: {e}")
            insights = ["🤖 Intelligence system active", "📊 Gathering insights..."]
        
        return insights[:6]
    
    def get_pending_training_questions(self):
        """Get pending training questions for AI learning."""
        return db_client.get_training_questions()
    
    def get_training_stats(self):
        """Get training session statistics."""
        return db_client.get_training_stats()
    
    def generate_ai_question(self):
        """Generate an intelligent training question."""
        try:
            questions = self.get_pending_training_questions()
            if not questions:
                return None
            
            question_data = random.choice(questions)
            context = question_data.get('context_data', {})
            
            # Generate contextual question based on type
            if question_data['question_type'] == 'genre_uncertainty':
                genres = context.get('genres', ['House', 'Techno'])
                reason = context.get('reason', 'Classification uncertain')
                question_text = f"I'm unsure between {genres[0]} and {genres[1]}. {reason}. What genre is this?"
            
            elif question_data['question_type'] == 'artist_profiling':
                artist = context.get('artist', 'Unknown Artist')
                distribution = context.get('genre_distribution', {})
                question_text = f"Artist '{artist}' has diverse tracks: {', '.join([f'{g}({c})' for g, c in distribution.items()])}. What's their primary specialty?"
            
            elif question_data['question_type'] == 'label_specialization':
                label = context.get('label', 'Unknown Label')
                usual = context.get('usual_genre', 'Trance')
                this_track = context.get('this_track_genre', 'House')
                question_text = f"Label '{label}' usually releases {usual}, but this track seems like {this_track}. Correct classification?"
            
            elif question_data['question_type'] == 'tempo_analysis':
                bpm = context.get('bpm_detected', 128)
                genres = context.get('genres', ['House', 'Techno'])
                reason = context.get('reason', 'Tempo classification uncertain')
                question_text = f"Track at {bpm} BPM could be {genres[0]} or {genres[1]}. {reason}. What's the correct genre?"
            
            else:
                question_text = "I need your expertise to improve my accuracy. Can you help train me?"
            
            return {
                'id': question_data['id'],
                'question': question_text,
                'type': question_data['question_type'],
                'context': context,
                'uncertainty_score': question_data.get('uncertainty_score', 0.65),
                'track_info': f"Track analysis pending..."
            }
            
        except Exception as e:
            logger.error(f"Error generating AI question: {e}")
            return {
                'id': 1,
                'question': "Help me learn! What genre would you classify an energetic 128 BPM track with four-on-the-floor kicks?",
                'type': 'demo_question',
                'context': {'bpm': 128, 'pattern': 'four-on-the-floor'},
                'uncertainty_score': 0.65,
                'track_info': "Demo track for training"
            }
    
    def process_training_response(self, question_id, response_data):
        """Process human training response."""
        try:
            # Record training session in live database
            session_data = {
                'question_id': question_id,
                'question_type': response_data.get('question_type', 'user_feedback'),
                'question_text': response_data.get('question', ''),
                'human_response': response_data,
                'response_text': response_data.get('response_text', ''),
                'answered_at': datetime.now().isoformat(),
                'feedback_quality': response_data.get('quality_rating', 5),
                'response_time_ms': response_data.get('response_time', 2000)
            }
            
            # Save to live database
            success = db_client.create_training_session(session_data)
            
            if success and question_id:
                # Mark question as processed in live database
                db_client.update_training_queue(question_id, {
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat(),
                    'human_response': response_data
                })
            
            # Log the learning
            genre = response_data.get('genre', 'Unknown')
            confidence = response_data.get('confidence', 0.8)
            
            logger.info(f"🎓 LIVE AI Learning: Question {question_id} → Genre: {genre} (Confidence: {confidence})")
            logger.info(f"📊 Training session recorded in live database")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing training response: {e}")
            return False

# Initialize dashboard data
dashboard_data = EnhancedDashboardData()

@app.route('/')
def dashboard():
    """Main live training dashboard optimized for Rekordbox workflow."""
    return render_template('live_training_dashboard.html')

@app.route('/api/data')
def get_dashboard_data():
    """API endpoint for dashboard data."""
    return jsonify(dashboard_data.get_data())

@app.route('/api/training/respond', methods=['POST'])
def handle_training_response():
    """Handle training response from user."""
    try:
        response_data = request.json
        question_id = response_data.get('question_id')
        
        success = dashboard_data.process_training_response(question_id, response_data)
        
        if success:
            # Emit update to all clients
            socketio.emit('training_update', {
                'message': f"✅ Thanks! Learned: {response_data.get('genre', 'feedback')}",
                'timestamp': datetime.now().isoformat()
            })
            
            return jsonify({'status': 'success', 'message': 'Training response recorded'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to process response'}), 500
            
    except Exception as e:
        logger.error(f"Training response error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/training/question')
def get_training_question():
    """Get next training question for AI learning."""
    try:
        question = dashboard_data.generate_ai_question()
        if question:
            return jsonify({'status': 'success', 'question': question})
        else:
            return jsonify({'status': 'success', 'question': None, 'message': 'No pending questions'})
    except Exception as e:
        logger.error(f"Error getting training question: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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

@socketio.on('request_question')
def handle_question_request():
    """Handle request for new AI training question."""
    question = dashboard_data.generate_ai_question()
    emit('new_question', question)

def background_updater():
    """Background thread for regular data updates."""
    while True:
        try:
            time.sleep(15)  # Update every 15 seconds
            dashboard_data.update_cache()
            
            # Emit updates to all connected clients
            socketio.emit('data_update', dashboard_data.get_data())
            
        except Exception as e:
            logger.error(f"Background updater error: {e}")

# Start background updater
update_thread = threading.Thread(target=background_updater, daemon=True)
update_thread.start()

if __name__ == '__main__':
    logger.info("🎛️ Enhanced Cultural Intelligence Dashboard Starting...")
    logger.info("🌐 Dashboard URL: http://172.22.17.37:8082")
    logger.info("🎓 Interactive AI Training Zone Enabled!")
    logger.info("📡 Perfect for livestreaming AI learning!")
    logger.info("=" * 60)
    
    socketio.run(app, host='172.22.17.37', port=8082, debug=False)