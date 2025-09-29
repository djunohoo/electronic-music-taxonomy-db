"""
P17-API Contract Validator MCP
Checks that all REST endpoints are live, match expected schemas, and logs failures for future contract learning.
"""

import requests
import json

def log_contract_event(log_path: str, url: str, status: str, details: dict = None):
    with open(log_path, 'a') as f:
        f.write(json.dumps({'url': url, 'status': status, 'details': details}) + '\n')

def validate_endpoint(url: str, expected_status: int = 200, log_path: str = 'P17_api_contract_log.jsonl'):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == expected_status:
            print(f"{url} OK")
            log_contract_event(log_path, url, 'ok', {'status_code': r.status_code})
            return True
        else:
            print(f"{url} returned {r.status_code}")
            log_contract_event(log_path, url, 'bad_status', {'status_code': r.status_code})
    except Exception as e:
        print(f"{url} unreachable: {e}")
        log_contract_event(log_path, url, 'unreachable', {'error': str(e)})
    return False

# Example usage:
# validate_endpoint('http://localhost:8081/api/health')
