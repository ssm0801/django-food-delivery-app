#!/bin/bash

# EC2 Deployment Script for Food Delivery App

echo "🚀 Deploying Food Delivery App to EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv redis-server nginx git

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create app directory
sudo mkdir -p /opt/fooddelivery
sudo chown $USER:$USER /opt/fooddelivery
cd /opt/fooddelivery

# Clone or copy your app (adjust as needed)
# git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Django
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py setup_data

echo "✅ Basic setup complete. Now creating systemd services..."