#!/usr/bin/env python3
"""
CULTURAL INTELLIGENCE SYSTEM v1.7 - Batch Processing & Twitch Integration
=========================================================================
Enhanced batch processing system with Twitch chat integration, version tracking,
and advanced pattern analysis. Processes collections in 250-file batches,
reports to Twitch, and continuously learns from accumulated data.

New v1.7 Features:
- Batch processing with 250-file chunks
- Twitch chat integration for live reporting
- Version tracking and scan history
- Advanced pattern probability analysis
- Incremental learning system
- Progress persistence between scans
"""

import os
import sys
import json
import time
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

# Import existing components
try:
    from cultural_intelligence_scanner import CulturalIntelligenceScanner
    from cultural_database_client import CulturalDatabaseClient
    from comprehensive_intelligence_scan import ComprehensiveIntelligenceScan
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("Using fallback implementations")
    CulturalIntelligenceScanner = None
    CulturalDatabaseClient = None
    ComprehensiveIntelligenceScan = None

# Twitch integration
try:
    import websocket
    import threading
    TWITCH_AVAILABLE = True
except ImportError:
    print("Installing Twitch integration dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websocket-client"])
    import websocket
    import threading
    TWITCH_AVAILABLE = True

# Version information
VERSION = "1.7.0"
VERSION_DATE = "2025-09-29"
BATCH_SIZE = 250

@dataclass
class ScanSession:
    """Represents a batch scan session with version tracking"""
    session_id: str
    version: str
    batch_number: int
    start_time: datetime
    end_time: Optional[datetime]
    files_processed: int
    success_rate: float
    patterns_learned: int
    new_artists: int
    duplicates_found: int
    intelligence_score: float
    status: str  # 'running', 'completed', 'failed'

class TwitchChatIntegration:
    """Handles Twitch chat integration for live reporting"""
    
    def __init__(self, channel: str, oauth_token: str = None):
        self.channel = channel.lower()
        self.oauth_token = oauth_token
        self.ws = None
        self.connected = False
        
        # Use environment variables if no token provided
        if not oauth_token:
            self.oauth_token = os.getenv('TWITCH_OAUTH_TOKEN')
            
        if not self.oauth_token:
            print("⚠️ No Twitch OAuth token provided. Chat integration disabled.")
            print("Set TWITCH_OAUTH_TOKEN environment variable or pass token directly.")
            
    def connect(self):
        """Connect to Twitch IRC"""
        if not self.oauth_token:
            return False
            
        try:
            self.ws = websocket.WebSocketApp("wss://irc-ws.chat.twitch.tv:443",
                                           on_open=self._on_open,
                                           on_message=self._on_message,
                                           on_error=self._on_error,
                                           on_close=self._on_close)
            
            # Run in separate thread
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # Wait for connection
            time.sleep(2)
            return self.connected
            
        except Exception as e:
            print(f"❌ Twitch connection failed: {e}")
            return False
            
    def _on_open(self, ws):
        """Handle WebSocket open"""
        print("🔗 Connected to Twitch IRC")
        
        # Send authentication
        ws.send("CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands")
        ws.send(f"PASS {self.oauth_token}")
        ws.send("NICK culturalai_scanner")
        ws.send(f"JOIN #{self.channel}")
        
        self.connected = True
        
    def _on_message(self, ws, message):
        """Handle incoming messages"""
        if message.startswith("PING"):
            ws.send("PONG :tmi.twitch.tv")
            
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"❌ Twitch WebSocket error: {error}")
        
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print("🔌 Twitch connection closed")
        self.connected = False
        
    def send_message(self, message: str):
        """Send message to Twitch chat"""
        if not self.connected or not self.ws:
            print(f"📢 [CHAT DISABLED] {message}")
            return False
            
        try:
            formatted_msg = f"PRIVMSG #{self.channel} :{message}"
            self.ws.send(formatted_msg)
            print(f"📢 [TWITCH] {message}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send Twitch message: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from Twitch"""
        if self.ws:
            self.ws.close()
            self.connected = False

class VersionedScanDatabase:
    """Database for tracking scan sessions and versions"""
    
    def __init__(self, db_path: str = "cultural_intelligence_v17.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize versioned scan database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Scan sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_sessions (
                session_id TEXT PRIMARY KEY,
                version TEXT NOT NULL,
                batch_number INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                files_processed INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                patterns_learned INTEGER DEFAULT 0,
                new_artists INTEGER DEFAULT 0,
                duplicates_found INTEGER DEFAULT 0,
                intelligence_score REAL DEFAULT 0.0,
                status TEXT DEFAULT 'running',
                scan_results TEXT
            )
        ''')
        
        # File processing history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                session_id TEXT NOT NULL,
                version TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                intelligence_score REAL,
                classification_confidence REAL,
                patterns_detected TEXT,
                FOREIGN KEY (session_id) REFERENCES scan_sessions (session_id)
            )
        ''')
        
        # Pattern evolution tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_key TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                weight_value REAL NOT NULL,
                confidence_level REAL,
                session_id TEXT NOT NULL,
                version TEXT NOT NULL,
                learned_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES scan_sessions (session_id)
            )
        ''')
        
        # Version upgrades log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS version_upgrades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_version TEXT,
                to_version TEXT,
                upgrade_date TEXT NOT NULL,
                files_requiring_rescan INTEGER DEFAULT 0,
                upgrade_notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def create_scan_session(self, batch_number: int) -> str:
        """Create new scan session"""
        session_id = f"v{VERSION}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_batch{batch_number}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scan_sessions 
            (session_id, version, batch_number, start_time, status)
            VALUES (?, ?, ?, ?, 'running')
        ''', (session_id, VERSION, batch_number, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return session_id
        
    def update_scan_session(self, session_id: str, updates: Dict):
        """Update scan session with results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'scan_results' and isinstance(value, dict):
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            values.append(value)
            
        values.append(session_id)
        
        query = f"UPDATE scan_sessions SET {', '.join(set_clauses)} WHERE session_id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
    def mark_file_processed(self, file_path: str, file_hash: str, session_id: str, 
                          intelligence_score: float, classification_confidence: float,
                          patterns: List[str]):
        """Mark file as processed with version tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO file_history 
            (file_path, file_hash, session_id, version, processed_at, 
             intelligence_score, classification_confidence, patterns_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_path, file_hash, session_id, VERSION, datetime.now().isoformat(),
              intelligence_score, classification_confidence, json.dumps(patterns)))
        
        conn.commit()
        conn.close()
        
    def get_processed_files(self, version: str = None) -> List[Dict]:
        """Get list of processed files, optionally filtered by version"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if version:
            cursor.execute('''
                SELECT file_path, file_hash, version, processed_at, intelligence_score
                FROM file_history WHERE version = ?
                ORDER BY processed_at DESC
            ''', (version,))
        else:
            cursor.execute('''
                SELECT file_path, file_hash, version, processed_at, intelligence_score
                FROM file_history ORDER BY processed_at DESC
            ''')
            
        results = []
        for row in cursor.fetchall():
            results.append({
                'file_path': row[0],
                'file_hash': row[1],
                'version': row[2],
                'processed_at': row[3],
                'intelligence_score': row[4]
            })
            
        conn.close()
        return results
        
    def save_pattern_evolution(self, patterns: Dict, session_id: str):
        """Save pattern weights for evolution tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern_key, weight in patterns.items():
            pattern_type = pattern_key.split(':')[0] if ':' in pattern_key else 'unknown'
            
            cursor.execute('''
                INSERT INTO pattern_evolution 
                (pattern_key, pattern_type, weight_value, session_id, version, learned_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pattern_key, pattern_type, weight, session_id, VERSION, datetime.now().isoformat()))
            
        conn.commit()
        conn.close()

class CulturalIntelligenceV17:
    """Enhanced Cultural Intelligence System v1.7 with batch processing and Twitch integration"""
    
    def __init__(self, twitch_channel: str = None, twitch_oauth: str = None):
        self.version = VERSION
        self.batch_size = BATCH_SIZE
        
        # Initialize components with fallbacks
        if ComprehensiveIntelligenceScan:
            self.scanner = ComprehensiveIntelligenceScan(".")
        else:
            print("⚠️ Using fallback scanner implementation")
            self.scanner = self._create_fallback_scanner()
            
        self.db = VersionedScanDatabase()
        self.twitch = TwitchChatIntegration(twitch_channel, twitch_oauth) if twitch_channel else None
        
        # Dashboard integration
        self.dashboard_url = "http://172.22.17.37:8081"
        self.dashboard_running = self._check_dashboard_status()
        
        # Pattern analysis
        self.accumulated_patterns = defaultdict(float)
        self.pattern_confidence = defaultdict(list)
        self.cross_pattern_correlations = defaultdict(lambda: defaultdict(int))
        
        print(f"🧠 Cultural Intelligence System v{VERSION} initialized")
        print(f"📦 Batch size: {self.batch_size} files")
        print(f"📅 Version date: {VERSION_DATE}")
        
        if self.twitch:
            print(f"📺 Twitch integration: Enabled ({twitch_channel})")
        else:
            print("📺 Twitch integration: Disabled")
            
    def connect_twitch(self) -> bool:
        """Connect to Twitch chat"""
        if self.twitch:
            success = self.twitch.connect()
            if success:
                self.twitch.send_message(f"🧠 Cultural Intelligence v{VERSION} is now online! Ready to analyze music collections.")
            return success
        return False
        
    def disconnect_twitch(self):
        """Disconnect from Twitch"""
        if self.twitch:
            self.twitch.send_message(f"📊 Cultural Intelligence v{VERSION} scan complete. See you next time!")
            self.twitch.disconnect()
            
    def get_unprocessed_files(self, music_directory: str) -> List[str]:
        """Get files that haven't been processed in current version"""
        
        # Get all audio files
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}
        all_files = []
        
        music_path = Path(music_directory)
        for file_path in music_path.rglob('*'):
            if file_path.suffix.lower() in audio_extensions:
                all_files.append(str(file_path))
                
        # Get already processed files
        processed_files = self.db.get_processed_files(VERSION)
        processed_paths = {f['file_path'] for f in processed_files}
        
        # Return unprocessed files
        unprocessed = [f for f in all_files if f not in processed_paths]
        
        return unprocessed
        
    def analyze_accumulated_patterns(self) -> Dict[str, Any]:
        """Analyze all accumulated pattern data for new insights"""
        
        print("🔍 Analyzing accumulated pattern intelligence...")
        
        # Load all historical patterns
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_key, pattern_type, weight_value, confidence_level, session_id, version
            FROM pattern_evolution ORDER BY learned_at ASC
        ''')
        
        pattern_history = []
        for row in cursor.fetchall():
            pattern_history.append({
                'pattern_key': row[0],
                'pattern_type': row[1],
                'weight_value': row[2],
                'confidence_level': row[3],
                'session_id': row[4],
                'version': row[5]
            })
            
        conn.close()
        
        analysis = {
            'total_patterns': len(pattern_history),
            'pattern_evolution': {},
            'cross_correlations': {},
            'confidence_trends': {},
            'version_improvements': {},
            'predictive_weights': {}
        }
        
        # Analyze pattern evolution over time
        pattern_evolution = defaultdict(list)
        for entry in pattern_history:
            pattern_evolution[entry['pattern_key']].append({
                'weight': entry['weight_value'],
                'version': entry['version'],
                'session': entry['session_id']
            })
            
        # Calculate growth rates and confidence trends
        for pattern_key, evolution in pattern_evolution.items():
            if len(evolution) > 1:
                weights = [e['weight'] for e in evolution]
                growth_rate = (weights[-1] - weights[0]) / len(weights)
                analysis['pattern_evolution'][pattern_key] = {
                    'growth_rate': growth_rate,
                    'current_weight': weights[-1],
                    'stability': 1.0 - (max(weights) - min(weights)) / max(weights, 0.001),
                    'sessions_reinforced': len(evolution)
                }
                
        # Identify cross-pattern correlations
        filename_patterns = [p for p in pattern_evolution.keys() if p.startswith('filename:')]
        folder_patterns = [p for p in pattern_evolution.keys() if p.startswith('folder:')]
        
        for fp in filename_patterns:
            for fop in folder_patterns:
                genre_fp = fp.split(':')[-1]
                genre_fop = fop.split(':')[-1]
                if genre_fp == genre_fop:
                    correlation = min(pattern_evolution[fp][-1]['weight'], 
                                    pattern_evolution[fop][-1]['weight'])
                    analysis['cross_correlations'][f"{genre_fp}_combined"] = correlation
                    
        # Predict new pattern weights based on trends
        for pattern_key, evolution_data in analysis['pattern_evolution'].items():
            if evolution_data['growth_rate'] > 0.1:  # Significant growth
                predicted_weight = evolution_data['current_weight'] * (1 + evolution_data['growth_rate'])
                analysis['predictive_weights'][pattern_key] = predicted_weight
                
        return analysis
        
    def process_batch(self, files: List[str], batch_number: int) -> ScanSession:
        """Process a single batch of files"""
        
        session_id = self.db.create_scan_session(batch_number)
        start_time = time.time()
        
        print(f"\n🚀 Starting Batch {batch_number} - {len(files)} files")
        print(f"📊 Session ID: {session_id}")
        
        if self.twitch:
            self.twitch.send_message(
                f"🔄 Starting Batch {batch_number}: Analyzing {len(files)} tracks with Cultural Intelligence v{VERSION}"
            )
            
        # Process files using existing comprehensive scan
        self.scanner.music_directory = Path(files[0]).parent if files else Path(".")
        results = []
        successful = 0
        patterns_learned = 0
        new_artists = set()
        
        for i, file_path in enumerate(files, 1):
            try:
                # Progress reporting
                if i % 50 == 0 or i == len(files):
                    progress = (i / len(files)) * 100
                    print(f"   📈 Batch {batch_number} Progress: {i}/{len(files)} ({progress:.1f}%)")
                    
                    if self.twitch and i % 100 == 0:  # Twitch updates every 100 files
                        self.twitch.send_message(
                            f"📈 Batch {batch_number}: {i}/{len(files)} files processed ({progress:.1f}%)"
                        )
                        
                # Process single file
                analysis = self.scanner.process_single_file(file_path)
                
                if not analysis.get('error'):
                    successful += 1
                    
                    # Track new patterns
                    filename_intelligence = analysis.get('filename_intelligence', {})
                    folder_intelligence = analysis.get('folder_intelligence', {})
                    
                    patterns_detected = []
                    patterns_detected.extend(filename_intelligence.get('genre_hints', []))
                    patterns_detected.extend(folder_intelligence.get('genre_hints', []))
                    
                    if patterns_detected:
                        patterns_learned += len(patterns_detected)
                        
                    # Track new artists
                    artist_intelligence = analysis.get('artist_intelligence', {})
                    if artist_intelligence.get('artist_name'):
                        new_artists.add(artist_intelligence['artist_name'])
                        
                    # Mark as processed
                    file_hash = hashlib.sha256(str(file_path).encode()).hexdigest()
                    intelligence_score = analysis.get('intelligence_summary', {}).get('overall_intelligence_score', 0.0)
                    classification_confidence = analysis.get('intelligence_summary', {}).get('classification_confidence', 0.0)
                    
                    self.db.mark_file_processed(
                        file_path, file_hash, session_id, 
                        intelligence_score, classification_confidence, patterns_detected
                    )
                    
                results.append(analysis)
                
            except Exception as e:
                print(f"   ❌ Error processing {Path(file_path).name}: {e}")
                results.append({'file_path': file_path, 'error': str(e)})
                
        # Calculate session metrics
        processing_time = time.time() - start_time
        success_rate = successful / len(files) if files else 0
        
        # Save accumulated patterns
        if hasattr(self.scanner, 'pattern_weights'):
            self.db.save_pattern_evolution(dict(self.scanner.pattern_weights), session_id)
            
        # Create session summary
        session = ScanSession(
            session_id=session_id,
            version=VERSION,
            batch_number=batch_number,
            start_time=datetime.now(),
            end_time=datetime.now(),
            files_processed=successful,
            success_rate=success_rate,
            patterns_learned=patterns_learned,
            new_artists=len(new_artists),
            duplicates_found=0,  # Would be calculated from results
            intelligence_score=sum(r.get('intelligence_summary', {}).get('overall_intelligence_score', 0) 
                                 for r in results if not r.get('error')) / max(successful, 1),
            status='completed'
        )
        
        # Update database
        self.db.update_scan_session(session_id, {
            'end_time': session.end_time.isoformat(),
            'files_processed': session.files_processed,
            'success_rate': session.success_rate,
            'patterns_learned': session.patterns_learned,
            'new_artists': session.new_artists,
            'intelligence_score': session.intelligence_score,
            'status': 'completed',
            'scan_results': {'processing_time': processing_time, 'batch_size': len(files)}
        })
        
        # Report to Twitch
        if self.twitch:
            self.twitch.send_message(
                f"✅ Batch {batch_number} Complete! Processed {successful}/{len(files)} files "
                f"({success_rate:.1%} success) in {processing_time:.1f}s. "
                f"Found {patterns_learned} new patterns, {len(new_artists)} new artists!"
            )
            
        print(f"✅ Batch {batch_number} completed in {processing_time:.1f}s")
        print(f"   Success: {successful}/{len(files)} ({success_rate:.1%})")
        print(f"   Patterns: {patterns_learned}, Artists: {len(new_artists)}")
        
        return session
        
    def run_full_scan(self, music_directory: str) -> List[ScanSession]:
        """Run complete scan with batch processing"""
        
        print(f"🎵 Cultural Intelligence v{VERSION} - Full Collection Scan")
        print("=" * 70)
        
        # Connect to Twitch
        if self.twitch:
            self.connect_twitch()
            
        # Get unprocessed files
        unprocessed_files = self.get_unprocessed_files(music_directory)
        
        if not unprocessed_files:
            print("✅ All files already processed in current version!")
            if self.twitch:
                self.twitch.send_message(f"✅ Collection already fully analyzed with v{VERSION}!")
                self.disconnect_twitch()
            return []
            
        print(f"📊 Found {len(unprocessed_files)} unprocessed files")
        total_batches = (len(unprocessed_files) + self.batch_size - 1) // self.batch_size
        print(f"📦 Will process in {total_batches} batches of {self.batch_size} files each")
        
        if self.twitch:
            self.twitch.send_message(
                f"🎵 Starting full scan: {len(unprocessed_files)} files in {total_batches} batches. "
                f"Cultural Intelligence v{VERSION} is learning!"
            )
            
        # Process in batches
        completed_sessions = []
        
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(unprocessed_files))
            batch_files = unprocessed_files[start_idx:end_idx]
            
            session = self.process_batch(batch_files, batch_num + 1)
            completed_sessions.append(session)
            
            # Analyze patterns between batches
            if batch_num % 5 == 4:  # Every 5 batches
                pattern_analysis = self.analyze_accumulated_patterns()
                if self.twitch:
                    total_patterns = pattern_analysis['total_patterns']
                    self.twitch.send_message(
                        f"🧠 Pattern Analysis: {total_patterns} total patterns learned! "
                        f"Intelligence is evolving..."
                    )
                    
        # Final analysis
        print(f"\n🎉 Full scan completed! Processed {total_batches} batches")
        
        final_analysis = self.analyze_accumulated_patterns()
        
        if self.twitch:
            self.twitch.send_message(
                f"🎉 SCAN COMPLETE! Cultural Intelligence v{VERSION} has analyzed your entire collection. "
                f"Total patterns learned: {final_analysis['total_patterns']}. "
                f"Your music database is now supercharged! 🚀"
            )
            
            # Disconnect
            time.sleep(2)
            self.disconnect_twitch()
            
        return completed_sessions
    
    def _create_fallback_scanner(self):
        """Create fallback scanner when full system not available"""
        class FallbackScanner:
            def __init__(self, directory):
                self.music_directory = Path(directory)
                
            def process_single_file(self, file_path):
                """Basic file analysis without full Cultural Intelligence"""
                try:
                    file_path = Path(file_path)
                    file_stats = file_path.stat()
                    
                    return {
                        'file_path': str(file_path),
                        'filename_intelligence': {
                            'genre_hints': self._extract_genre_from_filename(file_path.name)
                        },
                        'folder_intelligence': {
                            'genre_hints': self._extract_genre_from_path(str(file_path.parent))
                        },
                        'file_metadata': {
                            'size_mb': file_stats.st_size / (1024 * 1024),
                            'modified_date': file_stats.st_mtime
                        },
                        'intelligence_summary': {
                            'overall_intelligence_score': 0.5,  # Basic score
                            'classification_confidence': 0.4
                        }
                    }
                except Exception as e:
                    return {'file_path': str(file_path), 'error': str(e)}
                    
            def _extract_genre_from_filename(self, filename):
                """Basic genre extraction from filename"""
                genres = ['house', 'techno', 'trance', 'dnb', 'dubstep', 'ambient', 'breaks']
                filename_lower = filename.lower()
                return [genre for genre in genres if genre in filename_lower]
                
            def _extract_genre_from_path(self, path):
                """Basic genre extraction from folder path"""
                genres = ['house', 'techno', 'trance', 'dnb', 'dubstep', 'ambient', 'breaks']
                path_lower = path.lower()
                return [genre for genre in genres if genre in path_lower]
                
        return FallbackScanner(".")
        
    def _check_dashboard_status(self):
        """Check if dashboard is running"""
        try:
            import requests
            response = requests.get(self.dashboard_url, timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def send_to_dashboard(self, message_type: str, data: dict):
        """Send updates to dashboard if available"""
        if not self.dashboard_running:
            return False
            
        try:
            import requests
            requests.post(f"{self.dashboard_url}/api/v17_update", 
                         json={'type': message_type, 'data': data}, 
                         timeout=1)
            return True
        except:
            return False

def main():
    """Main execution function"""
    
    if len(sys.argv) < 2:
        print(f"Cultural Intelligence System v{VERSION}")
        print("Usage: python cultural_intelligence_v17.py <music_directory> [twitch_channel]")
        print("Example: python cultural_intelligence_v17.py '/path/to/music' 'your_channel'")
        sys.exit(1)
        
    music_directory = sys.argv[1]
    twitch_channel = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(music_directory):
        print(f"❌ Directory not found: {music_directory}")
        sys.exit(1)
        
    # Initialize system
    system = CulturalIntelligenceV17(twitch_channel)
    
    # Run full scan
    try:
        sessions = system.run_full_scan(music_directory)
        
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Version: {VERSION}")
        print(f"   Batches completed: {len(sessions)}")
        if sessions:
            total_files = sum(s.files_processed for s in sessions)
            avg_success = sum(s.success_rate for s in sessions) / len(sessions)
            total_patterns = sum(s.patterns_learned for s in sessions)
            total_artists = sum(s.new_artists for s in sessions)
            
            print(f"   Files processed: {total_files}")
            print(f"   Average success rate: {avg_success:.1%}")
            print(f"   Patterns learned: {total_patterns}")
            print(f"   New artists: {total_artists}")
            
        print(f"\n✨ Cultural Intelligence v{VERSION} scan complete!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Scan interrupted by user")
        if system.twitch:
            system.twitch.send_message("⏹️ Scan interrupted. Cultural Intelligence will resume later!")
            system.disconnect_twitch()
        
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        if system.twitch:
            system.twitch.send_message(f"❌ Scan encountered an error: {str(e)}")
            system.disconnect_twitch()

if __name__ == "__main__":
    main()