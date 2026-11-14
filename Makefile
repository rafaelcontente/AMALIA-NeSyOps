.PHONY: test coverage check-coverage set-baseline clean

test:
	python -m pytest tests/ -q --tb=short

coverage:
	python -m pytest tests/ -q --cov=core --cov=gate --cov=policy --cov=audit \
	  --cov=ingest --cov=reasoning --cov=formalize --cov=integration --cov-report=term-missing

check-coverage:
	python scripts/check_coverage.py

set-baseline:
	python scripts/check_coverage.py --set-baseline

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov coverage.json coverage.xml
