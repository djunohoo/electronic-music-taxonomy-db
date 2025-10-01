#!/usr/bin/env python3
"""
MetaCrate Multi-User Setup and Launcher
Quick setup script for MetaCrate multi-user operations.

This script helps you:
1. Install required dependencies
2. Configure multiple users
3. Launch the dashboard or CLI controller
4. Test the multi-user system
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    dependencies = [
        'fastapi',
        'uvicorn[standard]',
        'websockets',
        'pydantic'
    ]
    
    print("📦 Installing dependencies...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {dep}")
    
    print("✅ Dependencies installation complete!")

def check_metacrate_directory():
    """Check if MetaCrate USERS directory exists"""
    metacrate_path = r"X:\\lightbulb networ IUL Dropbox\\Automation\\MetaCrate\\USERS"
    
    if os.path.exists(metacrate_path):
        users = [d for d in os.listdir(metacrate_path) if os.path.isdir(os.path.join(metacrate_path, d))]
        print(f"✅ MetaCrate USERS directory found with {len(users)} users: {', '.join(users)}")
        return True
    else:
        print(f"❌ MetaCrate USERS directory not found at: {metacrate_path}")
        print("   Please ensure the directory exists and is accessible")
        return False

def create_example_config():
    """Create example configuration file"""
    config = {
        "multi_user_settings": {
            "max_concurrent_users": 3,
            "default_batch_size": 250,
            "default_interval_minutes": 15
        },
        "user_configs": {
            "DJUNOHOO": {
                "enabled": True,
                "batch_size": 100,
                "interval_minutes": 10,
                "priority": 8,
                "twitch_notifications": True
            },
            "EXAMPLE_USER": {
                "enabled": False,
                "batch_size": 250,
                "interval_minutes": 15,
                "priority": 5,
                "twitch_notifications": False
            }
        },
        "twitch_config": {
            "enabled": False,
            "username": "your_bot_username",
            "oauth_token": "oauth:your_token_here",
            "channel": "your_channel"
        }
    }
    
    config_file = Path("metacrate_multiuser_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📝 Created example config file: {config_file}")

def launch_dashboard():
    """Launch the web dashboard"""
    print("🚀 Launching MetaCrate Multi-User Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8082")
    
    try:
        subprocess.run([sys.executable, 'metacrate_multiuser_dashboard.py'])
    except KeyboardInterrupt:
        print("\\n🛑 Dashboard stopped")

def launch_cli():
    """Launch the CLI controller"""
    print("🚀 Launching MetaCrate Multi-User CLI Controller...")
    
    try:
        subprocess.run([sys.executable, 'metacrate_user_controller.py', '--interactive'])
    except KeyboardInterrupt:
        print("\\n🛑 CLI controller stopped")

def test_system():
    """Test the multi-user system"""
    print("🧪 Testing MetaCrate Multi-User System...")
    
    try:
        from metacrate_multiuser_orchestrator_v1_8 import MetaCrateMultiUserOrchestrator
        
        # Create orchestrator
        orchestrator = MetaCrateMultiUserOrchestrator(max_concurrent_users=2)
        
        print(f"✅ Orchestrator created successfully")
        print(f"📊 Discovered {len(orchestrator.user_configs)} users:")
        
        for username, config in orchestrator.user_configs.items():
            status = "✅ ENABLED" if config.enabled else "❌ DISABLED"
            print(f"   {username:15} | {status} | Batch: {config.batch_size} | Interval: {config.interval_minutes}m")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_help():
    """Show available commands"""
    print("""
🎵 MetaCrate Multi-User Setup and Launcher

Available commands:
  install      - Install required dependencies
  check        - Check MetaCrate directory structure
  config       - Create example configuration file
  test         - Test the multi-user system
  dashboard    - Launch web dashboard (http://localhost:8082)
  cli          - Launch CLI controller (interactive mode)
  help         - Show this help message

Quick Start:
  1. python setup_metacrate_multiuser.py install
  2. python setup_metacrate_multiuser.py check
  3. python setup_metacrate_multiuser.py dashboard

Examples:
  python setup_metacrate_multiuser.py install
  python setup_metacrate_multiuser.py dashboard
  python setup_metacrate_multiuser.py cli
    """)

def main():
    """Main setup script"""
    print("🎵 MetaCrate Multi-User Setup v1.8")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'install':
        install_dependencies()
    
    elif command == 'check':
        check_metacrate_directory()
    
    elif command == 'config':
        create_example_config()
    
    elif command == 'test':
        if test_system():
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
    
    elif command == 'dashboard':
        if not check_metacrate_directory():
            print("❌ Cannot launch dashboard without MetaCrate directory")
            return
        launch_dashboard()
    
    elif command == 'cli':
        if not check_metacrate_directory():
            print("❌ Cannot launch CLI without MetaCrate directory")
            return
        launch_cli()
    
    elif command == 'help':
        show_help()
    
    else:
        print(f"❓ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()