-- =====================================================
-- MANUAL FRESH DATABASE CREATION COMMANDS
-- =====================================================
-- Run these commands ONE BY ONE via command line psql
-- SECURITY: Replace 'your_secure_password' with your actual password
-- DO NOT commit this file with real passwords

-- Step 1: Connect as superuser to default database
-- psql -h YOUR_HOST -U postgres -d postgres

-- Step 2: Drop existing database if needed (CAREFUL!)
DROP DATABASE IF EXISTS cultural_intelligence;

-- Step 3: Create fresh database (run this command alone)
CREATE DATABASE cultural_intelligence
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Step 4: Create user (run this command alone)
-- IMPORTANT: Replace 'your_secure_password' with a strong password
DROP USER IF EXISTS cultural_intel_user;
CREATE USER cultural_intel_user WITH PASSWORD 'your_secure_password';

-- Step 5: Grant database privileges (run this command alone)
GRANT ALL PRIVILEGES ON DATABASE cultural_intelligence TO cultural_intel_user;

-- Step 6: Switch to new database
-- \c cultural_intelligence

-- Step 7: Set up schema permissions
GRANT USAGE ON SCHEMA public TO cultural_intel_user;
GRANT CREATE ON SCHEMA public TO cultural_intel_user;
GRANT ALL ON SCHEMA public TO cultural_intel_user;

-- Step 8: Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cultural_intel_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cultural_intel_user;

-- Step 9: Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- VERIFICATION COMMANDS
-- =====================================================

-- Check database was created
SELECT datname, datdba, encoding FROM pg_database WHERE datname = 'cultural_intelligence';

-- Check user was created
SELECT usename, usecreatedb, usesuper FROM pg_user WHERE usename = 'cultural_intel_user';

-- Check extensions
SELECT extname, extversion FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm');

-- Success message
SELECT '🎵 Fresh Cultural Intelligence Database Ready! 🚀' as status;