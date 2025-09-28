#!/usr/bin/env python3
"""
CULTURAL INTELLIGENCE API - STATUS CHECKER
==========================================
Check if the API is running and test basic functionality.
"""

import requests
import json
import sys

def check_api_status():
    """Check if the Cultural Intelligence API is running"""
    
    print("🎵 Cultural Intelligence API - Status Check")
    print("=" * 45)
    
    api_base = "http://172.22.17.37:5000/api/v3.2"
    
    try:
        # Health check
        print("🔄 Checking API health...")
        response = requests.get(f"{api_base}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API is RUNNING!")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Version: {health_data.get('version', 'unknown')}")
            print(f"   Database: {'Connected' if health_data.get('database_connected') else 'Disconnected'}")
            
            # Test database query
            print("\n🔄 Testing database connection...")
            stats_response = requests.get(f"{api_base}/stats", timeout=5)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print("✅ Database queries working!")
                print(f"   Tracks: {stats.get('tracks', 0)}")
                print(f"   Artists: {stats.get('artists', 0)}")
                print(f"   Labels: {stats.get('labels', 0)}")
                print(f"   Patterns: {stats.get('patterns', 0)}")
            else:
                print("⚠️ Database queries not responding")
            
            print(f"\n📡 API Endpoints Available:")
            print(f"   • Health: {api_base}/health")
            print(f"   • Stats: {api_base}/stats") 
            print(f"   • Analyze: {api_base}/analyze")
            print(f"   • Lookup: {api_base}/lookup/<hash>")
            print(f"   • Batch: {api_base}/batch")
            
            return True
            
        else:
            print(f"❌ API returned status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API is NOT running")
        print("💡 Start it with: python start_api.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ API is not responding (timeout)")
        return False
        
    except Exception as e:
        print(f"❌ Error checking API: {e}")
        return False

def main():
    """Main function"""
    if check_api_status():
        print("\n🎉 Cultural Intelligence System is READY!")
        return 0
    else:
        print("\n💡 Start the API service with: python start_api.py")
        return 1

if __name__ == "__main__":
    exit(main())