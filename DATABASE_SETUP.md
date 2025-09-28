# 🎵 Cultural Intelligence System v3.2 - Database Setup Guide

## Self-Hosted Supabase Database Creation at 172.22.17.138

### 📋 Prerequisites
- Access to your self-hosted Supabase PostgreSQL instance
- Admin/superuser credentials (usually `postgres` user)
- psql client or database management tool

### 🚀 Step-by-Step Setup

#### **Step 1: Connect to PostgreSQL**
```bash
# Connect to your Supabase PostgreSQL instance
psql -h 172.22.17.138 -p 5432 -U postgres -d postgres
```
**Or via your Supabase dashboard SQL editor at:**
```
http://172.22.17.138:8000/dashboard
```

#### **Step 2: Create the Database**
Copy and paste the contents of `create_database.sql`:

```sql
-- Creates the database and user
CREATE DATABASE cultural_intelligence
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE cultural_intelligence 
    IS 'Cultural Intelligence System v3.2 - Electronic Music Taxonomy Database';

CREATE USER cultural_intel_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE cultural_intelligence TO cultural_intel_user;
```

#### **Step 3: Connect to New Database**
```sql
-- Switch to the new database
\c cultural_intelligence
```

#### **Step 4: Create Schema & Tables**
Copy and paste the entire contents of `cultural_intelligence_schema.sql`

This will create:
- ✅ 8 core tables (tracks, duplicates, classifications, etc.)
- ✅ All performance indexes
- ✅ Pre-seeded electronic music data
- ✅ Monitoring views

#### **Step 5: Verify Setup**
```sql
-- Check tables were created
\dt

-- Check data was seeded
SELECT COUNT(*) FROM label_profiles;
SELECT COUNT(*) FROM artist_profiles;
SELECT COUNT(*) FROM patterns;

-- Should show:
-- label_profiles: 8 records
-- artist_profiles: 8 records  
-- patterns: 12 records
```

### 🔑 Get Your Supabase Credentials

After setup, you'll need:

1. **Database URL**: `postgresql://cultural_intel_user:your_password@172.22.17.138:5432/cultural_intelligence`
2. **Supabase API URL**: `http://172.22.17.138:8000`
3. **Anon Key**: Found in your Supabase dashboard settings

### ⚡ Quick Commands Summary

```bash
# 1. Connect as superuser
psql -h 172.22.17.138 -p 5432 -U postgres -d postgres

# 2. Create database (paste create_database.sql)

# 3. Switch to new database
\c cultural_intelligence

# 4. Create tables (paste cultural_intelligence_schema.sql)

# 5. Verify
\dt
SELECT COUNT(*) FROM label_profiles;
```

### 🎯 Next Steps

After database setup:
1. Update your system config with credentials
2. Test the MetaCrate API connection
3. Run your first music collection scan

**Database ready for Cultural Intelligence System v3.2!** 🚀