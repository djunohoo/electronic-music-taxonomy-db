# 🎵 Cultural Intelligence System v3.2 - Database Setup Guide

## Database Setup

### 📋 Prerequisites
- Access to your PostgreSQL database instance
- Admin/superuser credentials (usually `postgres` user)
- psql client or database management tool

### 🚀 Step-by-Step Setup

#### **Step 1: Connect to PostgreSQL**
```bash
# Connect to your PostgreSQL instance
# Replace YOUR_HOST with your database hostname or IP
psql -h YOUR_HOST -p 5432 -U postgres -d postgres
```
**Or via your database dashboard/SQL editor**

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

-- IMPORTANT: Replace 'your_secure_password_here' with a strong password
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

### 🔑 Get Your Database Credentials

After setup, configure your `.env` file:

```bash
# Copy .env.example to .env and fill in your values
DB_URL=postgresql://cultural_intel_user:your_password@YOUR_HOST:5432/cultural_intelligence
SUPABASE_URL=http://YOUR_HOST:8000
SUPABASE_ANON_KEY=your_anon_key_from_dashboard
```

### ⚡ Quick Commands Summary

```bash
# 1. Connect as superuser (replace YOUR_HOST)
psql -h YOUR_HOST -p 5432 -U postgres -d postgres

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
1. Update your `.env` file with credentials
2. Test the MetaCrate API connection
3. Run your first music collection scan

**Database ready for Cultural Intelligence System v3.2!** 🚀