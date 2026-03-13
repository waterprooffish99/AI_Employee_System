"""
Skills module - Helper functions that Claude Code can use.

Note: According to Hackathon-0 spec, Claude Code does the reasoning.
These are utility functions that can be called by Claude Code via MCP or directly.
"""

import os
from pathlib import Path
from datetime import datetime
import json

# Vault Path Configuration
# The Obsidian Vault is located in AI_Employee_Vault/ within the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / 'AI_Employee_Vault'

# Optional: Override with environment variable
if os.getenv('VAULT_PATH_OVERRIDE'):
    VAULT_PATH = Path(os.getenv('VAULT_PATH_OVERRIDE'))


def read_skill(skill_name: str) -> str:
    """Read a skill definition file."""
    skill_file = PROJECT_ROOT / "skills" / f"{skill_name}.md"
    if skill_file.exists():
        return skill_file.read_text()
    return f"Skill not found: {skill_name}"


def list_skills() -> list:
    """List all available skills."""
    skills_dir = PROJECT_ROOT / "skills"
    if skills_dir.exists():
        return [f.stem for f in skills_dir.glob("*.md")]
    return []


def get_pending_tasks() -> list:
    """Get list of pending tasks from Needs_Action."""
    needs_action = VAULT_PATH / "Needs_Action"
    if needs_action.exists():
        return [f.name for f in needs_action.glob("*.md")]
    return []


def get_pending_approvals() -> list:
    """Get list of pending approvals."""
    pending = VAULT_PATH / "Pending_Approval"
    if pending.exists():
        return [f.name for f in pending.glob("*.md")]
    return []


def get_approved_actions() -> list:
    """Get list of approved actions ready for execution."""
    approved = VAULT_PATH / "Approved"
    if approved.exists():
        return [f.name for f in approved.glob("*.md")]
    return []


def read_file(filepath: str) -> str:
    """Read a file from the vault."""
    path = Path(filepath)
    if not path.is_absolute():
        path = VAULT_PATH / filepath
    if path.exists():
        return path.read_text()
    return f"File not found: {filepath}"


def write_file(filepath: str, content: str) -> bool:
    """Write content to a file in the vault."""
    try:
        path = Path(filepath)
        if not path.is_absolute():
            path = VAULT_PATH / filepath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def move_file(source: str, destination: str) -> bool:
    """Move a file from source to destination."""
    try:
        src = Path(source)
        dst = Path(destination)
        if not src.is_absolute():
            src = VAULT_PATH / src
        if not dst.is_absolute():
            dst = VAULT_PATH / dst
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        return True
    except Exception as e:
        print(f"Error moving file: {e}")
        return False


def log_event(event_type: str, data: dict, actor: str = "claude_code") -> str:
    """Log an event to the daily log file."""
    logs_dir = VAULT_PATH / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "actor": actor,
        "data": data,
        "result": "success"
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return str(log_file)


def get_company_handbook() -> str:
    """Read the Company Handbook."""
    handbook = VAULT_PATH / "Company_Handbook.md"
    if handbook.exists():
        return handbook.read_text()
    return "Company Handbook not found."


def get_business_goals() -> str:
    """Read the Business Goals."""
    goals = VAULT_PATH / "Business_Goals.md"
    if goals.exists():
        return goals.read_text()
    return "Business Goals not found."


def get_dashboard() -> str:
    """Read the current Dashboard."""
    dashboard = VAULT_PATH / "Dashboard.md"
    if dashboard.exists():
        return dashboard.read_text()
    return "Dashboard not found."
