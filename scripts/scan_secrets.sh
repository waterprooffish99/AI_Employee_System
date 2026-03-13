#!/bin/bash
# Secret Scanning Script for AI Employee System
# Scans for accidentally committed secrets before push

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "======================================"
echo "AI Employee Secret Scanner"
echo "======================================"
echo ""

# Directories to scan
SCAN_DIRS=(
    "AI_Employee_Vault"
    "src"
    "specs"
    "docs"
    "scripts"
)

# Patterns that indicate secrets
SECRET_PATTERNS=(
    # AWS Access Key
    "AKIA[0-9A-Z]{16}"
    # AWS Secret Key
    "[A-Za-z0-9/+=]{40}"
    # GitHub Personal Access Token
    "ghp_[a-zA-Z0-9]{36}"
    # GitHub OAuth Access Token
    "gho_[a-zA-Z0-9]{36}"
    # GitHub App Installation Token
    "ghu_[a-zA-Z0-9]{36}"
    # GitHub Refresh Token
    "ghr_[a-zA-Z0-9]{36}"
    # Slack Token
    "xox[baprs]-[0-9a-zA-Z]{10,48}"
    # Slack Webhook
    "https://hooks.slack.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}"
    # Google API Key
    "AIza[0-9A-Za-z\\-_]{35}"
    # Google OAuth
    "[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com"
    # Generic API Key
    "api[_-]?key[_-]?[=:]"
    # Generic Secret
    "secret[_-]?[=:]"
    # Password patterns
    "password[_-]?[=:]"
    # Private Key Header
    "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
    # Base64 encoded secrets (common length)
    "[A-Za-z0-9+/]{50,}={0,2}"
    # Odoo API Key pattern
    "odoo[_-]?api[_-]?key"
    # Database connection strings
    "mongodb(\\+srv)?://[^\\s]+:[^\\s]+@"
    "postgres(ql)?://[^\\s]+:[^\\s]+@"
    "mysql://[^\\s]+:[^\\s]+@"
)

# Files to always skip
SKIP_FILES=(
    ".gitignore"
    ".syncthingignore"
    "*.md"
    "*.txt"
    "*.xml"
    "*.json"
    "scan_secrets.sh"
    "security.md"
)

FOUND_SECRETS=false
SCANNED_FILES=0
SCANNED_LINES=0

# Function to check if file should be skipped
should_skip() {
    local file="$1"
    local basename=$(basename "$file")
    
    for pattern in "${SKIP_FILES[@]}"; do
        if [[ "$basename" == $pattern ]]; then
            return 0
        fi
    done
    
    # Skip binary files
    if file "$file" | grep -q "binary"; then
        return 0
    fi
    
    return 1
}

# Function to scan a file
scan_file() {
    local file="$1"
    
    if should_skip "$file"; then
        return
    fi
    
    ((SCANNED_FILES++)) || true
    
    local line_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        ((SCANNED_LINES++)) || true
        
        for pattern in "${SECRET_PATTERNS[@]}"; do
            if echo "$line" | grep -qiE "$pattern" 2>/dev/null; then
                echo -e "${RED}⚠ POTENTIAL SECRET DETECTED${NC}"
                echo "  File: $file"
                echo "  Line: $line_num"
                echo "  Pattern: $pattern"
                echo "  Content: ${line:0:100}..."
                echo ""
                FOUND_SECRETS=true
            fi
        done
    done < "$file"
}

# Scan directories
echo "Scanning directories..."
echo ""

for dir in "${SCAN_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Scanning: $dir"
        while IFS= read -r -d '' file; do
            scan_file "$file"
        done < <(find "$dir" -type f -print0 2>/dev/null)
    fi
done

# Check for .env files that shouldn't exist
echo ""
echo "Checking for exposed .env files..."

ENV_FILES=$(find . -name ".env*" -not -path "./.git/*" 2>/dev/null || true)
if [ -n "$ENV_FILES" ]; then
    echo -e "${YELLOW}⚠ Found .env files:${NC}"
    echo "$ENV_FILES"
    echo ""
    echo "These should be in .gitignore. Verify they are not tracked:"
    echo "  git ls-files | grep '.env'"
    echo ""
fi

# Check git tracking for sensitive files
echo ""
echo "Checking git tracking for sensitive patterns..."

GIT_TRACKED=$(git ls-files 2>/dev/null | grep -E "(\.env|\.token|\.key|\.pem|credentials|sessions)" || true)
if [ -n "$GIT_TRACKED" ]; then
    echo -e "${RED}❌ CRITICAL: Sensitive files are tracked in git!${NC}"
    echo "$GIT_TRACKED"
    echo ""
    echo "Remove immediately with:"
    echo "  git rm --cached <file>"
    echo "  git commit -m 'Remove sensitive files'"
    echo ""
    FOUND_SECRETS=true
fi

# Summary
echo ""
echo "======================================"
echo "Scan Summary"
echo "======================================"
echo "Files scanned: $SCANNED_FILES"
echo "Lines scanned: $SCANNED_LINES"
echo ""

if [ "$FOUND_SECRETS" = true ]; then
    echo -e "${RED}❌ POTENTIAL SECRETS DETECTED${NC}"
    echo ""
    echo "ACTION REQUIRED:"
    echo "1. Review the findings above"
    echo "2. Remove secrets from files"
    echo "3. If committed, rotate the credentials"
    echo "4. Remove from git history if necessary"
    echo ""
    echo "To remove from git history:"
    echo "  git filter-branch --force --index-filter \\"
    echo "    'git rm --cached --ignore-unmatch <file>' \\"
    echo "    --prune-empty --tag-name-filter cat -- --all"
    echo ""
    exit 1
else
    echo -e "${GREEN}✓ NO SECRETS DETECTED${NC}"
    echo ""
    echo "Your code appears clean, but always:"
    echo "- Review before committing"
    echo "- Use pre-commit hooks"
    echo "- Rotate credentials regularly"
    echo ""
    exit 0
fi
