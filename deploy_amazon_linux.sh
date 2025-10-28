#!/bin/bash

# Amazon Linux EC2 Deployment Script

echo "🚀 Deploying Food Delivery App to Amazon Linux EC2..."

# Update system
sudo yum update -y

# Install required packages
sudo yum install -y python3 python3-pip git

# Install Redis
sudo amazon-linux-extras install redis6 -y
sudo systemctl start redis
sudo systemctl enable redis

# Create app directory
sudo mkdir -p /opt/fooddelivery
sudo chown ec2-user:ec2-user /opt/fooddelivery
cd /opt/fooddelivery

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

echo "✅ Setup complete!"