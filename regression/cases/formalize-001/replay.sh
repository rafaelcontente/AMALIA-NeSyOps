#!/bin/bash
# Replay do caso formalize-001
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_formalize.py -v
