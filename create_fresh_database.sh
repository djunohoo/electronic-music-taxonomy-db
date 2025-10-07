#!/bin/bash
# =====================================================
# Fresh Database Creation Script for Cultural Intelligence System
# =====================================================
# SECURITY: This script requires environment variables to be set
# Set DB_PASSWORD before running: export DB_PASSWORD="your_password"

# Check for required environment variables
if [ -z "$DB_HOST" ]; then
    echo "❌ Error: DB_HOST environment variable not set"
    echo "Please set: export DB_HOST=your_database_host"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ Error: DB_PASSWORD environment variable not set"
    echo "Please set: export DB_PASSWORD=your_secure_password"
    exit 1
fi

DB_NAME="${DB_NAME:-cultural_intelligence}"
DB_USER="${DB_USER:-cultural_intel_user}"

echo "🎵 Creating Fresh Cultural Intelligence Database..."
echo "=================================================="
echo "Host: $DB_HOST"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo ""

# Connect to PostgreSQL and create database
psql -h "$DB_HOST" -U postgres -d postgres -c "
-- Drop existing database if it exists (CAUTION!)
DROP DATABASE IF EXISTS $DB_NAME;

-- Create fresh database
CREATE DATABASE $DB_NAME
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Add comment
COMMENT ON DATABASE $DB_NAME 
    IS 'Cultural Intelligence System v3.2 - Electronic Music Taxonomy Database - Fresh Install';

-- Create dedicated user
DROP USER IF EXISTS $DB_USER;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
"

echo "✅ Database created successfully!"
echo "🔑 Database: $DB_NAME"
echo "🔑 User: $DB_USER"
echo ""
echo "Next step: Connect to new database and run schema..."

# Now connect to the new database and set up schema permissions
psql -h "$DB_HOST" -U postgres -d "$DB_NAME" -c "
-- Grant schema permissions
GRANT USAGE ON SCHEMA public TO $DB_USER;
GRANT CREATE ON SCHEMA public TO $DB_USER;
GRANT ALL ON SCHEMA public TO $DB_USER;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $DB_USER;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";
"

echo "✅ Database permissions and extensions set up!"
echo "🚀 Ready for schema installation!"