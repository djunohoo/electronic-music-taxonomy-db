#!/usr/bin/env python3
"""
Quick API Test - Tests if service is running WITHOUT blocking terminal
"""

import requests
import time

def quick_test():
    """Quick non-blocking test of the API"""
    print("🔍 Quick API Test (non-blocking)...")
    
    try:
        # Quick health check with short timeout
        response = requests.get("http://172.22.17.37:5000/health", timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is working!")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Database: {data.get('database', 'Unknown')}")
            print(f"   Uptime: {data.get('uptime_seconds', 0)} seconds")
            return True
        else:
            print(f"⚠️  API responding but status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API not responding - service may not be started")
        return False
    except requests.exceptions.Timeout:
        print("❌ API timeout - service may be starting up")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    quick_test()