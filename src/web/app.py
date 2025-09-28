"""
Flask web application for the Electronic Music Taxonomy Database.
"""
import os
import sys
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database import SessionLocal, init_database
from src.models import Genre, Characteristic, AudioFeature, Timeline, GenreKeyword

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database on startup
try:
    init_database()
    print("Database initialized successfully!")
except Exception as e:
    print(f"Database initialization error: {e}")

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let routes handle it

@app.route('/')
def index():
    """Homepage with overview and recent genres."""
    db = get_db()
    try:
        # Get total genre count
        total_genres = db.query(Genre).count()
        
        # Get recent genres (or just first 6 if no recent data)
        recent_genres = db.query(Genre).order_by(desc(Genre.created_at)).limit(6).all()
        
        return render_template('index.html', 
                             total_genres=total_genres,
                             recent_genres=recent_genres)
    except Exception as e:
        flash(f"Error loading homepage: {e}", 'error')
        return render_template('index.html', total_genres=0, recent_genres=[])
    finally:
        db.close()

@app.route('/genres')
def list_genres():
    """List all genres with pagination and search."""
    db = get_db()
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        per_page = 12
        
        query = db.query(Genre)
        
        if search:
            query = query.filter(Genre.name.ilike(f'%{search}%'))
        
        genres = query.order_by(Genre.name).offset((page - 1) * per_page).limit(per_page).all()
        total = query.count()
        
        # Calculate pagination info
        has_prev = page > 1
        has_next = (page * per_page) < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        return render_template('genres.html',
                             genres=genres,
                             page=page,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_num=prev_num,
                             next_num=next_num,
                             search=search,
                             total=total)
    except Exception as e:
        flash(f"Error loading genres: {e}", 'error')
        return render_template('genres.html', genres=[], page=1, total=0)
    finally:
        db.close()

@app.route('/genre/<int:genre_id>')
def genre_detail(genre_id):
    """Detailed view of a specific genre."""
    db = get_db()
    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            flash('Genre not found', 'error')
            return redirect(url_for('list_genres'))
        
        # Get related data
        characteristics = db.query(Characteristic).filter(Characteristic.genre_id == genre_id).all()
        audio_features = db.query(AudioFeature).filter(AudioFeature.genre_id == genre_id).first()
        timeline_events = db.query(Timeline).filter(Timeline.genre_id == genre_id).order_by(Timeline.year).all()
        
        return render_template('genre_detail.html',
                             genre=genre,
                             characteristics=characteristics,
                             audio_features=audio_features,
                             timeline_events=timeline_events)
    except Exception as e:
        flash(f"Error loading genre details: {e}", 'error')
        return redirect(url_for('list_genres'))
    finally:
        db.close()

@app.route('/search')
def search():
    """Advanced search page."""
    db = get_db()
    try:
        query_text = request.args.get('q', '')
        bpm_min = request.args.get('bpm_min', type=int)
        bpm_max = request.args.get('bpm_max', type=int)
        year_min = request.args.get('year_min', type=int)
        year_max = request.args.get('year_max', type=int)
        
        results = []
        
        if query_text or bpm_min or bpm_max or year_min or year_max:
            query = db.query(Genre)
            
            if query_text:
                query = query.filter(
                    Genre.name.ilike(f'%{query_text}%') |
                    Genre.description.ilike(f'%{query_text}%')
                )
            
            if bpm_min:
                query = query.filter(Genre.bpm_min >= bpm_min)
            
            if bpm_max:
                query = query.filter(Genre.bpm_max <= bpm_max)
            
            if year_min:
                query = query.filter(Genre.origin_year >= year_min)
            
            if year_max:
                query = query.filter(Genre.origin_year <= year_max)
            
            results = query.order_by(Genre.name).limit(50).all()
        
        return render_template('search.html',
                             results=results,
                             query_text=query_text,
                             bpm_min=bpm_min,
                             bpm_max=bpm_max,
                             year_min=year_min,
                             year_max=year_max)
    except Exception as e:
        flash(f"Search error: {e}", 'error')
        return render_template('search.html', results=[])
    finally:
        db.close()

@app.route('/timeline')
def timeline():
    """Timeline view of genre development."""
    db = get_db()
    try:
        # Get genres with years for timeline
        genres_with_years = db.query(Genre).filter(Genre.origin_year.isnot(None)).order_by(Genre.origin_year).all()
        
        # Group by decade
        timeline_data = {}
        for genre in genres_with_years:
            decade = (genre.origin_year // 10) * 10
            if decade not in timeline_data:
                timeline_data[decade] = []
            timeline_data[decade].append(genre)
        
        return render_template('timeline.html', timeline_data=timeline_data)
    except Exception as e:
        flash(f"Error loading timeline: {e}", 'error')
        return render_template('timeline.html', timeline_data={})
    finally:
        db.close()

@app.route('/analyze_audio')
def analyze_audio():
    """Audio analysis upload page."""
    return render_template('analyze_audio.html')

@app.route('/api/genres')
def api_genres():
    """API endpoint to get all genres."""
    db = get_db()
    try:
        genres = db.query(Genre).all()
        return jsonify([{
            'id': genre.id,
            'name': genre.name,
            'slug': genre.slug,
            'description': genre.description,
            'origin_year': genre.origin_year,
            'origin_location': genre.origin_location,
            'bpm_min': genre.bpm_min,
            'bpm_max': genre.bpm_max,
            'bpm_typical': genre.bpm_typical,
            'energy_level': genre.energy_level
        } for genre in genres])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/genre/<int:genre_id>')
def api_genre_detail(genre_id):
    """API endpoint to get specific genre details."""
    db = get_db()
    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            return jsonify({'error': 'Genre not found'}), 404
        
        return jsonify({
            'id': genre.id,
            'name': genre.name,
            'slug': genre.slug,
            'description': genre.description,
            'wikipedia_url': genre.wikipedia_url,
            'origin_year': genre.origin_year,
            'origin_location': genre.origin_location,
            'bpm_min': genre.bpm_min,
            'bpm_max': genre.bpm_max,
            'bpm_typical': genre.bpm_typical,
            'energy_level': genre.energy_level,
            'created_at': genre.created_at.isoformat() if genre.created_at else None,
            'updated_at': genre.updated_at.isoformat() if genre.updated_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)