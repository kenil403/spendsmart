#!/usr/bin/env bash
# Build script for Render

set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized')"
