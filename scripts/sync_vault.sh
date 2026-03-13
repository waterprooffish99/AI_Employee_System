#!/bin/bash
# Vault Sync Script - Git Method
# Run this on both cloud and local machines

set -e

# Configuration
VAULT_DIR="${VAULT_DIR:-$HOME/ai-employee-system/AI_Employee_Vault}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
GIT_BRANCH="${GIT_BRANCH:-main}"
LOG_FILE="${LOG_FILE:-$HOME/logs/sync_vault.log}"
AUTO_COMMIT="${AUTO_COMMIT:-true}"
SYNC_INTERVAL="${SYNC_INTERVAL:-300}"  # 5 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    log "${GREEN}✓ $1${NC}"
}

log_warning() {
    log "${YELLOW}⚠ $1${NC}"
}

log_error() {
    log "${RED}✗ $1${NC}"
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log "Starting vault sync..."

# Check if vault directory exists
if [ ! -d "$VAULT_DIR" ]; then
    log_error "Vault directory not found: $VAULT_DIR"
    exit 1
fi

cd "$VAULT_DIR"

# Check if git repository
if [ ! -d ".git" ]; then
    log_error "Not a git repository. Initialize with: git init"
    exit 1
fi

# Fetch latest from remote
log "Fetching from remote..."
if ! git fetch "$GIT_REMOTE" 2>&1 | tee -a "$LOG_FILE"; then
    log_error "Failed to fetch from remote"
    exit 1
fi
log_success "Fetch completed"

# Check for local changes
LOCAL_CHANGES=$(git status --porcelain 2>/dev/null || true)

if [ -n "$LOCAL_CHANGES" ]; then
    log_warning "Local changes detected:"
    echo "$LOCAL_CHANGES" | tee -a "$LOG_FILE"
    
    if [ "$AUTO_COMMIT" = true ]; then
        log "Auto-committing local changes..."
        git add .
        if git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Local changes committed"
        else
            log_warning "No changes to commit or commit failed"
        fi
    else
        log_warning "Auto-commit disabled. Please commit manually."
    fi
else
    log_success "No local changes"
fi

# Check for remote changes
REMOTE_AHEAD=$(git rev-list HEAD.."$GIT_REMOTE/$GIT_BRANCH" --count 2>/dev/null || echo "0")

if [ "$REMOTE_AHEAD" -gt 0 ]; then
    log "Remote changes detected: $REMOTE_AHEAD commit(s)"
    
    # Pull with strategy to prefer remote for markdown files
    log "Pulling remote changes..."
    if git pull --strategy-option=theirs "$GIT_REMOTE" "$GIT_BRANCH" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Remote changes pulled"
    else
        log_error "Failed to pull remote changes (conflict?)"
        log "Manual resolution required:"
        log "  1. Review conflicts: git status"
        log "  2. Resolve: git mergetool or edit files"
        log "  3. Complete: git add <files> && git commit"
        exit 1
    fi
else
    log_success "Up to date with remote"
fi

# Push local changes (if any)
log "Pushing to remote..."
if git push "$GIT_REMOTE" "$GIT_BRANCH" 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Push completed"
else
    log_error "Failed to push to remote"
    log "Possible causes:"
    log "  - Remote has changes you don't have (pull first)"
    log "  - Network issue"
    log "  - Permission denied (check SSH keys)"
    exit 1
fi

# Show current status
log "Current status:"
git status --short 2>&1 | tee -a "$LOG_FILE"

# Show last commit
log "Last commit:"
git log -1 --oneline 2>&1 | tee -a "$LOG_FILE"

log_success "Vault sync completed successfully"

# Output sync info
echo ""
echo "Sync Summary:"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Vault: $VAULT_DIR"
echo "  Remote: $GIT_REMOTE/$GIT_BRANCH"
echo "  Log: $LOG_FILE"
echo ""
