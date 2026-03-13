# Cloud Deployment Guide - Platinum Tier

## Overview

This guide walks you through deploying the AI Employee system on a cloud VM for 24/7 operation.

## Prerequisites

- Oracle Cloud account (or AWS/GCP account)
- Domain name (optional, for HTTPS)
- SSH key pair
- Credit card for cloud verification (even for free tier)

## Step 1: Create Oracle Cloud Free Tier Account

1. Go to https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in registration details
4. Verify identity (phone, credit card)
5. Wait for account approval (usually instant)

**Note**: Oracle Cloud Free Tier includes:
- 2 ARM-based VMs (4 OCPU each, 24GB RAM each)
- 200GB block storage
- Always Free resources

## Step 2: Launch Ubuntu VM

### 2.1 Create Instance

1. Log into Oracle Cloud Console
2. Navigate to **Compute** → **Instances**
3. Click **Create Instance**
4. Configure:
   - **Name**: `ai-employee-cloud`
   - **Compartment**: Select your compartment
   - **Availability Domain**: Any (prefer AD-1)
   - **Image**: Ubuntu 22.04 LTS (aarch64/ARM)
   - **Shape**: VM.Standard.A1.Flex (ARM Ampere)
     - OCPUs: 4
     - Memory: 24 GB
   - **Networking**:
     - VCN: Create new (default)
     - Subnet: Public
     - Assign public IPv4: Yes
   - **SSH Keys**: Upload your public key (`~/.ssh/id_rsa.pub`)

### 2.2 Configure Boot Volume

1. Under **Boot Volume**:
   - Size: 200 GB
   - Performance: Balanced

### 2.3 Launch

1. Review configuration
2. Click **Create**
3. Wait for instance to be RUNNING (2-5 minutes)
4. Note the public IP address

## Step 3: Configure Firewall

### 3.1 Oracle Cloud Network Security Group

1. In Oracle Cloud Console, go to **Networking** → **Virtual Cloud Networks**
2. Click your VCN
3. Click **Security Lists** → **Default Security List**
4. Add **Ingress Rules**:
   ```
   Rule 1:
   - Source CIDR: 0.0.0.0/0
   - Destination Port Range: 22 (SSH)
   - Description: SSH Access

   Rule 2:
   - Source CIDR: 0.0.0.0/0
   - Destination Port Range: 443 (HTTPS)
   - Description: HTTPS Access

   Rule 3:
   - Source CIDR: 0.0.0.0/0
   - Destination Port Range: 80 (HTTP)
   - Description: HTTP (for Let's Encrypt)
   ```

### 3.2 Ubuntu Firewall (UFW)

SSH into your VM:
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<YOUR_VM_IP>
```

Configure UFW:
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check status
sudo ufw status verbose
```

## Step 4: Install Docker and Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group (no sudo needed)
sudo usermod -aG docker $USER

# Enable Docker on boot
sudo systemctl enable docker
sudo systemctl enable containerd

# Verify installation
docker --version
docker compose version
```

**Logout and login again** for group changes to take effect.

## Step 5: Deploy Odoo Community 19+

### 5.1 Create Directory Structure

```bash
# Create Odoo directory
mkdir -p ~/odoo/{data,addons}
cd ~/odoo
```

### 5.2 Create Docker Compose File

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: odoo
    restart: unless-stopped
    ports:
      - "443:8069"
    depends_on:
      - db
    environment:
      - HOST=db
      - DATABASE=odoo_db
      - USER=odoo
      - PASSWORD=<STRONG_ODOO_PASSWORD>
    volumes:
      - ./data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
    networks:
      - odoo-network

  db:
    image: postgres:15
    container_name: odoo-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=odoo_db
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=<STRONG_ODOO_PASSWORD>
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - odoo-network

volumes:
  db-data:

networks:
  odoo-network:
    driver: bridge
```

**Important**: Replace `<STRONG_ODOO_PASSWORD>` with a strong password.

### 5.3 Start Odoo

```bash
cd ~/odoo
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f odoo
```

Odoo should now be accessible at `https://<YOUR_VM_IP>`

## Step 6: Set Up HTTPS with Let's Encrypt

### 6.1 Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 6.2 Get SSL Certificate

**Option A: With Domain**
```bash
sudo certbot certonly --standalone -d your-domain.com
```

**Option B: Without Domain (Self-Signed)**
```bash
# Create self-signed certificate
sudo mkdir -p /etc/ssl/odoo
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/odoo/odoo.key \
  -out /etc/ssl/odoo/odoo.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### 6.3 Configure Nginx Reverse Proxy

```bash
sudo apt install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/odoo
```

Add configuration:
```nginx
server {
    listen 80;
    server_name _;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    # SSL certificates
    ssl_certificate /etc/ssl/odoo/odoo.crt;
    ssl_certificate_key /etc/ssl/odoo/odoo.key;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Odoo proxy
    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Configure Odoo Database

1. Open browser: `https://<YOUR_VM_IP>`
2. Create Odoo database:
   - **Master Password**: Generate strong password
   - **Database Name**: `odoo_db`
   - **Email**: Your admin email
   - **Password**: Admin password
3. Install Accounting module:
   - Go to Apps
   - Search "Accounting"
   - Install "Invoicing" (free) or "Accounting" (full)

## Step 8: Set Up Automated Backups

### 8.1 Create Backup Script

Create `~/scripts/backup_odoo.sh`:
```bash
#!/bin/bash

BACKUP_DIR=~/odoo/backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker exec odoo-db pg_dump -U odoo odoo_db > $BACKUP_DIR/db_$DATE.sql

# Backup filestore
tar -czf $BACKUP_DIR/files_$DATE.tar.gz ~/odoo/data

# Keep only last 7 backups
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "files_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable:
```bash
chmod +x ~/scripts/backup_odoo.sh
```

### 8.2 Schedule Daily Backups

```bash
crontab -e
```

Add line:
```bash
0 2 * * * /home/ubuntu/scripts/backup_odoo.sh >> /home/ubuntu/logs/backup.log 2>&1
```

## Step 9: Install AI Employee System

### 9.1 Clone Repository

```bash
cd ~
git clone https://github.com/your-username/ai-employee-system.git
cd ai-employee-system
```

### 9.2 Install Python

```bash
# Install Python 3.13
sudo apt install -y python3.13 python3.13-venv python3-pip

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 9.3 Configure Environment

```bash
# Copy example env
cp .env.example .env.cloud

# Edit with your credentials
nano .env.cloud
```

Set cloud-specific variables:
```bash
# Cloud mode
CLOUD_MODE=true
DRY_RUN=false

# Odoo configuration
ODOO_URL=https://<YOUR_VM_IP>
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_API_KEY=<ODOO_API_KEY>

# Gmail (for cloud watcher)
GMAIL_CREDENTIALS=/home/ubuntu/credentials.json

# Social Media
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret

# Sync configuration
SYNC_METHOD=git
GIT_REMOTE_URL=git@github.com:your-username/ai-employee-vault.git
```

## Step 10: Set Up Systemd Services

### 10.1 Create Cloud Watcher Service

Create `/etc/systemd/system/ai-employee-cloud.service`:
```ini
[Unit]
Description=AI Employee Cloud Watcher
After=network.target docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-employee-system
ExecStart=/home/ubuntu/.local/bin/uv run python -m src.watchers.gmail_watcher
Restart=always
RestartSec=10
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
```

### 10.2 Create Orchestrator Service

Create `/etc/systemd/system/ai-employee-orchestrator.service`:
```ini
[Unit]
Description=AI Employee Orchestrator
After=network.target docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-employee-system
ExecStart=/home/ubuntu/.local/bin/uv run python main.py
Restart=always
RestartSec=10
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin:/bin"
EnvironmentFile=/home/ubuntu/ai-employee-system/.env.cloud

[Install]
WantedBy=multi-user.target
```

### 10.3 Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable ai-employee-cloud
sudo systemctl enable ai-employee-orchestrator

# Start services
sudo systemctl start ai-employee-cloud
sudo systemctl start ai-employee-orchestrator

# Check status
sudo systemctl status ai-employee-cloud
sudo systemctl status ai-employee-orchestrator
```

## Step 11: Configure Health Monitoring

### 11.1 Create Health Check Script

Create `src/monitoring/health_check.py`:
```python
#!/usr/bin/env python3
"""Health check endpoint for cloud services."""

import json
import os
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            health = get_health_status()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logging


def get_health_status() -> dict:
    """Get current health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": get_uptime(),
        "services": {
            "watchers": check_service("ai-employee-cloud"),
            "orchestrator": check_service("ai-employee-orchestrator"),
            "odoo": check_odoo(),
        }
    }


def get_uptime() -> str:
    """Get system uptime."""
    result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
    return result.stdout.strip()


def check_service(service_name: str) -> str:
    """Check if systemd service is running."""
    result = subprocess.run(
        ['systemctl', 'is-active', service_name],
        capture_output=True,
        text=True
    )
    return "running" if result.stdout.strip() == "active" else "failed"


def check_odoo() -> str:
    """Check if Odoo is accessible."""
    import requests
    try:
        response = requests.get(os.getenv('ODOO_URL', 'http://localhost:8069'), timeout=5)
        return "running" if response.status_code == 200 else "failed"
    except:
        return "failed"


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    print("Health check server running on port 8080")
    server.serve_forever()
```

### 11.2 Create Health Check Service

Create `/etc/systemd/system/ai-employee-health.service`:
```ini
[Unit]
Description=AI Employee Health Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-employee-system
ExecStart=/home/ubuntu/.local/bin/uv run python src/monitoring/health_check.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-health
sudo systemctl start ai-employee-health
sudo systemctl status ai-employee-health
```

## Step 12: Configure Git Sync

### 12.1 Create Private Git Repository

1. Go to GitHub/GitLab
2. Create private repository: `ai-employee-vault`
3. Copy SSH clone URL

### 12.2 Configure SSH Key for Git

```bash
# Generate SSH key for Git
ssh-keygen -t ed25519 -C "ai-employee-sync" -f ~/.ssh/id_ed25519_git

# Copy public key
cat ~/.ssh/id_ed25519_git.pub

# Add to GitHub/GitLab SSH keys
```

### 12.3 Initialize Vault Repository

```bash
cd ~/ai-employee-system/AI_Employee_Vault
git init
git remote add origin git@github.com:your-username/ai-employee-vault.git

# Create .gitignore
cat > .gitignore << EOF
.env*
*.token
*.key
*.pem
*.crt
sessions/
credentials/
*.secret
EOF

# Initial commit
git add .
git commit -m "Initial vault structure"
git push -u origin main
```

## Step 13: Test Deployment

### 13.1 Verify Services

```bash
# Check all services
sudo systemctl status ai-employee-cloud
sudo systemctl status ai-employee-orchestrator
sudo systemctl status ai-employee-health
sudo systemctl status nginx
sudo systemctl status docker

# Check Odoo
curl -k https://localhost

# Check health endpoint
curl http://localhost:8080/health
```

### 13.2 Test Sync

```bash
# Make change in vault
echo "# Test Update" >> AI_Employee_Vault/Dashboard.md

# Commit and push
cd AI_Employee_Vault
git add .
git commit -m "Test update"
git push

# Verify on local machine
git pull
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u ai-employee-cloud -n 50
sudo journalctl -u ai-employee-orchestrator -n 50

# Restart service
sudo systemctl restart ai-employee-cloud
```

### Odoo Not Accessible

```bash
# Check Odoo container
docker compose ps
docker compose logs odoo

# Restart Odoo
docker compose restart odoo
```

### Sync Issues

```bash
# Check Git status
cd AI_Employee_Vault
git status
git log -n 5

# Force pull (careful!)
git fetch origin
git reset --hard origin/main
```

## Next Steps

1. Configure local machine
2. Set up approval workflow
3. Test cloud/local interaction
4. Run Platinum demo scenario

---

*Guide Version: 1.0.0 | Platinum Tier*
