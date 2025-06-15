#!/bin/bash
set -e

# Init DB
python init_db.py

# Start API
exec uvicorn main:app --host 0.0.0.0 --port 8000
