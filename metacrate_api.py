#!/usr/bin/env python3
"""
Cultural Intelligence System v3.2 - MetaCrate Integration API
============================================================

FastAPI service providing real-time taxonomy intelligence to MetaCrate.
Delivers instant classification, duplicate detection, and metadata intelligence.
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("⚠️  Installing Flask for API service...")
    os.system("pip install flask flask-cors")
    from flask import Flask, jsonify, request
    from flask_cors import CORS

from taxonomy_v32 import TaxonomyConfig
from taxonomy_scanner import MetadataExtractor, PatternAnalyzer

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Global instances
config = TaxonomyConfig()
metadata_extractor = MetadataExtractor()
pattern_analyzer = PatternAnalyzer()

# In-memory cache for fast lookups (production would use Redis/database)
classification_cache = {}
duplicate_cache = {}

class MetaCrateAPI:
    """MetaCrate integration API for real-time taxonomy intelligence"""
    
    def __init__(self):
        self.request_count = 0
        self.start_time = time.time()
        
        # Load any existing classification data
        self._load_cached_data()
    
    def _load_cached_data(self):
        """Load existing classification data for fast lookups"""
        # In production, this would load from Supabase
        # For now, try to load from recent scan results
        try:
            # Look for recent scan files
            scan_files = [f for f in os.listdir('.') if f.startswith('taxonomy_scan_') and f.endswith('.json')]
            if scan_files:
                latest_scan = max(scan_files, key=os.path.getctime)
                with open(latest_scan, 'r') as f:
                    data = json.load(f)
                
                # Cache classifications by hash
                for classification in data.get('classifications', []):
                    file_hash = classification.get('file_hash')
                    if file_hash:
                        classification_cache[file_hash] = classification
                
                # Cache duplicate information
                for group in data.get('duplicate_groups', []):
                    group_hash = group.get('hash')
                    if group_hash:
                        duplicate_cache[group_hash] = group
                
                print(f"Loaded {len(classification_cache)} classifications from {latest_scan}")
        except Exception as e:
            print(f"Could not load cached data: {e}")
    
    def get_file_intelligence(self, file_path: str = None, file_hash: str = None) -> Dict:
        """Get comprehensive intelligence for a file"""
        start_time = time.time()
        
        try:
            # Generate hash if not provided
            if file_path and not file_hash:
                file_hash = self._generate_hash(file_path)
            
            # Check cache first
            cached_result = classification_cache.get(file_hash) if file_hash else None
            
            if cached_result:
                # Return cached classification with duplicate info
                result = {
                    "status": "success",
                    "source": "cached",
                    "file_hash": file_hash,
                    "classification": {
                        "artist": cached_result.get('artist'),
                        "track_name": cached_result.get('track_name'),
                        "remix_info": cached_result.get('remix_info'),
                        "genre": cached_result.get('genre'),
                        "subgenre": cached_result.get('subgenre'),
                        "label": cached_result.get('label'),
                        "bpm": cached_result.get('bpm'),
                        "confidence": cached_result.get('genre_confidence', 0.0)
                    },
                    "duplicates": self._get_duplicate_info(file_hash),
                    "metadata": cached_result.get('metadata', {}),
                    "processing_info": {
                        "processed_at": cached_result.get('processed_at'),
                        "classification_sources": cached_result.get('classification_sources', [])
                    }
                }
            else:
                # Perform real-time analysis
                if not file_path or not os.path.exists(file_path):
                    return {
                        "status": "error",
                        "error": "File not found or file_path not provided",
                        "file_hash": file_hash
                    }
                
                result = self._analyze_file_realtime(file_path, file_hash)
            
            # Add API metadata
            result["api_info"] = {
                "response_time_ms": int((time.time() - start_time) * 1000),
                "api_version": "v3.2",
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "file_hash": file_hash,
                "api_info": {
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def _generate_hash(self, file_path: str) -> str:
        """Generate file hash for lookup"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def _get_duplicate_info(self, file_hash: str) -> Dict:
        """Get duplicate information for file"""
        duplicate_group = duplicate_cache.get(file_hash)
        if duplicate_group:
            return {
                "is_duplicate": True,
                "duplicate_count": duplicate_group.get('count', 1),
                "duplicate_files": duplicate_group.get('files', []),
                "primary_file": duplicate_group.get('files', [None])[0]  # First file as primary
            }
        else:
            return {
                "is_duplicate": False,
                "duplicate_count": 1
            }
    
    def _analyze_file_realtime(self, file_path: str, file_hash: str) -> Dict:
        """Perform real-time analysis of file"""
        try:
            # Extract metadata
            metadata = metadata_extractor.extract_metadata(file_path)
            
            # Analyze patterns  
            filename_analysis = pattern_analyzer.analyze_filename(Path(file_path).name)
            folder_analysis = pattern_analyzer.analyze_folder_path(str(Path(file_path).parent))
            metadata_analysis = pattern_analyzer.analyze_metadata_fields(metadata)
            
            # Combine for classification
            genre_hints = []
            for hint in filename_analysis.get('genre_hints', []):
                genre_hints.append(('filename', hint, 0.7))
            for hint in folder_analysis.get('genre_hints', []):
                genre_hints.append(('folder', hint, 0.9))
            for hint in metadata_analysis.get('genre_hints', []):
                genre_hints.append(('metadata', hint, 0.95))
            
            # Determine best genre
            if genre_hints:
                from collections import defaultdict
                genre_scores = defaultdict(float)
                for source, genre, confidence in genre_hints:
                    genre_scores[genre] += confidence
                best_genre = max(genre_scores.items(), key=lambda x: x[1])
                final_genre = best_genre[0]
                genre_confidence = min(best_genre[1] / len(genre_hints), 1.0)
            else:
                final_genre = 'Electronic'
                genre_confidence = 0.1
            
            # Build response
            result = {
                "status": "success",
                "source": "realtime_analysis",
                "file_hash": file_hash,
                "classification": {
                    "artist": (metadata_analysis.get('artist') or 
                             filename_analysis.get('artist') or 'Unknown Artist'),
                    "track_name": (metadata_analysis.get('track') or 
                                 filename_analysis.get('track') or Path(file_path).stem),
                    "remix_info": filename_analysis.get('remix_type'),
                    "genre": final_genre,
                    "subgenre": None,  # Would need more sophisticated analysis
                    "label": metadata_analysis.get('label'),
                    "bpm": metadata_analysis.get('bpm'),
                    "confidence": genre_confidence
                },
                "duplicates": {
                    "is_duplicate": False,  # Real-time can't check against full database
                    "duplicate_count": 1,
                    "note": "Real-time analysis - run full scan for duplicate detection"
                },
                "metadata": metadata,
                "processing_info": {
                    "processed_at": datetime.now().isoformat(),
                    "classification_sources": genre_hints,
                    "analysis_method": "realtime"
                }
            }
            
            # Cache the result
            classification_cache[file_hash] = result['classification']
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Analysis failed: {str(e)}",
                "file_hash": file_hash
            }

# Initialize API instance
metacrate_api = MetaCrateAPI()

# =====================================================
# FLASK API ENDPOINTS
# =====================================================

@app.route('/api/v3.2/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    uptime = time.time() - metacrate_api.start_time
    return jsonify({
        "status": "healthy",
        "service": "Cultural Intelligence System v3.2",
        "purpose": "MetaCrate Integration API",
        "uptime_seconds": int(uptime),
        "cached_classifications": len(classification_cache),
        "cached_duplicates": len(duplicate_cache),
        "total_requests": metacrate_api.request_count,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v3.2/file/hash/<file_hash>', methods=['GET'])
def get_file_by_hash(file_hash):
    """Get file intelligence by hash"""
    metacrate_api.request_count += 1
    
    result = metacrate_api.get_file_intelligence(file_hash=file_hash)
    
    # Log request for monitoring
    print(f"Hash lookup: {file_hash[:8]}... | Status: {result.get('status')} | "
          f"Response: {result.get('api_info', {}).get('response_time_ms', 0)}ms")
    
    return jsonify(result)

@app.route('/api/v3.2/file/analyze', methods=['POST'])
def analyze_file():
    """Analyze file by path (real-time)"""
    metacrate_api.request_count += 1
    
    data = request.json
    file_path = data.get('file_path') if data else None
    
    if not file_path:
        return jsonify({
            "status": "error",
            "error": "file_path required in JSON body"
        }), 400
    
    result = metacrate_api.get_file_intelligence(file_path=file_path)
    
    # Log request
    print(f"Real-time analysis: {Path(file_path).name} | Status: {result.get('status')} | "
          f"Response: {result.get('api_info', {}).get('response_time_ms', 0)}ms")
    
    return jsonify(result)

@app.route('/api/v3.2/file/path', methods=['GET'])
def get_file_by_path():
    """Get file intelligence by path (query parameter)"""
    metacrate_api.request_count += 1
    
    file_path = request.args.get('path')
    
    if not file_path:
        return jsonify({
            "status": "error", 
            "error": "path parameter required"
        }), 400
    
    result = metacrate_api.get_file_intelligence(file_path=file_path)
    
    return jsonify(result)

@app.route('/api/v3.2/stats', methods=['GET'])
def get_api_stats():
    """Get API usage statistics"""
    return jsonify({
        "service_stats": {
            "uptime_seconds": int(time.time() - metacrate_api.start_time),
            "total_requests": metacrate_api.request_count,
            "requests_per_minute": metacrate_api.request_count / ((time.time() - metacrate_api.start_time) / 60) if metacrate_api.request_count > 0 else 0
        },
        "cache_stats": {
            "classifications_cached": len(classification_cache),
            "duplicates_cached": len(duplicate_cache)
        },
        "supported_operations": [
            "GET /api/v3.2/file/hash/<hash>",
            "POST /api/v3.2/file/analyze", 
            "GET /api/v3.2/file/path?path=<path>",
            "GET /api/v3.2/health",
            "GET /api/v3.2/stats"
        ]
    })

@app.route('/api/v3.2/batch', methods=['POST'])
def batch_analyze():
    """Batch file analysis for MetaCrate efficiency"""
    metacrate_api.request_count += 1
    
    data = request.json
    file_paths = data.get('file_paths', []) if data else []
    
    if not file_paths or not isinstance(file_paths, list):
        return jsonify({
            "status": "error",
            "error": "file_paths array required in JSON body"
        }), 400
    
    results = []
    for file_path in file_paths[:50]:  # Limit batch size
        result = metacrate_api.get_file_intelligence(file_path=file_path)
        results.append({
            "file_path": file_path,
            "result": result
        })
    
    return jsonify({
        "status": "success",
        "batch_size": len(results),
        "results": results,
        "api_info": {
            "timestamp": datetime.now().isoformat(),
            "batch_limit": 50
        }
    })

# =====================================================
# MetaCrate SDK/Client Library
# =====================================================

class MetaCrateClient:
    """Python client for MetaCrate integration"""
    
    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url.rstrip('/')
        self.base_path = "/api/v3.2"
    
    def get_file_intelligence(self, file_path: str = None, file_hash: str = None) -> Dict:
        """Get intelligence for a file"""
        import requests
        
        if file_hash:
            url = f"{self.api_url}{self.base_path}/file/hash/{file_hash}"
            response = requests.get(url)
        elif file_path:
            url = f"{self.api_url}{self.base_path}/file/path"
            response = requests.get(url, params={"path": file_path})
        else:
            return {"status": "error", "error": "file_path or file_hash required"}
        
        return response.json()
    
    def analyze_file(self, file_path: str) -> Dict:
        """Real-time file analysis"""
        import requests
        
        url = f"{self.api_url}{self.base_path}/file/analyze"
        response = requests.post(url, json={"file_path": file_path})
        return response.json()
    
    def batch_analyze(self, file_paths: List[str]) -> Dict:
        """Batch analysis for efficiency"""
        import requests
        
        url = f"{self.api_url}{self.base_path}/batch"
        response = requests.post(url, json={"file_paths": file_paths})
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health"""
        import requests
        
        url = f"{self.api_url}{self.base_path}/health"
        response = requests.get(url)
        return response.json()

def main():
    """Start the MetaCrate API service"""
    print("CULTURAL INTELLIGENCE SYSTEM v3.2 - MetaCrate API")
    print("=" * 55)
    print("Starting API service for real-time taxonomy intelligence")
    print()
    
    host = config.get('api.host', '0.0.0.0')
    port = config.get('api.port', 5000)
    debug = config.get('api.debug', False)
    
    print(f"API Endpoints:")
    print(f"   Health Check: http://{host}:{port}/api/v3.2/health")
    print(f"   File Hash:    http://{host}:{port}/api/v3.2/file/hash/<hash>")  
    print(f"   File Path:    http://{host}:{port}/api/v3.2/file/path?path=<path>")
    print(f"   Analyze:      POST http://{host}:{port}/api/v3.2/file/analyze")
    print(f"   Batch:        POST http://{host}:{port}/api/v3.2/batch")
    print()
    print(f"Cached Data:")
    print(f"   Classifications: {len(classification_cache)}")
    print(f"   Duplicates: {len(duplicate_cache)}")
    print()
    print("Ready for MetaCrate integration!")
    print("=" * 55)
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()