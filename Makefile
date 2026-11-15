.PHONY: install test test-security eval run clean lint

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -q --tb=short

test-security:
	python -m pytest tests/security/ -v

eval:
	python scripts/generate_eval_report.py

run:
	uvicorn integration.api:app --host 0.0.0.0 --port 8000 --reload

lint:
	python -m flake8 core gate policy audit

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
