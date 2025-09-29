#!/usr/bin/env python3
"""
Limited Cultural Intelligence Scanner - Scans only specified number of files
"""
import sys
from cultural_intelligence_scanner import CulturalIntelligenceScanner
import logging

class LimitedScanner(CulturalIntelligenceScanner):
    def __init__(self, config_file="taxonomy_config.json", file_limit=250):
        super().__init__(config_file)
        self.file_limit = file_limit
        self.files_processed_count = 0
        
    def scan_directory(self, directory):
        """Override scan_directory to limit files processed."""
        logger = logging.getLogger(__name__)
        logger.info(f"Starting LIMITED scan of directory: {directory} (max {self.file_limit} files)")
        
        # Create scan session
        session_data = {
            'scan_path': directory,
            'status': 'running'
        }
        session_id = self.db.create_scan_session(session_data)
        
        stats = {
            'files_discovered': 0,
            'files_processed': 0,
            'files_classified': 0,
            'duplicates_found': 0,
            'errors': 0
        }
        
        import os
        import time
        from pathlib import Path
        from datetime import datetime
        
        start_time = time.time()
        
        try:
            # Walk through all subdirectories but limit processing
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if self.files_processed_count >= self.file_limit:
                        logger.info(f"Reached file limit of {self.file_limit} files!")
                        break
                        
                    if Path(file).suffix.lower() in self.audio_extensions:
                        stats['files_discovered'] += 1
                        file_path = os.path.join(root, file)
                        
                        result = self.process_file(file_path, session_id)
                        if result:
                            stats['files_processed'] += 1
                            self.files_processed_count += 1
                        else:
                            stats['errors'] += 1
                            
                        # Progress logging every 50 files for smaller batches
                        if stats['files_discovered'] % 50 == 0:
                            logger.info(f"Processed {stats['files_processed']}/{stats['files_discovered']} files")
                            
                if self.files_processed_count >= self.file_limit:
                    break
                    
            # Detect duplicates
            logger.info("Detecting duplicates...")
            duplicates = self.detect_duplicates()
            stats['duplicates_found'] = len(duplicates)
            
            # Update artist profiles
            logger.info("Building artist profiles...")
            self.build_all_artist_profiles()
            
            end_time = time.time()
            processing_time = int(end_time - start_time)
            
            # Update scan session
            self.db.update_scan_session(session_id, {
                'completed_at': datetime.now().isoformat(),
                'files_discovered': stats['files_discovered'],
                'files_analyzed': stats['files_processed'],
                'files_classified': stats['files_processed'],
                'duplicates_found': stats['duplicates_found'],
                'processing_time': processing_time,
                'status': 'completed'
            })
            
            logger.info(f"LIMITED SCAN COMPLETED! ({self.file_limit} file limit)")
            logger.info(f"Files processed: {stats['files_processed']}")
            logger.info(f"Duplicates found: {stats['duplicates_found']}")
            logger.info(f"Processing time: {processing_time}s")
            
        except Exception as e:
            logger.error(f"Error during limited scan: {e}")
            self.db.update_scan_session(session_id, {
                'status': 'error',
                'error_message': str(e)
            })
            
        return stats

if __name__ == "__main__":
    print("Limited Cultural Intelligence Scanner")
    print("Dashboard should remain running during scan!")
    
    scanner = LimitedScanner(file_limit=250)
    scanner.run_single_scan()