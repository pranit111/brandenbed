#!/usr/bin/env bash
# Exit on error
set -o errexit  

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Build frontend (if using npm + flowbite)
echo "Installing Node.js dependencies..."
npm install

# Collect Django static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Make migrations (ensure all migrations are created)
echo "Making migrations..."
python manage.py makemigrations

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# ✅ Create superuser automatically (only if none exists)
echo "Setting up superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username="admin",
        email="initcore25@gmail.com",
        password="0987poiu"
    )
    print("✅ Superuser created (username=admin, password=0987poiu)")
else:
    print("✅ Superuser already exists")
EOF

echo "Build process completed successfully!"
