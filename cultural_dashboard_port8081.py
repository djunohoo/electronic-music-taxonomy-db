#!/usr/bin/env python3
"""
Cultural Intelligence Dashboard (Enhanced) - Port 8081
Serves the enhanced dashboard template you provided.
"""

from flask import Flask, render_template, jsonify
from cultural_database_client import CulturalDatabaseClient
from flask_socketio import SocketIO
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cultural_intelligence_2025'
socketio = SocketIO(app, cors_allowed_origins="*")


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_client = CulturalDatabaseClient()

@app.route('/api/data')
def api_data():
    # Gather all data needed for the enhanced dashboard
    data = {
        'total_tracks': db_client.count_discovered_tracks(),
        'total_artists': db_client.count_artist_profiles(),
        'total_labels': len(db_client.get_all_label_profiles()),
        'total_patterns': db_client.count_learned_patterns(),
        'genre_distribution': get_genre_distribution(),
        'intelligence_insights': get_intelligence_insights(),
        'recent_activity': get_recent_activity(),
        'training_stats': db_client.get_training_stats(),
        'current_question': get_current_training_question(),
    }
    logger.info(f"/api/data: total_tracks={data['total_tracks']} genre_distribution={data['genre_distribution']}")
    return jsonify(data)

# Helper: Genre distribution for chart
def get_genre_distribution():
    tracks = db_client.get_all_track_analyses()
    genre_counts = {}
    for t in tracks:
        genre = t.get('genre', 'Unknown')
        if genre:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    return genre_counts

# Helper: Intelligence insights (example: last 5 insights)
def get_intelligence_insights():
    # For demo, use last 5 patterns or classifications
    patterns = db_client.get_all_patterns()[-5:]
    insights = [
        f"Learned pattern: {p.get('pattern_type','?')} = {p.get('pattern_value','?')} ({p.get('genre','?')})"
        for p in patterns
    ]
    return insights

# Helper: Recent activity (last 10 tracks)
def get_recent_activity():
    tracks = db_client.get_all_discovered_tracks()[-10:]
    activity = []
    for t in tracks:
        activity.append({
            'filename': t.get('filename', 'Unknown'),
            'file_size_mb': round(t.get('file_size', 0)/1024/1024, 2) if t.get('file_size') else 0,
            'processed_at': t.get('file_modified', t.get('file_created', '')),
        })
    return activity

# Helper: Current training question (use training_questions or fallback)
def get_current_training_question():
    questions = db_client.get_training_questions(limit=1)
    if questions:
        q = questions[0]
        # Flatten for frontend
        return {
            'id': q.get('id'),
            'question': q.get('question', {}).get('question', ''),
            'type': q.get('question', {}).get('type', ''),
            'context': q.get('context', {}),
            'priority': q.get('priority', 1),
            'uncertainty_score': 1.0 - (q.get('priority', 50)/100.0),
            'track_data': q.get('context', {}).get('track_data', {}),
        }
    return None


@app.route('/')
def index():
    return render_template('enhanced_dashboard.html')

@app.route('/download/<path:file_path>')
def download_track(file_path):
    """Serve track files for download/streaming"""
    try:
        from urllib.parse import unquote
        import os
        from flask import send_file, abort
        
        # Decode the URL-encoded path
        decoded_path = unquote(file_path)
        logger.info(f"Download request for: {decoded_path}")
        
        # Security check - ensure the file exists and is within reasonable bounds
        if os.path.exists(decoded_path) and os.path.isfile(decoded_path):
            # Check if it's an audio file
            audio_extensions = ['.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg']
            file_ext = os.path.splitext(decoded_path)[1].lower()
            
            if file_ext in audio_extensions:
                return send_file(decoded_path, as_attachment=True)
            else:
                logger.warning(f"File is not an audio file: {decoded_path}")
                abort(400)
        else:
            logger.warning(f"File not found: {decoded_path}")
            abort(404)
            
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        abort(500)

if __name__ == '__main__':
    # Use the static NIC IP to make dashboard accessible on LAN
    host_ip = '172.22.17.37'
    port = 8081
    logger.info(f"Starting Enhanced Dashboard on http://{host_ip}:{port} ...")
    logger.info(f"Dashboard will also be accessible from other machines on the network")
    logger.info(f"Supabase connection: {db_client.config['supabase']['url']}")
    
    # Test database connection on startup
    try:
        test_count = db_client.count_discovered_tracks()
        logger.info(f"Database connection successful - found {test_count} tracks in cultural_tracks")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Dashboard will start but data may not be available")
    
    socketio.run(app, host=host_ip, port=port, debug=False)
