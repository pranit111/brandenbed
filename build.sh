#!/usr/bin/env bash
# Exit on error
set -o errexit  

# Install Python deps
pip install -r requirements.txt

# Build frontend (if using npm + flowbite)
npm install

# Collect Django static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate --no-input  

# ✅ Create superuser automatically (only if none exists)
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username="admin",
        email="initcore25@gmail.com",
        password="0987poiu"
    )
    print("Superuser created  (username=admin, password=0987poiu)")
else:
    print("Superuser already exists ")
EOF
