#!/bin/bash
# Replay do caso reasoning-001
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_reasoning.py -v
