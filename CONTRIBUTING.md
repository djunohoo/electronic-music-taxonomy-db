# Contributing to Electronic Music Taxonomy DB

## Quick Start
- Clone the repo and install Python requirements
- Copy `.env.example` to `.env` and fill in your secrets
- Use the Makefile or provided scripts for common actions

## Workflow
- Use feature branches for new work
- Write or update tests for new features
- Run `make test` before submitting PRs

## Adding a New Genre or Pattern
- Update the taxonomy tables in the database (see `add_taxonomy_tables.sql`)
- Add new pattern logic in the relevant Python modules
- Update documentation if needed

## Common Issues
- See the README for troubleshooting tips
- If you hit a dependency error, run `pip install -r requirements.txt` again
