# Vault Sync Guide - Platinum Tier

**Bidirectional Git-based sync between Cloud and Local agents**

---

## Architecture

```
┌─────────────────────┐                    ┌─────────────────────┐
│   CLOUD AGENT       │                    │   LOCAL AGENT       │
│   (Oracle VM)       │                    │   (Your Laptop)     │
│                     │                    │                     │
│  /Updates/ ─┐       │                    │       ┌── /Updates/ │
│  /Signals/ ─┼───────┼── Git Push/Pull ───┼───────┼── /Signals/ │
│  /Plans/ ───┘       │      (5 min)       │       └── /Plans/  │
│                     │                    │                     │
│  In_Progress/cloud/ │                    │ │ In_Progress/local/│
│                     │                    │                     │
└─────────────────────┘                    └─────────────────────┘
              │                                        │
              └────────────┐              ┌────────────┘
                           │              │
                           ▼              │
                    ┌─────────────────────┐
                    │  Private Git Repo   │
                    │  (GitHub/GitLab)    │
                    │  - Markdown only    │
                    │  - No secrets       │
                    └─────────────────────┘
```

---

## Security Model

**What IS Synced** (Markdown/State files):
- ✅ `/Updates/` - Draft emails, social posts, Odoo actions
- ✅ `/Signals/` - Inter-agent notifications
- ✅ `/Plans/` - Execution plans
- ✅ `/In_Progress/<agent>/` - Claimed tasks
- ✅ `Dashboard.md` - Merged (local preferred)
- ✅ `Company_Handbook.md` - Shared rules
- ✅ `Business_Goals.md` - Shared objectives

**What is NEVER Synced** (Secrets):
- ❌ `.env` - Environment variables
- ❌ `*.session` - WhatsApp/email sessions
- ❌ `credentials.json` - OAuth credentials
- ❌ `*.token` - Access/refresh tokens
- ❌ `Audit_Logs/` - Contains sensitive data
- ❌ `CEO_Briefings/` - Business sensitive
- ❌ `Logs/` - May contain sensitive info

**Enforced by**: `.gitignore` (vault root)

---

## Setup Guide (15 minutes)

### Step 1: Create Private Git Repository

```bash
# GitHub (recommended)
# 1. Go to https://github.com/new
# 2. Repository name: ai-employee-vault
# 3. Visibility: Private
# 4. Do NOT initialize with README
# 5. Click "Create repository"
```

### Step 2: Generate SSH Key (Recommended over HTTPS)

```bash
# Generate key
ssh-keygen -t ed25519 -C "vault-sync" -f ~/.ssh/vault_sync

# Copy public key
cat ~/.ssh/vault_sync.pub

# Add to GitHub:
# Settings → SSH and GPG keys → New SSH Key
# Paste the key, name it "Vault Sync"
```

### Step 3: Initialize Vault Git Repository

```bash
cd AI_Employee_Vault

# Initialize git
git init
git checkout -b main

# Configure git
git config user.email "ai-employee@localhost"
git config user.name "AI Employee Sync"

# Add remote (replace with your repo URL)
git remote add origin git@github.com:YOUR_USERNAME/ai-employee-vault.git

# Verify .gitignore exists
cat .gitignore | head -20

# Initial commit
git add -A
git commit -m "Initial vault state"

# Push to remote
git push -u origin main
```

### Step 4: Configure Environment

```bash
# Edit .env on BOTH cloud and local
nano .env

# Add these lines:
VAULT_GIT_REPO_URL=git@github.com:YOUR_USERNAME/ai-employee-vault.git
VAULT_GIT_BRANCH=main
VAULT_SYNC_INTERVAL=300  # 5 minutes
```

### Step 5: Set Up Cron Jobs

#### Cloud VM (every 5 minutes):

```bash
# Edit crontab
crontab -e

# Add line:
*/5 * * * * cd /home/ubuntu/AI_Employee_System && bash scripts/cloud_vault_sync.sh
```

#### Local Machine (every 5 minutes):

**Linux/Mac**:
```bash
crontab -e

# Add line:
*/5 * * * * cd /path/to/AI_Employee_System && bash scripts/local_vault_sync.sh
```

**Windows (Task Scheduler)**:
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "-m src.utils.vault_sync_orchestrator --mode local" `
  -WorkingDirectory "C:\path\to\AI_Employee_System"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "VaultSync" `
  -Action $action -Trigger $trigger -User "YOUR_USER"
```

---

## Claim-by-Move Rule

**Problem**: Two agents might process the same task simultaneously.

**Solution**: Claim-by-move prevents double-processing.

### How It Works

1. **Task arrives** in `/Needs_Action/email_123.md`
2. **Cloud agent** sees task, wants to process
3. **Cloud moves** file:
   ```
   /Needs_Action/email_123.md
   → /In_Progress/cloud/email_123.md
   ```
4. **Local agent** scans `/Needs_Action/`
5. **Local sees** file NOT in `/Needs_Action/`
6. **Local ignores** task (already claimed)

### Manual Claim

```bash
# Cloud agent claims task
python -m src.utils.vault_sync_orchestrator \
  --mode cloud \
  --vault-path ./AI_Employee_Vault \
  --claim ./AI_Employee_Vault/Needs_Action/email_123.md
```

### Release Task (if agent can't complete)

```bash
# Python script
from src.utils.vault_sync_orchestrator import VaultSyncOrchestrator

orchestrator = VaultSyncOrchestrator(
    vault_path='./AI_Employee_Vault',
    agent_name='cloud'
)

task_file = Path('./AI_Employee_Vault/In_Progress/cloud/email_123.md')
orchestrator.release_task(task_file, reason="Requires local approval")
```

---

## Conflict Resolution

### Dashboard.md Conflicts

**Scenario**: Both cloud and local update Dashboard.md simultaneously.

**Resolution Strategy**: Local wins (preserves user's manual edits).

```bash
# If conflict detected:
# 1. Git marks conflict in Dashboard.md
# 2. Local agent keeps local version
# 3. Cloud agent accepts local version
# 4. No manual intervention needed
```

### Plan.md Conflicts

**Strategy**: Merge both plans (additive).

```bash
# Orchestrator automatically merges:
# - Cloud adds sections to Plan.md
# - Local adds sections to same Plan.md
# - Git auto-merges if no line conflicts
```

---

## Testing Sync

### Test 1: Cloud → Local

```bash
# 1. On cloud VM: Create test file
echo "Test from cloud" > AI_Employee_Vault/Updates/cloud_test.md

# 2. Run cloud sync
bash scripts/cloud_vault_sync.sh

# 3. Wait 5 minutes (or run immediately on local)
bash scripts/local_vault_sync.sh

# 4. Verify file exists on local
cat AI_Employee_Vault/Updates/cloud_test.md
```

### Test 2: Local → Cloud

```bash
# 1. On local: Create test file
echo "Test from local" > AI_Employee_Vault/Signals/local_test.md

# 2. Run local sync
bash scripts/local_vault_sync.sh

# 3. On cloud: Pull changes
bash scripts/cloud_vault_sync.sh

# 4. Verify file exists on cloud
cat AI_Employee_Vault/Signals/local_test.md
```

### Test 3: Claim-by-Move

```bash
# 1. Create test task
echo "Test task" > AI_Employee_Vault/Needs_Action/test_claim.md

# 2. Cloud claims task
python -m src.utils.vault_sync_orchestrator \
  --mode cloud \
  --vault-path ./AI_Employee_Vault \
  --claim ./AI_Employee_Vault/Needs_Action/test_claim.md

# 3. Verify moved
ls AI_Employee_Vault/In_Progress/cloud/test_claim.md
# Should exist

ls AI_Employee_Vault/Needs_Action/test_claim.md
# Should NOT exist
```

---

## Troubleshooting

### Issue: Git Push Fails (Permission Denied)

```bash
# Check SSH key
ssh -T git@github.com

# If fails, re-add SSH key:
# 1. Copy ~/.ssh/vault_sync.pub
# 2. Add to GitHub SSH keys
# 3. Test again
```

### Issue: Merge Conflicts in Dashboard.md

```bash
# Check conflict markers
grep -n "<<<<<<" AI_Employee_Vault/Dashboard.md

# If conflicts exist:
# 1. Edit Dashboard.md manually
# 2. Remove conflict markers
# 3. Keep desired content
# 4. git add Dashboard.md
# 5. git commit
# 6. git push
```

### Issue: Sync Not Running

```bash
# Check cron status
systemctl status cron  # Linux
crontab -l  # List cron jobs

# Check logs
tail -f AI_Employee_Vault/Logs/vault_sync_*.log

# Manual test
bash scripts/cloud_vault_sync.sh
# or
bash scripts/local_vault_sync.sh
```

### Issue: Large Files Blocking Sync

```bash
# Find large files
find AI_Employee_Vault -type f -size +1M

# Add to .gitignore if should not sync
echo "LargeFile.pdf" >> AI_Employee_Vault/.gitignore

# Remove from git cache
git rm --cached AI_Employee_Vault/LargeFile.pdf
git commit -m "Remove large file from sync"
```

---

## Performance Optimization

### Reduce Sync Frequency

```bash
# Edit .env
VAULT_SYNC_INTERVAL=600  # 10 minutes instead of 5
```

### Sync Only Critical Directories

```python
# Edit vault_sync_orchestrator.py
self.sync_dirs = ['Updates/', 'Signals/']  # Exclude Plans/
```

### Compress Git History

```bash
cd AI_Employee_Vault

# Garbage collect
git gc --aggressive

# Prune old objects
git prune

# Verify size
du -sh .git
```

---

## Acceptance Criteria Checklist

- [ ] Private GitHub repo created
- [ ] SSH key generated and added to GitHub
- [ ] Vault initialized as git repo
- [ ] `.gitignore` verified (secrets excluded)
- [ ] Initial commit pushed
- [ ] Cloud cron job configured
- [ ] Local cron job configured
- [ ] Cloud → Local sync tested
- [ ] Local → Cloud sync tested
- [ ] Claim-by-move tested
- [ ] No secrets synced (verified)

---

**Next Step**: Proceed to Phase 1.6 - Health Monitoring
