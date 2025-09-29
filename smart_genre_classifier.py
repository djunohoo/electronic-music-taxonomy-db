#!/usr/bin/env python3
"""
Smart Genre Classifier for electronic music terms
Automatically categorizes terms as genre, subgenre, or other
"""

import re

def classify_music_term(term):
    """
    Classify a term as genre, subgenre, or other
    Returns tuple: (classification, clean_term, parent_genre)
    """
    term_lower = term.lower().strip()
    
    # Core genre patterns - these are primary genres
    core_genres = {
        'house': ['house'],
        'techno': ['techno'],
        'trance': ['trance'],
        'drum and bass': ['drum and bass', 'dnb', 'drum & bass', 'drum n bass'],
        'dubstep': ['dubstep'],
        'breaks': ['breaks', 'breakbeat', 'break beat'],
        'hardcore': ['hardcore'],
        'hardstyle': ['hardstyle'],
        'trap': ['trap'],
        'ambient': ['ambient'],
        'disco': ['disco'],
        'funk': ['funk'],
        'electronica': ['electronica'],
        'experimental': ['experimental'],
        'glitch': ['glitch'],
        'dancehall': ['dancehall'],
        'reggae': ['reggae'],
        'dance': ['dance'],
        'soul': ['soul'],
        'latin': ['latin'],
        'world': ['world']
    }
    
    # Subgenre patterns - these have parent genres
    subgenres = {
        # House subgenres
        'tech house': ('subgenre', 'tech house', 'house'),
        'deep house': ('subgenre', 'deep house', 'house'),
        'progressive house': ('subgenre', 'progressive house', 'house'),
        'electro house': ('subgenre', 'electro house', 'house'),
        'bass house': ('subgenre', 'bass house', 'house'),
        'funky house': ('subgenre', 'funky house', 'house'),
        'soulful house': ('subgenre', 'soulful house', 'house'),
        'afro house': ('subgenre', 'afro house', 'house'),
        'disco house': ('subgenre', 'disco house', 'house'),
        'tribal house': ('subgenre', 'tribal house', 'house'),
        'jackin house': ('subgenre', 'jackin house', 'house'),
        'french house': ('subgenre', 'french house', 'house'),
        'mainstage': ('subgenre', 'mainstage', 'house'),
        'main floor': ('subgenre', 'mainstage', 'house'),
        'main_floor': ('subgenre', 'mainstage', 'house'),
        
        # Techno subgenres
        'minimal techno': ('subgenre', 'minimal techno', 'techno'),
        'hard techno': ('subgenre', 'hard techno', 'techno'),
        'detroit techno': ('subgenre', 'detroit techno', 'techno'),
        'industrial techno': ('subgenre', 'industrial techno', 'techno'),
        'dub techno': ('subgenre', 'dub techno', 'techno'),
        'acid techno': ('subgenre', 'acid techno', 'techno'),
        'melodic techno': ('subgenre', 'melodic techno', 'techno'),
        
        # Trance subgenres
        'progressive trance': ('subgenre', 'progressive trance', 'trance'),
        'uplifting trance': ('subgenre', 'uplifting trance', 'trance'),
        'psy trance': ('subgenre', 'psy trance', 'trance'),
        'psytrance': ('subgenre', 'psytrance', 'trance'),
        'hard trance': ('subgenre', 'hard trance', 'trance'),
        'vocal trance': ('subgenre', 'vocal trance', 'trance'),
        'tech trance': ('subgenre', 'tech trance', 'trance'),
        
        # Drum & Bass subgenres
        'liquid dnb': ('subgenre', 'liquid dnb', 'drum and bass'),
        'liquid drum and bass': ('subgenre', 'liquid drum and bass', 'drum and bass'),
        'liquid': ('subgenre', 'liquid', 'drum and bass'),
        'intelligent': ('subgenre', 'intelligent', 'drum and bass'),
        'atmospheric': ('subgenre', 'atmospheric', 'drum and bass'),
        'neurofunk': ('subgenre', 'neurofunk', 'drum and bass'),
        'jump up': ('subgenre', 'jump up', 'drum and bass'),
        'hardstep': ('subgenre', 'hardstep', 'drum and bass'),
        'jungle': ('subgenre', 'jungle', 'drum and bass'),
        
        # Dubstep subgenres
        'brostep': ('subgenre', 'brostep', 'dubstep'),
        'melodic dubstep': ('subgenre', 'melodic dubstep', 'dubstep'),
        'riddim': ('subgenre', 'riddim', 'dubstep'),
        'chillstep': ('subgenre', 'chillstep', 'dubstep'),
        'future bass': ('subgenre', 'future bass', 'dubstep'),
        
        # Breaks subgenres
        'nu skool breaks': ('subgenre', 'nu skool breaks', 'breaks'),
        'progressive breaks': ('subgenre', 'progressive breaks', 'breaks'),
        'melodic breaks': ('subgenre', 'melodic breaks', 'breaks'),
        'acid breaks': ('subgenre', 'acid breaks', 'breaks'),
        'b-boy breaks': ('subgenre', 'b-boy breaks', 'breaks'),
        'electro breaks': ('subgenre', 'electro breaks', 'breaks'),
        'driving breaks': ('subgenre', 'driving breaks', 'breaks'),
        'funky breaks': ('subgenre', 'funky breaks', 'breaks'),
        'peak time _ driving': ('subgenre', 'driving breaks', 'breaks'),
        'peak_time___driving': ('subgenre', 'driving breaks', 'breaks'),
        'classic _ detroit _ modern': ('subgenre', 'electro', 'breaks'),
        'classic___detroit___modern': ('subgenre', 'electro', 'breaks'),
        'classic detroit modern': ('subgenre', 'electro', 'breaks'),
        'garage': ('subgenre', 'garage', 'breaks'),
        'electro': ('subgenre', 'electro', 'breaks'),
        
        # Additional genuine genres/styles found in collection
        'tribal': ('subgenre', 'tribal', 'house'),  # Most tribal is house-based
        'acoustic': ('style', 'acoustic', 'electronica'),
        'raw feel': ('style', 'raw', 'underground'),
        'old skool': ('style', 'old school', 'classic'),
        
        # Artist patterns indicating breaks subgenres
        'deejay_shaolin_rerub': ('subgenre', 'melodic breaks', 'breaks'),
        'deejay shaolin': ('subgenre', 'melodic breaks', 'breaks'),
        'dj brownie': ('subgenre', 'breaks', 'breaks'),  # Could be funky florida or electro breaks
        'axel von greiff': ('subgenre', 'progressive breaks', 'breaks'),
        'dave gluskin rmx': ('subgenre', 'breaks', 'breaks'),
        
        # Former garage subgenres (now under breaks)
        'uk garage': ('subgenre', 'uk garage', 'breaks'),
        'speed garage': ('subgenre', 'speed garage', 'breaks'),
        '2 step': ('subgenre', '2 step', 'breaks'),
        
        # Trap subgenres
        'future trap': ('subgenre', 'future trap', 'trap'),
        'hard trap': ('subgenre', 'hard trap', 'trap'),
        
        # Hardcore subgenres
        'gabber': ('subgenre', 'gabber', 'hardcore'),
        'happy hardcore': ('subgenre', 'happy hardcore', 'hardcore'),
        
        # Ambient subgenres
        'dark ambient': ('subgenre', 'dark ambient', 'ambient'),
        'drone': ('subgenre', 'drone', 'ambient'),
        'chillout': ('subgenre', 'chillout', 'ambient'),
        'downtempo': ('subgenre', 'downtempo', 'ambient'),
        
        # Disco subgenres
        'nu disco': ('subgenre', 'nu disco', 'disco'),
        
        # Other subgenres
        'tropical pop': ('subgenre', 'tropical pop', 'pop'),
        'new jack swing': ('subgenre', 'new jack swing', 'r&b'),
        'afrobeat': ('subgenre', 'afrobeat', 'world'),
        'reggaeton': ('subgenre', 'reggaeton', 'latin'),
        'idm': ('subgenre', 'idm', 'electronica')
    }
    
    # First check exact subgenre matches
    if term_lower in subgenres:
        return subgenres[term_lower]
    
    # Check for core genre matches
    for genre, patterns in core_genres.items():
        for pattern in patterns:
            if term_lower == pattern:
                return ('genre', genre, None)
    
    # Check if term contains a genre even with production terms
    for genre, patterns in core_genres.items():
        for pattern in patterns:
            if pattern in term_lower:
                # Check if it's actually a subgenre
                for subgenre_key, subgenre_data in subgenres.items():
                    if subgenre_key in term_lower:
                        return subgenre_data
                # If not a known subgenre, it's the core genre
                return ('genre', genre, None)
    
    # Check for subgenre patterns in compound terms
    for subgenre_key, subgenre_data in subgenres.items():
        if subgenre_key in term_lower:
            return subgenre_data
    
    # If we can't classify it, it's probably not a genre/subgenre
    return ('other', term, None)

def process_genre_list(terms):
    """Process a list of terms and categorize them"""
    results = {
        'genres': {},
        'subgenres': {},
        'other': []
    }
    
    for term in terms:
        classification, clean_term, parent_genre = classify_music_term(term)
        
        if classification == 'genre':
            if clean_term not in results['genres']:
                results['genres'][clean_term] = []
        elif classification == 'subgenre':
            if parent_genre not in results['subgenres']:
                results['subgenres'][parent_genre] = []
            if clean_term not in results['subgenres'][parent_genre]:
                results['subgenres'][parent_genre].append(clean_term)
        else:
            results['other'].append(term)
    
    return results

if __name__ == "__main__":
    # Test with some sample terms
    test_terms = [
        "house", "tech house", "deep house remix", "trance", "progressive trance",
        "drum and bass", "liquid dnb", "dubstep", "riddim", "breaks",
        "uk garage", "hardcore", "ambient", "random track name", "artist name"
    ]
    
    results = process_genre_list(test_terms)
    
    print("📋 AUTOMATIC GENRE CLASSIFICATION:")
    print("=" * 50)
    
    print("\n🎵 GENRES:")
    for genre in sorted(results['genres'].keys()):
        print(f"  • {genre}")
    
    print("\n🎶 SUBGENRES:")
    for parent_genre in sorted(results['subgenres'].keys()):
        print(f"  {parent_genre.upper()}:")
        for subgenre in sorted(results['subgenres'][parent_genre]):
            print(f"    - {subgenre}")
    
    print("\n❓ OTHER (needs manual classification):")
    for item in results['other']:
        print(f"  • {item}")