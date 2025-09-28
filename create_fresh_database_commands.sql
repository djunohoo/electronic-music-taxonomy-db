-- =====================================================
-- FRESH DATABASE CREATION - Command Line Version
-- =====================================================
-- Run these commands ONE BY ONE via psql

-- Step 1: Drop if exists (optional - only if you want to start completely fresh)
-- DROP DATABASE IF EXISTS cultural_intelligence;

-- Step 2: Create the fresh database
CREATE DATABASE cultural_intelligence
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Step 3: Add comment
COMMENT ON DATABASE cultural_intelligence 
    IS 'Cultural Intelligence System v3.2 - Electronic Music Taxonomy Database - FRESH CLEAN INSTALL';

-- Step 4: Create dedicated user
CREATE USER cultural_intel_user WITH 
    PASSWORD 'CulturalIntel2025!' 
    CREATEDB 
    LOGIN;

-- Step 5: Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE cultural_intelligence TO cultural_intel_user;

-- Step 6: Connect to new database (run this separately)
-- \c cultural_intelligence

-- Step 7: Set up schema permissions (after connecting to new DB)
GRANT ALL ON SCHEMA public TO cultural_intel_user;
GRANT CREATE ON SCHEMA public TO cultural_intel_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cultural_intel_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cultural_intel_user;

-- Step 8: Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Step 9: Verification queries
SELECT 
    'DATABASE CREATED' as status,
    current_database() as database_name,
    current_user as connected_as;

SELECT extname, extversion FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm');