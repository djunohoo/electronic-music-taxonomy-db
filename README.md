# Electronic Music Taxonomy Database

A comprehensive database system for categorizing and identifying electronic music genres with advanced taxonomy features including hierarchical relationships, BPM analysis, energy levels, and DJ mixing compatibility.

## 🎵 Enhanced Features

### Genre Taxonomy
- **Hierarchical Classification**: Parent-child relationships between genres and subgenres
- **BPM Ranges**: Minimum, maximum, and typical BPM values for each genre
- **Energy Levels**: 1-10 scale rating system for genre intensity
- **Keywords & Aliases**: Advanced detection system with weighted keywords
- **Mixing Compatibility**: AI-calculated compatibility scores between genres
- **Label Associations**: Record label connections with strength indicators
- **Related Genres**: Similarity detection and recommendations

### Audio Analysis
- **Feature Extraction**: Tempo, spectral, harmonic, and MFCC analysis
- **Genre Classification**: Machine learning-powered genre identification
- **BPM Detection**: Automatic tempo analysis
- **Harmonic Analysis**: Key and chord progression detection

### Web Interface
- **Genre Browser**: Interactive exploration with filtering and search
- **Detailed Genre Pages**: Comprehensive information including mixing tips
- **Audio Analyzer**: Upload and analyze audio files
- **Timeline Visualization**: Historical development of electronic music
- **Mixing Compatibility Matrix**: DJ-friendly genre relationships

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database**:
   ```bash
   python init_db.py
   ```

3. **Run the web application**:
   ```bash
   python run_app.py
   ```

4. **Access the application**: Open http://localhost:5000 in your browser

## 📊 Database Schema

### Core Models
- **Genres**: Main genre classification with enhanced metadata
- **Characteristics**: Detailed musical characteristics and features
- **Audio Features**: Technical audio analysis parameters
- **Timeline**: Historical events and genre evolution

### Enhanced Models
- **Genre Keywords**: Detection aliases and tags with weights
- **Record Labels**: Label information and genre associations
- **Mixing Compatibility**: DJ mixing compatibility scores
- **Label Associations**: Strength-rated label-genre connections

## 🎛️ API Endpoints

### Core Endpoints
- `GET /api/genres` - List all genres with enhanced data
- `GET /api/genres/{id}` - Detailed genre information
- `GET /api/search?q={query}` - Search functionality
- `POST /api/analyze` - Audio file analysis

### Enhanced Endpoints
- `GET /api/mixing-compatibility/{id}` - Genre mixing compatibility
- `GET /admin/load-enhanced-data` - Load enhanced taxonomy data
- `GET /mixing-compatibility` - Compatibility matrix visualization
- `GET /labels` - Record label directory

## 🏗️ Project Structure

```
taxonomy-db/
├── src/
│   ├── models/          # Enhanced database models
│   ├── analysis/        # Audio analysis and ML
│   ├── data/           # Data loading and Wikipedia scraping
│   │   ├── scraper.py          # Wikipedia data extraction
│   │   ├── data_loader.py      # Basic data loading
│   │   └── enhanced_loader.py  # Enhanced taxonomy features
│   └── web/            # Flask web application
│       ├── app.py              # Main application
│       └── templates/          # HTML templates
├── tests/              # Unit and integration tests
├── init_db.py         # Database initialization
├── run_app.py         # Application launcher
└── requirements.txt   # Python dependencies
```

## 🎯 Enhanced Features Detail

### Hierarchical Genre System
- **Parent Genres**: House, Techno, Trance, Drum & Bass, etc.
- **Subgenres**: Deep House, Tech House, Progressive Trance, Liquid D&B
- **Cross-relationships**: Genres can have multiple parents and children

### BPM Analysis
- **Range Detection**: Minimum and maximum BPM values
- **Typical BPM**: Most common tempo for each genre
- **Mixing Compatibility**: BPM-based compatibility scoring

### Energy Level System
```
1-3:  Ambient, Downtempo, Chill
4-6:  Deep House, Minimal, Lounge
7-8:  House, Techno, Breakbeat
9-10: Hard Techno, Hardcore, Gabber
```

### Keywords & Detection
- **Aliases**: Alternative names for genres
- **Tags**: Style descriptors and sub-classifications
- **Descriptors**: Musical characteristics and attributes
- **Weighted Scoring**: Importance-based keyword weighting

### Mixing Compatibility
- **BPM Compatibility**: Tempo difference calculations
- **Energy Compatibility**: Energy level similarity
- **Harmonic Compatibility**: Key relationship analysis
- **Overall Score**: Combined compatibility rating (0.0-1.0)

### Record Label Associations
- **Label Information**: Founding year, country, website
- **Genre Strength**: Association strength ratings
- **Artist Connections**: Key artists and releases

## 🧪 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Adding New Genres
1. Update `enhanced_loader.py` with new genre data
2. Include BPM ranges, energy levels, and keywords
3. Add hierarchical relationships if applicable
4. Run `python init_db.py` to update database

## 🎧 Usage Examples

### DJ Mixing Compatibility
```python
# Find genres compatible with House music
compatible = get_mixing_compatibility("House")
# Returns: Tech House (0.85), Deep House (0.78), Disco (0.72)
```

### Genre Detection
```python
# Analyze audio file
result = analyze_audio("track.wav")
# Returns: genre prediction, confidence, features
```

### BPM Matching
```python
# Find genres within BPM range
genres = find_genres_by_bpm(125, 130)
# Returns: House, Tech House, Deep House
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string
- `DEBUG`: Enable debug mode
- `SECRET_KEY`: Flask secret key

### Features Toggle
- Audio analysis requires librosa installation
- Wikipedia scraping needs internet connection
- ML classification requires trained models

## 📈 Data Sources

- **Wikipedia**: List of Electronic Music Genres
- **Audio Analysis**: librosa, scikit-learn
- **Genre Relationships**: Curated taxonomy data
- **BPM Data**: Community-sourced and analyzed
- **Label Information**: Music industry databases

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure code quality standards
5. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Access the Electronic Music Taxonomy Database at http://localhost:5000 after running the application!**