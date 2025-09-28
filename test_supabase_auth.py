#!/usr/bin/env python3
"""
Test Supabase authentication methods for Cultural Intelligence System
"""

import psycopg2
import requests
import json

# MetaCrate credentials from user
SUPABASE_URL = "http://172.22.17.138:8000"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJzZXJ2aWNlX3JvbGUiLAogICAgImlzcyI6ICJzdXBhYmFzZS1kZW1vIiwKICAgICJpYXQiOiAxNjQxNzY5MjAwLAogICAgImV4cCI6IDE3OTk1MzU2MDAKfQ.DaYlNEoUrrEn2Ig7tqibS-PHK5vgusbcbo7X36XVt4Q"

def test_direct_postgres():
    """Test direct PostgreSQL connection methods"""
    print("\n🔍 Testing Direct PostgreSQL Methods:")
    
    # Method 1: Use JWT as password
    try:
        conn_string1 = f"postgresql://postgres:{SERVICE_ROLE_KEY}@172.22.17.138:5432/postgres"
        print(f"  Method 1: JWT as password...")
        conn = psycopg2.connect(conn_string1)
        print(f"  ✅ SUCCESS with JWT as password!")
        conn.close()
        return conn_string1
    except Exception as e:
        print(f"  ❌ Method 1 failed: {e}")
    
    # Method 2: Use 'service_role' user with JWT password
    try:
        conn_string2 = f"postgresql://service_role:{SERVICE_ROLE_KEY}@172.22.17.138:5432/postgres"
        print(f"  Method 2: service_role user...")
        conn = psycopg2.connect(conn_string2)
        print(f"  ✅ SUCCESS with service_role user!")
        conn.close()
        return conn_string2
    except Exception as e:
        print(f"  ❌ Method 2 failed: {e}")
    
    # Method 3: Default postgres user with empty password
    try:
        conn_string3 = f"postgresql://postgres:@172.22.17.138:5432/postgres"
        print(f"  Method 3: Empty password...")
        conn = psycopg2.connect(conn_string3)
        print(f"  ✅ SUCCESS with empty password!")
        conn.close()
        return conn_string3
    except Exception as e:
        print(f"  ❌ Method 3 failed: {e}")
    
    return None

def test_supabase_api():
    """Test Supabase REST API access"""
    print("\n🌐 Testing Supabase REST API:")
    
    try:
        headers = {
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }
        
        # Test API access
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        print(f"  API Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Supabase REST API accessible!")
            
            # Try to list tables
            tables_response = requests.get(f"{SUPABASE_URL}/rest/v1/cultural_tracks?limit=1", headers=headers)
            print(f"  Tables query status: {tables_response.status_code}")
            
            if tables_response.status_code == 200:
                print(f"  ✅ Can query cultural_tracks table!")
                return True
            else:
                print(f"  ⚠️  Can access API but not tables: {tables_response.text}")
        
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
    
    return False

def main():
    """Test all connection methods"""
    print("🔐 SUPABASE AUTHENTICATION TESTING")
    print("="*50)
    
    # Test direct PostgreSQL connections
    working_conn = test_direct_postgres()
    
    # Test Supabase REST API
    api_works = test_supabase_api()
    
    print(f"\n📋 RESULTS:")
    
    if working_conn:
        print(f"✅ Direct PostgreSQL: {working_conn}")
        
        # Update our config with working connection
        config_file = "taxonomy_config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config['supabase']['url'] = working_conn
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated {config_file} with working connection")
        
    else:
        print(f"❌ Direct PostgreSQL: All methods failed")
    
    if api_works:
        print(f"✅ Supabase REST API: Working")
    else:
        print(f"❌ Supabase REST API: Failed")
    
    if working_conn or api_works:
        print(f"\n🚀 Ready to deploy Cultural Intelligence Service!")
    else:
        print(f"\n⚠️  Need to investigate Supabase configuration")

if __name__ == "__main__":
    main()