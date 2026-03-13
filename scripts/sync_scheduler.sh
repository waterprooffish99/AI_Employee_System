#!/bin/bash
# Sync Scheduler for AI Employee Vault
# Run this via cron to sync vault periodically

set -e

# Configuration
VAULT_DIR="${VAULT_DIR:-$HOME/ai-employee-system/AI_Employee_Vault}"
SYNC_METHOD="${SYNC_METHOD:-git}"  # git or syncthing
LOG_FILE="${LOG_FILE:-$HOME/logs/sync_scheduler.log}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
GIT_BRANCH="${GIT_BRANCH:-main}"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log "Starting sync scheduler (method: $SYNC_METHOD)..."

# Check if vault directory exists
if [ ! -d "$VAULT_DIR" ]; then
    log "ERROR: Vault directory not found: $VAULT_DIR"
    exit 1
fi

cd "$VAULT_DIR"

if [ "$SYNC_METHOD" = "git" ]; then
    # Check if git repository
    if [ ! -d ".git" ]; then
        log "ERROR: Not a git repository. Initialize with: git init"
        exit 1
    fi

    log "Running Git sync..."
    
    # Fetch latest from remote
    if ! git fetch "$GIT_REMOTE" 2>&1 | tee -a "$LOG_FILE"; then
        log "ERROR: Failed to fetch from remote"
        exit 1
    fi
    log "✓ Fetch completed"

    # Check for local changes
    LOCAL_CHANGES=$(git status --porcelain 2>/dev/null || true)

    if [ -n "$LOCAL_CHANGES" ]; then
        log "Local changes detected, committing..."
        git add .
        if git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')" 2>&1 | tee -a "$LOG_FILE"; then
            log "✓ Local changes committed"
        else
            log "No changes to commit or commit failed"
        fi
    else
        log "✓ No local changes"
    fi

    # Check for remote changes
    REMOTE_AHEAD=$(git rev-list HEAD.."$GIT_REMOTE/$GIT_BRANCH" --count 2>/dev/null || echo "0")

    if [ "$REMOTE_AHEAD" -gt 0 ]; then
        log "Remote changes detected: $REMOTE_AHEAD commit(s), pulling..."
        if git pull --strategy-option=theirs "$GIT_REMOTE" "$GIT_BRANCH" 2>&1 | tee -a "$LOG_FILE"; then
            log "✓ Remote changes pulled"
        else
            log "ERROR: Failed to pull remote changes (conflict?)"
            exit 1
        fi
    else
        log "✓ Up to date with remote"
    fi

    # Push local changes
    log "Pushing to remote..."
    if git push "$GIT_REMOTE" "$GIT_BRANCH" 2>&1 | tee -a "$LOG_FILE"; then
        log "✓ Push completed"
    else
        log "ERROR: Failed to push to remote"
        exit 1
    fi

    log "✓ Git sync completed successfully"

elif [ "$SYNC_METHOD" = "syncthing" ]; then
    # For Syncthing, just verify it's running
    log "Checking Syncthing status..."
    
    if pgrep -x "syncthing" > /dev/null; then
        log "✓ Syncthing is running"
    else
        log "WARNING: Syncthing is not running"
        log "Start Syncthing manually or via systemd service"
    fi

    log "✓ Syncthing sync check completed"
else
    log "ERROR: Unknown sync method: $SYNC_METHOD"
    log "Valid methods: git, syncthing"
    exit 1
fi

log "Sync scheduler completed at $(date)"
