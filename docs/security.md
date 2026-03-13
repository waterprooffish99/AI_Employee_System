# Security Guide - Platinum Tier

## Overview

This document outlines security best practices for the AI Employee Platinum Tier deployment.

## Critical Security Rules

### Rule 1: Secrets Never Sync

**NEVER commit or sync these files**:

```bash
# Environment files
.env
.env.local
.env.*.local

# Token files
*.token
*.access_token
*.refresh_token

# Key files
*.key
*.pem
*.crt
*.p12
*.pfx

# Credential directories
sessions/
credentials/
oauth/
auth/

# Secret files
*.secret
*.secrets
*.password
*.passwd
```

**Verification**:
```bash
# Before any commit
git status
git add .
git status  # Review carefully

# Scan for secrets
./scripts/scan_secrets.sh
```

### Rule 2: Cloud is Draft-Only

**Cloud Agent Capabilities**:
- ✅ Read emails (Gmail Watcher)
- ✅ Draft email replies
- ✅ Monitor social media
- ✅ Draft social posts
- ✅ Monitor Odoo
- ✅ Draft invoices
- ❌ **Cannot send emails directly**
- ❌ **Cannot post to social media directly**
- ❌ **Cannot post invoices directly**

**Local Agent Capabilities**:
- ✅ Review cloud drafts
- ✅ Approve/reject actions
- ✅ Send emails (after approval)
- ✅ Post to social media (after approval)
- ✅ Post invoices (after approval)
- ✅ WhatsApp messaging (local only)
- ✅ Banking operations (local only)

### Rule 3: Separate Secrets by Environment

**Cloud Secrets** (stored on cloud VM only):
```bash
# /home/ubuntu/ai-employee-system/.env.cloud
CLOUD_MODE=true
ODOO_URL=https://<cloud-ip>
GMAIL_CREDENTIALS=/home/ubuntu/credentials.json
FACEBOOK_APP_ID=xxx
TWITTER_API_KEY=xxx
```

**Local Secrets** (stored on local machine only):
```bash
# ~/.ai-employee/.env.local
LOCAL_MODE=true
WHATSAPP_SESSION_PATH=~/.whatsapp/session
BANK_API_TOKEN=xxx
PAYMENT_TOKEN=xxx
```

**Never Stored in Sync**:
- Any `.env` files
- Any tokens
- Any keys
- Any credentials

## Firewall Configuration

### Cloud VM Firewall

**Oracle Cloud NSG**:
```
Ingress Rules:
- Port 22 (SSH): 0.0.0.0/0 (Your IP recommended)
- Port 443 (HTTPS): 0.0.0.0/0
- Port 80 (HTTP): 0.0.0.0/0 (Let's Encrypt)
- All others: DENY
```

**Ubuntu UFW**:
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (restrict to your IP)
sudo ufw allow from <YOUR_IP> to any port 22

# Allow HTTPS
sudo ufw allow 443/tcp

# Allow HTTP (for Let's Encrypt)
sudo ufw allow 80/tcp

# Status
sudo ufw status verbose
```

### Local Machine Firewall

**macOS**:
```bash
# Enable firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on

# Block incoming connections
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setblockall on
```

**Linux**:
```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

## SSH Key Management

### Generate Dedicated Keys

```bash
# For cloud VM access
ssh-keygen -t ed25519 -C "cloud-vm-access" -f ~/.ssh/id_ed25519_cloud

# For Git sync
ssh-keygen -t ed25519 -C "vault-sync" -f ~/.ssh/id_ed25519_vault

# Set permissions
chmod 600 ~/.ssh/id_ed25519_*
chmod 600 ~/.ssh/id_ed25519_*.pub
```

### SSH Configuration

Create `~/.ssh/config`:
```
# Cloud VM
Host ai-cloud
    HostName <CLOUD_IP>
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519_cloud
    IdentitiesOnly yes

# GitHub (vault sync)
Host github.com
    IdentityFile ~/.ssh/id_ed25519_vault
    IdentitiesOnly yes
```

## Secret Scanning

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Scan for secrets before commit
echo "Scanning for secrets..."

# Patterns to check
PATTERNS=(
    "AKIA[0-9A-Z]{16}"           # AWS Access Key
    "ghp_[a-zA-Z0-9]{36}"        # GitHub Personal Access Token
    "xox[baprs]-[0-9a-zA-Z]{10}" # Slack Token
    "password\s*=\s*['\"][^'\"]+['\"]"
    "api_key\s*=\s*['\"][^'\"]+['\"]"
    "secret\s*=\s*['\"][^'\"]+['\"]"
)

FOUND=false
for pattern in "${PATTERNS[@]}"; do
    if git diff --cached --all-match --quiet -G "$pattern"; then
        continue
    else
        echo "⚠ Potential secret detected: $pattern"
        FOUND=true
    fi
done

if [ "$FOUND" = true ]; then
    echo "❌ Commit blocked: Potential secrets detected"
    echo "Review files before committing"
    exit 1
fi

echo "✓ No secrets detected"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Secret Scan Script

Create `scripts/scan_secrets.sh`:
```bash
#!/bin/bash

echo "Scanning for secrets..."

# Directories to scan
SCAN_DIRS=(
    "AI_Employee_Vault"
    "src"
    "specs"
    "docs"
)

# Patterns to check
PATTERNS=(
    ".env"
    "*.token"
    "*.key"
    "*.pem"
    "password="
    "api_key="
    "secret="
)

FOUND=false
for dir in "${SCAN_DIRS[@]}"; do
    for pattern in "${PATTERNS[@]}"; do
        if find "$dir" -name "$pattern" 2>/dev/null | grep -q .; then
            echo "⚠ Found: $dir/$pattern"
            FOUND=true
        fi
    done
done

if [ "$FOUND" = true ]; then
    echo "❌ Review files above - should not be committed"
    exit 1
fi

echo "✓ No secrets found"
exit 0
```

## Access Control

### Cloud VM Access

**Authorized Users Only**:
```bash
# /home/ubuntu/.ssh/authorized_keys
# Add only authorized public keys
ssh-ed25519 AAAA... user@local-machine
```

**Restrict SSH**:
```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers ubuntu
```

### Local Machine Access

- Use strong password
- Enable disk encryption
- Lock screen when away
- No remote access unless necessary

## Audit Logging

### Enable Comprehensive Logging

All actions logged to `AI_Employee_Vault/Audit_Logs/`:
- Email drafts created
- Social drafts created
- Odoo drafts created
- Approvals requested
- Approvals granted/rejected
- Actions executed
- Sync operations

### Review Logs Regularly

```bash
# Daily log review
tail -100 AI_Employee_Vault/Audit_Logs/audit.log

# Search for specific action
grep "email_sent" AI_Employee_Vault/Audit_Logs/audit.log

# Check for errors
grep "ERROR" AI_Employee_Vault/Audit_Logs/audit.log
```

## Incident Response

### If Secrets Are Leaked

1. **Immediate Actions**:
   ```bash
   # Revoke compromised credentials
   # Change passwords
   # Rotate API keys
   ```

2. **Investigate**:
   ```bash
   # Check git history
   git log --all --full-history -- .env
   
   # Check who accessed
   git log --format="%H %an %ad" -- .env
   ```

3. **Prevent Recurrence**:
   - Update `.gitignore`
   - Add pre-commit hooks
   - Review access controls

### If Cloud Is Compromised

1. **Isolate**:
   - Stop cloud VM
   - Revoke cloud API keys
   - Change cloud passwords

2. **Investigate**:
   - Review cloud logs
   - Check for unauthorized access
   - Audit all actions

3. **Recover**:
   - Deploy new cloud VM
   - Rotate all credentials
   - Restore from backup

## Security Checklist

### Before Deployment

- [ ] All secrets in `.gitignore`
- [ ] SSH keys generated and configured
- [ ] Firewall rules configured
- [ ] Pre-commit hooks installed
- [ ] Secret scanning script tested

### Weekly

- [ ] Review audit logs
- [ ] Check for secret exposure
- [ ] Verify firewall rules
- [ ] Update system packages
- [ ] Review access logs

### Monthly

- [ ] Rotate API keys
- [ ] Review authorized users
- [ ] Test backup restoration
- [ ] Security audit
- [ ] Update documentation

## Compliance Considerations

### Data Privacy

- Personal data stored locally only
- Cloud has draft-only access
- User approval required for all actions
- Comprehensive audit trail maintained

### Data Retention

- Audit logs: 90 days
- CEO Briefings: 1 year
- Drafts: Until approved/rejected
- Sync history: Git history (indefinite)

---

*Guide Version: 1.0.0 | Platinum Tier*
