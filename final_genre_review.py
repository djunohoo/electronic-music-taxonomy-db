#!/usr/bin/env python3
"""
Final manual review of potentially genuine genre terms
"""

# After aggressive filtering, manually review these potential genres
potential_genre_terms = [
    "abstraction", "acoustic", "beatz", "borderline", "dance", "defected",
    "enhanced", "glasgow underground", "golden ticket", "latin", "lyrics", 
    "old skool slide", "paul oakenfold", "raw feel", "soul", "soulflul", 
    "tribal", "tronic", "world"
]

# Actually meaningful genre terms from manual review
genuine_genres = {
    # Confirmed genres/subgenres that aren't already classified
    "dance": "genre - general dance music",
    "soul": "genre - soul/funk influenced electronic", 
    "tribal": "subgenre - tribal house/techno",
    "latin": "genre - latin influenced electronic",
    "world": "genre - world music fusion",
    "acoustic": "style - acoustic elements (not pure electronic)",
    "raw feel": "style - raw/underground sound",
    "old skool": "style - old school/classic style",
    
    # Labels/artists that might indicate styles but aren't genres
    "defected": "LABEL - Defected Records (house music)",
    "enhanced": "LABEL - Enhanced Music", 
    "glasgow underground": "LABEL - Glasgow Underground",
    "paul oakenfold": "ARTIST - not a genre",
    "tronic": "LABEL - Tronic Music",
    
    # Obvious non-genres to skip
    "beatz": "SKIP - generic term",
    "lyrics": "SKIP - not a genre", 
    "borderline": "SKIP - song title",
    "golden ticket": "SKIP - song title",
    "soulflul": "SKIP - misspelling of soulful (descriptor)"
}

print("🎯 FINAL GENRE CLASSIFICATION RESULTS")
print("=" * 50)

actual_genres = []
non_genres = []

for term, classification in genuine_genres.items():
    if classification.startswith("genre") or classification.startswith("subgenre") or classification.startswith("style"):
        actual_genres.append((term, classification))
        print(f"✅ {term:<15} → {classification}")
    else:
        non_genres.append((term, classification))

print(f"\n❌ NOT ACTUAL GENRES:")
for term, reason in non_genres:
    print(f"🗑️ {term:<15} → {reason}")

print(f"\n📊 FINAL SUMMARY:")
print(f"  • Started with: 287 unclassified terms")
print(f"  • After filtering: {len(genuine_genres)} potential terms reviewed")
print(f"  • Actual genres found: {len(actual_genres)}")
print(f"  • Non-genres identified: {len(non_genres)}")
print(f"  • Total reduction: {((287 - len(actual_genres)) / 287) * 100:.1f}%")

print(f"\n🎵 GENUINE MUSIC TERMS TO ADD TO CLASSIFICATION:")
for term, classification in actual_genres:
    print(f"  '{term}': {classification}")