# Configuration Files

## Overview

This directory contains configuration files for the Cultural Intelligence System.

## Configuration Files

### Environment Variables (.env)
**Location**: `.env` (create from `.env.example`)
**Purpose**: Sensitive credentials and environment-specific settings
**Security**: NEVER commit this file to git

```bash
# Create your .env file
cp .env.example .env

# Edit with your credentials
nano .env
```

### Taxonomy Configuration (taxonomy_config.json)
**Location**: `taxonomy_config.json` (create from `taxonomy_config.json.example`)
**Purpose**: System-wide configuration for scanning and classification
**Security**: This file may contain sensitive paths or settings, DO NOT commit

```bash
# Create your config file
cp taxonomy_config.json.example taxonomy_config.json

# Edit with your settings
nano taxonomy_config.json
```

### Performance Configurations
**Files**: 
- `optimal_config.json.example` - Balanced performance settings
- `raid0_config.json.example` - High-performance RAID0 optimized settings

**Purpose**: Performance tuning for different hardware configurations
**Security**: These example files are safe to commit

```bash
# Copy the appropriate config for your setup
cp optimal_config.json.example optimal_config.json
# OR
cp raid0_config.json.example raid0_config.json
```

## Configuration Priority

The system loads configuration in this order (later overrides earlier):

1. Default values in code
2. `taxonomy_config.json` file
3. Environment variables from `.env`
4. System environment variables

## Security Best Practices

1. **Never commit**:
   - `.env` file
   - `taxonomy_config.json` file (if it contains sensitive data)
   - Any file with real credentials

2. **Always use**:
   - `.example` files as templates
   - Environment variables for sensitive data
   - Strong passwords and rotate regularly

3. **Verify**:
   ```bash
   # Run security audit
   python security_audit.py
   
   # Check .gitignore
   git status --ignored
   ```

## Example Configurations

### Development Setup
```bash
# .env for development
DB_URL=postgresql://user:pass@localhost:5432/cultural_intelligence_dev
API_HOST=localhost
API_PORT=5000
DASHBOARD_PORT=8083
```

### Production Setup
```bash
# .env for production
DB_URL=postgresql://user:secure_pass@prod-db-host:5432/cultural_intelligence
API_HOST=0.0.0.0
API_PORT=5000
DASHBOARD_PORT=8083
SERVICE_MODE=production
```

## Troubleshooting

### Configuration not loading
- Verify `.env` file exists in project root
- Check file permissions (should be readable)
- Ensure `python-dotenv` is installed: `pip install python-dotenv`

### Wrong values being used
- Check configuration priority order above
- Verify environment variable names match exactly
- Use `python -c "from taxonomy_v32 import TaxonomyConfig; print(TaxonomyConfig().config)"` to debug

## See Also

- [SECURITY.md](SECURITY.md) - Security policy
- [SECURITY_MIGRATION.md](SECURITY_MIGRATION.md) - Migration guide
- [README.md](README.md) - Setup instructions
