# electronic-music-taxonomy-db

[![Feedback Analytics](https://github.com/djunohoo/electronic-music-taxonomy-db/actions/workflows/feedback_analytics.yml/badge.svg)](https://github.com/djunohoo/electronic-music-taxonomy-db/actions/workflows/feedback_analytics.yml)
Comprehensive Electronic Music Taxonomy Database with hierarchical genres, BPM analysis, energy levels, mixing compatibility, and audio classification for DJs and music professionals

## Quick Start
1. Copy `.env.example` to `.env` and fill in your credentials
2. Install Python requirements: `pip install -r requirements.txt`
3. Use the Makefile or `scripts/quick_launch.ps1` for common actions
4. To scan a collection: `make scan DIR=/path/to/music`
5. To launch the dashboard: `make dashboard` or run the PowerShell script

## Common Issues & Fixes
- If you see a missing dependency error, run `pip install -r requirements.txt`
- For database errors, check your `.env` and DB connection
- For dashboard/API issues, ensure the correct port is open and not in use

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
