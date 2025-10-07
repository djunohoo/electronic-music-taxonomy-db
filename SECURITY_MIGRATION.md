# Security Migration Guide

## Overview

This repository previously contained hardcoded credentials and IP addresses. This guide helps you migrate to the secure, environment-variable-based configuration.

## What Changed

### Before (Insecure ❌)
```python
# Hard-coded credentials in code
db_url = "postgresql://postgres:CulturalIntel2025!@172.22.17.138:5432/postgres"
api_host = "172.22.17.37"
```

### After (Secure ✅)
```python
# Load from environment variables
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DB_URL")
api_host = os.getenv("API_HOST", "localhost")
```

## Migration Steps

### Step 1: Update Your Environment File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   # Database Configuration
   DB_URL=postgresql://user:password@your-host:5432/cultural_intelligence
   DB_HOST=your-database-host
   DB_PORT=5432
   DB_NAME=cultural_intelligence
   DB_USER=cultural_intel_user
   DB_PASSWORD=your_secure_password
   
   # API Configuration
   API_HOST=your-api-host
   API_PORT=5000
   
   # Dashboard Configuration
   DASHBOARD_HOST=your-dashboard-host
   DASHBOARD_PORT=8083
   ```

3. **Important**: Never commit the `.env` file to git!

### Step 2: Update Your Python Files

For any custom Python files you've created, update them to use environment variables:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use environment variables
db_url = os.getenv("DB_URL")
api_host = os.getenv("API_HOST", "localhost")
api_port = int(os.getenv("API_PORT", 5000))
```

### Step 3: Update Shell Scripts

For any custom shell scripts, use environment variables:

```bash
#!/bin/bash
# Load from environment or use defaults
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-cultural_intelligence}"

# Use the variables
psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -d "$DB_NAME"
```

### Step 4: Rotate Credentials

Since credentials were previously exposed in the repository:

1. **Change all database passwords**:
   ```sql
   ALTER USER cultural_intel_user WITH PASSWORD 'new_secure_password';
   ```

2. **Regenerate API keys** in your Supabase dashboard

3. **Update your `.env` file** with the new credentials

### Step 5: Verify Configuration

Run the security audit tool:
```bash
python security_audit.py
```

This will scan your codebase for any remaining hardcoded credentials.

## Common Patterns to Fix

### Pattern 1: Hardcoded Database URL
```python
# ❌ Before
conn = psycopg2.connect("postgresql://user:pass@172.22.17.138:5432/db")

# ✅ After
from dotenv import load_dotenv
import os
load_dotenv()
conn = psycopg2.connect(os.getenv("DB_URL"))
```

### Pattern 2: Hardcoded API Host
```python
# ❌ Before
app.run(host='172.22.17.37', port=5000)

# ✅ After
from dotenv import load_dotenv
import os
load_dotenv()
app.run(
    host=os.getenv("API_HOST", "localhost"),
    port=int(os.getenv("API_PORT", 5000))
)
```

### Pattern 3: Hardcoded Credentials in SQL
```sql
-- ❌ Before
CREATE USER cultural_intel_user WITH PASSWORD 'CulturalIntel2025!';

-- ✅ After (in script that calls SQL)
export DB_PASSWORD="your_secure_password"
psql -c "CREATE USER cultural_intel_user WITH PASSWORD '$DB_PASSWORD';"
```

## Files Updated (Core System)

The following core system files have been updated to use environment variables:

- ✅ `taxonomy_v32.py` - Main configuration module
- ✅ `install_cultural_intelligence.py` - Database installer
- ✅ `create_fresh_database.sh` - Database creation script
- ✅ `docker_create_database.sh` - Docker database script
- ✅ `create_database.sql` - SQL setup script
- ✅ `DATABASE_SETUP.md` - Setup documentation

## Files That May Still Need Updates

The following files were identified as containing hardcoded values. If you're using these files, you'll need to update them:

### Python Files to Update:
- `enhanced_cultural_dashboard.py`
- `cultural_dashboard.py`
- `metacrate_integration_api.py`
- `simple_rest_api.py`
- `supabase_client.py`
- And others (run `python security_audit.py` to see full list)

### Update Pattern for These Files:

1. Add at the top:
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   ```

2. Replace hardcoded values:
   ```python
   # Replace this:
   host = '172.22.17.37'
   
   # With this:
   host = os.getenv("API_HOST", "localhost")
   ```

## Testing Your Migration

1. **Test database connection**:
   ```bash
   python test_db.py
   ```

2. **Test API**:
   ```bash
   python test_api.py
   ```

3. **Run security audit**:
   ```bash
   python security_audit.py
   ```

## Troubleshooting

### Issue: "Database connection failed"
- Check that `DB_URL` is set correctly in `.env`
- Verify credentials are correct
- Ensure database server is running

### Issue: "Module 'dotenv' not found"
```bash
pip install python-dotenv
```

### Issue: "Environment variable not found"
- Make sure `.env` file exists in the project root
- Verify `load_dotenv()` is called before accessing variables
- Check that variable names match exactly

## Security Checklist

After migration, verify:

- [ ] `.env` file exists and contains your credentials
- [ ] `.env` is listed in `.gitignore`
- [ ] No `.env` file is committed to git
- [ ] All database passwords have been rotated
- [ ] All API keys have been regenerated
- [ ] `python security_audit.py` shows no issues
- [ ] Repository is set to PRIVATE on GitHub
- [ ] All team members have updated their local `.env` files

## Need Help?

- See [SECURITY.md](SECURITY.md) for security best practices
- See [README.md](README.md) for setup instructions
- Run `python security_audit.py` to find remaining issues
