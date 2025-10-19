#!/bin/bash

# AWS EC2 Deployment Script for Food Delivery App

echo "Starting deployment..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv nginx redis-server -y

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Clone repository (replace with your repo URL)
# git clone <your-repo-url> /home/ubuntu/fooddelivery
# cd /home/ubuntu/fooddelivery

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn daphne

# Run migrations
python manage.py migrate
python manage.py setup_data

# Collect static files
python manage.py collectstatic --noinput

# Create systemd service for Django
sudo tee /etc/systemd/system/fooddelivery.service > /dev/null <<EOF
[Unit]
Description=Food Delivery Django App
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/fooddelivery
Environment=PATH=/home/ubuntu/fooddelivery/venv/bin
ExecStart=/home/ubuntu/fooddelivery/venv/bin/daphne -b 0.0.0.0 -p 8000 fooddelivery.asgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/sites-available/fooddelivery > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /home/ubuntu/fooddelivery/static/;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/fooddelivery /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
sudo systemctl daemon-reload
sudo systemctl start fooddelivery
sudo systemctl enable fooddelivery
sudo systemctl restart nginx

echo "Deployment completed!"
echo "Access your app at: http://your-ec2-public-ip"