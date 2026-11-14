#!/bin/bash
# Replay do caso policy-001
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_policy.py -v
