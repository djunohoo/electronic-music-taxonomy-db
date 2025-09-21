"""
Run the Electronic Music Taxonomy Database web application.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.web.app import app
    print("Successfully imported app")
    print("Starting Electronic Music Taxonomy Database...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)