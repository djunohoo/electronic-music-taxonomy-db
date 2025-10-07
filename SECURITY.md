# Security Policy

## Important Notice

**This repository should be PRIVATE.** It contains sensitive configuration for a production music taxonomy system.

## Removed Security Issues (Fixed)

This repository previously contained:
- ❌ Hardcoded database passwords 
- ❌ Hardcoded IP addresses
- ❌ Production credentials in source code

**These have been removed and replaced with environment variables.**

## Secure Configuration

### 1. Environment Variables

All sensitive configuration is now managed through environment variables:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```bash
   # NEVER commit this file to git!
   DB_URL=postgresql://user:password@hostname:5432/database_name
   SUPABASE_ANON_KEY=your_actual_key_here
   ```

3. The `.env` file is automatically ignored by git (see `.gitignore`)

### 2. Database Credentials

**Never hardcode database credentials in:**
- Python files
- Shell scripts
- SQL files
- Documentation files

**Always use:**
- Environment variables via `.env` file
- Secure credential storage (e.g., AWS Secrets Manager, Azure Key Vault)
- Proper access control and least privilege

### 3. IP Addresses and Hostnames

**Do not hardcode:**
- Production IP addresses
- Internal network addresses
- Hostnames

**Instead use:**
- Environment variables: `API_HOST`, `DB_HOST`
- Configuration files that are not committed to git
- Service discovery or DNS names

### 4. Files That Should Never Be Committed

The following are now protected by `.gitignore`:
- `.env` - Environment variables
- `*.db` - SQLite databases
- `*.log` - Log files
- Credential files
- Private keys

## Best Practices

1. **Repository Visibility**: Keep this repository PRIVATE
2. **Credential Rotation**: Rotate all passwords and keys regularly
3. **Access Control**: Limit repository access to authorized users only
4. **Code Review**: Review all commits for accidentally committed secrets
5. **Secret Scanning**: Use GitHub's secret scanning feature

## What To Do If Credentials Are Exposed

If you accidentally commit credentials:

1. **Immediately rotate** all exposed credentials
2. **Change passwords** in the production system
3. **Revoke and regenerate** API keys
4. **Review access logs** for unauthorized access
5. **Remove from git history** using tools like `git-filter-repo` or BFG Repo-Cleaner

## Reporting Security Issues

If you discover a security issue:
- Do NOT create a public issue
- Contact the repository owner directly
- Provide details about the vulnerability

## Migration Guide

For users migrating from the old insecure configuration:

1. **Update all scripts** to use environment variables
2. **Rotate all passwords** that were previously hardcoded
3. **Update your `.env` file** with new credentials
4. **Verify** that no secrets are in your git history
5. **Test** your configuration with the new secure setup

## Environment Variable Reference

Required environment variables:

```bash
# Database
DB_URL=postgresql://user:password@host:port/database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cultural_intelligence
DB_USER=cultural_intel_user
DB_PASSWORD=your_secure_password

# Supabase
SUPABASE_URL=http://localhost:8000
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_KEY=your_service_key

# API
API_HOST=localhost
API_PORT=5000

# Dashboard
DASHBOARD_HOST=localhost
DASHBOARD_PORT=8083
```

## Checklist for Secure Deployment

- [ ] Repository is set to PRIVATE
- [ ] `.env` file is created with actual credentials
- [ ] `.env` file is NOT committed to git
- [ ] All hardcoded credentials have been removed
- [ ] All hardcoded IP addresses have been removed
- [ ] Database passwords have been rotated
- [ ] API keys have been regenerated
- [ ] Access control is properly configured
- [ ] Secret scanning is enabled on GitHub
