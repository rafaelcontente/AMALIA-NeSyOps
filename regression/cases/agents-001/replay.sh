#!/bin/bash
# Replay do caso agents-001
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_agents.py -v
