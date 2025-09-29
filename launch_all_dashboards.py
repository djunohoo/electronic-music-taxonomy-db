#!/usr/bin/env python3
"""
LAUNCH ALL DASHBOARDS - Find Your Perfect One!
=============================================
Launches multiple dashboard versions on different ports so you can find the right one.
Never compromise on your ambition - we'll run them ALL!
"""

import subprocess
import time
import threading
import sys
from pathlib import Path

# Dashboard configurations
DASHBOARDS = [
    {
        'name': '🎛️ Enhanced Cultural Dashboard (Fixed)',
        'file': 'enhanced_cultural_dashboard_fixed.py',
        'port': 8081,
        'description': 'Main production dashboard with real-time intelligence'
    },
    {
        'name': '🎯 Enhanced Cultural Dashboard',
        'file': 'enhanced_cultural_dashboard.py', 
        'port': 8082,
        'description': 'Original enhanced version with full features'
    },
    {
        'name': '🎪 Cultural Dashboard (Core)',
        'file': 'cultural_dashboard.py',
        'port': 8083,
        'description': 'Core cultural intelligence dashboard'
    },
    {
        'name': '🚀 Working Enhanced Dashboard',
        'file': 'working_enhanced_dashboard.py',
        'port': 8084,
        'description': 'Proven working enhanced version'
    },
    {
        'name': '⚡ Simple Dashboard',
        'file': 'simple_dashboard.py',
        'port': 8085,
        'description': 'Lightweight fast dashboard'
    },
    {
        'name': '🛡️ Safe Dashboard Test',
        'file': 'safe_dashboard_test.py',
        'port': 8086,
        'description': 'Safe testing dashboard'
    },
    {
        'name': '🔧 Quick Fix Dashboard',
        'file': 'quick_fix_dashboard.py',
        'port': 8087,
        'description': 'Quick fix implementation'
    }
]

def modify_dashboard_port(file_path, target_port):
    """Modify dashboard file to run on specific port"""
    
    if not Path(file_path).exists():
        print(f"⚠️ File not found: {file_path}")
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find and replace port configurations
        modified = False
        
        # Common port patterns
        port_patterns = [
            ('port=8081', f'port={target_port}'),
            ('port=5000', f'port={target_port}'),
            (':8081', f':{target_port}'),
            (':5000', f':{target_port}'),
            ('8081', str(target_port)),
            ('5000', str(target_port))
        ]
        
        for old_pattern, new_pattern in port_patterns:
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                modified = True
                
        if modified:
            # Create modified version
            modified_file = file_path.replace('.py', f'_port{target_port}.py')
            with open(modified_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return modified_file
        else:
            return file_path
            
    except Exception as e:
        print(f"❌ Error modifying {file_path}: {e}")
        return False

def launch_dashboard(dashboard_config):
    """Launch a single dashboard"""
    
    print(f"\n🚀 Launching {dashboard_config['name']} on port {dashboard_config['port']}")
    
    # Modify file for correct port
    original_file = dashboard_config['file']
    target_port = dashboard_config['port']
    
    modified_file = modify_dashboard_port(original_file, target_port)
    
    if not modified_file:
        print(f"❌ Failed to prepare {original_file}")
        return None
        
    try:
        # Launch dashboard
        process = subprocess.Popen(
            [sys.executable, modified_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path.cwd()
        )
        
        print(f"✅ {dashboard_config['name']} launched!")
        print(f"🌐 URL: http://172.22.17.37:{target_port}")
        print(f"📝 Description: {dashboard_config['description']}")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to launch {original_file}: {e}")
        return None

def main():
    """Launch all dashboards"""
    
    print("🎛️ LAUNCHING ALL DASHBOARDS - FIND YOUR PERFECT ONE!")
    print("=" * 70)
    print("Your ambition knows no bounds - we're launching EVERYTHING!")
    print()
    
    processes = []
    successful_launches = []
    
    for dashboard in DASHBOARDS:
        process = launch_dashboard(dashboard)
        if process:
            processes.append(process)
            successful_launches.append(dashboard)
            time.sleep(2)  # Stagger launches
    
    print(f"\n🎉 DASHBOARD LAUNCH COMPLETE!")
    print(f"✅ Successfully launched {len(successful_launches)} dashboards")
    print("\n📋 DASHBOARD DIRECTORY:")
    print("-" * 50)
    
    for dashboard in successful_launches:
        print(f"🌐 {dashboard['name']}")
        print(f"   URL: http://172.22.17.37:{dashboard['port']}")
        print(f"   Description: {dashboard['description']}")
        print()
    
    print("🎯 Try each URL to find your perfect dashboard!")
    print("🔥 Your Cultural Intelligence System deserves the BEST interface!")
    
    try:
        print("\n⏸️ Press Ctrl+C to stop all dashboards...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all dashboards...")
        
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
                
        print("✅ All dashboards stopped")

if __name__ == "__main__":
    main()