#!/bin/bash
# Replay do caso core-001
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_core.py -v
