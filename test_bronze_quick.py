#!/usr/bin/env python3
"""Quick Bronze Tier test"""

import time
from pathlib import Path

# Start watcher
from src.watchers.filesystem_watcher import FileSystemWatcher

vault = Path('./AI_Employee_Vault')
drop = vault / 'Drop'
drop.mkdir(exist_ok=True)

print("Starting watcher...")
watcher = FileSystemWatcher(str(vault), str(drop))
watcher.start()

print("Waiting 2 seconds for watcher to initialize...")
time.sleep(2)

print("Creating test file...")
test_file = drop / f"test_{int(time.time())}.txt"
test_file.write_text("Bronze Tier Test File")
print(f"Created: {test_file}")

print("Waiting 5 seconds for processing...")
time.sleep(5)

print("\n=== Needs_Action contents ===")
needs_action = vault / 'Needs_Action'
for f in needs_action.iterdir():
    if f.is_file() and not f.name.startswith('.'):
        print(f"  ✓ {f.name}")

print("\n=== Stopping watcher ===")
watcher.stop()
print("Done!")
