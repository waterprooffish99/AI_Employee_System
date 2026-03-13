#!/bin/bash
# AI Employee System - Stop All Watchers

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== AI Employee System - Stopping Watchers ==="
echo ""

# Stop watchers by PID
for pid_file in .specify/scripts/pids/*.pid; do
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        name=$(basename "$pid_file" .pid)
        
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $name (PID: $pid)..."
            kill "$pid"
            echo "  ✓ Stopped"
        else
            echo "  ⚠ $name not running"
        fi
        
        rm "$pid_file"
    fi
done

# Also kill by process name
echo ""
echo "Killing any remaining watcher processes..."
pkill -f "src.watchers" 2>/dev/null || true
pkill -f "src.orchestrator" 2>/dev/null || true

echo ""
echo "=== All Watchers Stopped ==="
