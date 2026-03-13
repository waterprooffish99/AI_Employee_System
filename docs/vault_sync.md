# Vault Sync Guide - Platinum Tier

## Overview

This guide covers vault synchronization between cloud and local environments.

## Sync Methods

### Method 1: Git Sync (Recommended)

**Pros**:
- Version history
- Conflict resolution
- Audit trail
- Works with any Git provider

**Cons**:
- Periodic sync (not real-time)
- Manual conflict resolution sometimes needed

### Method 2: Syncthing (Alternative)

**Pros**:
- Real-time sync
- Automatic conflict detection
- No central server needed

**Cons**:
- Both sides must be online
- Less audit history

## Git Sync Setup

### Step 1: Create Private Git Repository

1. Go to GitHub/GitLab/Bitbucket
2. Create **private** repository: `ai-employee-vault`
3. Do NOT initialize with README
4. Copy SSH clone URL

### Step 2: Generate SSH Key for Sync

```bash
# Generate dedicated SSH key for vault sync
ssh-keygen -t ed25519 -C "ai-employee-sync" -f ~/.ssh/id_ed25519_vault

# Copy public key
cat ~/.ssh/id_ed25519_vault.pub

# Add to GitHub/GitLab:
# GitHub: Settings → SSH and GPG keys → New SSH key
# GitLab: Settings → SSH Keys
```

### Step 3: Initialize Vault Repository

On **local machine**:
```bash
cd AI_Employee_Vault

# Initialize git
git init

# Add remote
git remote add origin git@github.com:your-username/ai-employee-vault.git

# Create .gitignore (CRITICAL - excludes secrets)
cat > .gitignore << 'EOF'
# Environment files (contain secrets)
.env
.env.*
.env.local
.env.*.local

# Token files
*.token
*.tokens
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

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs (contain sensitive data)
../AI_Employee_Vault/Audit_Logs/
../AI_Employee_Vault/CEO_Briefings/
EOF

# Initial commit
git add .
git commit -m "Initial vault structure (no secrets)"

# Push to remote
git branch -M main
git push -u origin main
```

### Step 4: Configure Cloud for Sync

On **cloud VM**:
```bash
cd ~/ai-employee-system/AI_Employee_Vault

# Initialize git
git init

# Add remote
git remote add origin git@github.com:your-username/ai-employee-vault.git

# Configure SSH for Git
cat >> ~/.ssh/config << 'EOF'
Host github.com
  IdentityFile ~/.ssh/id_ed25519_vault
  IdentitiesOnly yes
EOF

chmod 600 ~/.ssh/config

# Pull vault structure
git pull origin main
```

### Step 5: Create Sync Script

Create `scripts/sync_vault.sh`:
```bash
#!/bin/bash

# Vault sync script
# Run this on both cloud and local

VAULT_DIR=~/ai-employee-system/AI_Employee_Vault
cd "$VAULT_DIR" || exit 1

echo "Syncing vault at $(date)"

# Fetch latest
git fetch origin

# Check for changes
LOCAL_CHANGES=$(git status --porcelain)
REMOTE_CHANGES=$(git rev-list HEAD..origin/main --count)

if [ -n "$LOCAL_CHANGES" ]; then
    echo "Local changes detected:"
    echo "$LOCAL_CHANGES"
    
    # Commit local changes
    git add .
    git commit -m "Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
fi

if [ "$REMOTE_CHANGES" -gt 0 ]; then
    echo "Remote changes detected: $REMOTE_CHANGES commits"
    
    # Pull with strategy to prefer remote for markdown
    git pull --strategy-option=theirs
fi

# Push local changes
git push origin main

echo "Sync completed at $(date)"
```

Make executable:
```bash
chmod +x scripts/sync_vault.sh
```

### Step 6: Schedule Sync (Cron)

On **cloud VM**:
```bash
crontab -e
```

Add line (sync every 5 minutes):
```bash
*/5 * * * * /home/ubuntu/ai-employee-system/scripts/sync_vault.sh >> /home/ubuntu/logs/sync.log 2>&1
```

On **local machine** (Mac/Linux):
```bash
crontab -e
```

Add same line with appropriate path.

## Syncthing Setup (Alternative)

### Step 1: Install Syncthing

**Cloud VM**:
```bash
# Install Syncthing
curl -s https://syncthing.net/install.sh | sudo bash

# Start Syncthing
syncthing -no-browser -gui-address="127.0.0.1:8384"

# Create systemd service (optional)
sudo systemctl enable syncthing@ubuntu
sudo systemctl start syncthing@ubuntu
```

**Local Machine**:
- Download from https://syncthing.net/downloads/
- Install and run

### Step 2: Configure Syncthing

1. Open Syncthing UI (local): http://localhost:8384
2. Open Syncthing UI (cloud): SSH tunnel required
   ```bash
   ssh -L 8384:localhost:8384 ubuntu@<CLOUD_IP>
   ```
   Then open http://localhost:8384

3. Add devices:
   - Exchange device IDs between cloud and local
   - Accept pairing requests

4. Add folder:
   - Folder path: `~/ai-employee-system/AI_Employee_Vault`
   - Folder ID: `ai-employee-vault`
   - Share with: other device

### Step 3: Configure Ignore Patterns

In Syncthing UI, edit folder → Ignore Patterns:
```
.env*
*.token
*.key
*.pem
*.crt
sessions/
credentials/
*.secret
Audit_Logs/
CEO_Briefings/
```

## Security Rules

### NEVER Sync These Files

1. **Environment Files**:
   - `.env`
   - `.env.local`
   - `.env.*.local`

2. **Token Files**:
   - `*.token`
   - `*.access_token`
   - `*.refresh_token`

3. **Key Files**:
   - `*.key`
   - `*.pem`
   - `*.crt`
   - `*.p12`

4. **Credential Directories**:
   - `sessions/`
   - `credentials/`
   - `oauth/`
   - `auth/`

5. **Secret Files**:
   - `*.secret`
   - `*.password`

### Verify .gitignore

Before any commit:
```bash
cd AI_Employee_Vault
git status
git add .
git status  # Review what will be committed
```

**If you see any secrets**:
1. DO NOT COMMIT
2. Update `.gitignore`
3. Remove secrets from staging: `git reset`
4. Delete secrets if accidentally committed

## Conflict Resolution

### Git Conflicts

When conflicts occur:

```bash
cd AI_Employee_Vault

# See conflicts
git status

# View conflict
cat path/to/conflicted_file.md

# Resolve manually
# Edit file, remove conflict markers

# Or accept remote version
git checkout --theirs path/to/file

# Or accept local version
git checkout --ours path/to/file

# Complete merge
git add path/to/file
git commit
git push
```

### Syncthing Conflicts

Syncthing creates conflict copies:
- `filename.conflict-20260107-100000-ABC123.md`

Review and merge manually, then delete conflict copy.

## Testing Sync

### Test 1: Cloud → Local

1. On cloud: Create test file
   ```bash
   echo "# Test from Cloud" > AI_Employee_Vault/Test_Cloud.md
   ```

2. Run sync on cloud:
   ```bash
   ./scripts/sync_vault.sh
   ```

3. Run sync on local:
   ```bash
   ./scripts/sync_vault.sh
   ```

4. Verify file exists on local:
   ```bash
   cat AI_Employee_Vault/Test_Cloud.md
   ```

### Test 2: Local → Cloud

1. On local: Create test file
   ```bash
   echo "# Test from Local" > AI_Employee_Vault/Test_Local.md
   ```

2. Run sync on local

3. Run sync on cloud

4. Verify file exists on cloud

### Test 3: Secret Exclusion

1. Create test secret:
   ```bash
   echo "SECRET_KEY=12345" > AI_Employee_Vault/.env.test
   ```

2. Run sync:
   ```bash
   ./scripts/sync_vault.sh
   ```

3. Verify secret was NOT synced:
   - Check git status: should not show `.env.test`
   - Check remote: should not contain file

## Troubleshooting

### Sync Fails with Permission Error

```bash
# Fix SSH key permissions
chmod 600 ~/.ssh/id_ed25519_vault
chmod 600 ~/.ssh/config
```

### Git Conflict on Every Sync

```bash
# Reset to remote
git fetch origin
git reset --hard origin/main
```

### Syncthing Not Connecting

1. Check firewall (port 22000)
2. Verify device IDs exchanged
3. Check both devices online

### Large Sync Delays

- Git: Check network connection
- Syncthing: Check bandwidth limits in settings

## Best Practices

1. **Sync Before Important Operations**: Always sync before starting work
2. **Commit Often**: Small, frequent commits reduce conflicts
3. **Review Before Push**: Always review what will be synced
4. **Test Regularly**: Run sync tests weekly
5. **Backup**: Keep separate backups in addition to sync

---

*Guide Version: 1.0.0 | Platinum Tier*
