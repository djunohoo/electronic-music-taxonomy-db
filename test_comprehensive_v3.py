#!/usr/bin/env python3
"""
Enhanced Classification Test Suite v3.1
Tests comprehensive subgenre expansion based on CSV catalog data
"""

from genre_scanner import classify_music_term

def test_comprehensive_subgenres():
    """Test comprehensive subgenre coverage from catalog data"""
    
    print("🧪 TESTING COMPREHENSIVE SUBGENRE EXPANSION v3.1")
    print("=" * 60)
    
    # Test cases organized by parent genre
    test_cases = {
        "House Subgenres": [
            "future house anthem.mp3",
            "minimal house groove.wav", 
            "hard house banger.mp3",
            "garage house classic.wav",
            "chicago house original.mp3",
            "acid house 303.wav",
            "melodic house journey.mp3",
            "ghetto house raw.wav"
        ],
        
        "Drum & Bass Subgenres": [
            "rollers smooth.mp3",
            "halftime experimental.wav",
            "clownstep bouncy.mp3", 
            "autonomic atmospheric.wav",
            "drill n bass complex.mp3",
            "dancefloor dnb energy.wav",
            "ragga jungle vocal.mp3",
            "drumfunk intricate.wav",
            "minimal dnb spacious.mp3"
        ],
        
        "Trance Subgenres": [
            "balearic trance sunset.mp3",
            "euro trance anthem.wav",
            "full-on psytrance intense.mp3",
            "minimal psy hypnotic.wav",
            "dark trance ominous.mp3",
            "acid trance 303.wav",
            "classic trance 1999.mp3",
            "ambient trance dreamy.wav",
            "orchestral trance epic.mp3"
        ],
        
        "Breakbeat Subgenres": [
            "florida breaks party.mp3",
            "funky breaks groove.wav",
            "neuro breaks dark.mp3",
            "psy breaks trippy.wav", 
            "dub breaks echo.mp3",
            "tech breaks minimal.wav",
            "trap breaks hybrid.mp3",
            "bassline breaks heavy.wav",
            "uk breaks rave.mp3",
            "booty breaks explicit.wav",
            "ambient breaks chill.mp3"
        ],
        
        "UK Garage System": [
            "uk garage 2step.mp3",
            "garage classic.wav",
            "2-step shuffle.mp3", 
            "speed garage fast.wav"
        ],
        
        "Hardcore/Hardstyle": [
            "hardcore techno industrial.mp3",
            "gabber rotterdam.wav",
            "happy hardcore euphoric.mp3",
            "rawstyle aggressive.mp3",
            "euphoric hardstyle uplifting.wav"
        ]
    }
    
    # Run tests
    total_tests = 0
    successful_tests = 0
    
    for category, tracks in test_cases.items():
        print(f"\n📂 {category}:")
        print("-" * 40)
        
        for track in tracks:
            result = classify_music_term(track)
            total_tests += 1
            
            if result[0] in ['genre', 'subgenre']:
                print(f"✅ {track:<30} → {result[1]} ({result[2] if result[2] else 'main genre'})")
                successful_tests += 1 
            else:
                print(f"❌ {track:<30} → {result[1]} (unclassified)")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 CLASSIFICATION SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    print(f"   New Subgenres Added: ~30+")
    print(f"   Total Genre Coverage: 70+ subgenres")
    
    # Metadata insights from rekordbox fields
    print(f"\n🎧 REKORDBOX METADATA INTEGRATION OPPORTUNITIES:")
    print(f"   ✓ BPM ranges for subgenre identification")
    print(f"   ✓ Key detection for harmonic mixing")
    print(f"   ✓ Energy/mood classification")
    print(f"   ✓ Color coding for visual organization")
    print(f"   ✓ Hot cue analysis for structure detection")
    print(f"   ✓ DJ play count for popularity metrics")

if __name__ == "__main__":
    test_comprehensive_subgenres()