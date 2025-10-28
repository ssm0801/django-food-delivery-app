#!/bin/bash

# Amazon Linux EC2 Deployment Script

echo "🚀 Deploying Food Delivery App to Amazon Linux EC2..."

# Update system
sudo yum update -y

# Install required packages
sudo yum install -y python3 python3-pip git

# Install Redis
sudo amazon-linux-extras install redis6 -y
sudo systemctl start redis6
sudo systemctl enable redis6
sudo systemctl status redis6

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Django
export DJANGO_SETTINGS_MODULE=fooddelivery.settings
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py setup_data
nohup daphne -b 0.0.0.0 -p 8000 fooddelivery.asgi:application > app.log 2>&1 &

echo "✅ Setup complete!"