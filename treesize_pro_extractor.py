#!/usr/bin/env python3
"""
TreeSize Pro CLI Metadata Extractor
===================================
Professional metadata extraction using TreeSize Pro command line interface
"""

import os
import sys
import json
import subprocess
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TreeSizeProExtractor:
    """Professional metadata extraction using TreeSize Pro CLI."""
    
    def __init__(self):
        """Initialize TreeSize Pro extractor."""
        self.treesize_exe = r"C:\Program Files\JAM Software\TreeSize\TreeSize.exe"
        
        # Verify TreeSize Pro is available
        if not os.path.exists(self.treesize_exe):
            raise FileNotFoundError(f"TreeSize Pro not found at {self.treesize_exe}")
            
    def extract_metadata_csv(self, directory: str, output_file: str = None) -> List[Dict]:
        """Extract metadata using TreeSize Pro CSV export."""
        if not output_file:
            output_file = os.path.join(os.path.dirname(__file__), 'treesize_export.csv')
            
        try:
            # TreeSize Pro command for CSV export with detailed metadata
            cmd = [
                self.treesize_exe,
                '/SCAN', directory,
                '/CSV', output_file,
                '/NOGUI',  # No GUI
                '/EXPAND', '1',  # Expand first level
                '/EXPORTFILES'  # Include individual files
            ]
            
            logger.info(f"Running TreeSize Pro: {' '.join(cmd)}")
            
            # Execute TreeSize Pro
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300,  # 5 minute timeout
                                  cwd=os.path.dirname(self.treesize_exe))
            
            if result.returncode != 0:
                logger.error(f"TreeSize Pro failed: {result.stderr}")
                return []
                
            # Parse CSV output
            return self.parse_csv_output(output_file)
            
        except subprocess.TimeoutExpired:
            logger.error("TreeSize Pro timed out")
            return []
        except Exception as e:
            logger.error(f"TreeSize Pro extraction failed: {e}")
            return []
            
    def extract_metadata_xml(self, directory: str, output_file: str = None) -> List[Dict]:
        """Extract metadata using TreeSize Pro XML export."""
        if not output_file:
            output_file = os.path.join(os.path.dirname(__file__), 'treesize_export.xml')
            
        try:
            # TreeSize Pro command for XML export
            cmd = [
                self.treesize_exe,
                '/SCAN', directory,
                '/XML', output_file,
                '/NOGUI',
                '/EXPAND', '2'  # Expand 2 levels for better detail
            ]
            
            logger.info(f"Running TreeSize Pro XML export: {' '.join(cmd)}")
            
            result = subprocess.run(cmd,
                                  capture_output=True,
                                  text=True,
                                  timeout=300,
                                  cwd=os.path.dirname(self.treesize_exe))
            
            if result.returncode != 0:
                logger.error(f"TreeSize Pro XML export failed: {result.stderr}")
                return []
                
            # Parse XML output
            return self.parse_xml_output(output_file)
            
        except Exception as e:
            logger.error(f"TreeSize Pro XML extraction failed: {e}")
            return []
            
    def parse_csv_output(self, csv_file: str) -> List[Dict]:
        """Parse TreeSize Pro CSV output."""
        files_data = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8-sig', newline='') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                delimiter = ';' if ';' in sample else ','
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row in reader:
                    # Extract relevant metadata
                    file_data = {
                        'path': row.get('Full Path', row.get('Path', '')),
                        'name': row.get('Name', ''),
                        'size': self.parse_size(row.get('Size', '0')),
                        'size_on_disk': self.parse_size(row.get('Size on Disk', '0')),
                        'modified': row.get('Last Modified', ''),
                        'created': row.get('Created', ''),
                        'accessed': row.get('Last Accessed', ''),
                        'file_count': self.parse_int(row.get('Files', '0')),
                        'folder_count': self.parse_int(row.get('Folders', '0')),
                        'extension': row.get('Extension', ''),
                        'type': row.get('Type', ''),
                        'owner': row.get('Owner', ''),
                        'attributes': row.get('Attributes', '')
                    }
                    
                    # Only include actual files (not directories)
                    if file_data['path'] and os.path.isfile(file_data['path']):
                        files_data.append(file_data)
                        
            logger.info(f"Parsed {len(files_data)} files from CSV")
            return files_data
            
        except Exception as e:
            logger.error(f"CSV parsing failed: {e}")
            return []
            
    def parse_xml_output(self, xml_file: str) -> List[Dict]:
        """Parse TreeSize Pro XML output."""
        files_data = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Navigate XML structure to find file entries
            for item in root.iter():
                if item.tag in ['File', 'Directory'] and item.get('Type') == 'File':
                    file_data = {
                        'path': item.get('Path', ''),
                        'name': item.get('Name', ''),
                        'size': self.parse_size(item.get('Size', '0')),
                        'size_on_disk': self.parse_size(item.get('SizeOnDisk', '0')),
                        'modified': item.get('LastModified', ''),
                        'created': item.get('Created', ''),
                        'accessed': item.get('LastAccessed', ''),
                        'extension': item.get('Extension', ''),
                        'type': item.get('FileType', ''),
                        'owner': item.get('Owner', ''),
                        'attributes': item.get('Attributes', '')
                    }
                    
                    if file_data['path']:
                        files_data.append(file_data)
                        
            logger.info(f"Parsed {len(files_data)} files from XML")
            return files_data
            
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            return []
            
    def parse_size(self, size_str: str) -> int:
        """Parse size string to bytes."""
        try:
            # Remove commas and convert to int
            size_str = size_str.replace(',', '').replace(' ', '')
            
            # Handle units (KB, MB, GB, TB)
            multipliers = {
                'KB': 1024,
                'MB': 1024**2, 
                'GB': 1024**3,
                'TB': 1024**4
            }
            
            for unit, mult in multipliers.items():
                if unit in size_str.upper():
                    return int(float(size_str.upper().replace(unit, '')) * mult)
                    
            return int(size_str)
            
        except (ValueError, AttributeError):
            return 0
            
    def parse_int(self, int_str: str) -> int:
        """Parse integer string safely."""
        try:
            return int(int_str.replace(',', ''))
        except (ValueError, AttributeError):
            return 0
            
    def get_file_metadata_enhanced(self, directory: str) -> List[Dict]:
        """Get enhanced file metadata using best available method."""
        # Try XML first (more detailed), fallback to CSV
        metadata = self.extract_metadata_xml(directory)
        
        if not metadata:
            logger.info("XML extraction failed, trying CSV...")
            metadata = self.extract_metadata_csv(directory)
            
        if not metadata:
            logger.warning("TreeSize Pro extraction failed, using fallback")
            return self.fallback_extraction(directory)
            
        return metadata
        
    def fallback_extraction(self, directory: str) -> List[Dict]:
        """Fallback extraction using basic file system operations."""
        files_data = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        stat_info = os.stat(file_path)
                        
                        file_data = {
                            'path': file_path,
                            'name': file,
                            'size': stat_info.st_size,
                            'size_on_disk': stat_info.st_size,  # Approximation
                            'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                            'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                            'accessed': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                            'extension': os.path.splitext(file)[1],
                            'type': 'File',
                            'owner': '',
                            'attributes': ''
                        }
                        
                        files_data.append(file_data)
                        
                    except Exception as e:
                        logger.warning(f"Failed to get stats for {file_path}: {e}")
                        continue
                        
            return files_data
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return []

def test_treesize_integration():
    """Test TreeSize Pro integration."""
    print("Testing TreeSize Pro Integration")
    print("=" * 40)
    
    try:
        extractor = TreeSizeProExtractor()
        
        # Test with a small directory
        test_dir = r"C:\Users\Public\Music"
        if not os.path.exists(test_dir):
            test_dir = os.path.expanduser("~/Music")
            
        if not os.path.exists(test_dir):
            print("No test directory available")
            return False
            
        print(f"Testing with directory: {test_dir}")
        
        # Extract metadata
        metadata = extractor.get_file_metadata_enhanced(test_dir)
        
        print(f"Extracted metadata for {len(metadata)} files")
        
        # Show sample
        if metadata:
            sample = metadata[0]
            print("\\nSample file metadata:")
            for key, value in sample.items():
                print(f"  {key}: {value}")
                
        return len(metadata) > 0
        
    except Exception as e:
        print(f"TreeSize Pro test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_treesize_integration()
    print(f"\\nTreeSize Pro Integration: {'✅ SUCCESS' if success else '❌ FAILED'}")