#!/bin/bash
# Replay do caso knowledge-001
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_knowledge.py -v
