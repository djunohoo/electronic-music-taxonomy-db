#!/usr/bin/env python3
"""
MetaCrate Client Example - How to Integrate with Cultural Intelligence
======================================================================

This demonstrates exactly how MetaCrate can submit tracks and get guaranteed
responses with artist, track, remix info, genre, and subgenre.
"""

import requests
import json
import time

class MetaCrateIntelligenceClient:
    """Client for MetaCrate to get track intelligence from Cultural Intelligence System."""
    
    def __init__(self, api_url="http://172.22.17.37:5000"):
        self.api_url = api_url.rstrip('/')
        
    def get_track_intelligence(self, file_path, file_hash=None):
        """
        Get complete track intelligence for MetaCrate with duplicate handling.
        
        Args:
            file_path: Full path to the audio file
            file_hash: Optional - if provided, skips hash calculation for speed
            
        Returns:
            dict: Response indicating whether to process or skip the track
                 - status: "success" = process track (includes track data)
                 - status: "duplicate_skip" = skip track (no track data)
                 - status: "error" = error occurred (includes fallback track data)
        """
        
        try:
            response = requests.post(
                f"{self.api_url}/api/track/analyze",
                json={
                    "file_path": file_path,
                    "file_hash": file_hash  # Optional for speed
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Return safe defaults on error
                return self._get_error_fallback(file_path, f"API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            # Return safe defaults on connection error
            return self._get_error_fallback(file_path, f"Connection error: {str(e)}")
    
    def should_process_track(self, file_path, file_hash=None):
        """
        Simplified method for MetaCrate - returns True if track should be processed.
        
        Returns:
            tuple: (should_process: bool, track_data: dict or None)
        """
        result = self.get_track_intelligence(file_path, file_hash)
        
        if result['status'] == 'duplicate_skip':
            return False, None  # MetaCrate should skip this duplicate
        
        elif result['status'] == 'success':
            return True, result['track']  # MetaCrate should process this track
        
        else:  # error
            # On error, process with fallback data to be safe
            return True, result.get('track')
    
    def _get_error_fallback(self, file_path, error_msg):
        """Provide safe defaults when API is unavailable."""
        from pathlib import Path
        
        return {
            "status": "error",
            "error": error_msg,
            "track": {
                "artist": "Unknown Artist",
                "track_name": Path(file_path).stem,
                "remix_info": "Original Mix",
                "genre": "Electronic", 
                "subgenre": None,
                "confidence": 0.0
            },
            "metadata": {
                "file_hash": None,
                "is_duplicate": False,
                "source": "error_fallback"
            }
        }
    
    def batch_analyze(self, file_paths):
        """Analyze multiple tracks efficiently."""
        try:
            response = requests.post(
                f"{self.api_url}/api/track/batch",
                json={"file_paths": file_paths},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Batch API error: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Batch connection error: {str(e)}"}
    
    def health_check(self):
        """Check if the Cultural Intelligence API is available."""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=5)
            return response.status_code == 200 and response.json().get('status') == 'healthy'
        except:
            return False

# =====================================================
# EXAMPLE USAGE FOR METACRATE
# =====================================================

def example_metacrate_integration():
    """Example showing how MetaCrate would use this system."""
    
    # Initialize client
    client = MetaCrateIntelligenceClient()
    
    # Check if Cultural Intelligence System is available
    if not client.health_check():
        print("⚠️  Cultural Intelligence System not available")
        print("   MetaCrate can still function with default values")
        return
    
    print("✅ Cultural Intelligence System connected!")
    print()
    
    # Example tracks (adjust paths for your system)
    example_tracks = [
        r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals\Deadmau5 - Strobe.mp3",
        r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals\Armin van Buuren - Shivers (Original Mix).mp3"
    ]
    
    for track_path in example_tracks:
        print(f"🎵 Analyzing: {track_path}")
        
        # Get intelligence (this is what MetaCrate would call)
        result = client.get_track_intelligence(track_path)
        
        if result['status'] == 'success':
            track = result['track']
            metadata = result['metadata']
            
            # MetaCrate gets guaranteed fields:
            print(f"   Artist: {track['artist']}")
            print(f"   Track:  {track['track_name']}")
            print(f"   Remix:  {track['remix_info']}")
            print(f"   Genre:  {track['genre']}")
            print(f"   Subgenre: {track['subgenre'] or 'N/A'}")
            print(f"   Confidence: {track['confidence']:.2f}")
            print(f"   Source: {metadata['source']}")
            
            # MetaCrate can now use this data for:
            # - Automatic genre tagging
            # - Smart playlisting
            # - Duplicate detection
            # - Collection organization
            
        else:
            print(f"   Error: {result.get('error')}")
            # Even on error, MetaCrate still gets safe defaults
            track = result['track']
            print(f"   Fallback - Artist: {track['artist']}, Genre: {track['genre']}")
        
        print()

def example_batch_processing():
    """Example of efficient batch processing for large collections."""
    
    client = MetaCrateIntelligenceClient()
    
    # Example: Process entire folder
    import glob
    
    # Get all audio files (adjust path)
    audio_files = glob.glob(r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals\*.mp3")[:10]  # First 10 files
    
    if audio_files:
        print(f"📦 Batch processing {len(audio_files)} tracks...")
        
        result = client.batch_analyze(audio_files)
        
        if 'results' in result:
            for item in result['results']:
                file_path = item['file_path']
                track_result = item['result']
                
                if track_result['status'] == 'success':
                    track = track_result['track']
                    print(f"✅ {track['artist']} - {track['track_name']} ({track['genre']})")
                else:
                    print(f"❌ Error processing {file_path}")
        else:
            print(f"❌ Batch error: {result.get('error')}")

def example_metacrate_workflow():
    """Complete example workflow for MetaCrate integration with duplicate handling."""
    
    print("🎛️ MetaCrate + Cultural Intelligence System Integration")
    print("=" * 60)
    
    client = MetaCrateIntelligenceClient()
    
    # 1. Health check
    print("1. Checking Cultural Intelligence System...")
    if client.health_check():
        print("   ✅ System available")
    else:
        print("   ⚠️  System unavailable - using fallback mode")
    
    # 2. Example tracks including duplicates
    print("\n2. Processing tracks with duplicate detection...")
    
    example_tracks = [
        r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals\Deadmau5 - Strobe.mp3",
        r"X:\lightbulb networ IUL Dropbox\Temp\Deadmau5 - Strobe.mp3",  # Duplicate in temp folder
        r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals\Armin - Shivers.mp3"
    ]
    
    processed_count = 0
    skipped_count = 0
    
    for track_path in example_tracks:
        print(f"\n   🎵 Analyzing: {track_path}")
        
        # MetaCrate's new duplicate-aware workflow:
        should_process, track_data = client.should_process_track(track_path)
        
        if should_process:
            # Process this track normally
            processed_count += 1
            print(f"      ✅ PROCESSING - {track_data['artist']} - {track_data['track_name']}")
            print(f"         Genre: {track_data['genre']} | Remix: {track_data['remix_info']}")
            print(f"         Confidence: {track_data['confidence']:.1%}")
            
            # MetaCrate would now:
            # - Add to database with proper tags
            # - Include in collection statistics
            # - Make available for playlisting
            
        else:
            # Skip this duplicate
            skipped_count += 1
            print(f"      ⏭️  SKIPPING - Duplicate detected")
            
            # MetaCrate benefits:
            # - Saves processing time
            # - Avoids duplicate entries
            # - Keeps database clean
    
    # 3. Summary
    print(f"\n3. Processing Summary:")
    print(f"   ✅ Processed: {processed_count} tracks")
    print(f"   ⏭️  Skipped: {skipped_count} duplicates")
    print(f"   💾 Database stays clean and efficient")
    
    # 4. MetaCrate integration benefits
    print("\n4. MetaCrate benefits with duplicate handling:")
    print("   ✅ Automatic duplicate detection")
    print("   ✅ Only process best versions of tracks")
    print("   ✅ Faster collection processing")
    print("   ✅ Clean database without duplicates")
    print("   ✅ Guaranteed track data format")
    print("   ✅ Intelligent genre classification")

if __name__ == "__main__":
    print("🎵 Cultural Intelligence System - MetaCrate Integration Example")
    print()
    
    try:
        example_metacrate_workflow()
        print("\n" + "=" * 60)
        print("✅ Integration example completed!")
        print("MetaCrate can now get instant track intelligence!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Cultural Intelligence API is running at http://172.22.17.37:5000")