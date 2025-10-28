#!/bin/bash

# Setup systemd service for background running

echo "🔧 Setting up systemd service..."

# Copy service file
sudo cp fooddelivery.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable fooddelivery
sudo systemctl start fooddelivery

# Check status
sudo systemctl status fooddelivery

echo "✅ Service setup complete!"
echo "📱 App running at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo ""
echo "🔧 Service commands:"
echo "  Start:   sudo systemctl start fooddelivery"
echo "  Stop:    sudo systemctl stop fooddelivery"
echo "  Restart: sudo systemctl restart fooddelivery"
echo "  Status:  sudo systemctl status fooddelivery"
echo "  Logs:    sudo journalctl -u fooddelivery -f"