#!/usr/bin/env python3
"""
Enhanced genre filter to remove non-genre terms from classification results
"""

def is_definitely_not_genre(term):
    """
    Aggressive filtering to remove terms that are definitely not genres/subgenres
    """
    term_lower = term.lower().strip()
    
    # Skip very short terms (likely codes/abbreviations)
    if len(term_lower) <= 3:
        return True
    
    # Artist/remixer patterns
    artist_patterns = [
        'rmx', 'remix', 'rerub', 'rework', 'edit', 'flip', 'bootleg',
        'mash', 'remode', 'retouch', 'refresh', 'rendition',
        'dj ', 'feat ', 'ft.', 'ft ', 'with ', '&amp;', 'aka ',
        'presents', 'vs ', 'x ', 'and ', 'the '
    ]
    
    # Label/catalog/technical patterns  
    technical_patterns = [
        'cd ', 'vol', 'ep', 'lp', 'single', 'album',
        'rec', 'records', 'music', 'media', 'trax',
        'exclusive', 'digital', 'vinyl', 'release',
        'out now', 'bonus', 'main', 'full', 'voxless',
        'min', 'sec', 'bpm', 'key', 'mix', 'version'
    ]
    
    # Random codes/numbers/special chars
    code_patterns = [
        r'^\d+[a-z]\d+$',  # 033g02, 124-a
        r'^[a-z]\d+[a-z]\d+$',  # 4q0u8v
        r'^[a-z]+\d+$',  # asot679, htcb02
        r'^\d+\w*$',  # numbers
        r'^[a-z]{1,6}\d+[a-z]*$'  # short codes
    ]
    
    # Song title indicators
    song_patterns = [
        'i ', 'you ', 'my ', 'the ', 'a ', 'an ', 'on ', 'in ', 'for ',
        'never ', 'always ', 'forever ', 'tonight ', 'today ',
        'feel ', 'love ', 'like ', 'want ', 'need ', 'got ',
        'when ', 'where ', 'how ', 'what ', 'why ',
        'all ', 'every', 'some', 'any'
    ]
    
    # Location indicators
    location_patterns = [
        'city', 'beach', 'angeles', 'mexico', 'italy', 'spain', 
        'detroit', 'london', 'berlin', 'miami', 'ibiza'
    ]
    
    # Check against all patterns
    import re
    
    # Check artist patterns
    for pattern in artist_patterns:
        if pattern in term_lower:
            return True
    
    # Check technical patterns        
    for pattern in technical_patterns:
        if pattern in term_lower:
            return True
            
    # Check song patterns
    for pattern in song_patterns:
        if term_lower.startswith(pattern) or f' {pattern}' in term_lower:
            return True
            
    # Check location patterns
    for pattern in location_patterns:
        if pattern in term_lower:
            return True
    
    # Check regex patterns for codes
    for pattern in code_patterns:
        if re.match(pattern, term_lower):
            return True
    
    # Special cases - obvious non-genres
    non_genres = [
        'acoustic', 'lyrics', 'instrumental', 'vocal', 'radio',
        'extended', 'original', 'club', 'radio edit', 'clean',
        'explicit', 'censored', 'live', 'studio', 'demo',
        'preview', 'snippet', 'intro', 'outro', 'interlude'
    ]
    
    for non_genre in non_genres:
        if non_genre in term_lower:
            return True
    
    return False

def filter_genuine_genres(terms_list):
    """
    Filter out non-genre terms and return only potential genres/subgenres
    """
    genuine_terms = []
    filtered_out = []
    
    for term in terms_list:
        if is_definitely_not_genre(term):
            filtered_out.append(term)
        else:
            genuine_terms.append(term)
    
    return genuine_terms, filtered_out

if __name__ == "__main__":
    # Test with some of the unclassified terms
    test_terms = [
        "#asot2015", "baby anne rerub", "acoustic", "tribal", "latin",
        "dance", "soul", "world", "4q0u8v", "dj brownie rmx",
        "feel good", "never let it go", "detroit calling", "liquid",
        "atmospheric", "funky florida", "florida", "breakbeat"
    ]
    
    genuine, filtered = filter_genuine_genres(test_terms)
    
    print("🎵 POTENTIAL GENRES/SUBGENRES:")
    for term in genuine:
        print(f"  ✅ {term}")
    
    print(f"\n❌ FILTERED OUT ({len(filtered)}):")
    for term in filtered:
        print(f"  🗑️ {term}")