# Platinum Tier Migration Guide

**From**: Gold Tier (v0.3.0)
**To**: Platinum Tier (v0.4.0)
**Estimated Time**: 2-4 hours

---

## Overview

This guide helps you migrate from Gold Tier (single-machine) to Platinum Tier (cloud + local architecture).

---

## Prerequisites

Before migrating, ensure you have:

- [ ] Gold Tier system working correctly
- [ ] All Gold Tier tests passing
- [ ] Recent backup of your vault
- [ ] Cloud VM account (Oracle Cloud Free Tier recommended)
- [ ] Domain name (optional, for HTTPS)
- [ ] SSH key pair

---

## Migration Steps

### Phase 1: Cloud Setup (1-2 hours)

#### Step 1.1: Deploy Cloud VM

Follow `docs/cloud_deployment.md` to:
1. Create Oracle Cloud account
2. Launch Ubuntu 22.04 VM
3. Configure firewall
4. Set up SSH keys

#### Step 1.2: Install Dependencies

On cloud VM:
```bash
# Run installation script
bash scripts/cloud_install_docker.sh

# Verify installation
docker --version
docker compose version
```

#### Step 1.3: Deploy Odoo

```bash
# Copy docker-compose.yml to cloud
scp docker-compose.yml ubuntu@<CLOUD_IP>:~/odoo/

# Start Odoo
cd ~/odoo
docker compose up -d

# Verify Odoo running
docker compose ps
```

#### Step 1.4: Configure Health Monitoring

```bash
# Copy health check script
scp src/monitoring/health_check.py ubuntu@<CLOUD_IP>:~/ai-employee-system/

# Create systemd service
sudo nano /etc/systemd/system/ai-employee-health.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-health
sudo systemctl start ai-employee-health
```

---

### Phase 2: Vault Sync Setup (30 minutes)

#### Step 2.1: Create Git Repository

1. Create private GitHub/GitLab repository: `ai-employee-vault`
2. Generate SSH key for sync:
   ```bash
   ssh-keygen -t ed25519 -C "vault-sync" -f ~/.ssh/id_ed25519_vault
   ```
3. Add public key to GitHub/GitLab

#### Step 2.2: Initialize Vault Sync

On **local machine**:
```bash
cd AI_Employee_Vault
git init
git remote add origin git@github.com:your-username/ai-employee-vault.git
git add .
git commit -m "Initial vault structure"
git push -u origin main
```

On **cloud VM**:
```bash
cd ~/ai-employee-system/AI_Employee_Vault
git init
git remote add origin git@github.com:your-username/ai-employee-vault.git
git pull origin main
```

#### Step 2.3: Configure Sync Schedule

On both cloud and local:
```bash
# Add to crontab
crontab -e

# Add line (sync every 5 minutes)
*/5 * * * * /path/to/scripts/sync_scheduler.sh
```

---

### Phase 3: Work-Zone Configuration (30 minutes)

#### Step 3.1: Update Cloud Configuration

On cloud VM, create `.env.cloud`:
```bash
CLOUD_MODE=true
DRY_RUN=false

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_API_KEY=<your-api-key>

# Gmail (for cloud watcher)
GMAIL_CREDENTIALS=/home/ubuntu/credentials.json

# Sync
SYNC_METHOD=git
GIT_REMOTE_URL=git@github.com:your-username/ai-employee-vault.git
```

#### Step 3.2: Update Local Configuration

On local machine, create `.env.local`:
```bash
LOCAL_MODE=true
DRY_RUN=false

# WhatsApp (local only)
WHATSAPP_SESSION_PATH=~/.whatsapp/session

# Banking (local only)
BANK_API_TOKEN=<your-token>

# Sync
SYNC_METHOD=git
GIT_REMOTE_URL=git@github.com:your-username/ai-employee-vault.git
```

#### Step 3.3: Create Domain Folders

```bash
# Run folder creation script
mkdir -p AI_Employee_Vault/Needs_Action/{cloud,local,shared}
mkdir -p AI_Employee_Vault/In_Progress/{cloud,local}
mkdir -p AI_Employee_Vault/Pending_Approval/{cloud,local}
mkdir -p AI_Employee_Vault/Updates/{email_drafts,social_drafts,odoo_drafts,health}
mkdir -p AI_Employee_Vault/Signals/{cloud_to_local}
touch AI_Employee_Vault/Needs_Action/{cloud,local,shared}/.gitkeep
touch AI_Employee_Vault/In_Progress/{cloud,local}/.gitkeep
touch AI_Employee_Vault/Pending_Approval/{cloud,local}/.gitkeep
touch AI_Employee_Vault/Updates/{email_drafts,social_drafts,odoo_drafts,health}/.gitkeep
touch AI_Employee_Vault/Signals/{cloud_to_local}/.gitkeep
```

---

### Phase 4: Security Hardening (15 minutes)

#### Step 4.1: Install Pre-commit Hook

```bash
# Copy pre-commit hook
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### Step 4.2: Run Security Audit

```bash
# Run security audit
bash scripts/security_audit.sh

# Fix any issues reported
```

#### Step 4.3: Verify Secret Exclusion

```bash
# Run secret scan
bash scripts/scan_secrets.sh

# Verify .gitignore is correct
cat AI_Employee_Vault/.gitignore
```

---

### Phase 5: Testing (15 minutes)

#### Step 5.1: Run Platinum Demo Test

```bash
# Run demo test
uv run python tests/test_platinum_demo.py --vault ./AI_Employee_Vault --verbose

# Verify all steps pass
```

#### Step 5.2: Test Sync

```bash
# On cloud: create test file
echo "# Cloud Test" > AI_Employee_Vault/Test_Cloud.md
bash scripts/sync_vault.sh

# On local: verify file received
cat AI_Employee_Vault/Test_Cloud.md

# On local: create test file
echo "# Local Test" > AI_Employee_Vault/Test_Local.md
bash scripts/sync_vault.sh

# On cloud: verify file received
cat AI_Employee_Vault/Test_Local.md
```

#### Step 5.3: Test Approval Workflow

1. Create draft in `/Updates/email_drafts/` on cloud
2. Sync to local
3. Local moves to `/Pending_Approval/local/`
4. User approves (moves to `/Approved/`)
5. Verify execution

---

## Rollback Procedure

If migration fails, rollback to Gold Tier:

### Step 1: Stop Cloud Services

```bash
# On cloud VM
sudo systemctl stop ai-employee-health
sudo systemctl stop ai-employee-cloud
sudo systemctl stop ai-employee-orchestrator
```

### Step 2: Restore Vault from Backup

```bash
# On local machine
cd AI_Employee_Vault
git reset --hard <pre-migration-commit>
```

### Step 3: Restore Gold Tier Configuration

```bash
# Restore .env
cp .env.gold .env

# Restart Gold Tier services
python main.py
```

---

## Post-Migration Checklist

After migration, verify:

- [ ] Cloud VM running and accessible
- [ ] Odoo accessible via HTTPS
- [ ] Health monitoring working
- [ ] Sync working (cloud → local)
- [ ] Sync working (local → cloud)
- [ ] Cloud can create drafts
- [ ] Local can approve drafts
- [ ] Local can execute actions
- [ ] Security audit passes
- [ ] No secrets in git
- [ ] Platinum demo test passes

---

## Troubleshooting

### Sync Not Working

1. Check SSH keys configured correctly
2. Verify git remote URL
3. Check `.gitignore` not blocking files
4. Run `bash scripts/sync_vault.sh` manually

### Cloud Can't Create Drafts

1. Check `.env.cloud` configuration
2. Verify `/Updates/` directory exists
3. Check file permissions

### Local Can't Approve

1. Check `.env.local` configuration
2. Verify `/Pending_Approval/local/` directory exists
3. Check approval handler imports correctly

### Security Audit Fails

1. Review specific failures
2. Fix file permissions: `chmod 600 .env*`
3. Remove secrets from git: `git rm --cached <file>`

---

## Next Steps

After successful migration:

1. **Monitor for 48 hours**: Watch for sync issues, approval bottlenecks
2. **Configure alerts**: Set up health monitoring alerts
3. **Train users**: Show approval workflow to users
4. **Document customizations**: Update this guide with your specific setup

---

*Migration Guide v1.0.0 | Platinum Tier*
