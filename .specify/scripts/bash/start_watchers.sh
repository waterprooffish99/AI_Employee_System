#!/bin/bash
# AI Employee System - Run All Watchers
# Silver Tier: Start all watchers for continuous monitoring

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== AI Employee System - Starting Watchers ==="
echo ""
echo "Project Root: $PROJECT_ROOT"
echo ""

# Function to start a watcher in background
start_watcher() {
    local name=$1
    local module=$2
    
    echo "Starting $name..."
    uv run python -m $module &
    PID=$!
    echo "  ✓ $name started (PID: $PID)"
    echo $PID > ".specify/scripts/pids/${name}.pid"
}

# Create pids directory
mkdir -p .specify/scripts/pids

# Start watchers
start_watcher "filesystem_watcher" "src.watchers.filesystem_watcher"
sleep 1

start_watcher "gmail_watcher" "src.watchers.gmail_watcher"
sleep 1

start_watcher "whatsapp_watcher" "src.watchers.whatsapp_watcher"
sleep 1

# Start orchestrator
start_watcher "orchestrator" "src.orchestrator.main"
sleep 1

echo ""
echo "=== All Watchers Started ==="
echo ""
echo "Running processes:"
ps aux | grep -E "(watcher|orchestrator)" | grep -v grep
echo ""
echo "To stop all watchers:"
echo "  bash .specify/scripts/bash/stop_watchers.sh"
echo ""
echo "Logs: AI_Employee_Vault/Logs/"
