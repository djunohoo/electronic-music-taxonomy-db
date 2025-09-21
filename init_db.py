"""
Initialize database and load sample data.
"""
from src.database import init_database
from src.data.data_loader import DataLoader
from src.data.enhanced_loader_simple import EnhancedDataLoader

def main():
    """Initialize the database with tables and sample data."""
    print("Initializing Electronic Music Taxonomy Database...")
    
    # Create database tables
    print("Creating database tables...")
    init_database()
    
    # Load basic sample data
    print("Loading basic sample data...")
    loader = DataLoader()
    loader.initialize_sample_data()
    
    # Load enhanced taxonomy features
    print("Loading enhanced taxonomy features...")
    enhanced_loader = EnhancedDataLoader()
    enhanced_loader.load_all_enhanced_data()
    
    print("Database initialization complete!")
    print("\nTo start the web application, run:")
    print("python src/web/app.py")

if __name__ == "__main__":
    main()