#!/bin/bash
# SpeckitPlus Setup Script for AI Employee System
# This script sets up the project structure and validates the environment

set -e

echo "=== AI Employee System - SpeckitPlus Setup ==="

# Check UV is installed
if ! command -v uv &> /dev/null; then
    echo "Error: UV is not installed. Please install UV first."
    exit 1
fi
echo "✓ UV found"

# Check Python version
PYTHON_VERSION=$(uv run python --version 2>&1)
echo "✓ Python: $PYTHON_VERSION"

# Sync dependencies
echo "Syncing dependencies..."
uv sync
echo "✓ Dependencies synced"

# Create required directories
DIRS=("Inbox" "Needs_Action" "Plans" "Pending_Approval" "Approved" "Rejected" "Done" "Logs")
for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
done
echo "✓ Directories created"

# Validate structure
echo ""
echo "=== Project Structure ==="
echo ".specify/     - SpeckitPlus configuration"
echo "skills/       - Agent Skills (Claude prompts)"
echo "src/          - Python source code"
echo "  - orchestrator/"
echo "  - watchers/"
echo "  - skills/"
echo "  - utils/"
echo ""

# Run validation
echo "=== Running Validation ==="
uv run python -c "
from src.orchestrator.main import Orchestrator
from src.skills import list_skills
from src.watchers import FileSystemWatcher

skills = list_skills()
print(f'✓ Skills loaded: {len(skills)}')
print(f'✓ All imports successful')
"

echo ""
echo "=== Setup Complete ==="
echo "Run 'python main.py' to start the orchestrator"
