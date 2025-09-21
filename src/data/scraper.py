"""
Data scraping and processing from Wikipedia's List of Electronic Music Genres.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from dataclasses import dataclass

@dataclass
class GenreData:
    """Data structure for genre information."""
    name: str
    description: str
    wikipedia_url: str
    origin_year: Optional[int] = None
    origin_location: Optional[str] = None
    parent_genres: List[str] = None
    characteristics: List[Dict[str, str]] = None

class WikipediaGenreScraper:
    """Scraper for Wikipedia's List of Electronic Music Genres."""
    
    BASE_URL = "https://en.wikipedia.org/wiki/List_of_electronic_music_genres"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_genre_list(self) -> List[GenreData]:
        """Scrape the main genre list from Wikipedia."""
        response = self.session.get(self.BASE_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        genres = []
        
        # Find the main content div
        content = soup.find('div', {'class': 'mw-parser-output'})
        
        # Look for genre sections
        for section in content.find_all(['h2', 'h3', 'h4']):
            genre_name = self._clean_genre_name(section.get_text())
            if self._is_valid_genre(genre_name):
                genre_data = self._extract_genre_data(section, genre_name)
                if genre_data:
                    genres.append(genre_data)
        
        return genres
    
    def _clean_genre_name(self, name: str) -> str:
        """Clean and normalize genre name."""
        # Remove edit links and extra whitespace
        name = re.sub(r'\[edit\]', '', name).strip()
        # Remove section numbers
        name = re.sub(r'^\d+\.?\s*', '', name)
        return name
    
    def _is_valid_genre(self, name: str) -> bool:
        """Check if the name represents a valid genre."""
        invalid_sections = [
            'contents', 'references', 'external links', 'see also',
            'notes', 'bibliography', 'further reading'
        ]
        return (
            len(name) > 2 and 
            name.lower() not in invalid_sections and
            not name.startswith('List of') and
            not name.startswith('Category:')
        )
    
    def _extract_genre_data(self, section, genre_name: str) -> Optional[GenreData]:
        """Extract detailed data for a genre."""
        # Find the next paragraph or list after the heading
        next_element = section.find_next_sibling(['p', 'ul', 'div'])
        description = ""
        
        if next_element and next_element.name == 'p':
            description = next_element.get_text().strip()
        
        # Extract Wikipedia URL if available
        genre_link = section.find('a')
        wikipedia_url = ""
        if genre_link and genre_link.get('href'):
            href = genre_link.get('href')
            if href.startswith('/wiki/'):
                wikipedia_url = f"https://en.wikipedia.org{href}"
        
        # Extract year and location from description
        origin_year = self._extract_year(description)
        origin_location = self._extract_location(description)
        
        return GenreData(
            name=genre_name,
            description=description,
            wikipedia_url=wikipedia_url,
            origin_year=origin_year,
            origin_location=origin_location,
            characteristics=[]
        )
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract origin year from text."""
        # Look for patterns like "1980s", "early 1990s", "1995"
        year_patterns = [
            r'\b(19|20)\d{2}\b',  # Exact year
            r'\b(19|20)\d{2}s\b'  # Decade
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text)
            if match:
                year_str = match.group()
                if year_str.endswith('s'):
                    return int(year_str[:-1])  # Remove 's' from decade
                return int(year_str)
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract origin location from text."""
        # Common location patterns
        location_patterns = [
            r'\b(Detroit|Chicago|London|Berlin|Manchester|New York|Los Angeles|Miami|Ibiza)\b',
            r'\b(UK|USA|US|Germany|France|Italy|Netherlands|Belgium)\b',
            r'\b(United States|United Kingdom|Electronic music)\b'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return None

class GenreCharacteristicsExtractor:
    """Extract musical characteristics from genre descriptions."""
    
    def extract_tempo_info(self, description: str) -> Dict[str, str]:
        """Extract BPM and tempo information."""
        tempo_info = {}
        
        # BPM patterns
        bpm_pattern = r'(\d{2,3})\s*[-–]\s*(\d{2,3})\s*BPM'
        bpm_match = re.search(bpm_pattern, description, re.IGNORECASE)
        
        if bpm_match:
            tempo_info['bpm_min'] = bpm_match.group(1)
            tempo_info['bpm_max'] = bpm_match.group(2)
        
        # Tempo descriptors
        tempo_descriptors = ['slow', 'fast', 'moderate', 'uptempo', 'downtempo']
        for descriptor in tempo_descriptors:
            if descriptor in description.lower():
                tempo_info['tempo_style'] = descriptor
                break
        
        return tempo_info
    
    def extract_instruments(self, description: str) -> List[str]:
        """Extract typical instruments and equipment."""
        instruments = []
        
        # Common electronic music equipment
        equipment_patterns = [
            r'\b(synthesizer|synth|drum machine|sampler|sequencer)\b',
            r'\b(808|909|303|Jupiter|Moog|Prophet)\b',  # Specific models
            r'\b(bass|bassline|lead|pad|arp)\b',  # Synth types
        ]
        
        for pattern in equipment_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            instruments.extend(matches)
        
        return list(set(instruments))  # Remove duplicates

if __name__ == "__main__":
    scraper = WikipediaGenreScraper()
    genres = scraper.scrape_genre_list()
    print(f"Scraped {len(genres)} genres")
    for genre in genres[:5]:  # Print first 5
        print(f"- {genre.name}: {genre.description[:100]}...")