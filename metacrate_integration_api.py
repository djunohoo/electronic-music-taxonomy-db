#!/usr/bin/env python3
"""
MetaCrate Integration API - Perfect Track Intelligence
======================================================

Provides instant track intelligence for MetaCrate with guaranteed response format:
- Artist, Track Name, Remix Info (defaults to "Original Mix"), Genre, Subgenre
- Fast hash-based lookups for previously scanned tracks
- Consistent API response format for MetaCrate integration

Usage:
POST /api/track/analyze
{
    "file_path": "/path/to/track.mp3"
    "file_hash": "optional_hash"  // If provided, skips hash calculation
}

Response:
{
    "status": "success",
    "track": {
        "artist": "Deadmau5",
        "track_name": "Strobe", 
        "remix_info": "Original Mix",
        "genre": "Progressive House",
        "subgenre": "Melodic Progressive",
        "confidence": 0.92
    },
    "metadata": {
        "file_hash": "abc123...",
        "is_duplicate": false,
        "source": "database_lookup"
    }
}
"""

import os
import time
import hashlib
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from cultural_database_client import CulturalDatabaseClient

app = Flask(__name__)
CORS(app)

# Initialize database client
db = CulturalDatabaseClient()

# API Statistics
stats = {
    'start_time': time.time(),
    'total_requests': 0,
    'cache_hits': 0,
    'new_analyses': 0,
    'errors': 0
}

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash for audio file."""
    try:
        if not os.path.exists(file_path):
            return None
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def check_duplicate_status(file_hash, file_path):
    """Check if file is a duplicate and determine if it's the best version for MetaCrate."""
    try:
        # Get all tracks with same hash (duplicates)
        tracks = db.get_all_tracks()
        duplicate_tracks = [track for track in tracks if track.get('file_hash') == file_hash]
        
        if len(duplicate_tracks) <= 1:
            # Not a duplicate
            return {
                'is_duplicate': False,
                'is_best_version': True,
                'duplicate_count': 1,
                'primary_file': file_path,
                'reason': 'unique_file'
            }
        
        # Multiple files with same hash = duplicates
        # Determine best version based on criteria:
        # 1. Shortest path (likely organized better)
        # 2. Largest file size (likely better quality)
        # 3. Most recent modification date
        
        best_track = None
        best_score = -1
        
        for track in duplicate_tracks:
            score = 0
            track_path = track.get('file_path', '')
            
            # Prefer shorter paths (better organization)
            path_score = max(0, 200 - len(track_path))
            
            # Prefer larger files (better quality)
            size_score = track.get('file_size', 0) / 1000000  # MB
            
            # Prefer files in organized folders (no temp/trash indicators)
            if any(bad in track_path.lower() for bad in ['temp', 'tmp', 'trash', 'recycle', 'duplicate']):
                organization_score = -100
            else:
                organization_score = 50
            
            total_score = path_score + size_score + organization_score
            
            if total_score > best_score:
                best_score = total_score
                best_track = track
        
        # Check if current file is the best version
        is_best = (best_track and best_track.get('file_path') == file_path)
        
        return {
            'is_duplicate': True,
            'is_best_version': is_best,
            'duplicate_count': len(duplicate_tracks),
            'primary_file': best_track.get('file_path') if best_track else file_path,
            'reason': 'best_quality_and_location' if is_best else 'duplicate_of_better_version'
        }
        
    except Exception as e:
        # On error, assume not duplicate to be safe
        return {
            'is_duplicate': False,
            'is_best_version': True,
            'duplicate_count': 1,
            'primary_file': file_path,
            'reason': f'error_checking_duplicates: {str(e)}'
        }

def extract_basic_metadata(file_path):
    """Extract basic metadata using mutagen or similar."""
    try:
        # Try using mutagen if available
        try:
            from mutagen import File
            audio_file = File(file_path)
            if audio_file is None:
                return {}
            
            metadata = {}
            
            # Common fields
            if 'TIT2' in audio_file:  # Title
                metadata['title'] = str(audio_file['TIT2'][0])
            elif 'TITLE' in audio_file:
                metadata['title'] = str(audio_file['TITLE'][0])
            
            if 'TPE1' in audio_file:  # Artist
                metadata['artist'] = str(audio_file['TPE1'][0])
            elif 'ARTIST' in audio_file:
                metadata['artist'] = str(audio_file['ARTIST'][0])
            
            if 'TALB' in audio_file:  # Album
                metadata['album'] = str(audio_file['TALB'][0])
            elif 'ALBUM' in audio_file:
                metadata['album'] = str(audio_file['ALBUM'][0])
            
            if 'TCON' in audio_file:  # Genre
                metadata['genre'] = str(audio_file['TCON'][0])
            elif 'GENRE' in audio_file:
                metadata['genre'] = str(audio_file['GENRE'][0])
            
            if 'TPE2' in audio_file:  # Album Artist / Label
                metadata['label'] = str(audio_file['TPE2'][0])
            elif 'ALBUMARTIST' in audio_file:
                metadata['label'] = str(audio_file['ALBUMARTIST'][0])
            
            return metadata
            
        except ImportError:
            # Fallback - no metadata extraction
            return {}
            
    except Exception:
        return {}

def parse_filename_for_track_info(filename):
    """Parse filename for artist, track, and remix info."""
    import re
    
    # Remove file extension
    name = Path(filename).stem
    
    # Common patterns for artist - track (remix)
    patterns = [
        r'^(.+?)\s*[-–—]\s*(.+?)\s*\(([^)]+)\)$',  # Artist - Track (Remix)
        r'^(.+?)\s*[-–—]\s*(.+?)$',                   # Artist - Track
        r'^(.+?)\s+(.+?)\s*\(([^)]+)\)$',            # Artist Track (Remix)
    ]
    
    result = {
        'artist': 'Unknown Artist',
        'track_name': name,
        'remix_info': 'Original Mix'
    }
    
    for pattern in patterns:
        match = re.match(pattern, name, re.IGNORECASE)
        if match:
            if len(match.groups()) >= 2:
                result['artist'] = match.group(1).strip()
                result['track_name'] = match.group(2).strip()
                
            if len(match.groups()) >= 3:
                remix = match.group(3).strip()
                # Clean up remix info
                if remix and remix.lower() not in ['original', 'original mix']:
                    result['remix_info'] = remix
                else:
                    result['remix_info'] = 'Original Mix'
            break
    
    return result

def analyze_track_intelligence(file_path, file_hash):
    """Analyze track and return complete intelligence with duplicate handling for MetaCrate."""
    try:
        # Check if track exists in database
        existing_track = None
        if file_hash:
            tracks = db.get_all_tracks()
            for track in tracks:
                if track.get('file_hash') == file_hash:
                    existing_track = track
                    break
        
        if existing_track:
            # Check if this is a duplicate and if it's the best version
            duplicate_info = check_duplicate_status(file_hash, file_path)
            
            if duplicate_info['is_duplicate'] and not duplicate_info['is_best_version']:
                # This is a duplicate, tell MetaCrate to skip it
                return {
                    'status': 'duplicate_skip',
                    'message': 'This is a duplicate track. MetaCrate should skip processing.',
                    'duplicate_info': {
                        'is_duplicate': True,
                        'is_best_version': False,
                        'primary_file': duplicate_info['primary_file'],
                        'duplicate_count': duplicate_info['duplicate_count'],
                        'reason': duplicate_info['reason']
                    },
                    'track': None  # No track data for duplicates to skip
                }
            
            # This is either not a duplicate OR it's the best version of duplicates
            # Get classification for existing track
            classifications = db.get_classifications_by_track_id(existing_track['id'])
            if classifications:
                classification = classifications[0]  # Use first classification
                
                return {
                    'status': 'success',
                    'track': {
                        'artist': classification.get('artist', 'Unknown Artist'),
                        'track_name': classification.get('track_name', Path(file_path).stem),
                        'remix_info': classification.get('remix_info') or 'Original Mix',
                        'genre': classification.get('genre', 'Electronic'),
                        'subgenre': classification.get('subgenre'),
                        'confidence': float(classification.get('overall_confidence', 0.5))
                    },
                    'duplicate_info': {
                        'is_duplicate': duplicate_info['is_duplicate'],
                        'is_best_version': duplicate_info['is_best_version'],
                        'duplicate_count': duplicate_info['duplicate_count']
                    },
                    'metadata': {
                        'file_hash': file_hash,
                        'source': 'database_lookup',
                        'track_id': existing_track['id']
                    }
                }
        
        # New track - perform analysis
        # First check if this might be a duplicate of an unknown track
        duplicate_info = check_duplicate_status(file_hash, file_path) if file_hash else {
            'is_duplicate': False, 'is_best_version': True, 'duplicate_count': 1, 'primary_file': file_path, 'reason': 'no_hash'
        }
        
        if duplicate_info['is_duplicate'] and not duplicate_info['is_best_version']:
            # This is a duplicate, tell MetaCrate to skip it
            return {
                'status': 'duplicate_skip',
                'message': 'This is a duplicate track. MetaCrate should skip processing.',
                'duplicate_info': duplicate_info,
                'track': None  # No track data for duplicates to skip
            }
        
        # Continue with analysis for unique files or best versions
        metadata = extract_basic_metadata(file_path)
        filename_info = parse_filename_for_track_info(Path(file_path).name)
        
        # Determine best values
        artist = (metadata.get('artist') or 
                 filename_info.get('artist') or 
                 'Unknown Artist')
        
        track_name = (metadata.get('title') or 
                     filename_info.get('track_name') or 
                     Path(file_path).stem)
        
        remix_info = filename_info.get('remix_info', 'Original Mix')
        
        # Determine genre using patterns
        genre = 'Electronic'
        subgenre = None
        confidence = 0.3
        
        # Check folder patterns
        folder_path = str(Path(file_path).parent).lower()
        patterns = db.get_all_patterns()
        
        for pattern in patterns:
            pattern_value = pattern.get('pattern_value', '').lower()
            pattern_type = pattern.get('pattern_type', '')
            
            if pattern_type == 'folder' and pattern_value in folder_path:
                genre = pattern.get('genre', genre)
                subgenre = pattern.get('subgenre', subgenre)
                confidence = float(pattern.get('confidence', confidence))
                break
            elif pattern_type == 'filename' and pattern_value in Path(file_path).name.lower():
                genre = pattern.get('genre', genre)
                subgenre = pattern.get('subgenre', subgenre)
                confidence = float(pattern.get('confidence', confidence))
                break
            elif pattern_type == 'metadata' and metadata.get('genre'):
                if pattern_value in metadata.get('genre', '').lower():
                    genre = pattern.get('genre', genre)
                    subgenre = pattern.get('subgenre', subgenre)
                    confidence = float(pattern.get('confidence', confidence))
                    break
        
        # Use metadata genre if no pattern match and available
        if confidence < 0.5 and metadata.get('genre'):
            genre = metadata.get('genre')
            confidence = 0.7
        
        return {
            'status': 'success',
            'track': {
                'artist': artist,
                'track_name': track_name,
                'remix_info': remix_info,
                'genre': genre,
                'subgenre': subgenre,
                'confidence': confidence
            },
            'duplicate_info': duplicate_info,
            'metadata': {
                'file_hash': file_hash,
                'source': 'live_analysis',
                'raw_metadata': metadata
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'track': {
                'artist': 'Unknown Artist',
                'track_name': Path(file_path).stem if file_path else 'Unknown Track',
                'remix_info': 'Original Mix',
                'genre': 'Electronic',
                'subgenre': None,
                'confidence': 0.0
            },
            'metadata': {
                'file_hash': file_hash,
                'is_duplicate': False,
                'source': 'error_fallback'
            }
        }

# =====================================================
# API ENDPOINTS
# =====================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check."""
    uptime = time.time() - stats['start_time']
    
    try:
        # Test database connection
        tracks = db.get_all_tracks()
        db_status = 'connected'
        track_count = len(tracks)
    except Exception as e:
        db_status = f'error: {str(e)}'
        track_count = 0
    
    return jsonify({
        'status': 'healthy',
        'service': 'MetaCrate Integration API',
        'version': '3.2',
        'database': db_status,
        'statistics': {
            'uptime_seconds': int(uptime),
            'total_requests': stats['total_requests'],
            'cache_hits': stats['cache_hits'],
            'new_analyses': stats['new_analyses'],
            'errors': stats['errors'],
            'tracks_in_database': track_count
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/track/analyze', methods=['POST'])
def analyze_track():
    """
    Main endpoint for MetaCrate track analysis with duplicate handling.
    
    MetaCrate Integration Logic:
    1. If file is duplicate and NOT best version -> status: "duplicate_skip" (MetaCrate skips)
    2. If file is unique OR best version of duplicates -> status: "success" (MetaCrate processes)
    
    Response for duplicates to skip:
    {
        "status": "duplicate_skip",
        "message": "This is a duplicate track. MetaCrate should skip processing.",
        "duplicate_info": {
            "is_duplicate": true,
            "is_best_version": false,
            "primary_file": "/path/to/best/version.mp3",
            "duplicate_count": 3,
            "reason": "duplicate_of_better_version"
        },
        "track": null
    }
    
    Response for files to process:
    {
        "status": "success",
        "track": {
            "artist": "Deadmau5",
            "track_name": "Strobe",
            "remix_info": "Original Mix",
            "genre": "Progressive House", 
            "subgenre": "Melodic Progressive"
        },
        "duplicate_info": {
            "is_duplicate": false,  // or true if this is the best version
            "is_best_version": true,
            "duplicate_count": 1
        }
    }
    """
    stats['total_requests'] += 1
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            stats['errors'] += 1
            return jsonify({
                'status': 'error',
                'error': 'JSON body required'
            }), 400
        
        file_path = data.get('file_path')
        file_hash = data.get('file_hash')
        
        if not file_path:
            stats['errors'] += 1
            return jsonify({
                'status': 'error',
                'error': 'file_path required'
            }), 400
        
        # Calculate hash if not provided
        if not file_hash:
            file_hash = calculate_file_hash(file_path)
            if not file_hash:
                stats['errors'] += 1
                return jsonify({
                    'status': 'error',
                    'error': 'Could not calculate file hash',
                    'track': {
                        'artist': 'Unknown Artist',
                        'track_name': Path(file_path).stem,
                        'remix_info': 'Original Mix',
                        'genre': 'Electronic',
                        'subgenre': None,
                        'confidence': 0.0
                    }
                }), 400
        
        # Analyze the track
        result = analyze_track_intelligence(file_path, file_hash)
        
        # Update statistics
        if result['metadata']['source'] == 'database_lookup':
            stats['cache_hits'] += 1
        else:
            stats['new_analyses'] += 1
        
        # Add response timing
        result['api_info'] = {
            'response_time_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        stats['errors'] += 1
        return jsonify({
            'status': 'error',
            'error': str(e),
            'track': {
                'artist': 'Unknown Artist',
                'track_name': 'Error',
                'remix_info': 'Original Mix',
                'genre': 'Electronic',
                'subgenre': None,
                'confidence': 0.0
            }
        }), 500

@app.route('/api/track/batch', methods=['POST'])
def batch_analyze():
    """Batch analysis for multiple tracks."""
    stats['total_requests'] += 1
    
    try:
        data = request.get_json()
        file_paths = data.get('file_paths', [])
        
        if not file_paths:
            return jsonify({'error': 'file_paths array required'}), 400
        
        results = []
        for file_path in file_paths[:50]:  # Limit batch size
            file_hash = calculate_file_hash(file_path)
            result = analyze_track_intelligence(file_path, file_hash)
            results.append({
                'file_path': file_path,
                'result': result
            })
        
        return jsonify({
            'status': 'success',
            'batch_size': len(results),
            'results': results
        })
        
    except Exception as e:
        stats['errors'] += 1
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get API usage statistics."""
    uptime = time.time() - stats['start_time']
    
    return jsonify({
        'api_statistics': stats,
        'uptime_seconds': int(uptime),
        'requests_per_minute': stats['total_requests'] / (uptime / 60) if uptime > 0 else 0,
        'cache_hit_rate': stats['cache_hits'] / stats['total_requests'] if stats['total_requests'] > 0 else 0,
        'error_rate': stats['errors'] / stats['total_requests'] if stats['total_requests'] > 0 else 0
    })

if __name__ == '__main__':
    print("🎵 MetaCrate Integration API - Cultural Intelligence System")
    print("=" * 65)
    print("Starting track intelligence API...")
    print(f"Main endpoint: POST http://172.22.17.37:5000/api/track/analyze")
    print(f"Health check:  GET  http://172.22.17.37:5000/api/health")
    print(f"Batch process: POST http://172.22.17.37:5000/api/track/batch")
    print()
    print("Perfect for MetaCrate integration!")
    print("Returns: artist, track_name, remix_info, genre, subgenre")
    print("=" * 65)
    
    app.run(host='172.22.17.37', port=5000, debug=False)