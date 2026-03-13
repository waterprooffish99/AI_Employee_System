#!/bin/bash
# Validation Script for AI Employee System
# Validates the project structure against Hackathon-0 Silver Tier requirements

set -e

echo "=== AI Employee System - Silver Tier Validation ==="
echo ""

ERRORS=0
WARNINGS=0
TIER="Bronze"

# Check required project files
echo "Checking Project Files..."
REQUIRED_FILES=("README.md" "main.py" "pyproject.toml" ".env" "Hackathon-0.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        ((ERRORS++))
    fi
done

# Check required vault files
echo ""
echo "Checking Vault Files (AI_Employee_Vault/)..."
VAULT_FILES=("Dashboard.md" "Company_Handbook.md" "Business_Goals.md")
for file in "${VAULT_FILES[@]}"; do
    if [ -f "AI_Employee_Vault/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ AI_Employee_Vault/$file (MISSING)"
        ((ERRORS++))
    fi
done

# Check required vault directories
echo ""
echo "Checking Vault Directories..."
VAULT_DIRS=("Inbox" "Needs_Action" "Plans" "Pending_Approval" "Approved" "Rejected" "Done" "Logs" "Error")
for dir in "${VAULT_DIRS[@]}"; do
    if [ -d "AI_Employee_Vault/$dir" ]; then
        echo "  ✓ AI_Employee_Vault/$dir/"
    else
        echo "  ✗ AI_Employee_Vault/$dir/ (MISSING)"
        ((ERRORS++))
    fi
done

# Check SpeckitPlus structure
echo ""
echo "Checking SpeckitPlus structure..."
if [ -d ".specify" ]; then
    echo "  ✓ .specify/"
    if [ -d ".specify/memory" ]; then
        echo "  ✓ .specify/memory/"
    else
        echo "  ⚠ .specify/memory/ (MISSING)"
        ((WARNINGS++))
    fi
    if [ -d ".specify/templates" ]; then
        echo "  ✓ .specify/templates/"
    else
        echo "  ⚠ .specify/templates/ (MISSING)"
        ((WARNINGS++))
    fi
    if [ -d ".specify/scripts" ]; then
        echo "  ✓ .specify/scripts/"
    else
        echo "  ⚠ .specify/scripts/ (MISSING)"
        ((WARNINGS++))
    fi
else
    echo "  ✗ .specify/ (MISSING)"
    ((ERRORS++))
fi

# Check History structure
echo ""
echo "Checking History structure..."
if [ -d "history" ]; then
    echo "  ✓ history/"
    if [ -d "history/prompts" ]; then
        echo "  ✓ history/prompts/"
    else
        echo "  ✗ history/prompts/ (MISSING)"
        ((ERRORS++))
    fi
    if [ -d "history/templates" ]; then
        echo "  ✓ history/templates/"
    else
        echo "  ✗ history/templates/ (MISSING)"
        ((ERRORS++))
    fi
    PHR_COUNT=$(ls -1 history/prompts/*.md 2>/dev/null | wc -l)
    echo "  ✓ $PHR_COUNT PHR(s) recorded"
else
    echo "  ✗ history/ (MISSING)"
    ((ERRORS++))
fi

# Check Agent Skills
echo ""
echo "Checking Agent Skills..."
SKILLS_COUNT=$(ls -1 skills/*.md 2>/dev/null | wc -l)
if [ "$SKILLS_COUNT" -gt 0 ]; then
    echo "  ✓ $SKILLS_COUNT skill(s) found"
    ls -1 skills/*.md | while read skill; do
        echo "    - $(basename $skill)"
    done
else
    echo "  ✗ No skills found"
    ((ERRORS++))
fi

# Check Python structure
echo ""
echo "Checking Python structure..."
PYTHON_FILES=("src/__init__.py" "src/orchestrator/__init__.py" "src/watchers/__init__.py" "src/skills/__init__.py" "src/utils/__init__.py")
for file in "${PYTHON_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        ((ERRORS++))
    fi
done

# Check UV setup
echo ""
echo "Checking UV setup..."
if [ -f "pyproject.toml" ]; then
    echo "  ✓ pyproject.toml"
else
    echo "  ✗ pyproject.toml (MISSING)"
    ((ERRORS++))
fi

if [ -f "uv.lock" ]; then
    echo "  ✓ uv.lock"
else
    echo "  ⚠ uv.lock (MISSING - run 'uv sync')"
    ((WARNINGS++))
fi

# Check .env
echo ""
echo "Checking environment..."
if [ -f ".env" ]; then
    echo "  ✓ .env"
    if grep -q "DRY_RUN=true" .env; then
        echo "  ✓ DRY_RUN enabled (safe for development)"
    else
        echo "  ⚠ DRY_RUN not enabled (consider enabling for safety)"
        ((WARNINGS++))
    fi
    # Check for vault path configuration (either override or default)
    if grep -q "VAULT_PATH" .env || grep -q "AI_Employee_Vault" .env; then
        echo "  ✓ Vault path configured"
    else
        echo "  ℹ Using default vault path (AI_Employee_Vault/)"
    fi
else
    echo "  ✗ .env (MISSING)"
    ((ERRORS++))
fi

# Run Python validation
echo ""
echo "Running Python import validation..."
uv run python -c "
from src.orchestrator.main import Orchestrator
from src.skills import list_skills
from src.watchers import FileSystemWatcher, BaseWatcher
from src.utils import log_event, update_dashboard
from src.mcp.linkedin_poster import LinkedInPoster

# Import Silver Tier watchers directly
from src.watchers.gmail_watcher import GmailWatcher
from src.watchers.whatsapp_watcher import WhatsAppWatcher

skills = list_skills()
assert len(skills) >= 7, 'Need at least 7 skills for Silver Tier'
print(f'  ✓ All imports successful')
print(f'  ✓ {len(skills)} skills available (Silver Tier: 7+)')
print(f'  ✓ GmailWatcher available')
print(f'  ✓ WhatsAppWatcher available')
print(f'  ✓ LinkedInPoster available')
" || { echo "  ✗ Python validation failed"; ((ERRORS++)); }

# Silver Tier specific checks
echo ""
echo "=== Silver Tier Requirements ==="

# Check for watchers
echo "Checking Watchers..."
WATCHER_FILES=("src/watchers/gmail_watcher.py" "src/watchers/whatsapp_watcher.py" "src/watchers/filesystem_watcher.py")
for file in "${WATCHER_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        ((ERRORS++))
    fi
done

# Check for MCP servers
echo ""
echo "Checking MCP Servers..."
MCP_FILES=("src/mcp/email_mcp.py" "src/mcp/linkedin_poster.py")
for file in "${MCP_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        ((ERRORS++))
    fi
done

# Check for scheduling scripts
echo ""
echo "Checking Scheduling..."
SCHED_FILES=(".specify/scripts/bash/setup_cron.sh" ".specify/scripts/bash/start_watchers.sh")
for file in "${SCHED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        ((ERRORS++))
    fi
done

# Check for Silver Tier skills
echo ""
echo "Checking Silver Tier Skills..."
SILVER_SKILLS=("skills/06_create_plan.md" "skills/07_execute_approved_hitl.md")
for file in "${SILVER_SKILLS[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        ((ERRORS++))
    fi
done

# Summary
echo ""
echo "=== Validation Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✓ Validation PASSED - Silver Tier Complete! 🥈"
    exit 0
else
    echo "✗ Validation FAILED - Fix errors above"
    exit 1
fi
