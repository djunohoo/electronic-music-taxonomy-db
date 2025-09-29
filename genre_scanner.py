#!/usr/bin/env python3
"""
Genre/Subgenre Scanner for 1-originals folder
Extracts unique genre/subgenre terms from filenames and folder paths
"""

import os
import re
from pathlib import Path

def is_production_term(term):
    """Check if term is production-related rather than genre/subgenre"""
    production_patterns = [
        r'remix', r'mix', r'edit', r'version', r'dub', r'rework', r'remaster',
        r'bootleg', r'mashup', r'mash up', r'extended', r'radio', r'club',
        r'original', r'vocal', r'instrumental', r'acapella', r'vip',
        r'reinterpretation', r'treatment', r'interpretation', r'rethink',
        r'cut', r'loop', r'sample', r'pack', r'intro', r'outro',
        r'master', r'mastered', r'remastered', r'prod\.', r'produced',
        r'feat\.', r'featuring', r'vs\.', r'versus', r'meets',
        r'bpm', r'key', r'minute', r'second', r'hour',
        r'video', r'audio', r'official', r'unofficial', r'promo',
        r'release', r'ep', r'album', r'single', r'compilation',
        r'live', r'session', r'studio', r'demo', r'test',
        r'clean', r'dirty', r'explicit', r'censored',
        r'free', r'download', r'stream', r'preview',
        r'part', r'pt\.', r'vol\.', r'volume', r'chapter',
        r'records', r'recordings', r'music', r'entertainment',
        r'www\.', r'http', r'\.com', r'\.net', r'\.org',
        r'mp3', r'wav', r'flac', r'320', r'128',
        r'beatport', r'soundcloud', r'spotify', r'youtube',
        r'dropbox', r'bandcamp', r'mixcloud',
        r'january', r'february', r'march', r'april', r'may', r'june',
        r'july', r'august', r'september', r'october', r'november', r'december',
        r'2019', r'2020', r'2021', r'2022', r'2023', r'2024', r'2025',
        r'monday', r'tuesday', r'wednesday', r'thursday', r'friday', r'saturday', r'sunday'
    ]
    
    term_lower = term.lower().strip()
    
    # Check if term contains any production patterns
    for pattern in production_patterns:
        if re.search(pattern, term_lower):
            return True
    
    # Check if term is mostly numbers/symbols
    if re.match(r'^[0-9\-_\.\s]+$', term_lower):
        return True
    
    # Check if term is very short (likely not a genre)
    if len(term_lower.replace('_', '').replace('-', '').replace(' ', '')) < 3:
        return True
    
    return False

def extract_genre_terms(file_path):
    """Extract potential genre/subgenre terms from file path"""
    terms = set()
    
    # Common genre patterns to look for
    genre_patterns = [
        r'\b(house|tech house|deep house|progressive house|electro house|bass house|funky house|soulful house|afro house|disco house|tribal house|jackin house)\b',
        r'\b(techno|minimal techno|hard techno|detroit techno|industrial techno|dub techno|acid techno)\b',
        r'\b(trance|progressive trance|uplifting trance|psy trance|hard trance|vocal trance|tech trance)\b',
        r'\b(drum.*bass|dnb|liquid dnb|neurofunk|jungle|jump up|hardstep)\b',
        r'\b(dubstep|brostep|melodic dubstep|riddim|chillstep|future bass)\b',
        r'\b(breaks|breakbeat|nu skool breaks|progressive breaks)\b',
        r'\b(ambient|dark ambient|drone|chillout|downtempo)\b',
        r'\b(garage|uk garage|speed garage|2 step)\b',
        r'\b(trap|future trap|hard trap)\b',
        r'\b(hardstyle|hardcore|gabber|happy hardcore)\b',
        r'\b(electronica|idm|glitch|experimental)\b',
        r'\b(funk|disco|nu disco|french house)\b',
        r'\b(reggae|dub|reggaeton|dancehall)\b',
        r'\b(latin|tribal|afrobeat|world)\b'
    ]
    
    # Convert path to lowercase for matching
    path_lower = file_path.lower()
    
    # Extract from folder names and filename
    for pattern in genre_patterns:
        matches = re.findall(pattern, path_lower, re.IGNORECASE)
        for match in matches:
            if not is_production_term(match):
                terms.add(match.strip())
    
    # Look for other potential genre terms in brackets/parentheses
    label_patterns = re.findall(r'\[(.*?)\]|\((.*?)\)', path_lower)
    for pattern_group in label_patterns:
        for item in pattern_group:
            if item and len(item) > 2 and not is_production_term(item):
                terms.add(item.strip())
    
    return terms

def scan_originals_folder():
    """Scan a folder for unique genre/subgenre terms"""
    import sys
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals"
    
    if not os.path.exists(base_path):
        print(f"❌ Folder '{base_path}' not found")
        return []
    
    print(f"🔍 Scanning {base_path} recursively...")
    
    all_terms = set()
    file_count = 0
    
    # Walk through all files
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, base_path)
            # Extract terms from this file path
            terms = extract_genre_terms(relative_path)
            all_terms.update(terms)
            file_count += 1
            if file_count % 100 == 0:
                print(f"  Processed {file_count} files, found {len(all_terms)} unique terms...")
    print(f"✅ Scan complete: {file_count} files processed")
    print(f"📊 Found {len(all_terms)} unique terms")
    
    # Filter out production-related terms
    filtered_terms = set()
    for term in all_terms:
        if not is_production_term(term):
            filtered_terms.add(term)
    
    print(f"📊 After filtering: {len(filtered_terms)} genre/subgenre terms (removed {len(all_terms) - len(filtered_terms)} production terms)")
    
    # Sort terms alphabetically for easier review
    sorted_terms = sorted(list(filtered_terms))
    return sorted_terms

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
        'uk garage': ['uk garage', 'garage'],
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
        'electro': ('subgenre', 'electro', 'breaks'),
        
        # UK Garage subgenres  
        '2-step': ('subgenre', '2-step', 'uk garage'),
        'speed garage': ('subgenre', 'speed garage', 'uk garage'),
        
        # Comprehensive House subgenres from catalog
        'future house': ('subgenre', 'future house', 'house'),
        'minimal house': ('subgenre', 'minimal house', 'house'),
        'hard house': ('subgenre', 'hard house', 'house'),
        'garage house': ('subgenre', 'garage house', 'house'),
        'chicago house': ('subgenre', 'chicago house', 'house'),
        'acid house': ('subgenre', 'acid house', 'house'),
        'melodic house': ('subgenre', 'melodic house', 'house'),
        'ghetto house': ('subgenre', 'ghetto house', 'house'),
        
        # Comprehensive DnB subgenres from catalog
        'rollers': ('subgenre', 'rollers', 'drum and bass'),
        'halftime': ('subgenre', 'halftime', 'drum and bass'),
        'clownstep': ('subgenre', 'clownstep', 'drum and bass'),
        'autonomic': ('subgenre', 'autonomic', 'drum and bass'),
        'drill n bass': ('subgenre', 'drill n bass', 'drum and bass'),
        'dancefloor dnb': ('subgenre', 'dancefloor dnb', 'drum and bass'),
        'ragga jungle': ('subgenre', 'ragga jungle', 'drum and bass'),
        'drumfunk': ('subgenre', 'drumfunk', 'drum and bass'),
        'minimal dnb': ('subgenre', 'minimal dnb', 'drum and bass'),
        
        # Comprehensive Trance subgenres from catalog
        'balearic trance': ('subgenre', 'balearic trance', 'trance'),
        'euro trance': ('subgenre', 'euro trance', 'trance'),
        'full-on psytrance': ('subgenre', 'full-on psytrance', 'trance'),
        'minimal psy': ('subgenre', 'minimal psy', 'trance'),
        'dark trance': ('subgenre', 'dark trance', 'trance'),
        'acid trance': ('subgenre', 'acid trance', 'trance'),
        'classic trance': ('subgenre', 'classic trance', 'trance'),
        'ambient trance': ('subgenre', 'ambient trance', 'trance'),
        'orchestral trance': ('subgenre', 'orchestral trance', 'trance'),
        
        # Comprehensive Breakbeat subgenres from catalog
        'florida breaks': ('subgenre', 'florida breaks', 'breaks'),
        'funky breaks': ('subgenre', 'funky breaks', 'breaks'),
        'neuro breaks': ('subgenre', 'neuro breaks', 'breaks'),
        'psy breaks': ('subgenre', 'psy breaks', 'breaks'),
        'dub breaks': ('subgenre', 'dub breaks', 'breaks'),
        'tech breaks': ('subgenre', 'tech breaks', 'breaks'),
        'trap breaks': ('subgenre', 'trap breaks', 'breaks'),
        'bassline breaks': ('subgenre', 'bassline breaks', 'breaks'),
        'bass breaks': ('subgenre', 'bass breaks', 'breaks'),
        'uk breaks': ('subgenre', 'uk breaks', 'breaks'),
        'rave breaks': ('subgenre', 'rave breaks', 'breaks'),
        'booty breaks': ('subgenre', 'booty breaks', 'breaks'),
        'ghetto breaks': ('subgenre', 'ghetto breaks', 'breaks'),
        'ambient breaks': ('subgenre', 'ambient breaks', 'breaks'),
        'chill breaks': ('subgenre', 'chill breaks', 'breaks'),
        
        # Additional genuine genres/styles found in collection
        'tribal': ('subgenre', 'tribal', 'house'),  # Most tribal is house-based
        'acoustic': ('style', 'acoustic', 'electronica'),
        'raw feel': ('style', 'raw', 'underground'),
        'old skool': ('style', 'old school', 'classic'),
        
        # Major subgenres from comprehensive genre analysis
        'psytrance': ('subgenre', 'psytrance', 'trance'),
        'goa trance': ('subgenre', 'goa trance', 'trance'),
        'big beat': ('subgenre', 'big beat', 'breakbeat'),
        'neurofunk': ('subgenre', 'neurofunk', 'drum and bass'),
        'brostep': ('subgenre', 'brostep', 'dubstep'),
        '2-step': ('subgenre', '2-step', 'uk garage'),
        'speed garage': ('subgenre', 'speed garage', 'uk garage'),
        'gabber': ('subgenre', 'gabber', 'hardcore'),
        'happy hardcore': ('subgenre', 'happy hardcore', 'hardcore'),
        'rawstyle': ('subgenre', 'rawstyle', 'hardstyle'),
        'euphoric hardstyle': ('subgenre', 'euphoric hardstyle', 'hardstyle'),
        
        # Artist patterns indicating breaks subgenres
        'deejay_shaolin_rerub': ('subgenre', 'melodic breaks', 'breaks'),
        'deejay shaolin': ('subgenre', 'melodic breaks', 'breaks'),
        'dj brownie': ('subgenre', 'breaks', 'breaks'),  # Could be funky florida or electro breaks
        'axel von greiff': ('subgenre', 'progressive breaks', 'breaks'),
        'dave gluskin rmx': ('subgenre', 'breaks', 'breaks'),
        
        # Additional Hardstyle subgenres
        'rawstyle': ('subgenre', 'rawstyle', 'hardstyle'),
        'euphoric hardstyle': ('subgenre', 'euphoric hardstyle', 'hardstyle'),
        
        # Trap subgenres
        'future trap': ('subgenre', 'future trap', 'trap'),
        'hard trap': ('subgenre', 'hard trap', 'trap'),
        
        # Hardcore subgenres
        'hardcore techno': ('subgenre', 'hardcore techno', 'hardcore'),
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
    
    # Check for core genre matches (exact matches first)
    for genre, patterns in core_genres.items():
        for pattern in sorted(patterns, key=len, reverse=True):  # Check longer patterns first
            if term_lower == pattern:
                return ('genre', genre, None)
    
    # Check if term contains a genre even with production terms (longer patterns first)
    for genre, patterns in core_genres.items():
        for pattern in sorted(patterns, key=len, reverse=True):  # Check longer patterns first
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

if __name__ == "__main__":
    unique_terms = scan_originals_folder()
    
    # Classify all terms automatically
    results = {
        'genres': set(),
        'subgenres': {},
        'other': []
    }
    
    for term in unique_terms:
        classification, clean_term, parent_genre = classify_music_term(term)
        
        if classification == 'genre':
            results['genres'].add(clean_term)
        elif classification == 'subgenre':
            if parent_genre not in results['subgenres']:
                results['subgenres'][parent_genre] = set()
            results['subgenres'][parent_genre].add(clean_term)
        else:
            results['other'].append(term)
    
    print(f"\n📋 AUTOMATIC CLASSIFICATION RESULTS:")
    print("=" * 50)
    
    print(f"\n🎵 GENRES ({len(results['genres'])}):")
    for genre in sorted(results['genres']):
        print(f"  • {genre}")
    
    print(f"\n🎶 SUBGENRES:")
    total_subgenres = 0
    for parent_genre in sorted(results['subgenres'].keys()):
        subgenres_list = sorted(results['subgenres'][parent_genre])
        total_subgenres += len(subgenres_list)
        print(f"  {parent_genre.upper()} ({len(subgenres_list)}):")
        for subgenre in subgenres_list:
            print(f"    - {subgenre}")
    
    print(f"\n❓ NEEDS MANUAL CLASSIFICATION ({len(results['other'])}):")
    for i, item in enumerate(results['other'], 1):
        print(f"{i:3d}. {item}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Genres: {len(results['genres'])}")
    print(f"  Subgenres: {total_subgenres}")
    print(f"  Needs classification: {len(results['other'])}")
    print(f"  Total processed: {len(unique_terms)}")