#!/usr/bin/env python3
"""
Live Stream Assistant - Webhook Client Example
Demonstrates how the live stream assistant would send data back to the main taxonomy system
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any
import uuid
import time

class StreamAssistantWebhookClient:
    """
    Client for sending live stream data back to the main taxonomy system
    """
    
    def __init__(self, webhook_base_url: str, session_id: str = None):
        self.webhook_base_url = webhook_base_url.rstrip('/')
        self.session_id = session_id or str(uuid.uuid4())
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'StreamAssistant/1.0'
        }
    
    def send_track_classification(self, track_data: Dict[str, Any], stream_info: Dict[str, Any]):
        """
        Send track classification data when a new track is detected
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "dj_stream": stream_info,
            "track_data": track_data,
            "session_id": self.session_id,
            "event_type": "track_start"
        }
        
        try:
            response = requests.post(
                f"{self.webhook_base_url}/api/webhook/track-classified",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            print(f"✅ Track classification sent: {track_data['artist']} - {track_data['title']}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send track classification: {e}")
            return None
    
    def send_chat_interaction(self, message_data: Dict[str, Any], stream_info: Dict[str, Any]):
        """
        Send chat interaction data when the bot posts to Twitch
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "dj_stream": stream_info,
            "track_data": None,  # Not needed for chat interactions
            "chat_interaction": message_data,
            "session_id": self.session_id,
            "event_type": "chat_message"
        }
        
        try:
            response = requests.post(
                f"{self.webhook_base_url}/api/webhook/chat-interaction",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            print(f"💬 Chat interaction sent: {message_data['engagement_type']}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send chat interaction: {e}")
            return None
    
    def send_stream_stats(self, stream_info: Dict[str, Any], event_type: str = "stream_update"):
        """
        Send general stream statistics
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "dj_stream": stream_info,
            "track_data": None,
            "chat_interaction": None,
            "session_id": self.session_id,
            "event_type": event_type
        }
        
        try:
            response = requests.post(
                f"{self.webhook_base_url}/api/webhook/stream-stats",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            print(f"📊 Stream stats sent: {event_type}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send stream stats: {e}")
            return None

def simulate_live_stream_session():
    """
    Simulate a live DJ stream session with track changes and chat interactions
    """
    print("🎵 Starting simulated live stream session...")
    
    # Initialize webhook client
    webhook_client = StreamAssistantWebhookClient("http://localhost:8000")
    
    # Stream info
    stream_info = {
        "twitch_username": "djunohoo",
        "stream_title": "Deep House & Breakbeat Vibes",
        "viewer_count": 42,
        "platform": "twitch"
    }
    
    # Send stream start
    webhook_client.send_stream_stats(stream_info, "stream_start")
    
    # Simulate track 1: Liquid DnB
    print("\n🎧 Playing Track 1: Liquid DnB")
    track1_data = {
        "artist": "LTJ Bukem",
        "title": "Music",
        "album": "Journey Inwards",
        "bpm": 174,
        "key": "A minor",
        "classification": {
            "main_genre": "drum and bass",
            "subgenre": "liquid dnb",
            "confidence": 0.96,
            "characteristics": ["atmospheric", "jazzy", "melodic", "smooth"]
        }
    }
    
    webhook_client.send_track_classification(track1_data, stream_info)
    
    # Simulate chat interaction for track 1
    time.sleep(2)
    chat1_data = {
        "message_sent": "🌊 Liquid DnB detected! Notice those smooth jazz influences and atmospheric pads - this subgenre prioritizes emotion over aggression. Chat: What's your favorite liquid artist?",
        "engagement_type": "educational",
        "audience_reaction": "positive",
        "response_count": 8,
        "emoji_reactions": {"🌊": 5, "🔥": 3, "❤️": 2}
    }
    
    webhook_client.send_chat_interaction(chat1_data, stream_info)
    
    # Update viewer count
    stream_info["viewer_count"] = 67
    webhook_client.send_stream_stats(stream_info)
    
    # Simulate track 2: Florida Breaks
    print("\n🎧 Playing Track 2: Florida Breaks")
    time.sleep(5)
    track2_data = {
        "artist": "DJ Icey",
        "title": "Generate",
        "bpm": 135,
        "key": "G minor",
        "classification": {
            "main_genre": "breaks",
            "subgenre": "florida breaks",
            "confidence": 0.91,
            "characteristics": ["bouncy", "808-heavy", "party-driven", "electro-influenced"]
        }
    }
    
    webhook_client.send_track_classification(track2_data, stream_info)
    
    # Simulate chat interaction for track 2
    time.sleep(3)
    chat2_data = {
        "message_sent": "🌴 Florida breaks incoming! This is that classic Miami sound with 808 basslines and party energy. Perfect for getting the crowd moving! Anyone from the Florida scene?",
        "engagement_type": "hype",
        "audience_reaction": "positive",
        "response_count": 12,
        "emoji_reactions": {"🌴": 7, "🔥": 8, "💃": 4, "🕺": 3}
    }
    
    webhook_client.send_chat_interaction(chat2_data, stream_info)
    
    # Simulate track 3: Progressive House
    print("\n🎧 Playing Track 3: Progressive House")
    time.sleep(5)
    stream_info["viewer_count"] = 89
    track3_data = {
        "artist": "Eric Prydz",
        "title": "Opus",
        "bpm": 126,
        "key": "F# minor",
        "classification": {
            "main_genre": "house",
            "subgenre": "progressive house",
            "confidence": 0.94,
            "characteristics": ["building", "melodic", "emotional", "epic"]
        }
    }
    
    webhook_client.send_track_classification(track3_data, stream_info)
    
    # Simulate technical analysis chat
    time.sleep(2)
    chat3_data = {
        "message_sent": "🎛️ Smooth transition from 135 BPM breaks to 126 BPM progressive house! Notice how the key change from Gm to F#m creates perfect harmonic tension. This is textbook mixing technique!",
        "engagement_type": "technical",
        "audience_reaction": "positive",
        "response_count": 6,
        "emoji_reactions": {"🎛️": 4, "🧠": 3, "👨‍🎓": 2}
    }
    
    webhook_client.send_chat_interaction(chat3_data, stream_info)
    
    # End stream
    time.sleep(3)
    print("\n📺 Ending stream session")
    webhook_client.send_stream_stats(stream_info, "stream_end")
    
    print(f"\n✅ Stream session complete! Session ID: {webhook_client.session_id}")
    print("Check your webhook endpoint for all the received data!")

if __name__ == "__main__":
    # Test the webhook integration
    print("🎵 Live Stream Assistant Webhook Client Demo")
    print("=" * 50)
    
    try:
        simulate_live_stream_session()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
    
    print("\n🎯 Demo complete! This shows how the live stream assistant")
    print("   would integrate with your main taxonomy database via webhooks.")