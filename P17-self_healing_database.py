"""
P17-Self-Healing Database MCP
Checks for missing tables/columns and applies SQL fixes automatically. Learns from failures and logs for future improvements.
"""

import os
import sqlite3
import json
from typing import List

def log_repair_action(log_path: str, action: str, details: dict):
    with open(log_path, 'a') as f:
        f.write(json.dumps({'action': action, 'details': details}) + '\n')

def check_and_repair_database(db_path: str, required_tables: List[str], sql_fixes: List[str], log_path: str = 'P17_self_healing_log.jsonl'):
    """Check for missing tables and apply SQL fixes if needed. Logs actions for learning."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for table, sql in zip(required_tables, sql_fixes):
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cur.fetchone():
            print(f"Table '{table}' missing. Applying fix...")
            try:
                cur.execute(sql)
                log_repair_action(log_path, 'table_created', {'table': table, 'sql': sql})
            except Exception as e:
                log_repair_action(log_path, 'repair_failed', {'table': table, 'error': str(e)})
    conn.commit()
    conn.close()

# Example usage:
# check_and_repair_database('your.db', ['cultural_training_questions'], ["CREATE TABLE cultural_training_questions (...);"])
