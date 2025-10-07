#!/bin/bash
# =====================================================
# Docker-based Fresh Database Creation
# =====================================================
# SECURITY: This script requires environment variables to be set
# Set DB_PASSWORD before running: export DB_PASSWORD="your_password"

# Check for required environment variables
if [ -z "$DB_PASSWORD" ]; then
    echo "❌ Error: DB_PASSWORD environment variable not set"
    echo "Please set: export DB_PASSWORD=your_secure_password"
    exit 1
fi

DB_NAME="${DB_NAME:-cultural_intelligence}"
DB_USER="${DB_USER:-cultural_intel_user}"

echo "🐳 Creating fresh database via Docker..."

# Find your Supabase database container
CONTAINER_ID=$(docker ps | grep postgres | grep supabase | awk '{print $1}')

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ No Supabase PostgreSQL container found"
    echo "Searching for any PostgreSQL containers..."
    docker ps | grep postgres
    exit 1
fi

echo "✅ Found PostgreSQL container: $CONTAINER_ID"

# Execute database creation inside container
docker exec -it $CONTAINER_ID psql -U postgres -d postgres -c "
-- Drop existing if needed
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

-- Create user
DROP USER IF EXISTS $DB_USER;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
"

echo "✅ Database created via Docker!"

# Set up permissions in new database
docker exec -it $CONTAINER_ID psql -U postgres -d "$DB_NAME" -c "
-- Schema permissions
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO $DB_USER;

-- Extensions
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";
"

echo "🚀 Fresh database ready for schema installation!"
echo ""
echo "🔑 Connection details:"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Host: (from your Docker configuration)"
echo "   Port: (from your Docker configuration)"