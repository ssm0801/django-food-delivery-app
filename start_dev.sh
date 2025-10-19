#!/bin/bash

# Quick start script for local development

echo "🚀 Starting Food Delivery App Development Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt venv/pyvenv.cfg ]; then
    echo "Installing/updating dependencies..."
    pip install -r requirements.txt
fi

# Run migrations if needed
echo "Checking for database migrations..."
python manage.py migrate

# Setup initial data if no users exist
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null | tail -1)
if [ "$USER_COUNT" = "0" ]; then
    echo "Setting up initial data..."
    python manage.py setup_data
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Please start Redis server:"
    echo "   macOS: brew services start redis"
    echo "   Ubuntu: sudo systemctl start redis-server"
    echo "   Manual: redis-server"
    echo ""
    echo "Chat functionality requires Redis to work properly."
    echo ""
fi

echo ""
echo "🎉 Starting Django development server..."
echo ""
echo "📱 Access the app at: http://127.0.0.1:8000"
echo ""
echo "👤 Default Login Credentials:"
echo "   Admin: Mobile 9999999999, OTP 1234"
echo "   Delivery Partner: Mobile 9876543211, OTP 1234"
echo "   Customer: Any mobile number, OTP 1234"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
python manage.py runserver