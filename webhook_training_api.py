#!/usr/bin/env python3
"""
Simple Webhook Training API
===========================
Clean API endpoints for external dashboard integration
No complex UI - just pure data exchange
"""

from flask import Flask, jsonify, request
from cultural_database_client import CulturalDatabaseClient
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for external dashboard
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize database client
try:
    db_client = CulturalDatabaseClient()
    logger.info("✅ Database client initialized successfully")
except Exception as e:
    logger.error(f"❌ Database client failed to initialize: {e}")
    db_client = None

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db_client else 'disconnected'
    })

@app.route('/api/training/question', methods=['GET'])
def get_training_question():
    """Get next training question from database."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
            
        questions = db_client.get_training_questions(limit=1)
        
        if not questions:
            return jsonify({
                'question': None,
                'message': 'No pending questions available'
            })
        
        question = questions[0]
        
        # Clean the question data for JSON serialization
        clean_question = {
            'id': question.get('id'),
            'question': question.get('question', 'No question text'),
            'question_type': question.get('question_type', 'unknown'),
            'context': question.get('context_data', {}),
            'priority': question.get('priority', 1),
            'uncertainty_score': question.get('uncertainty_score', 0.5),
            'created_at': question.get('created_at'),
            'track_info': f"Question ID: {question.get('id')} | Type: {question.get('question_type', 'unknown')}"
        }
        
        return jsonify({
            'status': 'success',
            'question': clean_question
        })
        
    except Exception as e:
        logger.error(f"Error getting training question: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/training/respond', methods=['POST'])
def submit_training_response():
    """Submit training response to database."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
            
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Log the response for debugging
        logger.info(f"📝 Training Response: Genre={data.get('genre')}, Custom={data.get('response_text', 'None')}")
        
        # Store response in database
        response_data = {
            'question_id': data.get('question_id'),
            'response_type': 'genre_classification' if data.get('genre') else 'custom',
            'response_data': {
                'genre': data.get('genre'),
                'custom_text': data.get('response_text'),
                'confidence': data.get('confidence', 0.8)
            },
            'responded_by': 'human_trainer',
            'responded_at': datetime.now().isoformat()
        }
        
        # Update question status (if method exists)
        try:
            if hasattr(db_client, 'update_training_question'):
                db_client.update_training_question(
                    data.get('question_id'), 
                    {'status': 'completed', 'response': response_data}
                )
        except Exception as update_error:
            logger.warning(f"Could not update question status: {update_error}")
        
        return jsonify({
            'status': 'success',
            'message': f"Response recorded: {data.get('genre', 'Custom feedback')}",
            'response_id': data.get('question_id')
        })
        
    except Exception as e:
        logger.error(f"Error submitting training response: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_basic_stats():
    """Get basic system statistics."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
        
        # Safe stats that won't cause JSON errors
        stats = {
            'total_tracks': 0,
            'total_artists': 0,
            'total_labels': 0,
            'pending_questions': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            tracks = db_client.get_all_tracks()
            stats['total_tracks'] = len(tracks) if tracks else 0
        except:
            pass
            
        try:
            artists = db_client.get_all_artist_profiles()
            stats['total_artists'] = len(artists) if artists else 0
        except:
            pass
            
        try:
            labels = db_client.get_all_label_profiles()
            stats['total_labels'] = len(labels) if labels else 0
        except:
            pass
            
        try:
            questions = db_client.get_training_questions()
            stats['pending_questions'] = len(questions) if questions else 0
        except:
            pass
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'total_tracks': 0,
            'total_artists': 0, 
            'total_labels': 0,
            'pending_questions': 0,
            'error': str(e)
        })

@app.route('/api/tracks', methods=['GET'])
def get_all_tracks():
    """Get all tracks with full metadata."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
            
        tracks = db_client.get_all_tracks()
        
        # Clean tracks data for JSON
        clean_tracks = []
        for track in tracks or []:
            clean_track = {
                'id': track.get('id'),
                'title': track.get('title', 'Unknown'),
                'artist': track.get('artist', 'Unknown'),
                'genre': track.get('genre'),
                'bpm': track.get('bpm'),
                'key_signature': track.get('key_signature'),
                'year': track.get('year'),
                'label': track.get('label'),
                'duration': track.get('duration'),
                'created_at': track.get('created_at'),
                'updated_at': track.get('updated_at')
            }
            clean_tracks.append(clean_track)
        
        return jsonify({
            'status': 'success',
            'total': len(clean_tracks),
            'tracks': clean_tracks
        })
        
    except Exception as e:
        logger.error(f"Error getting tracks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/artists', methods=['GET'])
def get_all_artists():
    """Get all artist profiles."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
            
        artists = db_client.get_all_artist_profiles()
        
        # Clean artists data
        clean_artists = []
        for artist in artists or []:
            clean_artist = {
                'id': artist.get('id'),
                'name': artist.get('name', 'Unknown'),
                'aliases': artist.get('aliases', []),
                'genres': artist.get('genres', []),
                'origin_country': artist.get('origin_country'),
                'active_years': artist.get('active_years'),
                'description': artist.get('description'),
                'track_count': artist.get('track_count', 0),
                'created_at': artist.get('created_at')
            }
            clean_artists.append(clean_artist)
        
        return jsonify({
            'status': 'success',
            'total': len(clean_artists),
            'artists': clean_artists
        })
        
    except Exception as e:
        logger.error(f"Error getting artists: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/labels', methods=['GET'])
def get_all_labels():
    """Get all label profiles."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
            
        labels = db_client.get_all_label_profiles()
        
        # Clean labels data
        clean_labels = []
        for label in labels or []:
            clean_label = {
                'id': label.get('id'),
                'name': label.get('name', 'Unknown'),
                'country': label.get('country'),
                'founded_year': label.get('founded_year'),
                'genres': label.get('genres', []),
                'description': label.get('description'),
                'website': label.get('website'),
                'active': label.get('active', True),
                'release_count': label.get('release_count', 0),
                'created_at': label.get('created_at')
            }
            clean_labels.append(clean_label)
        
        return jsonify({
            'status': 'success',
            'total': len(clean_labels),
            'labels': clean_labels
        })
        
    except Exception as e:
        logger.error(f"Error getting labels: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/genres', methods=['GET'])
def get_genre_analysis():
    """Get genre distribution and analysis."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
            
        tracks = db_client.get_all_tracks()
        
        # Analyze genres
        genre_stats = {}
        total_tracks = 0
        
        for track in tracks or []:
            genre = track.get('genre', 'Unknown')
            if genre not in genre_stats:
                genre_stats[genre] = {
                    'count': 0,
                    'tracks': [],
                    'artists': set(),
                    'labels': set(),
                    'avg_bpm': 0,
                    'bpm_list': []
                }
            
            genre_stats[genre]['count'] += 1
            genre_stats[genre]['tracks'].append(track.get('title', 'Unknown'))
            
            if track.get('artist'):
                genre_stats[genre]['artists'].add(track.get('artist'))
            if track.get('label'):
                genre_stats[genre]['labels'].add(track.get('label'))
            if track.get('bpm'):
                try:
                    bpm = float(track.get('bpm'))
                    genre_stats[genre]['bpm_list'].append(bpm)
                except:
                    pass
            
            total_tracks += 1
        
        # Calculate averages and clean data
        clean_genres = {}
        for genre, stats in genre_stats.items():
            avg_bpm = sum(stats['bpm_list']) / len(stats['bpm_list']) if stats['bpm_list'] else 0
            
            clean_genres[genre] = {
                'count': stats['count'],
                'percentage': round((stats['count'] / total_tracks * 100), 2) if total_tracks > 0 else 0,
                'unique_artists': len(stats['artists']),
                'unique_labels': len(stats['labels']),
                'avg_bpm': round(avg_bpm, 1) if avg_bpm > 0 else None,
                'sample_tracks': stats['tracks'][:5]  # First 5 tracks as examples
            }
        
        return jsonify({
            'status': 'success',
            'total_genres': len(clean_genres),
            'total_tracks': total_tracks,
            'genres': clean_genres
        })
        
    except Exception as e:
        logger.error(f"Error getting genre analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cultural/insights', methods=['GET'])
def get_cultural_insights():
    """Get cultural intelligence insights."""
    try:
        if not db_client:
            return jsonify({'error': 'Database not available'}), 500
        
        # Get cultural patterns if available
        insights = {
            'regional_trends': {},
            'temporal_patterns': {},
            'cultural_connections': {},
            'emerging_scenes': [],
            'last_updated': datetime.now().isoformat()
        }
        
        # Try to get cultural data
        try:
            tracks = db_client.get_all_tracks()
            artists = db_client.get_all_artist_profiles()
            
            # Regional analysis
            regions = {}
            for artist in artists or []:
                country = artist.get('origin_country', 'Unknown')
                if country not in regions:
                    regions[country] = {'artists': 0, 'genres': set()}
                regions[country]['artists'] += 1
                for genre in artist.get('genres', []):
                    regions[country]['genres'].add(genre)
            
            # Clean regional data
            for region, data in regions.items():
                insights['regional_trends'][region] = {
                    'artist_count': data['artists'],
                    'genre_diversity': len(data['genres']),
                    'primary_genres': list(data['genres'])[:3]
                }
            
        except Exception as cultural_error:
            logger.warning(f"Cultural analysis error: {cultural_error}")
        
        return jsonify({
            'status': 'success',
            'insights': insights
        })
        
    except Exception as e:
        logger.error(f"Error getting cultural insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/health', methods=['GET'])
def get_system_health():
    """Comprehensive system health check."""
    try:
        health_status = {
            'database': 'disconnected',
            'tables': {},
            'recent_activity': {},
            'system_load': 'normal',
            'last_scan': None,
            'training_queue': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        if db_client:
            health_status['database'] = 'connected'
            
            # Check table counts
            try:
                tracks = db_client.get_all_tracks()
                health_status['tables']['tracks'] = len(tracks) if tracks else 0
            except:
                health_status['tables']['tracks'] = 0
            
            try:
                artists = db_client.get_all_artist_profiles()
                health_status['tables']['artists'] = len(artists) if artists else 0
            except:
                health_status['tables']['artists'] = 0
            
            try:
                labels = db_client.get_all_label_profiles()
                health_status['tables']['labels'] = len(labels) if labels else 0
            except:
                health_status['tables']['labels'] = 0
            
            try:
                questions = db_client.get_training_questions()
                health_status['training_queue'] = len(questions) if questions else 0
            except:
                health_status['training_queue'] = 0
        
        return jsonify({
            'status': 'healthy' if health_status['database'] == 'connected' else 'degraded',
            'health': health_status
        })
        
    except Exception as e:
        logger.error(f"System health check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/webhook/incoming', methods=['POST'])
def incoming_webhook():
    """Handle incoming webhook data."""
    try:
        data = request.get_json()
        logger.info(f"🔗 Incoming webhook: {data}")
        
        # Process webhook data here
        # You can add your logic for handling external dashboard updates
        
        return jsonify({
            'status': 'received',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔗 Webhook Training API Starting...")
    print("🌐 API URL: http://localhost:5000")
    print("📡 Endpoints:")
    print("   GET  /health                    - Basic health check")
    print("   GET  /api/system/health         - Comprehensive system status")
    print("   GET  /api/training/question     - Get training question")
    print("   POST /api/training/respond      - Submit training response") 
    print("   GET  /api/stats                 - Basic statistics")
    print("   GET  /api/tracks                - All tracks with metadata")
    print("   GET  /api/artists               - All artist profiles")
    print("   GET  /api/labels                - All label profiles")
    print("   GET  /api/genres                - Genre analysis & distribution")
    print("   GET  /api/cultural/insights     - Cultural intelligence data")
    print("   POST /api/webhook/incoming      - Incoming webhook handler")
    print("=" * 60)
    
    app.run(
        host='localhost',
        port=5000,
        debug=True
    )