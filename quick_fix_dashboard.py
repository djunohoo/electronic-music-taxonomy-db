#!/usr/bin/env python3
"""
QUICK FIX - Enhanced Cultural Intelligence Dashboard
==================================================
Fixed version that actually works and shows questions!
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
import random
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cultural_intelligence_training_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Mock data for now - we'll get questions working first
class WorkingDashboard:
    def __init__(self):
        self.questions_pool = [
            {
                'id': 1,
                'question': 'This track has a distinctive 4/4 kick pattern with saw wave synths. The tempo is around 128 BPM. What genre classification would you assign?',
                'type': 'genre_classification',
                'track_info': 'Artist: Unknown | Tempo: 128 BPM | Key: C minor',
                'uncertainty_score': 0.65,
                'context': {'tempo': 128, 'key': 'C minor'}
            },
            {
                'id': 2,
                'question': 'Artist consistently releases tracks with rolling basslines and breakbeats around 175 BPM. This specific track has those characteristics. Genre?',
                'type': 'artist_profiling', 
                'track_info': 'Artist: DJ Unknown | Tempo: 175 BPM | Breakbeat pattern detected',
                'uncertainty_score': 0.45,
                'context': {'tempo': 175, 'pattern': 'breakbeat'}
            },
            {
                'id': 3,
                'question': 'Label specializes in melodic progressive content, but this track has harder techno elements at 132 BPM. Classification?',
                'type': 'label_specialization',
                'track_info': 'Label: Progressive Records | Tempo: 132 BPM | Hard elements detected',
                'uncertainty_score': 0.75,
                'context': {'tempo': 132, 'style': 'progressive/techno hybrid'}
            },
            {
                'id': 4,
                'question': 'Track features ethereal pads, no kick drum, around 90 BPM with long reverb tails. What genre best fits?',
                'type': 'tempo_analysis',
                'track_info': 'Tempo: 90 BPM | No percussion | Atmospheric pads',
                'uncertainty_score': 0.35,
                'context': {'tempo': 90, 'style': 'ambient'}
            },
            {
                'id': 5,
                'question': 'Heavy bass drops, syncopated rhythms at 140 BPM, with wobble bass synthesis. Classification?',
                'type': 'bass_analysis',
                'track_info': 'Tempo: 140 BPM | Wobble bass | Heavy drops',
                'uncertainty_score': 0.25,
                'context': {'tempo': 140, 'style': 'dubstep characteristics'}
            }
        ]
        self.current_question_index = 0
    
    def get_data(self):
        """Get dashboard data."""
        return {
            'total_tracks': 15247,
            'total_artists': 892,
            'total_labels': 156,
            'total_patterns': 2847,
            'training_stats': {
                'total_sessions': 342,
                'recent_sessions': 28,
                'avg_response_time': '2.3s'
            },
            'current_question': self.get_current_question(),
            'genre_distribution': {
                'House': 4200,
                'Techno': 3100,
                'Trance': 2800,
                'Progressive': 1900,
                'Dubstep': 1200,
                'Drum & Bass': 1500,
                'Ambient': 547
            },
            'intelligence_insights': [
                '🎵 Detected 15 new pattern variations in house sub-genres',  
                '🤖 AI confidence improved 12% on progressive classifications',
                '🔥 Breakthrough: Identified signature bass patterns for 3 major labels',
                '⚡ Real-time learning active: Processing human feedback'
            ],
            'recent_activity': [
                {'filename': 'progressive_house_master.mp3', 'file_size_mb': 8.2, 'processed_at': '2025-09-28T20:45:00Z'},
                {'filename': 'techno_underground_021.wav', 'file_size_mb': 52.1, 'processed_at': '2025-09-28T20:42:15Z'},
                {'filename': 'trance_uplifting_mix.flac', 'file_size_mb': 89.3, 'processed_at': '2025-09-28T20:38:30Z'}
            ]
        }
    
    def get_current_question(self):
        """Get the current training question."""
        if self.current_question_index >= len(self.questions_pool):
            self.current_question_index = 0
        
        question = self.questions_pool[self.current_question_index]
        return question
    
    def get_next_question(self):
        """Get next question in sequence."""
        self.current_question_index = (self.current_question_index + 1) % len(self.questions_pool)
        return self.get_current_question()

# Initialize dashboard
dashboard = WorkingDashboard()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('enhanced_dashboard.html')

@app.route('/api/data')
def get_dashboard_data():
    """Get all dashboard data."""
    try:
        return jsonify(dashboard.get_data())
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/question')
def get_training_question():
    """Get current training question."""
    try:
        question = dashboard.get_current_question()
        return jsonify({'status': 'success', 'question': question})
    except Exception as e:
        print(f"Question API Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/training/respond', methods=['POST'])
def submit_training_response():
    """Submit training response."""
    try:
        data = request.get_json()
        print(f"📝 Training Response: {data.get('genre', 'Custom')} - {data.get('response_text', 'No text')}")
        
        # Move to next question after response
        next_question = dashboard.get_next_question()
        
        return jsonify({
            'status': 'success',
            'message': 'Response recorded!',
            'next_question': next_question
        })
    except Exception as e:
        print(f"Response API Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"✅ Client connected: {request.sid}")
    emit('data_update', dashboard.get_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"❌ Client disconnected: {request.sid}")

@socketio.on('request_question')
def handle_question_request():
    """Handle request for new question."""
    question = dashboard.get_next_question()
    emit('new_question', question)

@socketio.on('request_update')
def handle_update_request():
    """Handle update request."""
    emit('data_update', dashboard.get_data())

if __name__ == '__main__':
    print("🎛️ QUICK FIX Dashboard Starting...")
    print("🌐 Dashboard URL: http://172.22.17.37:8081")
    print("🎓 Questions should actually load now!")
    print("=" * 50)
    
    socketio.run(
        app,
        host='172.22.17.37',
        port=8081,
        debug=False,
        allow_unsafe_werkzeug=True
    )