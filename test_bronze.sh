#!/bin/bash
# Bronze Tier Test Script

cd "/mnt/c/Users/WaterProof Fish/Documents/AI_Employee_System"

echo "=== BRONZE TIER TEST ==="
echo ""

# Step 1: Create Drop folder if missing
mkdir -p AI_Employee_Vault/Drop

# Step 2: Start watcher in background
echo "Starting Filesystem Watcher..."
uv run python -m src.watchers.filesystem_watcher --vault ./AI_Employee_Vault > /tmp/watcher.log 2>&1 &
WATCHER_PID=$!
echo "Watcher started with PID: $WATCHER_PID"

# Step 3: Wait for watcher to initialize
sleep 3

# Step 4: Create test file
echo "Creating test file..."
echo "Test file for Bronze Tier" > AI_Employee_Vault/Drop/test_bronze.txt

# Step 5: Wait for processing
sleep 5

# Step 6: Check results
echo ""
echo "=== Needs_Action contents ==="
ls -la AI_Employee_Vault/Needs_Action/

echo ""
echo "=== Watcher log ==="
tail -20 /tmp/watcher.log

# Step 7: Stop watcher
echo ""
echo "Stopping watcher..."
kill $WATCHER_PID

echo ""
echo "=== TEST COMPLETE ==="
