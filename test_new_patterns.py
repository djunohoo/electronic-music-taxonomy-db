#!/usr/bin/env python3
"""
Test the new classification patterns we just added
"""

from smart_genre_classifier import classify_music_term

def test_new_patterns():
    """Test the new classification patterns"""
    test_cases = [
        # Test classic detroit modern pattern
        "classic detroit modern house track.mp3",
        "classic_detroit_modern_remix.wav",
        
        # Test artist patterns
        "deejay shaolin rerub - track name.mp3",
        "dj brownie - funky track.mp3",
        "axel von greiff - progressive track.wav", 
        "dave gluskin rmx track.mp3",
        
        # Test existing patterns still work
        "driving breaks track.mp3",
        "liquid dnb track.wav",
        "melodic breaks tune.mp3",
        
        # Test new genres found in collection
        "dance music track.mp3",
        "soul music track.wav",
        "tribal house track.mp3",
        "latin music track.mp3",
        "world music track.wav"
    ]
    
    print("🧪 TESTING NEW CLASSIFICATION PATTERNS")
    print("=" * 50)
    
    for test_file in test_cases:
        result = classify_music_term(test_file)
        if result:
            classification_type, name, parent = result
            if classification_type == 'genre':
                print(f"✅ {test_file[:40]:<40} → Genre: {name}")
            else:
                print(f"✅ {test_file[:40]:<40} → {name} ({parent})")
        else:
            print(f"❌ {test_file[:40]:<40} → Not classified")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_new_patterns()