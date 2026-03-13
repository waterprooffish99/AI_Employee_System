#!/bin/bash
# Cloud Server Setup Script - Install Docker and Dependencies
# Run this on the cloud VM after initial setup

set -e

echo "======================================"
echo "AI Employee Cloud Server Setup"
echo "======================================"
echo ""

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install prerequisites
echo "Installing prerequisites..."
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
echo "Adding Docker GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo "Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
echo "Installing Docker..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
echo "Adding user to docker group..."
sudo usermod -aG docker $USER

# Enable Docker on boot
echo "Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl enable containerd

# Install Python 3.13
echo "Installing Python 3.13..."
sudo apt install -y python3.13 python3.13-venv python3-pip

# Install UV
echo "Installing UV package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Nginx
echo "Installing Nginx..."
sudo apt install -y nginx

# Install Certbot
echo "Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Create directories
echo "Creating directories..."
mkdir -p ~/odoo/{data,addons,backups}
mkdir -p ~/ai-employee-system
mkdir -p ~/logs
mkdir -p ~/scripts

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Logout and login again for docker group to take effect"
echo "2. Run: docker compose version"
echo "3. Run: docker --version"
echo "4. Deploy Odoo: cd ~/ai-employee-system && docker compose up -d"
echo ""
