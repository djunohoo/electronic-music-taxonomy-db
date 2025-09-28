#!/usr/bin/env python3
"""
Supabase REST API Client for Cultural Intelligence System
Uses REST API instead of direct PostgreSQL connection
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class SupabaseConfig:
    """Supabase configuration"""
    url: str
    service_role_key: str
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

class SupabaseClient:
    """REST API client for Supabase Cultural Intelligence database"""
    
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self.base_url = f"{config.url}/rest/v1"
        self.session = requests.Session()
        self.session.headers.update(config.headers)
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make REST API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Supabase API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            raise
    
    def insert_track(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert track into cultural_tracks table"""
        response = self._make_request("POST", "cultural_tracks", json=track_data)
        return response.json()[0] if response.json() else {}
    
    def get_track_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get track by file hash"""
        response = self._make_request(
            "GET", 
            f"cultural_tracks?file_hash=eq.{file_hash}&limit=1"
        )
        result = response.json()
        return result[0] if result else None
    
    def get_track_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get track by file path"""
        response = self._make_request(
            "GET", 
            f"cultural_tracks?file_path=eq.{file_path}&limit=1"
        )
        result = response.json()
        return result[0] if result else None
    
    def insert_classification(self, classification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert classification into cultural_classifications table"""
        response = self._make_request("POST", "cultural_classifications", json=classification_data)
        return response.json()[0] if response.json() else {}
    
    def get_classification(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Get classification for track"""
        response = self._make_request(
            "GET", 
            f"cultural_classifications?track_id=eq.{track_id}&limit=1"
        )
        result = response.json()
        return result[0] if result else None
    
    def insert_pattern(self, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update pattern"""
        response = self._make_request(
            "POST", 
            "cultural_patterns", 
            json=pattern_data,
            headers={"Prefer": "resolution=merge-duplicates"}
        )
        return response.json()[0] if response.json() else {}
    
    def get_patterns(self, pattern_type: str = None, genre: str = None) -> List[Dict[str, Any]]:
        """Get patterns with optional filtering"""
        query_parts = []
        if pattern_type:
            query_parts.append(f"pattern_type=eq.{pattern_type}")
        if genre:
            query_parts.append(f"genre=eq.{genre}")
        
        query = "&".join(query_parts)
        endpoint = f"cultural_patterns?{query}" if query else "cultural_patterns"
        
        response = self._make_request("GET", endpoint)
        return response.json()
    
    def get_artist_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get artist profile"""
        response = self._make_request(
            "GET", 
            f"cultural_artist_profiles?name=eq.{name}&limit=1"
        )
        result = response.json()
        return result[0] if result else None
    
    def insert_artist_profile(self, artist_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert artist profile"""
        response = self._make_request("POST", "cultural_artist_profiles", json=artist_data)
        return response.json()[0] if response.json() else {}
    
    def get_label_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get label profile"""
        response = self._make_request(
            "GET", 
            f"cultural_label_profiles?name=eq.{name}&limit=1"
        )
        result = response.json()
        return result[0] if result else None
    
    def insert_label_profile(self, label_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert label profile"""
        response = self._make_request("POST", "cultural_label_profiles", json=label_data)
        return response.json()[0] if response.json() else {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        # Count tracks
        response = self._make_request("GET", "cultural_tracks?select=count")
        stats['total_tracks'] = response.json()[0]['count'] if response.json() else 0
        
        # Count classifications
        response = self._make_request("GET", "cultural_classifications?select=count")
        stats['total_classifications'] = response.json()[0]['count'] if response.json() else 0
        
        # Count patterns
        response = self._make_request("GET", "cultural_patterns?select=count")
        stats['total_patterns'] = response.json()[0]['count'] if response.json() else 0
        
        # Count artists
        response = self._make_request("GET", "cultural_artist_profiles?select=count")
        stats['total_artists'] = response.json()[0]['count'] if response.json() else 0
        
        # Count labels
        response = self._make_request("GET", "cultural_label_profiles?select=count")
        stats['total_labels'] = response.json()[0]['count'] if response.json() else 0
        
        return stats
    
    def log_api_request(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log API request"""
        response = self._make_request("POST", "cultural_api_requests", json=log_data)
        return response.json()[0] if response.json() else {}

def create_supabase_client() -> SupabaseClient:
    """Create Supabase client from config"""
    
    # Load config
    with open("taxonomy_config.json", "r") as f:
        config_data = json.load(f)
    
    # Create Supabase config
    supabase_config = SupabaseConfig(
        url="http://172.22.17.138:8000",
        service_role_key=config_data["supabase"]["key"]
    )
    
    return SupabaseClient(supabase_config)

def test_supabase_client():
    """Test Supabase client functionality"""
    print("🧪 Testing Supabase REST API Client...")
    
    try:
        client = create_supabase_client()
        
        # Test statistics
        stats = client.get_statistics()
        print(f"✅ Database statistics: {stats}")
        
        # Test pattern retrieval
        patterns = client.get_patterns(pattern_type="folder")
        print(f"✅ Found {len(patterns)} folder patterns")
        
        # Test artist lookup
        artist = client.get_artist_profile("Deadmau5")
        if artist:
            print(f"✅ Found artist: {artist['name']} - {artist['primary_genres']}")
        
        print(f"🎉 Supabase REST API client working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase client test failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_client()