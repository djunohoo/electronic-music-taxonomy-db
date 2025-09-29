"""
P17-Automated Data Import MCP
Watches a folder for new data files, imports them into the database, and logs import history for learning.
"""
"""
P17-Automated Data Import MCP
Watches a folder for new data files, imports them into the database, and logs import history for learning.
"""

import os
import time
import sqlite3
import json

def log_import(log_path: str, filename: str, status: str, details: dict = None):
    with open(log_path, 'a') as f:
        f.write(json.dumps({'file': filename, 'status': status, 'details': details}) + '\n')

def watch_and_import(folder: str, db_path: str, import_func, log_path: str = 'P17_data_import_log.jsonl'):
    seen = set()
    while True:
        for fname in os.listdir(folder):
            if fname not in seen and fname.endswith('.csv'):
                print(f"Importing {fname}...")
                try:
                    import_func(os.path.join(folder, fname), db_path)
                    log_import(log_path, fname, 'success')
                except Exception as e:
                    log_import(log_path, fname, 'fail', {'error': str(e)})
                seen.add(fname)
        time.sleep(10)

# Define your import_func to handle CSV to DB logic.
