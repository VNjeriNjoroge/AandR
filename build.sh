#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Build the React Frontend
# Navigate to your frontend folder, install, and build
cd frontend
npm install
npm run build
cd ..

# 3. Collect Static Files
# This moves the React build files into a place Django can serve them
python manage.py collectstatic --no-input

# 4. Run Database Migrations
# This connects your models to your permanent Supabase DB
python manage.py migrate
