#!/usr/bin/env python3
"""
Quick test of MetaCrate Integration API
"""

import requests
import json

def test_api():
    """Test the MetaCrate Integration API"""
    
    base_url = "http://172.22.17.37:5000"
    
    print("🧪 Testing MetaCrate Integration API")
    print("=" * 40)
    
    # 1. Health check
    try:
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ API is healthy")
            print(f"   📊 Tracks in database: {health['statistics']['tracks_in_database']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # 2. Test track analysis with a non-existent file (should still return defaults)
    print("\n2. Testing track analysis...")
    try:
        test_payload = {
            "file_path": r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals\test_track.mp3"
        }
        
        response = requests.post(f"{base_url}/api/track/analyze", 
                               json=test_payload, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            track = result['track']
            
            print(f"   ✅ Analysis completed")
            print(f"   🎵 Artist: {track['artist']}")
            print(f"   🎵 Track: {track['track_name']}")
            print(f"   🎵 Remix: {track['remix_info']}")
            print(f"   🎵 Genre: {track['genre']}")
            print(f"   🎵 Subgenre: {track['subgenre'] or 'None'}")
            print(f"   📊 Confidence: {track['confidence']:.1%}")
            print(f"   ⚡ Response time: {result.get('api_info', {}).get('response_time_ms', 0)}ms")
            
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
    
    print("\n✅ MetaCrate API Test Complete!")
    print("\n🔗 Integration endpoints:")
    print(f"   Health: GET {base_url}/api/health")
    print(f"   Analyze: POST {base_url}/api/track/analyze")
    print(f"   Batch: POST {base_url}/api/track/batch")

if __name__ == "__main__":
    test_api()