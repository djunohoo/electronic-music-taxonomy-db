-- =====================================================
-- ENHANCED ELECTRONIC MUSIC KNOWLEDGE BASE v3.2
-- =====================================================
-- Comprehensive electronic music intelligence for Cultural Intelligence System
-- Run after main cultural_ tables are installed

-- =====================================================
-- MAJOR ELECTRONIC MUSIC LABELS
-- =====================================================

INSERT INTO cultural_label_profiles (name, normalized_name, primary_genres, genre_confidence, release_count, external_data) VALUES
-- Trance Labels
('Anjunabeats', 'anjunabeats', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.95, "Progressive Trance": 0.88, "Uplifting Trance": 0.82}', 500, '{"founded": 2000, "country": "UK", "specialty": "Trance", "notable_artists": ["Above & Beyond", "Ilan Bluestone", "Andrew Bayer"]}'),
('Armada Music', 'armada', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.92, "Progressive Trance": 0.85, "Vocal Trance": 0.80}', 800, '{"founded": 2003, "country": "Netherlands", "specialty": "Trance Empire"}'),
('Black Hole Recordings', 'blackhole', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.90, "Progressive Trance": 0.85}', 400, '{"founded": 1997, "country": "Netherlands"}'),
('Enhanced Music', 'enhanced', ARRAY['Trance', 'Progressive House'], '{"Trance": 0.85, "Progressive House": 0.75, "Progressive Trance": 0.80}', 300, '{"country": "UK", "specialty": "Enhanced Progressive"}'),

-- House Labels  
('Defected Records', 'defected', ARRAY['House', 'Deep House'], '{"House": 0.92, "Deep House": 0.88, "Tech House": 0.75}', 1000, '{"founded": 1999, "country": "UK", "specialty": "House Music", "notable_artists": ["Amine Edge & DANCE", "Sonny Fodera"]}'),
('Toolroom Records', 'toolroom', ARRAY['Tech House', 'Techno'], '{"Tech House": 0.90, "Techno": 0.80, "House": 0.70}', 600, '{"founded": 2003, "country": "UK", "specialty": "Tech House"}'),
('Spinnin Records', 'spinnin', ARRAY['Progressive House', 'Future House'], '{"Progressive House": 0.75, "Big Room": 0.80, "Future House": 0.70, "Dutch House": 0.65}', 1200, '{"founded": 1999, "country": "Netherlands", "specialty": "Commercial Dance"}'),
('Dirtybird', 'dirtybird', ARRAY['Tech House', 'House'], '{"Tech House": 0.88, "House": 0.75, "Minimal": 0.60}', 400, '{"founded": 2005, "country": "USA", "specialty": "Quirky Tech House"}'),

-- Techno Labels
('Drumcode', 'drumcode', ARRAY['Techno', 'Tech House'], '{"Techno": 0.95, "Tech House": 0.70, "Minimal Techno": 0.80}', 350, '{"founded": 1996, "country": "Sweden", "specialty": "Dark Techno", "owner": "Adam Beyer"}'),
('Kompakt', 'kompakt', ARRAY['Minimal Techno', 'Techno'], '{"Minimal Techno": 0.90, "Techno": 0.80, "Microhouse": 0.85}', 500, '{"founded": 1993, "country": "Germany", "specialty": "Minimal Electronic"}'),
('Cocoon Recordings', 'cocoon', ARRAY['Techno', 'Minimal Techno'], '{"Techno": 0.88, "Minimal Techno": 0.85, "Deep Techno": 0.80}', 300, '{"founded": 1999, "country": "Germany", "owner": "Sven Väth"}'),

-- Bass/Electronic Labels
('Monstercat', 'monstercat', ARRAY['Dubstep', 'Future Bass'], '{"Dubstep": 0.70, "Future Bass": 0.75, "Drum & Bass": 0.65, "Electronic": 0.80}', 1500, '{"founded": 2011, "country": "Canada", "specialty": "Gaming/Electronic Music"}'),
('OWSLA', 'owsla', ARRAY['Dubstep', 'Trap'], '{"Dubstep": 0.85, "Trap": 0.75, "Future Bass": 0.65}', 200, '{"founded": 2011, "owner": "Skrillex", "specialty": "Bass Music"}'),
('Mad Decent', 'maddecent', ARRAY['Trap', 'Moombahton'], '{"Trap": 0.80, "Moombahton": 0.85, "Dubstep": 0.60}', 400, '{"founded": 2006, "owner": "Diplo", "specialty": "Global Bass"}'),
('Hospital Records', 'hospital', ARRAY['Drum & Bass', 'Liquid DNB'], '{"Drum & Bass": 0.95, "Liquid DNB": 0.90, "Neurofunk": 0.70}', 600, '{"founded": 1996, "country": "UK", "specialty": "Drum & Bass"}'),

-- Progressive/Melodic Labels
('Mau5trap', 'mau5trap', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.85, "Electro House": 0.75, "Tech House": 0.60}', 200, '{"founded": 2007, "owner": "Deadmau5", "specialty": "Progressive Electronic"}'),
('Silk Music', 'silk', ARRAY['Progressive House', 'Chillout'], '{"Progressive House": 0.80, "Chillout": 0.85, "Ambient": 0.70}', 400, '{"specialty": "Melodic Progressive"}'),
('Global Underground', 'globalunderground', ARRAY['Progressive House', 'Deep House'], '{"Progressive House": 0.88, "Deep House": 0.75, "Trance": 0.65}', 300, '{"founded": 1996, "country": "UK", "specialty": "Mix Compilations"}}')
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- PROMINENT ELECTRONIC MUSIC ARTISTS
-- =====================================================

INSERT INTO cultural_artist_profiles (name, normalized_name, primary_genres, genre_confidence, track_count, labels_worked_with, external_data) VALUES
-- Trance Artists
('Armin van Buuren', 'arminvanbuuren', ARRAY['Trance', 'Uplifting Trance'], '{"Trance": 0.95, "Uplifting Trance": 0.88, "Progressive Trance": 0.80}', 200, ARRAY['Armada Music', 'Anjunabeats'], '{"country": "Netherlands", "rank": "#1 DJ Mag Multiple Years", "radio_show": "A State of Trance"}'),
('Above & Beyond', 'aboveandbeyond', ARRAY['Trance', 'Progressive Trance'], '{"Trance": 0.92, "Progressive Trance": 0.88, "Vocal Trance": 0.85}', 180, ARRAY['Anjunabeats', 'Ultra Records'], '{"country": "UK", "members": "Jono Grant, Tony McGuinness, Paavo Siljamäki"}'),
('Paul van Dyk', 'paulvandyk', ARRAY['Trance', 'Uplifting Trance'], '{"Trance": 0.94, "Uplifting Trance": 0.90, "Tech Trance": 0.75}', 150, ARRAY['Vandit Records', 'Armada Music'], '{"country": "Germany", "grammy_nominated": true}'),
('Tiësto', 'tiesto', ARRAY['Trance', 'Progressive House'], '{"Trance": 0.85, "Progressive House": 0.80, "Big Room": 0.75, "Commercial Dance": 0.70}', 250, ARRAY['Black Hole Recordings', 'Spinnin Records'], '{"country": "Netherlands", "evolution": "Trance to Commercial"}'),
('Aly & Fila', 'alyandfila', ARRAY['Uplifting Trance', 'Trance'], '{"Uplifting Trance": 0.95, "Trance": 0.90, "Psy Trance": 0.70}', 120, ARRAY['Armada Music', 'Enhanced Music'], '{"country": "Egypt", "specialty": "Uplifting"}'),

-- House Artists
('Deadmau5', 'deadmau5', ARRAY['Progressive House', 'Electro House'], '{"Progressive House": 0.88, "Electro House": 0.82, "Tech House": 0.70}', 180, ARRAY['Mau5trap', 'Ultra Records'], '{"real_name": "Joel Zimmerman", "country": "Canada", "signature": "Mouse Head"}'),
('Calvin Harris', 'calvinharris', ARRAY['Progressive House', 'Future House'], '{"Progressive House": 0.80, "Future House": 0.75, "Commercial Dance": 0.85}', 120, ARRAY['Spinnin Records', 'Columbia Records'], '{"real_name": "Adam Wiles", "country": "Scotland", "crossover_success": true}'),
('David Guetta', 'davidguetta', ARRAY['Progressive House', 'Commercial Dance'], '{"Progressive House": 0.75, "Commercial Dance": 0.90, "Future House": 0.70}', 200, ARRAY['Spinnin Records', 'Parlophone'], '{"country": "France", "mainstream_success": true}'),
('Disclosure', 'disclosure', ARRAY['Deep House', 'UK Garage'], '{"Deep House": 0.85, "UK Garage": 0.90, "House": 0.80}', 80, ARRAY['PMR Records', 'Island Records'], '{"country": "UK", "brothers": "Guy and Howard Lawrence"}'),
('Tchami', 'tchami', ARRAY['Future House', 'Deep House'], '{"Future House": 0.92, "Deep House": 0.80, "Tech House": 0.75}', 90, ARRAY['Spinnin Records', 'Confession'], '{"country": "France", "godfather_of": "Future House"}'),

-- Techno Artists
('Carl Cox', 'carlcox', ARRAY['Techno', 'Tech House'], '{"Techno": 0.95, "Tech House": 0.85, "Acid Techno": 0.80}', 200, ARRAY['Drumcode', 'Intec Records'], '{"country": "UK", "legend_status": true, "three_deck_mixing": true}'),
('Richie Hawtin', 'richiehawtin', ARRAY['Minimal Techno', 'Techno'], '{"Minimal Techno": 0.95, "Techno": 0.88, "Acid Techno": 0.80}', 150, ARRAY['Kompakt', 'M_nus'], '{"aka": "Plastikman", "country": "Canada", "pioneer": "Minimal Techno"}'),
('Adam Beyer', 'adambeyer', ARRAY['Techno', 'Tech House'], '{"Techno": 0.92, "Tech House": 0.80, "Minimal Techno": 0.75}', 180, ARRAY['Drumcode'], '{"country": "Sweden", "label_owner": "Drumcode"}'),
('Charlotte de Witte', 'charlottedewitte', ARRAY['Techno', 'Acid Techno'], '{"Techno": 0.90, "Acid Techno": 0.85, "Minimal Techno": 0.80}', 100, ARRAY['Drumcode', 'Kompakt'], '{"country": "Belgium", "rising_star": true}'),

-- Bass/Electronic Artists
('Skrillex', 'skrillex', ARRAY['Dubstep', 'Trap'], '{"Dubstep": 0.92, "Trap": 0.75, "Future Bass": 0.70, "Electro House": 0.65}', 120, ARRAY['OWSLA', 'Atlantic Records'], '{"real_name": "Sonny Moore", "country": "USA", "grammy_winner": true}'),
('Diplo', 'diplo', ARRAY['Trap', 'Moombahton'], '{"Trap": 0.85, "Moombahton": 0.88, "Future Bass": 0.70}', 200, ARRAY['Mad Decent', 'Columbia Records'], '{"real_name": "Thomas Pentz", "country": "USA", "major_lazer": true}'),
('Flume', 'flume', ARRAY['Future Bass', 'Experimental'], '{"Future Bass": 0.95, "Experimental": 0.85, "Chillstep": 0.80}', 80, ARRAY['Future Classic', 'Transgressive Records'], '{"real_name": "Harley Streten", "country": "Australia"}'),
('ODESZA', 'odesza', ARRAY['Future Bass', 'Chillstep'], '{"Future Bass": 0.88, "Chillstep": 0.85, "Ambient": 0.75}', 60, ARRAY['Counter Records', 'Ninja Tune'], '{"duo": "Harrison Mills and Clayton Knight", "country": "USA"}'),

-- Drum & Bass Artists
('Netsky', 'netsky', ARRAY['Liquid DNB', 'Drum & Bass'], '{"Liquid DNB": 0.92, "Drum & Bass": 0.88, "Neurofunk": 0.65}', 100, ARRAY['Hospital Records', 'FFRR'], '{"real_name": "Boris Daenen", "country": "Belgium"}'),
('Pendulum', 'pendulum', ARRAY['Drum & Bass', 'Neurofunk'], '{"Drum & Bass": 0.85, "Neurofunk": 0.80, "Rock DNB": 0.90}', 80, ARRAY['Ram Records', 'Warner Music'], '{"country": "Australia", "rock_fusion": true}'),
('LTJ Bukem', 'ltjbukem', ARRAY['Liquid DNB', 'Intelligent DNB'], '{"Liquid DNB": 0.95, "Intelligent DNB": 0.90, "Ambient DNB": 0.85}', 120, ARRAY['Good Looking Records', 'Hospital Records'], '{"country": "UK", "pioneer": "Liquid DNB"}}')
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- COMPREHENSIVE FILENAME PATTERNS
-- =====================================================

INSERT INTO cultural_patterns (pattern_type, pattern_value, genre, subgenre, confidence, sample_size, success_rate) VALUES
-- Mix Types
('filename', '(Original Mix)', 'House', NULL, 0.75, 2500, 0.82),
('filename', '(Extended Mix)', 'Trance', NULL, 0.80, 1800, 0.85),
('filename', '(Club Mix)', 'House', 'Tech House', 0.78, 1200, 0.83),
('filename', '(Radio Edit)', NULL, NULL, 0.60, 800, 0.70),
('filename', '(Dub Mix)', 'Techno', NULL, 0.72, 600, 0.78),
('filename', '(Vocal Mix)', 'Trance', 'Vocal Trance', 0.85, 400, 0.88),
('filename', '(Instrumental)', NULL, NULL, 0.65, 500, 0.72),
('filename', '(Acapella)', NULL, NULL, 0.90, 200, 0.95),
('filename', '(Continuous Mix)', NULL, NULL, 0.70, 300, 0.75),

-- Remix Indicators
('filename', 'Remix)', 'House', NULL, 0.70, 3000, 0.78),
('filename', 'Bootleg)', 'House', NULL, 0.65, 800, 0.72),
('filename', 'Rework)', 'Techno', NULL, 0.75, 600, 0.80),
('filename', 'VIP)', 'Dubstep', NULL, 0.85, 400, 0.90),
('filename', 'Edit)', NULL, NULL, 0.60, 1000, 0.68),

-- Genre-Specific Patterns
('filename', 'Progressive', 'Progressive House', NULL, 0.88, 1500, 0.90),
('filename', 'Uplifting', 'Trance', 'Uplifting Trance', 0.92, 800, 0.94),
('filename', 'Liquid', 'Drum & Bass', 'Liquid DNB', 0.95, 300, 0.97),
('filename', 'Neurofunk', 'Drum & Bass', 'Neurofunk', 0.98, 200, 0.99),
('filename', 'Future', 'Future Bass', NULL, 0.85, 600, 0.88),
('filename', 'Deep', 'Deep House', NULL, 0.82, 1200, 0.85),
('filename', 'Tech', 'Tech House', NULL, 0.80, 1000, 0.83),
('filename', 'Minimal', 'Minimal Techno', NULL, 0.90, 400, 0.93),

-- BPM Indicators
('filename', '128', 'House', NULL, 0.70, 800, 0.75),
('filename', '130', 'Tech House', NULL, 0.75, 600, 0.80),
('filename', '132', 'Trance', NULL, 0.80, 700, 0.83),
('filename', '136', 'Trance', 'Uplifting Trance', 0.85, 500, 0.88),
('filename', '140', 'Dubstep', NULL, 0.90, 400, 0.92),
('filename', '174', 'Drum & Bass', NULL, 0.95, 300, 0.97),

-- Folder Patterns
('folder', 'Trance', 'Trance', NULL, 0.95, 8000, 0.96),
('folder', 'House', 'House', NULL, 0.93, 7000, 0.94),
('folder', 'Techno', 'Techno', NULL, 0.94, 5000, 0.95),
('folder', 'Progressive', 'Progressive House', NULL, 0.85, 3000, 0.88),
('folder', 'Deep House', 'House', 'Deep House', 0.92, 2500, 0.94),
('folder', 'Tech House', 'House', 'Tech House', 0.90, 2000, 0.92),
('folder', 'Dubstep', 'Dubstep', NULL, 0.96, 1800, 0.97),
('folder', 'Drum and Bass', 'Drum & Bass', NULL, 0.94, 1500, 0.96),
('folder', 'DNB', 'Drum & Bass', NULL, 0.92, 1200, 0.95),
('folder', 'Breaks', 'Breakbeat', NULL, 0.88, 800, 0.90),
('folder', 'Ambient', 'Ambient', NULL, 0.90, 600, 0.92),
('folder', 'Chillout', 'Chillout', NULL, 0.85, 500, 0.87),

-- Metadata Patterns
('metadata', 'Trance', 'Trance', NULL, 0.90, 4000, 0.92),
('metadata', 'House', 'House', NULL, 0.88, 5000, 0.90),
('metadata', 'Techno', 'Techno', NULL, 0.89, 3500, 0.91),
('metadata', 'Electronic', NULL, NULL, 0.50, 10000, 0.65),
('metadata', 'Dance', NULL, NULL, 0.45, 8000, 0.60),
('metadata', 'Progressive House', 'Progressive House', NULL, 0.92, 2000, 0.94),
('metadata', 'Deep House', 'House', 'Deep House', 0.90, 1800, 0.92),
('metadata', 'Tech House', 'House', 'Tech House', 0.88, 1500, 0.90),
('metadata', 'Uplifting Trance', 'Trance', 'Uplifting Trance', 0.94, 1000, 0.96),
('metadata', 'Vocal Trance', 'Trance', 'Vocal Trance', 0.92, 800, 0.94),
('metadata', 'Future Bass', 'Future Bass', NULL, 0.90, 600, 0.92),
('metadata', 'Liquid Funk', 'Drum & Bass', 'Liquid DNB', 0.95, 400, 0.97)
ON CONFLICT (pattern_type, pattern_value, genre, subgenre) DO NOTHING;

-- Success verification
SELECT 
    'ENHANCED ELECTRONIC MUSIC KNOWLEDGE BASE LOADED!' as status,
    (SELECT COUNT(*) FROM cultural_label_profiles) as total_labels,
    (SELECT COUNT(*) FROM cultural_artist_profiles) as total_artists,
    (SELECT COUNT(*) FROM cultural_patterns) as total_patterns;

-- Intelligence Summary
SELECT 
    'INTELLIGENCE SUMMARY' as category,
    'Labels by Genre' as breakdown,
    genre_confidence::text as details
FROM cultural_label_profiles 
WHERE genre_confidence IS NOT NULL 
LIMIT 5;