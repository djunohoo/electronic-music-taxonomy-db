#!/usr/bin/env python3
"""
Cultural Intelligence System v3.2 - Production Launcher
======================================================

Complete system orchestration for electronic music taxonomy and MetaCrate integration.
Manages database initialization, scanning operations, API service, and web dashboard.
"""

import os
import sys
import json
import time
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from taxonomy_v32 import TaxonomyConfig, DatabaseSchema
    from taxonomy_scanner import TaxonomyScanner
    from metacrate_api import app, MetaCrateAPI
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Ensure all required files are present:")
    print("   - taxonomy_v32.py")
    print("   - taxonomy_scanner.py") 
    print("   - metacrate_api.py")
    sys.exit(1)

class CulturalIntelligenceSystem:
    """Main orchestration class for the complete system"""
    
    def __init__(self):
        self.config = TaxonomyConfig()
        self.api_thread = None
        self.scanner = None
        self.start_time = datetime.now()
        
        # Production settings
        self.production_mode = self.config.get('production.enabled', False)
        self.auto_start_api = self.config.get('api.auto_start', True)
        self.auto_open_dashboard = self.config.get('dashboard.auto_open', True)
        
        print("🎵 CULTURAL INTELLIGENCE SYSTEM v3.2")
        print("=" * 50)
        print("🚀 Electronic Music Taxonomy Database")
        print("🔗 MetaCrate Integration Ready")
        print("=" * 50)
    
    def initialize_system(self) -> bool:
        """Initialize complete system components"""
        try:
            print("🔧 Initializing system components...")
            
            # 1. Verify configuration
            if not self._verify_configuration():
                return False
            
            # 2. Initialize database schema (if using Supabase)
            if self.production_mode:
                if not self._initialize_database():
                    print("⚠️  Database initialization failed, continuing in development mode")
            
            # 3. Initialize scanner
            self.scanner = TaxonomyScanner(self.config)
            print("✅ Scanner initialized")
            
            # 4. Load existing data if available
            self._load_existing_data()
            
            print("✅ System initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    def _verify_configuration(self) -> bool:
        """Verify system configuration"""
        required_paths = [
            'taxonomy_v32.py',
            'taxonomy_scanner.py',
            'metacrate_api.py'
        ]
        
        for path in required_paths:
            if not os.path.exists(path):
                print(f"❌ Required file missing: {path}")
                return False
        
        print("✅ Configuration verified")
        return True
    
    def _initialize_database(self) -> bool:
        """Initialize production database"""
        try:
            # In production, would execute database schema
            db_schema = DatabaseSchema()
            print("✅ Database schema ready for production")
            return True
        except Exception as e:
            print(f"⚠️  Database initialization error: {e}")
            return False
    
    def _load_existing_data(self):
        """Load any existing scan results"""
        try:
            # Look for recent scan files
            scan_files = [f for f in os.listdir('.') if f.startswith('taxonomy_scan_') and f.endswith('.json')]
            if scan_files:
                latest_scan = max(scan_files, key=os.path.getctime)
                print(f"📊 Found existing scan data: {latest_scan}")
            else:
                print("📊 No existing scan data found")
        except Exception as e:
            print(f"⚠️  Error loading existing data: {e}")
    
    def start_api_service(self, background: bool = True) -> bool:
        """Start MetaCrate API service"""
        try:
            if background:
                print("🌐 Starting API service in background...")
                self.api_thread = threading.Thread(
                    target=self._run_api_service,
                    daemon=True
                )
                self.api_thread.start()
                
                # Give API time to start
                time.sleep(2)
                
                # Test API health
                if self._test_api_health():
                    print("✅ API service started successfully!")
                    return True
                else:
                    print("❌ API service failed to start properly")
                    return False
            else:
                print("🌐 Starting API service (foreground)...")
                self._run_api_service()
                return True
                
        except Exception as e:
            print(f"❌ Failed to start API service: {e}")
            return False
    
    def _run_api_service(self):
        """Run the Flask API service"""
        host = self.config.get('api.host', '0.0.0.0')
        port = self.config.get('api.port', 5000)
        debug = self.config.get('api.debug', False)
        
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    
    def _test_api_health(self) -> bool:
        """Test if API service is responding"""
        try:
            import requests
            
            host = self.config.get('api.host', 'localhost')
            port = self.config.get('api.port', 5000)
            
            response = requests.get(f"http://{host}:{port}/api/v3.2/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def open_dashboard(self):
        """Open web dashboard"""
        try:
            dashboard_path = Path('dashboard.html').absolute()
            if dashboard_path.exists():
                dashboard_url = f"file:///{dashboard_path}"
                print(f"🌐 Opening dashboard: {dashboard_url}")
                webbrowser.open(dashboard_url)
                return True
            else:
                print("❌ Dashboard file not found")
                return False
        except Exception as e:
            print(f"⚠️  Could not open dashboard: {e}")
            return False
    
    def run_collection_scan(self, scan_path: str, output_file: str = None) -> Dict:
        """Run complete collection scan"""
        print(f"\n📂 SCANNING COLLECTION: {scan_path}")
        print("=" * 50)
        
        if not os.path.exists(scan_path):
            print(f"❌ Scan path does not exist: {scan_path}")
            return {"status": "error", "error": "Path not found"}
        
        try:
            # Run scan
            results = self.scanner.scan_collection(scan_path)
            
            # Save results
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"taxonomy_scan_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Print summary
            print(f"\n📊 SCAN COMPLETE")
            print(f"Files processed: {results.get('total_files', 0)}")
            print(f"Duplicates found: {len(results.get('duplicate_groups', []))}")
            print(f"Classifications: {len(results.get('classifications', []))}")
            print(f"Results saved: {output_file}")
            
            return results
            
        except Exception as e:
            print(f"❌ Scan failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def interactive_mode(self):
        """Interactive command-line interface"""
        print("\n🎛️  INTERACTIVE MODE")
        print("Available commands:")
        print("  scan <path>     - Scan music collection")
        print("  api start       - Start API service")
        print("  api stop        - Stop API service") 
        print("  dashboard       - Open web dashboard")
        print("  status          - Show system status")
        print("  config          - Show configuration")
        print("  exit            - Exit system")
        print()
        
        while True:
            try:
                command = input("🎵 CIS> ").strip().lower()
                
                if command == "exit":
                    print("👋 Goodbye!")
                    break
                elif command.startswith("scan "):
                    path = command[5:].strip()
                    self.run_collection_scan(path)
                elif command == "api start":
                    self.start_api_service(background=True)
                elif command == "dashboard":
                    self.open_dashboard()
                elif command == "status":
                    self.show_status()
                elif command == "config":
                    self.show_configuration()
                elif command == "help":
                    print("📖 Help: Use commands like 'scan C:\\Music' or 'dashboard'")
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_status(self):
        """Show system status"""
        uptime = datetime.now() - self.start_time
        
        print(f"\n📊 SYSTEM STATUS")
        print(f"Uptime: {uptime}")
        print(f"Scanner ready: {'✅' if self.scanner else '❌'}")
        print(f"API running: {'✅' if self.api_thread and self.api_thread.is_alive() else '❌'}")
        print(f"Production mode: {'✅' if self.production_mode else '🔧'}")
    
    def show_configuration(self):
        """Show current configuration"""
        print(f"\n⚙️  CONFIGURATION")
        print(f"API Host: {self.config.get('api.host', 'localhost')}")
        print(f"API Port: {self.config.get('api.port', 5000)}")
        print(f"Production: {self.production_mode}")
        print(f"Auto-start API: {self.auto_start_api}")
        print(f"Auto-open dashboard: {self.auto_open_dashboard}")

def main():
    """Main entry point with command-line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Cultural Intelligence System v3.2 - Electronic Music Taxonomy"
    )
    
    parser.add_argument('--scan', type=str, help='Scan music collection at path')
    parser.add_argument('--api', action='store_true', help='Start API service only')
    parser.add_argument('--dashboard', action='store_true', help='Open dashboard only')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--output', type=str, help='Output file for scan results')
    parser.add_argument('--no-api', action='store_true', help='Skip API service startup')
    parser.add_argument('--no-dashboard', action='store_true', help='Skip dashboard opening')
    
    args = parser.parse_args()
    
    # Create system instance
    cis = CulturalIntelligenceSystem()
    
    # Initialize system
    if not cis.initialize_system():
        print("❌ System initialization failed!")
        sys.exit(1)
    
    # Handle command-line arguments
    if args.scan:
        # Scan mode
        if not args.no_api and cis.auto_start_api:
            cis.start_api_service(background=True)
        
        results = cis.run_collection_scan(args.scan, args.output)
        
        if not args.no_dashboard and cis.auto_open_dashboard:
            cis.open_dashboard()
        
        print(f"\n🎯 Scan completed! API available for MetaCrate integration.")
        
    elif args.api:
        # API only mode
        cis.start_api_service(background=False)
        
    elif args.dashboard:
        # Dashboard only mode
        cis.open_dashboard()
        input("Press Enter to exit...")
        
    elif args.interactive:
        # Interactive mode
        if not args.no_api and cis.auto_start_api:
            cis.start_api_service(background=True)
            
        if not args.no_dashboard and cis.auto_open_dashboard:
            cis.open_dashboard()
            
        cis.interactive_mode()
        
    else:
        # Default: Full system startup
        print("\n🚀 FULL SYSTEM STARTUP")
        
        # Start API service
        if not args.no_api and cis.auto_start_api:
            if cis.start_api_service(background=True):
                api_url = f"http://{cis.config.get('api.host', 'localhost')}:{cis.config.get('api.port', 5000)}"
                print(f"🌐 API available at: {api_url}/api/v3.2/health")
        
        # Open dashboard
        if not args.no_dashboard and cis.auto_open_dashboard:
            cis.open_dashboard()
        
        # Show next steps
        print(f"\n🎯 READY FOR OPERATION!")
        print(f"Next steps:")
        print(f"  1. Scan collection: python {sys.argv[0]} --scan \"C:\\Your\\Music\\Path\"")
        print(f"  2. Test API: Visit dashboard or use MetaCrate integration")
        print(f"  3. Interactive mode: python {sys.argv[0]} --interactive")
        print(f"\n🔗 MetaCrate Integration:")
        print(f"   API Base URL: http://localhost:{cis.config.get('api.port', 5000)}/api/v3.2")
        print(f"   Health Check: /health")
        print(f"   File Analysis: /file/analyze (POST)")
        print(f"   Hash Lookup: /file/hash/{{hash}} (GET)")
        
        # Keep alive
        try:
            input("\nPress Enter to exit...")
        except KeyboardInterrupt:
            print("\n👋 Shutdown complete!")

if __name__ == "__main__":
    main()