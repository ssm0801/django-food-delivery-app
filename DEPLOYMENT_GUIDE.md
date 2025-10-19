# AWS EC2 Deployment Guide

## Step 1: Launch EC2 Instance

1. **Login to AWS Console** and navigate to EC2
2. **Launch Instance:**
   - AMI: Ubuntu Server 20.04 LTS (Free tier eligible)
   - Instance Type: t2.micro (Free tier eligible)
   - Key Pair: Create or select existing key pair
   - Security Group: Create with following rules:
     - SSH (22) - Your IP
     - HTTP (80) - Anywhere
     - HTTPS (443) - Anywhere
     - Custom TCP (8000) - Anywhere (for development)

## Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Step 3: Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx redis-server git -y

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping  # Should return PONG
```

## Step 4: Deploy Application

```bash
# Clone your repository
git clone https://github.com/your-username/food-delivery-app.git
cd food-delivery-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn daphne

# Setup database
python manage.py migrate
python manage.py setup_data

# Test the application
python manage.py runserver 0.0.0.0:8000
```

## Step 5: Configure Production Settings

Create `fooddelivery/production_settings.py`:

```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['your-ec2-public-ip', 'your-domain.com']

# Use environment variables for sensitive data
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key')

# Database (optional - use PostgreSQL for production)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'fooddelivery',
#         'USER': 'your-db-user',
#         'PASSWORD': 'your-db-password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Static files
STATIC_ROOT = '/home/ubuntu/food-delivery-app/staticfiles'

# Redis configuration for production
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

## Step 6: Collect Static Files

```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=fooddelivery.production_settings

# Collect static files
python manage.py collectstatic --noinput
```

## Step 7: Configure Systemd Services

### Create Daphne service for ASGI (WebSocket support):

```bash
sudo nano /etc/systemd/system/fooddelivery-daphne.service
```

```ini
[Unit]
Description=Food Delivery Daphne ASGI Service
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/food-delivery-app
Environment=PATH=/home/ubuntu/food-delivery-app/venv/bin
Environment=DJANGO_SETTINGS_MODULE=fooddelivery.production_settings
ExecStart=/home/ubuntu/food-delivery-app/venv/bin/daphne -b 0.0.0.0 -p 8001 fooddelivery.asgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Create Gunicorn service for HTTP:

```bash
sudo nano /etc/systemd/system/fooddelivery-gunicorn.service
```

```ini
[Unit]
Description=Food Delivery Gunicorn Service
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/food-delivery-app
Environment=PATH=/home/ubuntu/food-delivery-app/venv/bin
Environment=DJANGO_SETTINGS_MODULE=fooddelivery.production_settings
ExecStart=/home/ubuntu/food-delivery-app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 fooddelivery.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Step 8: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/fooddelivery
```

```nginx
server {
    listen 80;
    server_name your-ec2-public-ip your-domain.com;

    # Static files
    location /static/ {
        alias /home/ubuntu/food-delivery-app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # WebSocket connections (for chat)
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # HTTP requests
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/fooddelivery /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t  # Test configuration
```

## Step 9: Start Services

```bash
# Start and enable services
sudo systemctl daemon-reload
sudo systemctl start fooddelivery-gunicorn
sudo systemctl start fooddelivery-daphne
sudo systemctl enable fooddelivery-gunicorn
sudo systemctl enable fooddelivery-daphne
sudo systemctl restart nginx

# Check service status
sudo systemctl status fooddelivery-gunicorn
sudo systemctl status fooddelivery-daphne
sudo systemctl status nginx
```

## Step 10: Configure Firewall (Optional)

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## Step 11: SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Troubleshooting

### Check logs:
```bash
# Application logs
sudo journalctl -u fooddelivery-gunicorn -f
sudo journalctl -u fooddelivery-daphne -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Redis logs
sudo journalctl -u redis-server -f
```

### Common issues:
1. **Port conflicts**: Ensure ports 8000, 8001 are not used by other services
2. **Permission issues**: Check file permissions for static files
3. **Redis connection**: Verify Redis is running and accessible
4. **WebSocket issues**: Ensure Daphne service is running for chat functionality

## Final Testing

1. Visit `http://your-ec2-public-ip` - Should show the home page
2. Login with admin credentials: mobile `9999999999`, OTP `1234`
3. Create a customer account with any mobile number and OTP `1234`
4. Test booking creation, assignment, and chat functionality

Your Food Delivery App is now live! 🚀