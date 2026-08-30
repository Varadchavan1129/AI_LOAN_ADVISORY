#!/bin/bash
# Tata Mitra — Start Backend
# Run this from anywhere with:  ./backend/start.sh

set -e
cd "$(dirname "$0")"          # go to backend/ folder
source venv/bin/activate       # activate Python env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
