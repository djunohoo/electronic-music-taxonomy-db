#!/usr/bin/env python3
"""
v3.2 Classification Test Suite - Real World Performance Analysis
Test our enhanced 70+ subgenre system on 250 random files and generate insights
"""

import os
import random
import json
from pathlib import Path
from genre_scanner import classify_music_term
from collections import defaultdict, Counter
import time

def find_music_files(base_path, max_files=250):
    """Find random music files for testing"""
    music_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'}
    music_files = []
    
    print(f"🔍 Scanning for music files in: {base_path}")
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in music_extensions):
                music_files.append(os.path.join(root, file))
                
                # Show progress every 1000 files
                if len(music_files) % 1000 == 0:
                    print(f"   Found {len(music_files)} files so far...")
    
    print(f"✅ Total files found: {len(music_files)}")
    
    # Randomly sample the requested number
    if len(music_files) > max_files:
        selected_files = random.sample(music_files, max_files)
        print(f"🎲 Randomly selected {max_files} files for testing")
    else:
        selected_files = music_files
        print(f"📁 Using all {len(selected_files)} files found")
    
    return selected_files

def analyze_classification_results(results):
    """Analyze and generate insights from classification results"""
    
    # Basic stats
    total_files = len(results)
    classified_files = len([r for r in results if r['classification'] != 'unclassified'])
    unclassified_files = total_files - classified_files
    
    # Genre breakdown
    main_genres = Counter()  
    subgenres = Counter()
    confidence_scores = []
    
    # Pattern analysis
    classification_patterns = defaultdict(list)
    filename_patterns = defaultdict(int)
    path_patterns = defaultdict(int)
    
    for result in results:
        filename = result['filename']
        classification = result['classification']
        confidence = result.get('confidence', 0)
        
        if classification != 'unclassified':
            # Extract main genre and subgenre
            if result.get('parent_genre'):
                main_genres[result['parent_genre']] += 1
                subgenres[f"{result['parent_genre']} → {classification}"] += 1
            else:
                main_genres[classification] += 1
            
            confidence_scores.append(confidence if confidence > 0 else 1.0)
            
            # Pattern analysis
            classification_patterns[classification].append(filename)
            
            # Analyze what patterns led to classification
            filename_lower = filename.lower()
            words = filename_lower.replace('_', ' ').replace('-', ' ').split()
            for word in words:
                if len(word) > 2:  # Skip very short words
                    filename_patterns[word] += 1
            
            # Path analysis
            path_parts = result['filepath'].lower().split(os.sep)
            for part in path_parts:
                if part and len(part) > 2:
                    path_patterns[part] += 1
    
    # Calculate statistics
    classification_rate = (classified_files / total_files) * 100
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    return {
        'summary': {
            'total_files': total_files,
            'classified_files': classified_files,
            'unclassified_files': unclassified_files,
            'classification_rate': classification_rate,
            'average_confidence': avg_confidence
        },
        'main_genres': dict(main_genres.most_common(20)),
        'subgenres': dict(subgenres.most_common(20)),
        'top_filename_patterns': dict(Counter(filename_patterns).most_common(20)),
        'top_path_patterns': dict(Counter(path_patterns).most_common(20)),
        'classification_examples': {
            genre: examples[:3] for genre, examples in classification_patterns.items() 
            if len(examples) >= 2  # Only show genres with multiple examples
        }
    }

def generate_performance_questions(analysis, results):
    """Generate insightful questions based on classification performance"""
    
    questions = []
    summary = analysis['summary']
    
    # Overall performance questions
    questions.append({
        'category': 'Overall Performance',
        'question': f"With a {summary['classification_rate']:.1f}% classification rate on 250 random files, how does our v3.2 system compare to the original v3.0 system that achieved 99.7% noise reduction?",
        'context': f"Classified {summary['classified_files']}/{summary['total_files']} files",
        'insight': 'This tests whether our comprehensive subgenre expansion maintained accuracy'
    })
    
    # Genre distribution questions
    top_genre = list(analysis['main_genres'].keys())[0] if analysis['main_genres'] else None
    if top_genre:
        questions.append({
            'category': 'Genre Distribution',
            'question': f"Why is '{top_genre}' the most frequently classified genre ({analysis['main_genres'][top_genre]} files)? Does this reflect the actual music collection or classification bias?",
            'context': f"Top 3 genres: {list(analysis['main_genres'].keys())[:3]}",
            'insight': 'This reveals whether our patterns favor certain genres over others'
        })
    
    # Subgenre accuracy questions
    if analysis['subgenres']:
        top_subgenre = list(analysis['subgenres'].keys())[0]
        questions.append({
            'category': 'Subgenre Performance', 
            'question': f"How accurate is our subgenre classification? The top result '{top_subgenre}' appears {list(analysis['subgenres'].values())[0]} times - are these correct classifications?",
            'context': f"Total unique subgenres detected: {len(analysis['subgenres'])}",
            'insight': 'This tests the precision of our 70+ subgenre taxonomy'
        })
    
    # Pattern recognition questions
    if analysis['top_filename_patterns']:
        top_pattern = list(analysis['top_filename_patterns'].keys())[0]
        pattern_count = analysis['top_filename_patterns'][top_pattern]
        questions.append({
            'category': 'Pattern Recognition',
            'question': f"The filename pattern '{top_pattern}' appears in {pattern_count} files. Is this pattern correctly driving classification decisions, or creating false positives?",
            'context': f"Top patterns: {list(analysis['top_filename_patterns'].keys())[:5]}",
            'insight': 'This evaluates whether our pattern matching is precise or too broad'
        })
    
    # Unclassified analysis
    if summary['unclassified_files'] > 0:
        unclassified_rate = (summary['unclassified_files'] / summary['total_files']) * 100
        questions.append({
            'category': 'Unclassified Files',
            'question': f"Why did {summary['unclassified_files']} files ({unclassified_rate:.1f}%) remain unclassified? Are these genuinely non-electronic music, or are we missing genre patterns?",
            'context': 'Manual review of unclassified files needed',
            'insight': 'This identifies gaps in our taxonomy coverage'
        })
    
    # Confidence analysis
    questions.append({
        'category': 'Classification Confidence',
        'question': f"With an average confidence of {summary['average_confidence']:.2f}, how reliable are our classifications? Should we set minimum confidence thresholds?",
        'context': f"Based on {len([r for r in results if r['classification'] != 'unclassified'])} classified files",
        'insight': 'This evaluates the reliability of our classification algorithm'
    })
    
    # New subgenre effectiveness
    new_subgenres = ['future house', 'minimal house', 'hard house', 'garage house', 'chicago house',
                    'rollers', 'halftime', 'clownstep', 'autonomic', 'drill n bass',
                    'balearic trance', 'euro trance', 'full-on psytrance', 'minimal psy',
                    'florida breaks', 'neuro breaks', 'psy breaks', 'dub breaks', 'tech breaks']
    
    detected_new = []
    for result in results:
        if result['classification'] in new_subgenres:
            detected_new.append(result['classification'])
    
    if detected_new:
        questions.append({
            'category': 'New Subgenre Detection',
            'question': f"Our v3.1 expansion added 30+ new subgenres. We detected {len(set(detected_new))} of them: {list(set(detected_new))}. Are these accurate classifications or false positives?",
            'context': f"New subgenres found: {Counter(detected_new)}",
            'insight': 'This validates whether our CSV catalog integration was successful'
        })
    
    return questions

def run_v32_classification_test(music_folder_path, sample_size=250):
    """Run comprehensive v3.2 classification test"""
    
    print("🎵 ELECTRONIC MUSIC TAXONOMY v3.2 - REAL WORLD TEST")
    print("=" * 60)
    print(f"📊 Testing enhanced 70+ subgenre system on {sample_size} random files")
    print("🎯 Goal: Validate comprehensive taxonomy performance in real-world conditions")
    print()
    
    # Find music files
    start_time = time.time()
    music_files = find_music_files(music_folder_path, sample_size)
    
    if not music_files:
        print("❌ No music files found! Please check the folder path.")
        return None
    
    print(f"\n🧪 STARTING CLASSIFICATION TEST")
    print("-" * 40)
    
    # Classify files
    results = []
    classified_count = 0
    
    for i, filepath in enumerate(music_files, 1):
        filename = os.path.basename(filepath)
        
        # Show progress
        if i % 25 == 0 or i == len(music_files):
            print(f"   Progress: {i}/{len(music_files)} files ({(i/len(music_files)*100):.1f}%)")
        
        # Classify the filename
        classification_result = classify_music_term(filename)
        
        result = {
            'filepath': filepath,
            'filename': filename,
            'classification': classification_result[1] if classification_result[0] in ['genre', 'subgenre'] else 'unclassified',
            'parent_genre': classification_result[2] if len(classification_result) > 2 else None,
            'confidence': 1.0 if classification_result[0] in ['genre', 'subgenre'] else 0.0
        }
        
        results.append(result)
        
        if result['classification'] != 'unclassified':
            classified_count += 1
    
    # Analyze results
    print(f"\n📈 ANALYZING RESULTS")
    print("-" * 40)
    
    analysis = analyze_classification_results(results)
    questions = generate_performance_questions(analysis, results)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Display results
    print(f"\n🎯 CLASSIFICATION SUMMARY")
    print("=" * 40)
    print(f"Files processed: {analysis['summary']['total_files']}")
    print(f"Successfully classified: {analysis['summary']['classified_files']}")
    print(f"Unclassified: {analysis['summary']['unclassified_files']}")
    print(f"Classification rate: {analysis['summary']['classification_rate']:.1f}%")
    print(f"Average confidence: {analysis['summary']['average_confidence']:.2f}")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Files per second: {len(music_files)/processing_time:.1f}")
    
    print(f"\n🎵 TOP GENRES DETECTED")
    print("-" * 30)
    for genre, count in list(analysis['main_genres'].items())[:10]:
        percentage = (count / classified_count) * 100 if classified_count > 0 else 0
        print(f"   {genre:<20} {count:>3} files ({percentage:>5.1f}%)")
    
    print(f"\n🎶 TOP SUBGENRES DETECTED")
    print("-" * 30)
    for subgenre, count in list(analysis['subgenres'].items())[:10]:
        percentage = (count / classified_count) * 100 if classified_count > 0 else 0
        print(f"   {subgenre:<30} {count:>3} files ({percentage:>5.1f}%)")
    
    print(f"\n❓ PERFORMANCE ANALYSIS QUESTIONS")
    print("=" * 50)
    
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. [{q['category']}]")
        print(f"   ❓ {q['question']}")
        print(f"   📊 Context: {q['context']}")
        print(f"   💡 Insight: {q['insight']}")
    
    # Save detailed results
    output_data = {
        'test_metadata': {
            'version': 'v3.2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sample_size': sample_size,
            'processing_time': processing_time,
            'files_per_second': len(music_files)/processing_time
        },
        'analysis': analysis,
        'questions': questions,
        'detailed_results': results[:50]  # First 50 results for manual review
    }
    
    with open('v32_classification_test_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: v32_classification_test_results.json")
    print(f"🎯 Manual review recommended for validation of key findings")
    
    return output_data

if __name__ == "__main__":
    # Test configuration
    MUSIC_FOLDER = r"X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\DJUNOHOO\1-Originals"
    SAMPLE_SIZE = 250
    
    print("🎵 Ready to test v3.2 classification system!")
    print(f"📁 Target folder: {MUSIC_FOLDER}")
    print(f"📊 Sample size: {SAMPLE_SIZE} files")
    print()
    
    if os.path.exists(MUSIC_FOLDER):
        results = run_v32_classification_test(MUSIC_FOLDER, SAMPLE_SIZE)
    else:
        print(f"❌ Folder not found: {MUSIC_FOLDER}")
        print("Please update the MUSIC_FOLDER path in the script and try again.")