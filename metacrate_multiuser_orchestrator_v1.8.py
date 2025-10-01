#!/usr/bin/env python3
"""
MetaCrate Multi-User Batch Orchestrator v1.8
Enhanced version with per-user control and concurrent user scanning support.

New Features:
- Per-user scan control (scan specific users only)
- Concurrent user processing (multiple users can run simultaneously)
- User-specific progress tracking and statistics
- User-specific Twitch notifications
- Enhanced user management and control
"""

import os
import json
import logging
import time
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from threading import Thread, Event
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import existing classes
from cultural_database_client import CulturalDatabaseClient
from cultural_intelligence_scanner import CulturalIntelligenceScanner

@dataclass
class UserScanConfig:
    """Configuration for individual user scans"""
    username: str
    user_path: str
    batch_size: int = 250
    interval_minutes: int = 15
    enabled: bool = True
    twitch_notifications: bool = False
    priority: int = 5  # 1-10, higher = more priority

@dataclass
class UserStats:
    """Statistics for individual user scanning"""
    username: str
    total_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    error_files: int = 0
    last_scan: Optional[datetime] = None
    scan_duration: float = 0.0
    batches_completed: int = 0
    is_running: bool = False
    session_start: Optional[datetime] = None

class TwitchBot:
    """Enhanced Twitch bot with user-specific notifications"""
    
    def __init__(self, username: str = None, oauth_token: str = None, channel: str = None):
        self.username = username.lower() if username else None
        self.oauth_token = oauth_token
        self.channel = channel.lower() if channel else None
        self.socket = None
        self.connected = False
        self.enabled = all([username, oauth_token, channel])
        self.logger = logging.getLogger(f'TwitchBot-{self.username}')
        
    def send_user_update(self, target_user: str, message: str, stats: UserStats = None):
        """Send user-specific update to Twitch"""
        if not self.enabled:
            return
            
        if stats:
            formatted_msg = f"[{target_user}] {message} | Files: {stats.processed_files}/{stats.total_files} | Batches: {stats.batches_completed}"
        else:
            formatted_msg = f"[{target_user}] {message}"
            
        self.send_message(formatted_msg)
    
    def send_message(self, message: str):
        """Send message to Twitch chat"""
        if not self.enabled or not self.connected:
            return
            
        try:
            formatted_message = f"PRIVMSG #{self.channel} :{message}\r\n"
            self.socket.send(formatted_message.encode())
            self.logger.info(f"Sent to #{self.channel}: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send Twitch message: {e}")

class MetaCrateMultiUserOrchestrator:
    """
    Enhanced MetaCrate orchestrator with per-user control and concurrent processing.
    
    Features:
    - Per-user scan configuration and control
    - Concurrent user processing with thread pool
    - User-specific progress tracking and statistics
    - Flexible user management (enable/disable users)
    - User-specific Twitch notifications
    - Priority-based user scheduling
    """
    
    def __init__(self, max_concurrent_users: int = 3):
        self.db_client = CulturalDatabaseClient()
        self.ai_scanner = CulturalIntelligenceScanner()
        
        # Multi-user configuration
        self.metacrate_base_path = r"X:\\lightbulb networ IUL Dropbox\\Automation\\MetaCrate\\USERS"
        self.max_concurrent_users = max_concurrent_users
        self.processing_version = 'v1.8'
        
        # User management
        self.user_configs: Dict[str, UserScanConfig] = {}
        self.user_stats: Dict[str, UserStats] = {}
        self.running_users: Set[str] = set()
        self.stop_events: Dict[str, Event] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_users)
        self.master_stop_event = Event()
        
        # Twitch integration
        self.twitch_bot: Optional[TwitchBot] = None
        
        # Setup logging
        self.logger = logging.getLogger('MetaCrateMultiUser')
        self.setup_logging()
        
        # Auto-discover users
        self.discover_users()
    
    def setup_logging(self):
        """Setup enhanced logging for multi-user operations"""
        log_file = Path(__file__).parent / "metacrate_multiuser_orchestrator.log"
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
    
    def discover_users(self):
        """Auto-discover users from MetaCrate USERS directory"""
        if not os.path.exists(self.metacrate_base_path):
            self.logger.error(f"MetaCrate base path not found: {self.metacrate_base_path}")
            return
        
        discovered_users = []
        for item in os.listdir(self.metacrate_base_path):
            user_path = os.path.join(self.metacrate_base_path, item)
            if os.path.isdir(user_path):
                username = item.upper()  # MetaCrate users are typically uppercase
                
                # Create user configuration
                config = UserScanConfig(
                    username=username,
                    user_path=user_path,
                    batch_size=250,
                    interval_minutes=15,
                    enabled=True
                )
                
                # Create user statistics
                stats = UserStats(username=username)
                
                self.user_configs[username] = config
                self.user_stats[username] = stats
                self.stop_events[username] = Event()
                
                discovered_users.append(username)
        
        self.logger.info(f"🔍 Discovered {len(discovered_users)} users: {', '.join(discovered_users)}")
    
    def configure_user(self, username: str, **kwargs):
        """Configure specific user settings"""
        username = username.upper()
        if username not in self.user_configs:
            self.logger.error(f"User {username} not found")
            return False
        
        config = self.user_configs[username]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                self.logger.info(f"Updated {username}.{key} = {value}")
        
        return True
    
    def enable_user(self, username: str, enabled: bool = True):
        """Enable or disable user scanning"""
        username = username.upper()
        if username in self.user_configs:
            self.user_configs[username].enabled = enabled
            status = "enabled" if enabled else "disabled"
            self.logger.info(f"👤 User {username} {status}")
            return True
        return False
    
    def start_user_scan(self, username: str) -> bool:
        """Start scanning for a specific user"""
        username = username.upper()
        
        if username not in self.user_configs:
            self.logger.error(f"❌ User {username} not configured")
            return False
        
        if username in self.running_users:
            self.logger.warning(f"⚠️  User {username} already running")
            return False
        
        if not self.user_configs[username].enabled:
            self.logger.warning(f"⚠️  User {username} is disabled")
            return False
        
        if len(self.running_users) >= self.max_concurrent_users:
            self.logger.warning(f"⚠️  Maximum concurrent users ({self.max_concurrent_users}) reached")
            return False
        
        # Start user scan in thread pool
        self.running_users.add(username)
        self.user_stats[username].is_running = True
        self.user_stats[username].session_start = datetime.now()
        
        future = self.executor.submit(self._user_scan_loop, username)
        
        self.logger.info(f"🚀 Started scan for user {username}")
        
        if self.twitch_bot:
            self.twitch_bot.send_user_update(
                username, 
                "Scan started", 
                self.user_stats[username]
            )
        
        return True
    
    def stop_user_scan(self, username: str) -> bool:
        """Stop scanning for a specific user"""
        username = username.upper()
        
        if username not in self.running_users:
            self.logger.warning(f"⚠️  User {username} not running")
            return False
        
        # Signal stop
        self.stop_events[username].set()
        
        self.logger.info(f"🛑 Stopping scan for user {username}")
        
        if self.twitch_bot:
            self.twitch_bot.send_user_update(
                username, 
                "Scan stopped", 
                self.user_stats[username]
            )
        
        return True
    
    def start_all_users(self):
        """Start scanning for all enabled users"""
        started_users = []
        for username, config in self.user_configs.items():
            if config.enabled and username not in self.running_users:
                if self.start_user_scan(username):
                    started_users.append(username)
                    time.sleep(2)  # Stagger starts
        
        self.logger.info(f"🚀 Started scans for {len(started_users)} users: {', '.join(started_users)}")
    
    def stop_all_users(self):
        """Stop scanning for all users"""
        stopped_users = list(self.running_users)
        for username in stopped_users:
            self.stop_user_scan(username)
        
        # Wait for graceful shutdown
        time.sleep(5)
        self.logger.info(f"🛑 Stopped scans for {len(stopped_users)} users")
    
    def get_user_stats(self, username: str = None) -> Dict:
        """Get statistics for specific user or all users"""
        if username:
            username = username.upper()
            return self.user_stats.get(username, {})
        else:
            return {
                'users': dict(self.user_stats),
                'running_users': list(self.running_users),
                'total_users': len(self.user_configs),
                'enabled_users': len([u for u in self.user_configs.values() if u.enabled])
            }
    
    def _user_scan_loop(self, username: str):
        """Main scanning loop for individual user"""
        config = self.user_configs[username]
        stats = self.user_stats[username]
        stop_event = self.stop_events[username]
        
        self.logger.info(f"🔄 Starting scan loop for {username}")
        
        try:
            while not stop_event.is_set() and not self.master_stop_event.is_set():
                loop_start = time.time()
                
                # Get batch of unprocessed files for this user
                batch_files = self._get_user_batch(username)
                
                if batch_files:
                    self.logger.info(f"📦 Processing batch of {len(batch_files)} files for {username}")
                    
                    # Process batch
                    processed_count = self._process_user_batch(username, batch_files)
                    
                    # Update statistics
                    stats.processed_files += processed_count
                    stats.batches_completed += 1
                    stats.last_scan = datetime.now()
                    stats.scan_duration = time.time() - loop_start
                    
                    self.logger.info(f"✅ {username}: Processed {processed_count}/{len(batch_files)} files")
                    
                    if self.twitch_bot:
                        self.twitch_bot.send_user_update(
                            username, 
                            f"Completed batch {stats.batches_completed}", 
                            stats
                        )
                else:
                    self.logger.info(f"ℹ️  {username}: No unprocessed files found")
                
                # Wait for next interval
                wait_time = config.interval_minutes * 60
                self.logger.info(f"⏱️  {username}: Waiting {config.interval_minutes} minutes until next scan...")
                
                if stop_event.wait(wait_time):
                    break
                    
        except Exception as e:
            self.logger.error(f"❌ Error in {username} scan loop: {e}")
        finally:
            # Cleanup
            self.running_users.discard(username)
            stats.is_running = False
            self.stop_events[username].clear()
            
            self.logger.info(f"🏁 Scan loop ended for {username}")
    
    def _get_user_batch(self, username: str) -> List[str]:
        """Get batch of unprocessed files for specific user"""
        config = self.user_configs[username]
        stats = self.user_stats[username]
        
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'}
        unprocessed_files = []
        
        # Get already processed files to avoid duplicates
        processed_files = set()
        try:
            discovered_tracks = self.db_client.get_discovered_tracks_by_version(self.processing_version)
            for track in discovered_tracks:
                if track['file_path'].startswith(config.user_path):
                    processed_files.add(track['file_path'])
                    processed_files.add(track.get('file_hash', ''))
        except Exception as e:
            self.logger.warning(f"Could not get processed files for {username}: {e}")
        
        # Scan user directory
        files_found = 0
        files_skipped = 0
        
        for root, dirs, files in os.walk(config.user_path):
            for file in files:
                if Path(file).suffix.lower() in audio_extensions:
                    file_path = os.path.join(root, file)
                    files_found += 1
                    
                    # Check if already processed
                    if file_path in processed_files:
                        files_skipped += 1
                        continue
                    
                    # Check file hash
                    try:
                        file_hash = self._calculate_file_hash(file_path)
                        if file_hash and file_hash in processed_files:
                            files_skipped += 1
                            continue
                        
                        unprocessed_files.append(file_path)
                        
                        if len(unprocessed_files) >= config.batch_size:
                            break
                    except OSError:
                        continue
            
            if len(unprocessed_files) >= config.batch_size:
                break
        
        # Update user statistics
        stats.total_files = files_found
        stats.skipped_files = files_skipped
        
        # Shuffle for variety
        random.shuffle(unprocessed_files)
        
        self.logger.info(f"📊 {username}: Found {files_found} files, skipped {files_skipped}, queued {len(unprocessed_files)}")
        
        return unprocessed_files[:config.batch_size]
    
    def _process_user_batch(self, username: str, file_paths: List[str]) -> int:
        """Process batch of files for specific user"""
        stats = self.user_stats[username]
        processed_count = 0
        
        for file_path in file_paths:
            try:
                # Use existing Cultural Intelligence Scanner
                result = self.ai_scanner.process_audio_file(file_path)
                
                if result.get('success'):
                    processed_count += 1
                    self.logger.debug(f"✅ {username}: Processed {file_path}")
                else:
                    stats.error_files += 1
                    self.logger.warning(f"⚠️  {username}: Failed to process {file_path}")
                    
            except Exception as e:
                stats.error_files += 1
                self.logger.error(f"❌ {username}: Error processing {file_path}: {e}")
        
        return processed_count
    
    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None
    
    def setup_twitch_bot(self, username: str, oauth_token: str, channel: str):
        """Setup Twitch bot for notifications"""
        self.twitch_bot = TwitchBot(username, oauth_token, channel)
        self.logger.info(f"🤖 Twitch bot configured for #{channel}")
    
    def print_status(self):
        """Print current status of all users"""
        print("\\n" + "="*80)
        print("🎵 METACRATE MULTI-USER ORCHESTRATOR STATUS")
        print("="*80)
        
        for username, stats in self.user_stats.items():
            config = self.user_configs[username]
            status = "🟢 RUNNING" if stats.is_running else "🔴 STOPPED"
            enabled = "✅ ENABLED" if config.enabled else "❌ DISABLED"
            
            print(f"\\n👤 {username}")
            print(f"   Status: {status} | Config: {enabled}")
            print(f"   Files: {stats.processed_files}/{stats.total_files} processed")
            print(f"   Batches: {stats.batches_completed} completed")
            print(f"   Errors: {stats.error_files}")
            if stats.last_scan:
                print(f"   Last Scan: {stats.last_scan.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\\n📊 SUMMARY:")
        print(f"   Total Users: {len(self.user_configs)}")
        print(f"   Running Users: {len(self.running_users)}")
        print(f"   Max Concurrent: {self.max_concurrent_users}")
        print("="*80 + "\\n")

def main():
    """Example usage of multi-user orchestrator"""
    
    # Create orchestrator
    orchestrator = MetaCrateMultiUserOrchestrator(max_concurrent_users=3)
    
    # Optional: Setup Twitch notifications
    # orchestrator.setup_twitch_bot("your_bot_username", "oauth:your_token", "your_channel")
    
    # Configure specific users (optional)
    orchestrator.configure_user("DJUNOHOO", batch_size=100, interval_minutes=10)
    orchestrator.configure_user("EXAMPLE_USER", enabled=False)  # Disable specific user
    
    # Start scanning for all enabled users
    orchestrator.start_all_users()
    
    try:
        # Monitor and print status every 5 minutes
        while True:
            time.sleep(300)  # 5 minutes
            orchestrator.print_status()
    except KeyboardInterrupt:
        print("\\n🛑 Stopping all user scans...")
        orchestrator.stop_all_users()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()