#!/usr/bin/env python3
"""
CULTURAL INTELLIGENCE SCHEDULER
==============================
Handles automatic scanning, learning, and intelligence updates for the Cultural Intelligence System.
"""

import time
import threading
import schedule
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from taxonomy_v32 import TaxonomyConfig
    from taxonomy_scanner import TaxonomyScanner
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install schedule psycopg2-binary")
    sys.exit(1)

class CulturalIntelligenceScheduler:
    """Automated scheduler for Cultural Intelligence operations"""
    
    def __init__(self):
        self.config = TaxonomyConfig()
        self.scanner = None
        self.last_scan_time = None
        self.last_pattern_update = None
        self.last_confidence_update = None
        self.running = True
        
        # Load configuration
        self.scan_config = self.config.config["scanning"]
        self.classification_config = self.config.config["classification"] 
        self.intelligence_config = self.config.config["intelligence"]
        
        self.log_file = Path("scheduler.log")
        
        # Initialize database connection
        try:
            db_url = self.config.config["supabase"]["url"]
            self.conn = psycopg2.connect(db_url)
            self.conn.autocommit = True
            self.log("Database connection established")
        except Exception as e:
            self.log(f"Database connection failed: {e}")
            self.conn = None
    
    def log(self, message: str):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except:
            pass
    
    def setup_schedules(self):
        """Set up all scheduled operations"""
        
        # Auto-scanning schedule
        if self.scan_config["auto_scan_enabled"]:
            scan_hours = self.scan_config["auto_scan_interval_hours"]
            schedule.every(scan_hours).hours.do(self.auto_scan_job)
            self.log(f"Auto-scan scheduled every {scan_hours} hours")
        
        # Pattern learning schedule  
        if self.classification_config["pattern_learning_enabled"]:
            pattern_hours = self.classification_config["pattern_update_interval_hours"]
            schedule.every(pattern_hours).hours.do(self.pattern_learning_job)
            self.log(f"Pattern learning scheduled every {pattern_hours} hours")
        
        # Intelligence updates
        if self.intelligence_config["learning_enabled"]:
            # Pattern analysis
            analysis_hours = self.intelligence_config["pattern_analysis_interval_hours"]
            schedule.every(analysis_hours).hours.do(self.pattern_analysis_job)
            
            # Confidence recalculation
            confidence_hours = self.intelligence_config["confidence_recalculation_hours"]
            schedule.every(confidence_hours).hours.do(self.confidence_update_job)
            
            # Duplicate checking
            duplicate_hours = self.intelligence_config["duplicate_check_interval_hours"] 
            schedule.every(duplicate_hours).hours.do(self.duplicate_check_job)
            
            self.log(f"Intelligence updates: analysis={analysis_hours}h, confidence={confidence_hours}h, duplicates={duplicate_hours}h")
        
        # Daily maintenance
        schedule.every().day.at("03:00").do(self.daily_maintenance_job)
        self.log("Daily maintenance scheduled at 3:00 AM")
    
    def auto_scan_job(self):
        """Automatic scanning for new tracks"""
        self.log("🔍 Starting automatic scan...")
        
        try:
            # Initialize scanner if needed
            if not self.scanner:
                self.scanner = TaxonomyScanner()
            
            # Get scan paths
            scan_paths = [
                self.config.config["paths"]["scan_root"],
                self.config.config["paths"]["current_target"]
            ]
            
            new_files_found = 0
            
            for path in scan_paths:
                if not os.path.exists(path):
                    continue
                    
                self.log(f"Scanning: {path}")
                
                # Incremental scan only (new/modified files)
                if self.scan_config["incremental_scan_only"]:
                    results = self.scanner.incremental_scan(
                        path, 
                        max_files=self.scan_config["max_files_per_scan"]
                    )
                else:
                    results = self.scanner.scan_collection(path)
                
                if results:
                    new_files = results.get('new_files', 0)
                    new_files_found += new_files
                    self.log(f"Found {new_files} new files in {path}")
            
            self.last_scan_time = datetime.now()
            self.log(f"✅ Auto-scan complete: {new_files_found} new files processed")
            
            # Update scan statistics
            self.update_scan_stats(new_files_found)
            
        except Exception as e:
            self.log(f"❌ Auto-scan failed: {e}")
    
    def pattern_learning_job(self):
        """Update classification patterns based on new data"""
        self.log("🧠 Starting pattern learning...")
        
        if not self.conn:
            self.log("❌ No database connection for pattern learning")
            return
        
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Analyze recent classifications for new patterns
            cursor.execute("""
                SELECT 
                    artist, genre, subgenre, label,
                    COUNT(*) as occurrence_count,
                    AVG(overall_confidence) as avg_confidence
                FROM cultural_classifications 
                WHERE classified_at > NOW() - INTERVAL %s
                    AND overall_confidence > %s
                GROUP BY artist, genre, subgenre, label
                HAVING COUNT(*) >= %s
            """, [
                f"{self.classification_config['pattern_update_interval_hours']} hours",
                self.classification_config['confidence_threshold'],
                self.classification_config['min_pattern_occurrences']
            ])
            
            new_patterns = cursor.fetchall()
            patterns_updated = 0
            
            for pattern in new_patterns:
                # Update or create pattern
                cursor.execute("""
                    INSERT INTO cultural_patterns 
                    (pattern_type, pattern_value, genre, subgenre, confidence, sample_size, success_rate)
                    VALUES ('artist_genre', %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (pattern_type, pattern_value, genre, subgenre) 
                    DO UPDATE SET
                        confidence = EXCLUDED.confidence,
                        sample_size = cultural_patterns.sample_size + EXCLUDED.sample_size,
                        last_updated = NOW()
                """, [
                    pattern['artist'],
                    pattern['genre'], 
                    pattern['subgenre'],
                    pattern['avg_confidence'],
                    pattern['occurrence_count'],
                    pattern['avg_confidence']
                ])
                patterns_updated += 1
            
            self.last_pattern_update = datetime.now()
            self.log(f"✅ Pattern learning complete: {patterns_updated} patterns updated")
            
        except Exception as e:
            self.log(f"❌ Pattern learning failed: {e}")
    
    def pattern_analysis_job(self):
        """Analyze existing patterns and update confidences"""
        self.log("📊 Starting pattern analysis...")
        
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Find patterns that need confidence updates
            cursor.execute("""
                UPDATE cultural_patterns 
                SET confidence = confidence * 0.99
                WHERE last_updated < NOW() - INTERVAL %s
                    AND confidence > 0.1
            """, [f"{self.intelligence_config['confidence_recalculation_hours']} hours"])
            
            updated_rows = cursor.rowcount
            self.log(f"✅ Pattern analysis complete: {updated_rows} patterns aged")
            
        except Exception as e:
            self.log(f"❌ Pattern analysis failed: {e}")
    
    def confidence_update_job(self):
        """Recalculate classification confidences based on new patterns"""
        self.log("🎯 Starting confidence recalculation...")
        
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Update confidences for recent classifications
            cursor.execute("""
                UPDATE cultural_classifications cc
                SET 
                    genre_confidence = LEAST(cc.genre_confidence * 1.05, 0.99),
                    overall_confidence = LEAST(cc.overall_confidence * 1.02, 0.99)
                FROM cultural_patterns cp
                WHERE cc.artist = cp.pattern_value 
                    AND cc.genre = cp.genre
                    AND cp.pattern_type = 'artist_genre'
                    AND cp.confidence > %s
                    AND cc.classified_at > NOW() - INTERVAL %s
            """, [
                self.classification_config['confidence_threshold'],
                f"{self.intelligence_config['confidence_recalculation_hours']} hours"
            ])
            
            updated_rows = cursor.rowcount
            self.last_confidence_update = datetime.now()
            self.log(f"✅ Confidence update complete: {updated_rows} classifications updated")
            
        except Exception as e:
            self.log(f"❌ Confidence update failed: {e}")
    
    def duplicate_check_job(self):
        """Check for new duplicates in recent additions"""
        self.log("🔍 Starting duplicate check...")
        
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Find potential duplicates in recent additions
            cursor.execute("""
                SELECT file_hash, COUNT(*) as dup_count, 
                       ARRAY_AGG(id) as track_ids,
                       SUM(file_size) as total_size
                FROM cultural_tracks 
                WHERE processed_at > NOW() - INTERVAL %s
                GROUP BY file_hash 
                HAVING COUNT(*) > 1
            """, [f"{self.intelligence_config['duplicate_check_interval_hours']} hours"])
            
            duplicates = cursor.fetchall()
            
            for dup in duplicates:
                # Insert or update duplicate record
                cursor.execute("""
                    INSERT INTO cultural_duplicates 
                    (file_hash, primary_track_id, duplicate_track_ids, duplicate_count, total_size_bytes, space_waste_bytes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (file_hash) DO UPDATE SET
                        duplicate_track_ids = EXCLUDED.duplicate_track_ids,
                        duplicate_count = EXCLUDED.duplicate_count,
                        detected_at = NOW()
                """, [
                    dup['file_hash'],
                    dup['track_ids'][0],  # First track as primary
                    dup['track_ids'],
                    dup['dup_count'],
                    dup['total_size'],
                    dup['total_size'] - (dup['total_size'] // dup['dup_count'])  # Space waste
                ])
            
            self.log(f"✅ Duplicate check complete: {len(duplicates)} duplicate groups processed")
            
        except Exception as e:
            self.log(f"❌ Duplicate check failed: {e}")
    
    def daily_maintenance_job(self):
        """Daily maintenance tasks"""
        self.log("🔧 Starting daily maintenance...")
        
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Clean old API request logs (keep 30 days)
            cursor.execute("""
                DELETE FROM cultural_api_requests 
                WHERE requested_at < NOW() - INTERVAL '30 days'
            """)
            deleted_requests = cursor.rowcount
            
            # Update artist/label statistics
            cursor.execute("""
                UPDATE cultural_artist_profiles 
                SET track_count = (
                    SELECT COUNT(*) FROM cultural_classifications 
                    WHERE artist = cultural_artist_profiles.name
                )
            """)
            
            cursor.execute("""
                UPDATE cultural_label_profiles 
                SET release_count = (
                    SELECT COUNT(DISTINCT catalog_number) FROM cultural_classifications 
                    WHERE label = cultural_label_profiles.name
                    AND catalog_number IS NOT NULL
                )
            """)
            
            self.log(f"✅ Daily maintenance complete: {deleted_requests} old API logs cleaned")
            
        except Exception as e:
            self.log(f"❌ Daily maintenance failed: {e}")
    
    def update_scan_stats(self, new_files: int):
        """Update scanning statistics"""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO cultural_processing_stats 
                (run_id, operation_type, files_processed, start_time, end_time, status)
                VALUES (gen_random_uuid(), 'auto_scan', %s, %s, %s, 'completed')
            """, [new_files, self.last_scan_time, datetime.now()])
            
        except Exception as e:
            self.log(f"Could not update scan stats: {e}")
    
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            "running": self.running,
            "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "last_pattern_update": self.last_pattern_update.isoformat() if self.last_pattern_update else None,
            "last_confidence_update": self.last_confidence_update.isoformat() if self.last_confidence_update else None,
            "next_jobs": [str(job) for job in schedule.jobs[:5]],  # Next 5 jobs
            "config": {
                "auto_scan_hours": self.scan_config["auto_scan_interval_hours"],
                "pattern_update_hours": self.classification_config["pattern_update_interval_hours"], 
                "confidence_update_hours": self.intelligence_config["confidence_recalculation_hours"]
            }
        }
    
    def run(self):
        """Main scheduler loop"""
        self.log("🎵 Cultural Intelligence Scheduler started")
        self.setup_schedules()
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.log("Scheduler stopped by user")
                break
            except Exception as e:
                self.log(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    """Main entry point"""
    scheduler = CulturalIntelligenceScheduler()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # Show status and exit
        status = scheduler.get_status()
        print(json.dumps(status, indent=2))
        return
    
    # Run scheduler
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("Scheduler stopped")

if __name__ == "__main__":
    main()