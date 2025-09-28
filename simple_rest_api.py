#!/usr/bin/env python3
"""
Simple Cultural Intelligence API using Supabase REST
Minimal working version for immediate MetaCrate integration
"""

from flask import Flask, request, jsonify
import hashlib
import os
import time
from pathlib import Path
from supabase_client import create_supabase_client

app = Flask(__name__)

# Initialize Supabase client
supabase_client = create_supabase_client()

# Statistics
start_time = time.time()
request_count = 0

def calculate_file_hash(file_path):
    """Calculate FILE_HASH for audio file"""
    try:
        if not os.path.exists(file_path):
            return None
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    except Exception as e:
        print(f"Hash calculation error: {e}")
        return None

def classify_file(file_path):
    """Basic file classification using patterns and filename analysis"""
    
    file_path = Path(file_path)
    
    # Get patterns from database
    folder_patterns = supabase_client.get_patterns(pattern_type="folder")
    filename_patterns = supabase_client.get_patterns(pattern_type="filename")
    
    classification = {
        "genre": None,
        "subgenre": None,
        "confidence": 0.0,
        "classification_source": "pattern_matching"
    }
    
    # Check folder patterns
    for pattern in folder_patterns:
        if pattern['pattern_value'].lower() in str(file_path.parent).lower():
            classification.update({
                "genre": pattern['genre'],
                "subgenre": pattern['subgenre'],
                "confidence": float(pattern['confidence']),
                "classification_source": f"folder_pattern: {pattern['pattern_value']}"
            })
            break
    
    # Check filename patterns
    if classification["confidence"] < 0.8:  # Only override if low confidence
        for pattern in filename_patterns:
            if pattern['pattern_value'].lower() in file_path.name.lower():
                classification.update({
                    "genre": pattern['genre'],
                    "subgenre": pattern['subgenre'], 
                    "confidence": float(pattern['confidence']),
                    "classification_source": f"filename_pattern: {pattern['pattern_value']}"
                })
                break
    
    return classification

@app.route('/health')
def health():
    """Health check endpoint"""
    global request_count
    request_count += 1
    
    uptime = time.time() - start_time
    
    try:
        stats = supabase_client.get_statistics()
        database_status = "connected"
    except Exception as e:
        stats = {"error": str(e)}
        database_status = "error"
    
    return jsonify({
        "status": "healthy",
        "service": "Cultural Intelligence API (Supabase REST)",
        "version": "3.2-rest",
        "database": database_status,
        "database_stats": stats,
        "uptime_seconds": int(uptime),
        "total_requests": request_count,
        "requests_per_minute": request_count / (uptime / 60) if uptime > 0 else 0
    })

@app.route('/analyze', methods=['POST'])
def analyze_file():
    """Analyze a file and return intelligence"""
    global request_count
    request_count += 1
    
    data = request.get_json()
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({"error": "file_path required"}), 400
    
    try:
        # Calculate hash
        file_hash = calculate_file_hash(file_path)
        if not file_hash:
            return jsonify({"error": "Could not calculate file hash"}), 400
        
        # Check if we already have this file
        existing_track = supabase_client.get_track_by_hash(file_hash)
        
        if existing_track:
            # Get existing classification
            classification = supabase_client.get_classification(existing_track['id'])
            
            return jsonify({
                "file_hash": file_hash,
                "file_path": file_path,
                "status": "known",
                "track_id": existing_track['id'],
                "classification": classification,
                "source": "database_lookup"
            })
        
        else:
            # New file - create track record and classify
            file_stats = os.stat(file_path)
            
            track_data = {
                "file_path": file_path,
                "file_hash": file_hash,
                "file_size": file_stats.st_size,
                "file_modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stats.st_mtime)),
                "filename": Path(file_path).name,
                "folder_path": str(Path(file_path).parent),
                "file_extension": Path(file_path).suffix.lower()
            }
            
            # Insert track
            track = supabase_client.insert_track(track_data)
            
            # Classify
            classification_result = classify_file(file_path)
            
            if classification_result["confidence"] > 0:
                classification_data = {
                    "track_id": track['id'],
                    "genre": classification_result.get("genre"),
                    "subgenre": classification_result.get("subgenre"),
                    "genre_confidence": classification_result.get("confidence"),
                    "classification_source": classification_result.get("classification_source"),
                    "overall_confidence": classification_result.get("confidence")
                }
                
                classification = supabase_client.insert_classification(classification_data)
            else:
                classification = None
            
            return jsonify({
                "file_hash": file_hash,
                "file_path": file_path,
                "status": "new",
                "track_id": track['id'],
                "classification": classification,
                "source": "live_analysis"
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/batch', methods=['POST'])
def batch_analyze():
    """Batch file analysis"""
    global request_count
    request_count += 1
    
    data = request.get_json()
    file_paths = data.get('file_paths', [])
    
    if not file_paths:
        return jsonify({"error": "file_paths required"}), 400
    
    results = []
    
    for file_path in file_paths[:100]:  # Limit to 100 files per batch
        try:
            # Get hash
            file_hash = calculate_file_hash(file_path)
            if not file_hash:
                results.append({
                    "file_path": file_path,
                    "status": "error",
                    "error": "Could not calculate hash"
                })
                continue
            
            # Check existing
            existing_track = supabase_client.get_track_by_hash(file_hash)
            
            if existing_track:
                classification = supabase_client.get_classification(existing_track['id'])
                results.append({
                    "file_path": file_path,
                    "file_hash": file_hash,
                    "status": "known",
                    "track_id": existing_track['id'],
                    "classification": classification
                })
            else:
                results.append({
                    "file_path": file_path,
                    "file_hash": file_hash,
                    "status": "new",
                    "note": "Use /analyze endpoint for full processing"
                })
        
        except Exception as e:
            results.append({
                "file_path": file_path,
                "status": "error",
                "error": str(e)
            })
    
    return jsonify({
        "processed": len(results),
        "results": results
    })

@app.route('/stats')
def get_stats():
    """Get database statistics"""
    try:
        stats = supabase_client.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎵 Cultural Intelligence API (Supabase REST)")
    print("="*50)
    print(f"Starting on 172.22.17.37:5000...")
    print(f"Health check: http://172.22.17.37:5000/health")
    print(f"Ready for MetaCrate integration!")
    
    app.run(host='172.22.17.37', port=5000, debug=True)