test:
	python -m pytest tests/ -v

coverage:
	python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov
