#!/bin/bash
# Replay do caso ingest-001
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_ingest.py -v
