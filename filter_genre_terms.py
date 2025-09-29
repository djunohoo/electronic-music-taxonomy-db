#!/usr/bin/env python3
"""
Filter genre terms to remove remix/production related terms
Keep only actual genre and subgenre terms
"""

import re

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

def filter_genre_terms(input_file="genre_terms.txt"):
    """Filter genre terms from scanner output"""
    
    # Read the scanner output to extract just the terms
    print("🔍 Filtering genre terms from scanner output...")
    
    # Read from the previous scanner output (hardcoded for now)
    # In a real scenario, we'd parse the actual output file
    raw_terms = []
    
    # For now, let's create a sample from the output we saw
    # This would normally read from a file or pipe
    sample_terms = [
        "house", "tech house", "deep house", "progressive house", 
        "techno", "minimal techno", "hard techno", "trance",
        "drum and bass", "dnb", "dubstep", "garage", "uk garage",
        "ambient", "breakbeat", "hardcore", "jungle", "trap",
        "bass house", "electro house", "tribal house", "acid techno",
        "progressive trance", "psytrance", "liquid dnb", "neurofunk",
        "melodic dubstep", "riddim", "future bass", "hardstyle",
        "gabber", "happy hardcore", "speed garage", "2 step",
        "nu disco", "french house", "afro house", "soulful house",
        "funky house", "jackin house", "disco house", "tribal",
        "afrobeat", "reggae", "dub", "dancehall", "reggaeton",
        "latin", "world", "funk", "disco", "electronica", "idm",
        "glitch", "experimental", "chillout", "downtempo",
        "dark ambient", "drone", "breaks", "nu skool breaks",
        "progressive breaks", "industrial techno", "dub techno",
        "detroit techno", "uplifting trance", "vocal trance",
        "tech trance", "hard trance", "jump up", "hardstep",
        "brostep", "chillstep", "new jack swing", "tropical pop"
    ]
    
    # Filter out production terms
    filtered_terms = []
    for term in sample_terms:
        if not is_production_term(term):
            filtered_terms.append(term)
    
    # Remove duplicates and sort
    unique_filtered = sorted(list(set(filtered_terms)))
    
    print(f"✅ Filtered {len(sample_terms)} terms down to {len(unique_filtered)} genre/subgenre terms")
    
    return unique_filtered

if __name__ == "__main__":
    filtered_terms = filter_genre_terms()
    
    print(f"\n📋 FILTERED GENRE/SUBGENRE TERMS:")
    print("=" * 50)
    
    for i, term in enumerate(filtered_terms, 1):
        print(f"{i:3d}. {term}")
    
    print(f"\n🎯 Total filtered terms: {len(filtered_terms)}")