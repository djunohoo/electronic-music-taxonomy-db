# electronic-music-taxonomy-db

[![Feedback Analytics](https://github.com/djunohoo/electronic-music-taxonomy-db/actions/workflows/feedback_analytics.yml/badge.svg)](https://github.com/djunohoo/electronic-music-taxonomy-db/actions/workflows/feedback_analytics.yml)

Comprehensive Electronic Music Taxonomy Database with hierarchical genres, BPM analysis, energy levels, mixing compatibility, and audio classification for DJs and music professionals

⚠️ **SECURITY NOTICE**: This repository contains sensitive configuration for a production music taxonomy system and should be kept PRIVATE. See [SECURITY.md](SECURITY.md) for important security information.

## Quick Start

### 1. Security Setup (IMPORTANT - Do This First!)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your actual credentials
# NEVER commit the .env file to git!
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
See [DATABASE_SETUP.md](DATABASE_SETUP.md) for complete database setup instructions.

### 4. Run the Application
```bash
# Use the Makefile for common actions
make scan DIR=/path/to/music
make dashboard
make api
```

Or use PowerShell scripts:
```powershell
# Launch services
scripts/quick_launch.ps1
```

## Common Issues & Fixes
- If you see a missing dependency error, run `pip install -r requirements.txt`
- For database errors, check your `.env` file and verify DB connection credentials
- For dashboard/API issues, ensure the correct port is open and not in use
- **Security**: Never commit `.env` files or credentials to git

## Configuration

All sensitive configuration is managed through environment variables in the `.env` file:
- Database credentials
- API keys
- Host/port settings

See `.env.example` for all available configuration options.

## Security Best Practices

1. **Keep this repository PRIVATE**
2. **Never commit** the `.env` file
3. **Rotate credentials** regularly
4. **Use strong passwords** for database access
5. See [SECURITY.md](SECURITY.md) for detailed security guidelines


## How to Add a New Genre or Pattern
- Edit `add_taxonomy_tables.sql` and update the relevant Python modules
- Run the migration or seed scripts as needed

## Project Structure

## Continuous Improvement & Project Memory

- Run `python scripts/feedback_analytics.py` to log test, lint, and type-check results over time. Review `feedback_analytics.log` for trends and issues.
- Contribute to `PROJECT_MEMORY.md` with lessons learned, common issues, and improvement ideas.

## Automation

- Use `make feedback` to run analytics and log results.
- Use `make memory` to open the project memory knowledge base for editing.
See `CONTRIBUTING.md` for more details.

## Setup Note

After installing requirements, run `pre-commit install` to enable automatic code checks on commit.
