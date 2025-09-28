#!/usr/bin/env python3
"""
Cultural Intelligence Database Client - Existing Tables Adapter
Works with existing cultural_ tables in MetaCrate database
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CulturalDatabaseClient:
    """Database client adapted for existing cultural_ tables."""
    
    def __init__(self, config_file: str = "taxonomy_config.json"):
        """Initialize client with configuration."""
        self.config = self._load_config(config_file)
        self.base_url = f"{self.config['supabase']['url']}/rest/v1"
        self.headers = {
            "apikey": self.config["supabase"]["service_role_key"],
            "Authorization": f"Bearer {self.config['supabase']['service_role_key']}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        with open(config_file, 'r') as f:
            return json.load(f)
            
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make REST API request with error handling."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Supabase API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
            
    # ================================
    # DISCOVERED TRACKS (cultural_tracks)
    # ================================
    
    def create_discovered_track(self, track_data: Dict) -> Optional[int]:
        """Create new discovered track record."""
        try:
            # Map to existing cultural_tracks structure
            cultural_track = {
                'file_path': track_data['file_path'],
                'file_hash': track_data['file_hash'],
                'file_size': track_data['file_size'],
                'file_modified': track_data['file_modified'],
                'raw_metadata': track_data.get('raw_metadata', {}),
                'filename': track_data['filename'],
                'folder_path': track_data['folder_path'],
                'file_extension': track_data['file_extension'],
                'processing_version': 'v4.0_scanner'
            }
            
            response = self._make_request('POST', 'cultural_tracks', json=cultural_track)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]['id']
            return None
            
        except Exception as e:
            logger.error(f"Error creating discovered track: {e}")
            return None
            
    def get_track_by_hash(self, file_hash: str) -> Optional[Dict]:
        """Get track by file hash."""
        try:
            response = self._make_request('GET', f'cultural_tracks?file_hash=eq.{file_hash}')
            result = response.json()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting track by hash: {e}")
            return None
            
    def get_all_discovered_tracks(self) -> List[Dict]:
        """Get all discovered tracks."""
        try:
            response = self._make_request('GET', 'cultural_tracks')
            return response.json()
        except Exception as e:
            logger.error(f"Error getting all tracks: {e}")
            return []
            
    def count_discovered_tracks(self) -> int:
        """Count total discovered tracks."""
        try:
            headers = {**self.headers, 'Prefer': 'count=exact'}
            response = requests.get(f"{self.base_url}/cultural_tracks?select=count", headers=headers)
            response.raise_for_status()
            
            # Supabase returns count in Content-Range header
            count_header = response.headers.get('Content-Range', '0')
            if '/' in count_header:
                return int(count_header.split('/')[-1])
            return 0
        except Exception as e:
            logger.error(f"Error counting tracks: {e}")
            return 0
            
    # ================================
    # TRACK ANALYSIS (cultural_classifications - reuse existing)
    # ================================
    
    def create_track_analysis(self, analysis_data: Dict) -> Optional[int]:
        """Create track analysis - store in cultural_classifications."""
        try:
            # Map analysis data to cultural_classifications structure
            classification = {
                'track_id': analysis_data['track_id'],
                'artist': analysis_data.get('metadata_artist') or analysis_data.get('filename_artist'),
                'track_name': analysis_data.get('metadata_title') or analysis_data.get('filename_track'),
                'remix_info': analysis_data.get('filename_remix'),
                'genre': analysis_data.get('metadata_genre'),
                'bpm': analysis_data.get('metadata_bpm'),
                'musical_key': None,  # Not extracted yet
                'duration_seconds': int(analysis_data.get('metadata_duration', 0)) if analysis_data.get('metadata_duration') else None,
                'classification_source': 'scanner_analysis',
                'genre_confidence': 0.5,  # Default
                'overall_confidence': 0.5,
                'needs_review': True  # Mark for review initially
            }
            
            response = self._make_request('POST', 'cultural_classifications', json=classification)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]['id']
            return None
            
        except Exception as e:
            logger.error(f"Error creating track analysis: {e}")
            return None
            
    def get_all_track_analyses(self) -> List[Dict]:
        """Get all track analyses."""
        try:
            response = self._make_request('GET', 'cultural_classifications')
            return response.json()
        except Exception as e:
            logger.error(f"Error getting track analyses: {e}")
            return []
            
    # ================================
    # TRACK CLASSIFICATIONS (cultural_classifications)
    # ================================
    
    def create_track_classification(self, classification_data: Dict) -> Optional[int]:
        """Create or update track classification."""
        try:
            # Check if classification already exists for this track
            existing_response = self._make_request('GET', f'cultural_classifications?track_id=eq.{classification_data["track_id"]}')
            existing = existing_response.json()
            
            classification = {
                'track_id': classification_data['track_id'],
                'artist': classification_data.get('artist'),
                'track_name': classification_data.get('track_name'),
                'remix_info': classification_data.get('remix_info'),
                'label': classification_data.get('label'),
                'genre': classification_data.get('primary_genre'),
                'subgenre': classification_data.get('subgenre'),
                'genre_confidence': classification_data.get('genre_confidence', 0.0),
                'subgenre_confidence': classification_data.get('subgenre_confidence', 0.0),
                'overall_confidence': classification_data.get('overall_confidence', 0.0),
                'classification_source': 'intelligence_scanner',
                'needs_review': classification_data.get('needs_review', False),
                'human_validated': False
            }
            
            if existing:
                # Update existing
                response = self._make_request('PATCH', f'cultural_classifications?id=eq.{existing[0]["id"]}', json=classification)
                return existing[0]['id']
            else:
                # Create new
                response = self._make_request('POST', 'cultural_classifications', json=classification)
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['id']
                return None
                
        except Exception as e:
            logger.error(f"Error creating track classification: {e}")
            return None
            
    # ================================
    # PATTERNS (cultural_patterns)
    # ================================
    
    def get_patterns(self, pattern_type: str = None, pattern_value: str = None, genre: str = None) -> List[Dict]:
        """Get learned patterns with optional filters."""
        try:
            filters = []
            if pattern_type:
                filters.append(f'pattern_type=eq.{pattern_type}')
            if pattern_value:
                filters.append(f'pattern_value=eq.{pattern_value}')
            if genre:
                filters.append(f'genre=eq.{genre}')
                
            query = '&'.join(filters)
            endpoint = f'cultural_patterns?{query}' if query else 'cultural_patterns'
            
            response = self._make_request('GET', endpoint)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting patterns: {e}")
            return []
            
    def create_pattern(self, pattern_type: str, pattern_value: str, genre: str, 
                      confidence: float, sample_size: int) -> Optional[int]:
        """Create new learned pattern."""
        try:
            pattern = {
                'pattern_type': pattern_type,
                'pattern_value': pattern_value,
                'genre': genre,
                'confidence': confidence,
                'sample_size': sample_size,
                'success_rate': confidence  # Initial success rate = confidence
            }
            
            response = self._make_request('POST', 'cultural_patterns', json=pattern)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]['id']
            return None
            
        except Exception as e:
            logger.error(f"Error creating pattern: {e}")
            return None
            
    def update_pattern(self, pattern_id: int, **updates) -> bool:
        """Update existing pattern."""
        try:
            # Add last_updated timestamp
            updates['last_updated'] = datetime.now().isoformat()
            
            response = self._make_request('PATCH', f'cultural_patterns?id=eq.{pattern_id}', json=updates)
            return True
        except Exception as e:
            logger.error(f"Error updating pattern: {e}")
            return False
            
    def count_learned_patterns(self) -> int:
        """Count total learned patterns."""
        try:
            headers = {**self.headers, 'Prefer': 'count=exact'}
            response = requests.get(f"{self.base_url}/cultural_patterns?select=count", headers=headers)
            response.raise_for_status()
            
            count_header = response.headers.get('Content-Range', '0')
            if '/' in count_header:
                return int(count_header.split('/')[-1])
            return 0
        except Exception as e:
            logger.error(f"Error counting patterns: {e}")
            return 0
            
    # ================================
    # ARTIST PROFILES (cultural_artist_profiles)
    # ================================
    
    def get_artist_profile(self, artist_name: str) -> Optional[Dict]:
        """Get artist profile by name."""
        try:
            # Try exact match first
            response = self._make_request('GET', f'cultural_artist_profiles?name=eq.{artist_name}')
            result = response.json()
            if result:
                return result[0]
                
            # Try normalized name match
            normalized = artist_name.lower().replace(' ', '').replace('&', 'and')
            response = self._make_request('GET', f'cultural_artist_profiles?normalized_name=eq.{normalized}')
            result = response.json()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting artist profile: {e}")
            return None
            
    def create_artist_profile(self, profile_data: Dict) -> Optional[int]:
        """Create new artist profile."""
        try:
            profile = {
                'name': profile_data['name'],
                'normalized_name': profile_data['normalized_name'],
                'primary_genres': list(profile_data.get('genres', {}).keys()),
                'genre_confidence': profile_data.get('genres', {}),
                'track_count': profile_data.get('total_tracks', 0),
                'labels_worked_with': profile_data.get('labels', []),
                'external_data': {'confidence': profile_data.get('confidence', 0.0)}
            }
            
            response = self._make_request('POST', 'cultural_artist_profiles', json=profile)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]['id']
            return None
            
        except Exception as e:
            logger.error(f"Error creating artist profile: {e}")
            return None
            
    def update_artist_profile(self, profile_id: int, profile_data: Dict) -> bool:
        """Update existing artist profile."""
        try:
            updates = {
                'primary_genres': list(profile_data.get('genres', {}).keys()),
                'genre_confidence': profile_data.get('genres', {}),
                'track_count': profile_data.get('total_tracks', 0),
                'labels_worked_with': profile_data.get('labels', []),
                'external_data': {'confidence': profile_data.get('confidence', 0.0)},
                'last_updated': datetime.now().isoformat()
            }
            
            response = self._make_request('PATCH', f'cultural_artist_profiles?id=eq.{profile_id}', json=updates)
            return True
        except Exception as e:
            logger.error(f"Error updating artist profile: {e}")
            return False
            
    def get_all_artist_profiles(self) -> List[Dict]:
        """Get all artist profiles."""
        try:
            response = self._make_request('GET', 'cultural_artist_profiles')
            return response.json()
        except Exception as e:
            logger.error(f"Error getting artist profiles: {e}")
            return []
            
    def count_artist_profiles(self) -> int:
        """Count total artist profiles."""
        try:
            headers = {**self.headers, 'Prefer': 'count=exact'}
            response = requests.get(f"{self.base_url}/cultural_artist_profiles?select=count", headers=headers)
            response.raise_for_status()
            
            count_header = response.headers.get('Content-Range', '0')
            if '/' in count_header:
                return int(count_header.split('/')[-1])
            return 0
        except Exception as e:
            logger.error(f"Error counting artist profiles: {e}")
            return 0
            
    # ================================
    # LABEL PROFILES (cultural_label_profiles)
    # ================================
    
    def get_all_label_profiles(self) -> List[Dict]:
        """Get all label profiles."""
        try:
            response = self._make_request('GET', 'cultural_label_profiles')
            return response.json()
        except Exception as e:
            logger.error(f"Error getting label profiles: {e}")
            return []
            
    # ================================
    # DUPLICATES (cultural_duplicates)
    # ================================
    
    def create_duplicate_group(self, duplicate_data: Dict) -> Optional[int]:
        """Create duplicate group record."""
        try:
            duplicate = {
                'file_hash': duplicate_data['file_hash'],
                'primary_track_id': duplicate_data['primary_track_id'],
                'duplicate_track_ids': duplicate_data['duplicate_track_ids'],
                'duplicate_count': duplicate_data['duplicate_count'],
                'total_size_bytes': duplicate_data['total_size_bytes'],
                'space_waste_bytes': duplicate_data['space_waste_bytes']
            }
            
            response = self._make_request('POST', 'cultural_duplicates', json=duplicate)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]['id']
            return None
            
        except Exception as e:
            logger.error(f"Error creating duplicate group: {e}")
            return None
            
    def count_duplicate_groups(self) -> int:
        """Count total duplicate groups."""
        try:
            headers = {**self.headers, 'Prefer': 'count=exact'}
            response = requests.get(f"{self.base_url}/cultural_duplicates?select=count", headers=headers)
            response.raise_for_status()
            
            count_header = response.headers.get('Content-Range', '0')
            if '/' in count_header:
                return int(count_header.split('/')[-1])
            return 0
        except Exception as e:
            logger.error(f"Error counting duplicates: {e}")
            return 0
            
    # ================================
    # SESSION MANAGEMENT (use API logs for now)
    # ================================
    
    def create_scan_session(self, session_data: Dict) -> int:
        """Create scan session (simulated with API log)."""
        try:
            session_log = {
                'endpoint': 'scan_session',
                'method': 'START',
                'request_path': session_data.get('scan_path'),
                'status_code': 200,
                'classification_returned': {
                    'session_type': 'automated_scan',
                    'status': session_data.get('status', 'running')
                }
            }
            
            response = self._make_request('POST', 'cultural_api_requests', json=session_log)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]['id']
            return 1  # Fallback ID
            
        except Exception as e:
            logger.error(f"Error creating scan session: {e}")
            return 1  # Fallback ID
            
    def update_scan_session(self, session_id: int, updates: Dict) -> bool:
        """Update scan session."""
        try:
            session_update = {
                'endpoint': 'scan_session',
                'method': 'UPDATE', 
                'status_code': 200,
                'classification_returned': {
                    'session_id': session_id,
                    'updates': updates
                }
            }
            
            response = self._make_request('POST', 'cultural_api_requests', json=session_update)
            return True
        except Exception as e:
            logger.error(f"Error updating scan session: {e}")
            return False
            
    def get_latest_scan_session(self) -> Optional[Dict]:
        """Get latest scan session info."""
        try:
            response = self._make_request('GET', 'cultural_api_requests?endpoint=eq.scan_session&order=requested_at.desc&limit=1')
            result = response.json()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting latest scan session: {e}")
            return None
            
    def log_processing_error(self, session_id: int, error_message: str) -> None:
        """Log processing error."""
        try:
            error_log = {
                'endpoint': 'processing_error',
                'method': 'ERROR',
                'status_code': 500,
                'classification_returned': {
                    'session_id': session_id,
                    'error': error_message
                }
            }
            
            self._make_request('POST', 'cultural_api_requests', json=error_log)
        except Exception as e:
            logger.error(f"Error logging processing error: {e}")

# Compatibility alias for the scanner
SupabaseClient = CulturalDatabaseClient