#!/bin/bash
# =====================================================
# Docker-based Fresh Database Creation
# =====================================================
# If your Supabase is running in Docker

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

-- Create user
DROP USER IF EXISTS cultural_intel_user;
CREATE USER cultural_intel_user WITH PASSWORD 'CulturalIntel2025!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cultural_intelligence TO cultural_intel_user;
"

echo "✅ Database created via Docker!"

# Set up permissions in new database
docker exec -it $CONTAINER_ID psql -U postgres -d cultural_intelligence -c "
-- Schema permissions
GRANT ALL ON SCHEMA public TO cultural_intel_user;
ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO cultural_intel_user;

-- Extensions
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";
"

echo "🚀 Fresh database ready for schema installation!"
echo ""
echo "🔑 Connection details:"
echo "   Database: cultural_intelligence"
echo "   User: cultural_intel_user"  
echo "   Password: CulturalIntel2025!"
echo "   Host: 172.22.17.138"
echo "   Port: 5432"