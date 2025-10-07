-- =====================================================
-- STEP 1: CREATE DATABASE FOR CULTURAL INTELLIGENCE SYSTEM
-- =====================================================
-- Execute this FIRST as superuser (postgres) on your database instance
-- SECURITY: Replace 'your_secure_password_here' with an actual secure password
-- DO NOT commit this file with real passwords to version control

-- Create the database
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
    IS 'Cultural Intelligence System v3.2 - Electronic Music Taxonomy Database';

-- Create a dedicated user for the application (optional but recommended)
-- IMPORTANT: Replace 'your_secure_password_here' with a strong password
CREATE USER cultural_intel_user WITH PASSWORD 'your_secure_password_here';

-- Grant all privileges on the new database to the user
GRANT ALL PRIVILEGES ON DATABASE cultural_intelligence TO cultural_intel_user;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO cultural_intel_user;
GRANT CREATE ON SCHEMA public TO cultural_intel_user;

-- =====================================================
-- AFTER RUNNING THIS, CONNECT TO THE NEW DATABASE
-- =====================================================
-- Next step: \c cultural_intelligence
-- Then run: cultural_intelligence_schema.sql