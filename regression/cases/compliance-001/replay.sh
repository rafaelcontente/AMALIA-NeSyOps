#!/bin/bash
cd ~/Documents/Projects/amalia-neysyops
source .venv/bin/activate
python -m pytest tests/test_compliance.py -v
