#!/usr/bin/env python3
"""
Quick Dashboard Diagnostics
===========================
Debug the enhanced dashboard issues
"""

print("🔍 ENHANCED DASHBOARD DIAGNOSTICS")
print("=" * 50)

try:
    print("1. Checking Python imports...")
    import flask
    print(f"   ✅ Flask version: {flask.__version__}")
    
    import flask_socketio
    print(f"   ✅ SocketIO version: {flask_socketio.__version__}")
    
    print("2. Checking file structure...")
    import os
    files_to_check = [
        'enhanced_cultural_dashboard.py',
        'cultural_database_client.py',
        'templates/dashboard.html'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ Found: {file}")
        else:
            print(f"   ❌ Missing: {file}")
    
    print("3. Testing database client...")
    try:
        from cultural_database_client import CulturalDatabaseClient
        db_client = CulturalDatabaseClient()
        print("   ✅ Database client imported and initialized")
    except Exception as db_e:
        print(f"   ❌ Database client error: {db_e}")
    
    print("4. Testing enhanced dashboard import...")
    try:
        sys.path.insert(0, '.')
        import enhanced_cultural_dashboard
        print("   ✅ Enhanced dashboard imported successfully")
    except ImportError as imp_e:
        print(f"   ❌ Import error: {imp_e}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()

    print("5. Testing Flask app creation...")
    try:
        from flask import Flask
        test_app = Flask(__name__)
        print("   ✅ Flask app creation works")
    except Exception as flask_e:
        print(f"   ❌ Flask app error: {flask_e}")

    print("\n🎯 DIAGNOSTIC COMPLETE")
    print("If all checks pass, try running: python enhanced_cultural_dashboard.py")
    
except Exception as main_e:
    print(f"❌ CRITICAL ERROR: {main_e}")
    import traceback
    traceback.print_exc()