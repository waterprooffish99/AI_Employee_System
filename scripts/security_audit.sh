#!/bin/bash
# Security Audit Script for AI Employee System
# Performs comprehensive security checks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "======================================"
echo "AI Employee Security Audit"
echo "======================================"
echo ""

AUDIT_PASSED=true
AUDIT_WARNINGS=0
AUDIT_CRITICAL=0

# Function to log pass
pass() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to log warning
warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((AUDIT_WARNINGS++)) || true
}

# Function to log critical
critical() {
    echo -e "${RED}❌${NC} $1"
    ((AUDIT_CRITICAL++)) || true
    AUDIT_PASSED=false
}

# Function to log info
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "=== File Permissions ==="
echo ""

# Check .env file permissions
if [ -f ".env" ] || [ -f ".env.cloud" ] || [ -f ".env.local" ]; then
    for env_file in .env .env.cloud .env.local; do
        if [ -f "$env_file" ]; then
            perms=$(stat -c %a "$env_file" 2>/dev/null || stat -f %A "$env_file" 2>/dev/null || echo "unknown")
            if [ "$perms" = "600" ] || [ "$perms" = "400" ]; then
                pass "$env_file has secure permissions ($perms)"
            else
                warn "$env_file has loose permissions ($perms), should be 600"
                info "  Fix: chmod 600 $env_file"
            fi
        fi
    done
else
    info "No .env files found in current directory"
fi

# Check scripts are executable
for script in scripts/*.sh; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            pass "$script is executable"
        else
            warn "$script is not executable"
            info "  Fix: chmod +x $script"
        fi
    fi
done

echo ""
echo "=== Git Security ==="
echo ""

# Check .gitignore exists
if [ -f ".gitignore" ]; then
    pass ".gitignore exists"
    
    # Check for critical patterns
    if grep -q "\.env" .gitignore; then
        pass ".gitignore excludes .env files"
    else
        critical ".gitignore does not exclude .env files"
    fi
    
    if grep -q "\.token" .gitignore; then
        pass ".gitignore excludes token files"
    else
        warn ".gitignore does not exclude token files"
    fi
else
    critical ".gitignore does not exist"
fi

# Check for secrets in git history
info "Checking for secrets in git history..."
if git ls-files | grep -qE "(\.env|\.token|credentials|sessions)"; then
    critical "Sensitive files are tracked in git!"
    git ls-files | grep -E "(\.env|\.token|credentials|sessions)" || true
else
    pass "No sensitive files tracked in git"
fi

# Check for pre-commit hook
if [ -f ".git/hooks/pre-commit" ]; then
    pass "Pre-commit hook exists"
    if grep -q "secret" .git/hooks/pre-commit 2>/dev/null; then
        pass "Pre-commit hook includes secret scanning"
    else
        warn "Pre-commit hook does not scan for secrets"
    fi
else
    warn "No pre-commit hook found"
    info "Consider adding secret scanning to .git/hooks/pre-commit"
fi

echo ""
echo "=== Directory Structure ==="
echo ""

# Check vault structure
VAULT_DIR="AI_Employee_Vault"
if [ -d "$VAULT_DIR" ]; then
    pass "Vault directory exists"
    
    # Check for domain separation
    if [ -d "$VAULT_DIR/Needs_Action/cloud" ] && [ -d "$VAULT_DIR/Needs_Action/local" ]; then
        pass "Cloud/Local domain separation implemented"
    else
        warn "Cloud/Local domain separation not fully implemented"
    fi
    
    # Check Updates directory for drafts
    if [ -d "$VAULT_DIR/Updates" ]; then
        pass "Updates directory exists (for cloud drafts)"
    else
        warn "Updates directory does not exist"
    fi
else
    critical "Vault directory does not exist"
fi

echo ""
echo "=== Configuration Files ==="
echo ""

# Check docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"
    
    # Check for hardcoded passwords
    if grep -qE "PASSWORD:.*ChangeMe" docker-compose.yml; then
        warn "docker-compose.yml contains default passwords"
        info "  Change default passwords before deployment"
    else
        pass "No default passwords detected in docker-compose.yml"
    fi
else
    info "docker-compose.yml not found (may not be needed)"
fi

# Check for syncthing config
if [ -f "syncthing-config.xml" ]; then
    pass "Syncthing configuration exists"
    
    # Check for default API key
    if grep -q "CHANGE-THIS-TO-SECURE-RANDOM-STRING" syncthing-config.xml; then
        warn "Syncthing config contains default API key"
        info "  Change the API key before deployment"
    else
        pass "Syncthing API key appears customized"
    fi
else
    info "Syncthing configuration not found (may use Git sync)"
fi

echo ""
echo "=== Documentation ==="
echo ""

# Check security documentation
if [ -f "docs/security.md" ]; then
    pass "Security documentation exists"
else
    warn "Security documentation not found"
fi

if [ -f "docs/cloud_deployment.md" ]; then
    pass "Cloud deployment documentation exists"
else
    warn "Cloud deployment documentation not found"
fi

if [ -f "docs/vault_sync.md" ]; then
    pass "Vault sync documentation exists"
else
    warn "Vault sync documentation not found"
fi

echo ""
echo "======================================"
echo "Audit Summary"
echo "======================================"
echo ""
echo "Critical Issues: $AUDIT_CRITICAL"
echo "Warnings: $AUDIT_WARNINGS"
echo ""

if [ "$AUDIT_PASSED" = true ]; then
    echo -e "${GREEN}✓ SECURITY AUDIT PASSED${NC}"
    echo ""
    echo "Your system appears to be securely configured."
    echo "Remember to:"
    echo "- Run this audit regularly"
    echo "- Keep dependencies updated"
    echo "- Review access logs"
    echo "- Rotate credentials periodically"
    exit 0
else
    echo -e "${RED}❌ SECURITY AUDIT FAILED${NC}"
    echo ""
    echo "ACTION REQUIRED:"
    echo "1. Address all critical issues above"
    echo "2. Review and fix warnings"
    echo "3. Re-run audit after fixes"
    exit 1
fi
