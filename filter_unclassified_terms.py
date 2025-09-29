#!/usr/bin/env python3
"""
Apply aggressive filtering to the 287 unclassified terms to find actual genres
"""

# The 287 unclassified terms from the scan
unclassified_terms = [
    "#asot2015", "- 10d", "- 10m", "- 11d", "- 11m", "- 12d", "- 12m",
    "033g02", "124-a min", "1hi72a", "2011 - rompecabeza", "4q0u8v", 
    "5e2n8y", "7re21z", "94j1ps", "9p4k3d", "9xo media", "_-_11m",
    "_soul_", "a better day", "a-aif", "a-aiff", "a_better_day",
    "about it", "abstraction", "acoustic", "african day", 
    "all the girls standing in the line for the bathroom",
    "armada collected markus schulz", "array", "art of trip", "asot679",
    "baby anne rerub", "bar25-052", "barong family", "bass in the place",
    "bear", "beatman and ludmilla rerub", "beatz", "beautiful needs",
    "bedroom muzik", "bfmb064", "bjorn akesson", "blaufield", "bonus track",
    "bonzai progressive", "borderline", "bre( - 11m", "bre(_-_11m",
    "broke classics", "but i didn't", "by adix6", "by_adix6",
    "cahulmafia.ru", "carlokou", "cd 1 assault", "chee & subtronics flip",
    "chiccaleaf (ita", "chp020", "col", "contemplating", "contour 1",
    "contour 2", "contour 3", "contour 4", "controversia (spinnin)",
    "cyo1u6", "da fresh rmx", "damon grey aka lucas reyes", "dance",
    "dance for me", "dash berlin mash-up", "decoder &( - 4m", "defected",
    "detroit calling", "digital exclusive", "diplo _ nina sky", "dj booty rmx",
    "dj drake", "dj ronald transition 98-125", "dj schmolli", "dj snow",
    "dj strobe soulful with hats", "dj topcat",
    "dj скай &amp; steve kauf mash-up", "dj_brownie_rmx",
    "dj_скай_&amp;_steve_kauf_mash-up", "earth people",
    "eat's 'twisted' remake", "edct", "edge1", "edge_1", "encore",
    "end is the beginning", "enhanced", "esp", "everybody dance now",
    "exit", "exx muzik", "fade away", "falling to pieces", "fast & furious",
    "feat bjoern bless", "feat denitia", "feat micah jey", "feat sia",
    "feat steff", "featured on armada sunset", "feel good", "feel my energy",
    "feel my love", "flashmob retouch", "fnl mstr", "for rock n_ roll",
    "for what_", "for_rock_n__roll", "forever", "framewerk rewerk",
    "fsoe", "ft tara mc donald", "ft. birdy & jaymes young", "ft. novel",
    "full", "futureshock main response", "general midi presents",
    "generation hex", "ger", "glasgow underground", "golden ticket",
    "good qual.", "guz (nl", "guz_(nl", "hear me tonight", "her vox",
    "here i am", "heroes", "however do you want me", "htcb02",
    "i think about you", "iku08b", "incorrect", "inland knights",
    "inland_knights", "inu", "irl", "ita", "italy", "john's quest",
    "joker remake", "just a little", "kdbfb3", "kono(usa",
    "krafty kuts re-kut", "latin", "lee coombs rerub", "leon (italy",
    "let the bass kick", "lion", "liva (br", "lmty", "long beach",
    "long_beach", "los angeles", "lost130", "lyrics", "m1c89s",
    "macarize", "main", "martin ez & brian boncher re-work",
    "martin flex 're-stitch'", "martin_ez_&_brian_boncher_re-work",
    "med", "merlyn's jackin grandtheft redo", "mexico city, mexico",
    "miau, tryple-d", "midnight riot", "minimalfreaks.pw",
    "move a little closer", "must be asked", "my daddy made that bass",
    "myon summer of love reboot", "n i g h t d r i v e iii", "na na na",
    "never let it go", "never_let_it_go", "nlmx3o", "no hype",
    "no, no, no", "novik", "nowhere nowhere", "objectiz-ed", "okay",
    "old skool slide", "on fire", "one", "oops!", "out now", "out_now",
    "parquet", "paul oakenfold",
    "paul oakenfold - full on fluoro 036 - 22.04.2014", "pawz",
    "peace to the hip hop crowd", "philly blunt mash", "philly_blunt_mash",
    "piss break", "playmobil", "pm90sw", "preaching paris", "qdion0",
    "qhp6gk", "r-you 100-122 transition", "rarri quick hit",
    "rarri_quick_hit", "raw feel", "recovery tech", "refined", "remode",
    "rick wain", "rob cokeless rendition", "run", "save the nightlife",
    "scott christina", "scott_christina", "set you", "shall not fade",
    "sharaz", "she's homeless", "she's_homeless", "shes homeless",
    "shes_homeless", "simon templar refresh", "slip & slide", "snoe",
    "so fuck you", "solotoko", "soso", "soul", "soulflul",
    "sounds of meow", "sounds_of_meow", "spain", "state of", "stay high",
    "stc", "stmpd rcrds", "stronger on my own", "suara", "swingin'",
    "tecktonik battle 2009", "that zipper track", "that_zipper_track",
    "the earth is burning", "the energy", "thriller", "throw ya hands up",
    "till the break of dawn", "tim davison", "to feel food", "to feel good",
    "toolroom trax", "tribal", "tronic", "tropical_pop", "u & i",
    "up by longer_7", "usanza", "uxj492", "victor menegaux", "vj7gpm",
    "vkior5", "voxless", "waiting 4 u", "when i think of you", "wingman",
    "with ellie goulding", "with josh pan and x&g", "with scrufizzer",
    "with the ones that i came with", "wmkigx", "world", "y3o54y",
    "yin yang", "yin_yang", "you got me", "yr201", "zhomek b( - 9m"
]

def is_potential_genre(term):
    """Check if term could be a music genre or subgenre"""
    term_lower = term.lower().strip()
    
    # Skip very short terms and obvious codes
    if len(term_lower) <= 2 or term_lower.isdigit():
        return False
        
    # Skip terms with special characters that indicate non-genres
    if any(char in term_lower for char in ['(', ')', '[', ']', '#', '&', '_', '-']):
        # Exception for compound words like "drum_and_bass" 
        if not any(genre_word in term_lower for genre_word in ['drum', 'bass', 'house', 'breaks']):
            return False
    
    # Skip obvious artist/track/technical terms
    skip_patterns = [
        'rmx', 'remix', 'rerub', 'rework', 'edit', 'flip', 'mash', 'remode',
        'feat', 'ft.', 'ft ', 'with ', 'dj ', 'aka ', 'presents', 'vs ',
        'cd ', 'vol', 'ep', 'lp', 'exclusive', 'digital', 'bonus', 'main',
        'min', 'sec', 'bpm', 'mix', 'version', 'out now', 'records', 'music',
        'i ', 'you ', 'my ', 'the ', 'a ', 'an ', 'on ', 'in ', 'for ',
        'feel ', 'love ', 'like ', 'want ', 'need ', 'got ', 'never ',
        'city', 'beach', 'angeles', 'mexico', 'italy', 'spain', 'calling',
        'tonight', 'today', 'forever', 'always', 'here', 'there'
    ]
    
    for pattern in skip_patterns:
        if pattern in term_lower:
            return False
    
    # Potential genre words
    potential_genres = [
        'dance', 'soul', 'world', 'latin', 'tribal', 'acoustic',
        'abstract', 'experimental', 'ambient', 'minimal', 'deep',
        'dark', 'hard', 'soft', 'smooth', 'rough', 'raw', 'pure',
        'classic', 'modern', 'old', 'new', 'future', 'retro',
        'underground', 'mainstream', 'alternative', 'indie'
    ]
    
    for genre_word in potential_genres:
        if genre_word in term_lower:
            return True
    
    # Single meaningful words that could be genres
    if ' ' not in term_lower and len(term_lower) > 3:
        # Skip obvious non-genres
        non_genre_single = [
            'bear', 'lion', 'array', 'exit', 'one', 'run', 'okay',
            'heroes', 'thriller', 'forever', 'encore', 'refined'
        ]
        if term_lower not in non_genre_single:
            return True
    
    return False

# Filter the terms
potential_genres = []
filtered_out = []

for term in unclassified_terms:
    if is_potential_genre(term):
        potential_genres.append(term)
    else:
        filtered_out.append(term)

print(f"🎵 POTENTIAL GENRES/SUBGENRES ({len(potential_genres)}):")
for i, term in enumerate(potential_genres, 1):
    print(f"{i:2d}. {term}")

print(f"\n❌ NON-GENRE TERMS FILTERED OUT: {len(filtered_out)}/{len(unclassified_terms)}")
print(f"📊 REDUCTION: {len(filtered_out)}/{len(unclassified_terms)} = {100*len(filtered_out)/len(unclassified_terms):.1f}%")

if len(potential_genres) < 50:
    print(f"\n🎯 MANUAL REVIEW NEEDED FOR {len(potential_genres)} TERMS:")
    print("These terms might be actual genres/subgenres that need classification.")