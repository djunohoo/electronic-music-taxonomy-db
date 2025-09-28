#!/usr/bin/env python3
"""
SIMPLE API LAUNCHER
==================
Just run the metacrate_api.py directly but with output suppressed
"""

import os
import sys

# Set encoding to avoid Unicode issues
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("Cultural Intelligence API Starting...")
print("Will bind to: 172.22.17.37:5000")
print("Press Ctrl+C to stop")
print("-" * 40)

# Just run the API file directly
if __name__ == "__main__":
    try:
        exec(open('metacrate_api.py').read())
    except KeyboardInterrupt:
        print("\nAPI stopped by user")
    except Exception as e:
        print(f"Error: {e}")