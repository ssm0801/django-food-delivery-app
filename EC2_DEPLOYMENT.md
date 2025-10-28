# EC2 Deployment Guide (Amazon Linux)

## Quick Deployment Steps

### 1. Launch EC2 Instance
- **AMI**: Amazon Linux 2
- **Instance Type**: t2.micro (or larger)
- **Security Group**: Allow ports 22 (SSH) and 8000 (HTTP)

### 2. Connect and Deploy
```bash
# Connect to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Upload your code (choose one method):
# Method 1: Git clone
git clone <your-repo-url>
cd django-food-delivery-app

# Method 2: SCP upload
# scp -i your-key.pem -r . ec2-user@your-ec2-ip:~/django-food-delivery-app

# Run deployment script
chmod +x deploy_amazon_linux.sh
./deploy_amazon_linux.sh
```

### 3. Setup Background Service
```bash
# Setup systemd service for background running
chmod +x setup_service.sh
./setup_service.sh
```

### 4. Access Your App
- **URL**: `http://your-ec2-public-ip:8000`
- **Admin**: Mobile `9999999999`, OTP `1234`

## Service Management

```bash
# Start service
sudo systemctl start fooddelivery

# Stop service
sudo systemctl stop fooddelivery

# Restart service
sudo systemctl restart fooddelivery

# Check status
sudo systemctl status fooddelivery

# View logs
sudo journalctl -u fooddelivery -f
```

## Security Group Settings

**Inbound Rules:**
- SSH (22): Your IP
- Custom TCP (8000): 0.0.0.0/0

## Troubleshooting

```bash
# Check if Redis is running
sudo systemctl status redis

# Check app logs
sudo journalctl -u fooddelivery -n 50

# Manual start for debugging
cd /opt/fooddelivery
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=fooddelivery.settings
daphne -b 0.0.0.0 -p 8000 fooddelivery.asgi:application
```

## Production Considerations

For production, consider:
- Use Nginx as reverse proxy
- Use PostgreSQL instead of SQLite
- Set `DEBUG = False`
- Use proper domain and SSL
- Configure proper logging