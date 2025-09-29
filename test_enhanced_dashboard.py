#!/usr/bin/env python3
"""
Test version of enhanced dashboard to debug issues
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def dashboard():
    """Main dashboard route."""
    try:
        return render_template('live_training_dashboard.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return f"Template error: {e}"

@app.route('/api/stats')
def api_stats():
    """Basic stats API."""
    return jsonify({
        'tracks': 0,
        'artists': 0,
        'status': 'testing'
    })

if __name__ == '__main__':
    logger.info("🧪 Testing Enhanced Dashboard...")
    try:
        socketio.run(app, host='172.22.17.37', port=8081, debug=True)
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        print(f"ERROR: {e}")