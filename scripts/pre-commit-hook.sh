"""
Pre-commit Hook for Secret Scanning
Install this as .git/hooks/pre-commit to scan for secrets before each commit.
"""

#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Running pre-commit secret scan..."

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

FOUND_SECRETS=false

# Patterns to check
PATTERNS=(
    "AKIA[0-9A-Z]{16}"                    # AWS Access Key
    "ghp_[a-zA-Z0-9]{36}"                 # GitHub Personal Access Token
    "xox[baprs]-[0-9a-zA-Z]{10}"          # Slack Token
    "AIza[0-9A-Za-z\\-_]{35}"             # Google API Key
    "-----BEGIN (RSA |EC |DSA )?PRIVATE"  # Private Key
    "password\\s*=\\s*['\"][^'\"]+['\"]"  # Password assignment
    "api_key\\s*=\\s*['\"][^'\"]+['\"]"   # API key assignment
    "secret\\s*=\\s*['\"][^'\"]+['\"]"    # Secret assignment
)

for file in $STAGED_FILES; do
    # Skip certain files
    if [[ "$file" == *".gitignore"* ]] || \
       [[ "$file" == *"scan_secrets.sh"* ]] || \
       [[ "$file" == *"security.md"* ]]; then
        continue
    fi
    
    # Get staged content
    content=$(git show ":$file" 2>/dev/null || true)
    
    if [ -z "$content" ]; then
        continue
    fi
    
    # Check for secrets
    for pattern in "${PATTERNS[@]}"; do
        if echo "$content" | grep -qiE "$pattern" 2>/dev/null; then
            echo -e "${RED}⚠ POTENTIAL SECRET in: $file${NC}"
            echo "  Pattern: $pattern"
            FOUND_SECRETS=true
        fi
    done
done

if [ "$FOUND_SECRETS" = true ]; then
    echo ""
    echo -e "${RED}❌ Pre-commit hook blocked commit: Potential secrets detected${NC}"
    echo ""
    echo "Review the files above and remove any secrets."
    echo "If this is a false positive, you can bypass with:"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ No secrets detected${NC}"
exit 0
