#!/bin/bash
# =====================================================
# Fresh Database Creation Script for Cultural Intelligence System
# =====================================================
# Run this on your Supabase server at 172.22.17.138

echo "🎵 Creating Fresh Cultural Intelligence Database..."
echo "=================================================="

# Connect to PostgreSQL and create database
psql -U postgres -d postgres -c "
-- Drop existing database if it exists (CAUTION!)
DROP DATABASE IF EXISTS cultural_intelligence;

-- Create fresh database
CREATE DATABASE cultural_intelligence
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Add comment
COMMENT ON DATABASE cultural_intelligence 
    IS 'Cultural Intelligence System v3.2 - Electronic Music Taxonomy Database - Fresh Install';

-- Create dedicated user
DROP USER IF EXISTS cultural_intel_user;
CREATE USER cultural_intel_user WITH PASSWORD 'CulturalIntel2025!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cultural_intelligence TO cultural_intel_user;
"

echo "✅ Database created successfully!"
echo "🔑 Database: cultural_intelligence"
echo "🔑 User: cultural_intel_user"
echo "🔑 Password: CulturalIntel2025!"
echo ""
echo "Next step: Connect to new database and run schema..."

# Now connect to the new database and set up schema permissions
psql -U postgres -d cultural_intelligence -c "
-- Grant schema permissions
GRANT USAGE ON SCHEMA public TO cultural_intel_user;
GRANT CREATE ON SCHEMA public TO cultural_intel_user;
GRANT ALL ON SCHEMA public TO cultural_intel_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cultural_intel_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cultural_intel_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO cultural_intel_user;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";
"

echo "✅ Database permissions and extensions set up!"
echo "🚀 Ready for schema installation!"