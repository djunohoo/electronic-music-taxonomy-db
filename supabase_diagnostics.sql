-- =====================================================
-- SUPABASE SETUP DIAGNOSTICS & SIMPLE INSTALLATION
-- =====================================================
-- Run this first to understand your current setup

-- Check what databases exist
SELECT datname as database_name 
FROM pg_database 
WHERE datistemplate = false;

-- Check current database and user
SELECT current_database(), current_user, session_user;

-- Check available schemas
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');

-- Check if we have create privileges
SELECT has_database_privilege(current_user, current_database(), 'CREATE') as can_create_objects;

-- Show current connection info
SELECT 
    inet_server_addr() as server_ip,
    inet_server_port() as server_port,
    version() as postgres_version;

-- =====================================================
-- IF DIAGNOSTICS SHOW YOU HAVE A WORKING DATABASE:
-- Skip CREATE DATABASE and run the schema directly!
-- =====================================================