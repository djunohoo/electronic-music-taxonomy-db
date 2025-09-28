#!/usr/bin/env python3
"""
Quick test script for MetaCrate API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metacrate_api import app

if __name__ == "__main__":
    print("🧪 Testing MetaCrate API...")
    print("🌐 Starting on http://localhost:5000")
    print("🔗 Test endpoints:")
    print("   http://localhost:5000/api/v3.2/health")
    print("   http://localhost:5000/api/v3.2/stats")
    
    app.run(host='localhost', port=5000, debug=True)