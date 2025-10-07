#!/usr/bin/env python3
"""
Security Migration Helper
=========================
This script helps identify files that may contain hardcoded credentials or IP addresses.
Run this to audit your codebase for security issues.

Usage:
    python security_audit.py
"""

import os
import re
from pathlib import Path

def find_security_issues(root_dir="."):
    """Find potential security issues in the codebase."""
    
    # Patterns to search for
    patterns = {
        "IP Addresses": r'\b(?:172\.22\.17\.\d+|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)\b',
        "Passwords": r'(?i)(password\s*=\s*["\'][^"\']+["\'])',
        "Database URLs": r'postgresql://[^:]+:[^@]+@[^/]+',
        "API Keys": r'(?i)(api[_-]?key\s*=\s*["\'][^"\']+["\'])',
    }
    
    issues_found = []
    
    # File types to check
    extensions = ['.py', '.sh', '.sql', '.md', '.js', '.json', '.yaml', '.yml']
    
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for issue_type, pattern in patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Get line number
                            line_num = content[:match.start()].count('\n') + 1
                            issues_found.append({
                                'file': file_path,
                                'line': line_num,
                                'type': issue_type,
                                'content': match.group(0)
                            })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return issues_found

def main():
    print("🔍 Security Audit - Scanning for hardcoded credentials and IP addresses...")
    print("=" * 70)
    
    issues = find_security_issues()
    
    if not issues:
        print("✅ No obvious security issues found!")
        return
    
    print(f"⚠️  Found {len(issues)} potential security issues:\n")
    
    # Group by file
    by_file = {}
    for issue in issues:
        file = issue['file']
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(issue)
    
    for file, file_issues in sorted(by_file.items()):
        print(f"\n📄 {file}")
        for issue in file_issues:
            print(f"   Line {issue['line']}: {issue['type']}")
            # Don't print the actual content for security reasons
            if issue['type'] == 'IP Addresses':
                print(f"   Found: {issue['content']}")
    
    print("\n" + "=" * 70)
    print("\n📋 Next Steps:")
    print("1. Review the files listed above")
    print("2. Replace hardcoded values with environment variables")
    print("3. Update your .env file with actual values")
    print("4. Ensure .env is in .gitignore")
    print("5. Rotate any exposed credentials")
    print("\nSee SECURITY.md for detailed guidance.")

if __name__ == "__main__":
    main()
