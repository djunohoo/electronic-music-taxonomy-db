"""Optional psycopg2 wrapper"""
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    
    class RealDictCursor:
        pass
        
    print("⚠️ psycopg2 not available - some database features may be limited")
