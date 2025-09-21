"""
Flask web application for the Electronic Music Taxonomy Database.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy.orm import Session
from src.database import get_db, init_database
from src.models import (
    Genre, Characteristic, AudioFeature, Timeline, GenreKeyword,
    RecordLabel, LabelAssociation, MixingCompatibility
)
from src.analysis.audio_analyzer import GenreAnalyzer
from src.data.scraper import WikipediaGenreScraper
from src.data.enhanced_loader_simple import EnhancedDataLoader
import os
from typing import List, Dict, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize components
genre_analyzer = GenreAnalyzer()

@app.route('/')
def index():
    """Home page with genre overview."""
    db: Session = next(get_db())
    try:
        # Get genre statistics
        total_genres = db.query(Genre).count()
        recent_genres = db.query(Genre).order_by(Genre.created_at.desc()).limit(5).all()
        
        return render_template('index.html', 
                             total_genres=total_genres,
                             recent_genres=recent_genres)
    finally:
        db.close()

@app.route('/genres')
def list_genres():
    """List all genres with pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 20
    
    db: Session = next(get_db())
    try:
        query = db.query(Genre)
        
        if search:
            query = query.filter(Genre.name.ilike(f'%{search}%'))
        
        # Simple pagination (would use proper pagination in production)
        offset = (page - 1) * per_page
        genres = query.offset(offset).limit(per_page).all()
        
        return render_template('genres.html', 
                             genres=genres,
                             search=search,
                             page=page)
    finally:
        db.close()

@app.route('/genre/<int:genre_id>')
def genre_detail(genre_id: int):
    """Detailed view of a specific genre."""
    db: Session = next(get_db())
    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            return "Genre not found", 404
        
        # Get related data
        characteristics = db.query(Characteristic).filter(Characteristic.genre_id == genre_id).all()
        audio_features = db.query(AudioFeature).filter(AudioFeature.genre_id == genre_id).first()
        timeline_events = db.query(Timeline).filter(Timeline.genre_id == genre_id).order_by(Timeline.year).all()
        keywords = db.query(GenreKeyword).filter(GenreKeyword.genre_id == genre_id).all()
        
        # Get label associations
        label_associations = db.query(LabelAssociation).filter(
            LabelAssociation.genre_id == genre_id
        ).join(RecordLabel).all()
        
        # Get mixing compatibility (top 5 most compatible)
        compatible_genres = db.query(MixingCompatibility).filter(
            MixingCompatibility.genre1_id == genre_id
        ).order_by(MixingCompatibility.compatibility_score.desc()).limit(5).all()
        
        return render_template('genre_detail.html',
                             genre=genre,
                             characteristics=characteristics,
                             audio_features=audio_features,
                             timeline_events=timeline_events,
                             keywords=keywords,
                             label_associations=label_associations,
                             compatible_genres=compatible_genres)
    finally:
        db.close()

@app.route('/search')
def search():
    """Search functionality."""
    query = request.args.get('q', '', type=str)
    category = request.args.get('category', 'all', type=str)
    
    if not query:
        return render_template('search.html', results=[], query=query)
    
    db: Session = next(get_db())
    try:
        results = []
        
        if category in ['all', 'genres']:
            # Search genres
            genre_results = db.query(Genre).filter(
                Genre.name.ilike(f'%{query}%') | 
                Genre.description.ilike(f'%{query}%')
            ).limit(20).all()
            
            results.extend([{
                'type': 'genre',
                'id': g.id,
                'name': g.name,
                'description': g.description[:200] + '...' if len(g.description) > 200 else g.description,
                'url': url_for('genre_detail', genre_id=g.id)
            } for g in genre_results])
        
        return render_template('search.html', 
                             results=results,
                             query=query,
                             category=category)
    finally:
        db.close()

@app.route('/timeline')
def timeline():
    """Historical timeline of electronic music."""
    db: Session = next(get_db())
    try:
        # Get timeline events with genre information
        events = db.query(Timeline).join(Genre).order_by(Timeline.year).all()
        
        # Group by decade for visualization
        decades = {}
        for event in events:
            decade = (event.year // 10) * 10
            if decade not in decades:
                decades[decade] = []
            decades[decade].append(event)
        
        return render_template('timeline.html', decades=decades)
    finally:
        db.close()

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_audio():
    """Audio analysis upload and result page."""
    if request.method == 'GET':
        return render_template('analyze.html')
    
    # Handle file upload
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save uploaded file temporarily
    upload_path = os.path.join('temp', file.filename)
    os.makedirs('temp', exist_ok=True)
    file.save(upload_path)
    
    try:
        # Analyze the audio file
        result = genre_analyzer.analyze_audio_file(upload_path)
        
        # Clean up temporary file
        os.remove(upload_path)
        
        return jsonify(result)
    
    except Exception as e:
        # Clean up temporary file
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500

# API Routes
@app.route('/api/genres')
def api_genres():
    """API endpoint for genres list."""
    db: Session = next(get_db())
    try:
        genres = db.query(Genre).all()
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'description': g.description,
            'origin_year': g.origin_year,
            'origin_location': g.origin_location,
            'wikipedia_url': g.wikipedia_url
        } for g in genres])
    finally:
        db.close()

@app.route('/api/genres/<int:genre_id>')
def api_genre_detail(genre_id: int):
    """API endpoint for genre details."""
    db: Session = next(get_db())
    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            return jsonify({'error': 'Genre not found'}), 404
        
        characteristics = db.query(Characteristic).filter(Characteristic.genre_id == genre_id).all()
        audio_features = db.query(AudioFeature).filter(AudioFeature.genre_id == genre_id).first()
        
        result = {
            'id': genre.id,
            'name': genre.name,
            'description': genre.description,
            'origin_year': genre.origin_year,
            'origin_location': genre.origin_location,
            'wikipedia_url': genre.wikipedia_url,
            'characteristics': [{
                'type': c.characteristic_type,
                'name': c.name,
                'description': c.description,
                'value': c.value
            } for c in characteristics]
        }
        
        if audio_features:
            result['audio_features'] = {
                'bpm_min': audio_features.bpm_min,
                'bpm_max': audio_features.bpm_max,
                'bpm_typical': audio_features.bpm_typical,
                'time_signature': audio_features.time_signature,
                'typical_instruments': audio_features.typical_instruments
            }
        
        return jsonify(result)
    finally:
        db.close()

@app.route('/api/search')
def api_search():
    """API endpoint for search."""
    query = request.args.get('q', '', type=str)
    if not query:
        return jsonify([])
    
    db: Session = next(get_db())
    try:
        genres = db.query(Genre).filter(
            Genre.name.ilike(f'%{query}%') | 
            Genre.description.ilike(f'%{query}%')
        ).limit(10).all()
        
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'description': g.description[:100] + '...' if len(g.description) > 100 else g.description
        } for g in genres])
    finally:
        db.close()

# Admin routes (for data management)
@app.route('/admin/load-data')
def admin_load_data():
    """Load data from Wikipedia (admin function)."""
    try:
        scraper = WikipediaGenreScraper()
        genres_data = scraper.scrape_genre_list()
        
        db: Session = next(get_db())
        try:
            loaded_count = 0
            for genre_data in genres_data:
                # Check if genre already exists
                existing = db.query(Genre).filter(Genre.name == genre_data.name).first()
                if not existing:
                    genre = Genre(
                        name=genre_data.name,
                        slug=genre_data.name.lower().replace(' ', '-'),
                        description=genre_data.description,
                        wikipedia_url=genre_data.wikipedia_url,
                        origin_year=genre_data.origin_year,
                        origin_location=genre_data.origin_location
                    )
                    db.add(genre)
                    loaded_count += 1
            
            db.commit()
            return jsonify({
                'message': f'Successfully loaded {loaded_count} new genres',
                'total_scraped': len(genres_data)
            })
        finally:
            db.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/load-enhanced-data')
def admin_load_enhanced_data():
    """Load enhanced taxonomy data (admin function)."""
    try:
        loader = EnhancedDataLoader()
        loader.load_all_enhanced_data()
        
        return jsonify({
            'message': 'Enhanced taxonomy data loaded successfully',
            'features': [
                'Hierarchical genres', 'BPM ranges', 'Energy levels',
                'Keywords and aliases', 'Mixing compatibility', 
                'Label associations', 'Related genres'
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mixing-compatibility')
def mixing_compatibility():
    """Mixing compatibility analysis page."""
    db: Session = next(get_db())
    try:
        # Get all genres with BPM info for compatibility matrix
        genres = db.query(Genre).filter(Genre.bpm_typical.isnot(None)).all()
        
        # Get top compatibility pairs
        top_compatibilities = db.query(MixingCompatibility).join(
            Genre, MixingCompatibility.genre1_id == Genre.id
        ).order_by(MixingCompatibility.compatibility_score.desc()).limit(20).all()
        
        return render_template('mixing_compatibility.html',
                             genres=genres,
                             top_compatibilities=top_compatibilities)
    finally:
        db.close()

@app.route('/labels')
def record_labels():
    """Record labels page."""
    db: Session = next(get_db())
    try:
        labels = db.query(RecordLabel).all()
        return render_template('labels.html', labels=labels)
    finally:
        db.close()

@app.route('/api/mixing-compatibility/<int:genre_id>')
def api_mixing_compatibility(genre_id: int):
    """API endpoint for mixing compatibility."""
    db: Session = next(get_db())
    try:
        compatible = db.query(MixingCompatibility).filter(
            MixingCompatibility.genre1_id == genre_id
        ).order_by(MixingCompatibility.compatibility_score.desc()).limit(10).all()
        
        return jsonify([{
            'genre_id': c.genre2_id,
            'genre_name': c.genre2.name,
            'compatibility_score': c.compatibility_score,
            'bpm_compatibility': c.bpm_compatibility,
            'energy_compatibility': c.energy_compatibility
        } for c in compatible])
    finally:
        db.close()

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)