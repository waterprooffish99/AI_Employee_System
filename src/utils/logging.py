"""
Logging utility - Simple logging for the AI Employee System.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Vault Path Configuration
# The Obsidian Vault is located in AI_Employee_Vault/ within the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / 'AI_Employee_Vault'

# Optional: Override with environment variable
if os.getenv('VAULT_PATH_OVERRIDE'):
    VAULT_PATH = Path(os.getenv('VAULT_PATH_OVERRIDE'))

LOG_DIR = VAULT_PATH / "Logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event_type: str, data: dict, actor: str = "system"):
    """
    Logs a structured event to a daily log file.
    
    Args:
        event_type: Type of event (e.g., 'orchestrator.started')
        data: Dictionary of event data
        actor: Who/what triggered the event
    """
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "actor": actor,
        "data": data
    }

    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return str(log_file)


if __name__ == "__main__":
    # Test logging
    log_file = log_event("test.event", {"message": "This is a test event."})
    print(f"Test log event created in {log_file}")
