# Makefile for common project actions

feedback:
	python scripts/feedback_analytics.py

memory:
	code PROJECT_MEMORY.md

.PHONY: scan train dashboard api backup test

scan:
	python cultural_intelligence_system.py --scan $(DIR)

train:
	python webhook_training_api.py

dashboard:
	python cultural_dashboard_port8083.py

api:
	python metacrate_api.py

backup:
	python create_fresh_database.sh

test:
	pytest
visualize:
	python scripts/visualize_feedback.py
