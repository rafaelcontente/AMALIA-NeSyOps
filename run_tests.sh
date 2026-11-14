#!/bin/bash
set -e
echo "Running AMALIA-NeSyOps test suite..."
python -m pytest tests/ -v --tb=short
echo "Done."
