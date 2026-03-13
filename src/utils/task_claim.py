"""
Task Claiming Utility for AI Employee System - Platinum Tier

Implements claim-by-move rule to prevent double-processing.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class TaskClaimer:
    """
    Task claiming utility.
    
    Features:
    - Claim tasks by moving to agent folder
    - Check if task is already claimed
    - Release tasks back to shared pool
    - Track task ownership
    """
    
    def __init__(self, vault_path: str | Path):
        """
        Initialize task claimer.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.in_progress_dir = self.vault_path / "In_Progress"
        self.done_dir = self.vault_path / "Done"
        
        # Ensure directories exist
        self.in_progress_dir.mkdir(parents=True, exist_ok=True)
    
    def claim_task(
        self,
        task_file: Path,
        agent: str,
    ) -> tuple[bool, str]:
        """
        Claim a task by moving to In_Progress/<agent>/.
        
        Args:
            task_file: Task file path
            agent: Agent name (cloud, local)
            
        Returns:
            Tuple of (success, message)
        """
        if not task_file.exists():
            return False, f"Task file not found: {task_file}"
        
        # Check if already claimed
        if str(task_file).startswith(str(self.in_progress_dir)):
            return True, f"Task already claimed: {task_file}"
        
        # Check if in Needs_Action
        if not str(task_file).startswith(str(self.needs_action_dir)):
            return False, f"Task not in Needs_Action: {task_file}"
        
        # Move to In_Progress/<agent>/
        target_dir = self.in_progress_dir / agent
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / task_file.name
        
        try:
            # Add claim metadata
            content = task_file.read_text()
            claim_metadata = f"""---
claimed_by: {agent}
claimed_at: {datetime.now().isoformat()}
---

"""
            content = claim_metadata + content
            target.write_text(content)
            
            # Move file
            task_file.unlink()
            
            logger.info(f"Task claimed: {task_file} -> {target} (agent: {agent})")
            return True, f"Task claimed: {target}"
            
        except Exception as e:
            logger.error(f"Failed to claim task: {e}")
            return False, f"Failed to claim task: {e}"
    
    def release_task(
        self,
        task_file: Path,
        reason: str = "",
    ) -> tuple[bool, str]:
        """
        Release a task back to Needs_Action/shared.
        
        Args:
            task_file: Task file path
            reason: Reason for release
            
        Returns:
            Tuple of (success, message)
        """
        if not task_file.exists():
            return False, f"Task file not found: {task_file}"
        
        # Move to Needs_Action/shared
        target_dir = self.needs_action_dir / "shared"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / task_file.name
        
        try:
            # Add release metadata
            content = task_file.read_text()
            release_metadata = f"""---
released_at: {datetime.now().isoformat()}
release_reason: {reason}
---

"""
            content = release_metadata + content
            target.write_text(content)
            
            # Move file
            task_file.unlink()
            
            logger.info(f"Task released: {task_file} -> {target} (reason: {reason})")
            return True, f"Task released: {target}"
            
        except Exception as e:
            logger.error(f"Failed to release task: {e}")
            return False, f"Failed to release task: {e}"
    
    def is_claimed(self, task_file: Path) -> tuple[bool, Optional[str]]:
        """
        Check if task is already claimed.
        
        Args:
            task_file: Task file path
            
        Returns:
            Tuple of (is_claimed, claiming_agent)
        """
        if not task_file.exists():
            return False, None
        
        # Check if in In_Progress
        if str(task_file).startswith(str(self.in_progress_dir)):
            # Extract agent from path
            parts = task_file.relative_to(self.in_progress_dir).parts
            if len(parts) > 1:
                return True, parts[0]
            return True, "unknown"
        
        # Check metadata
        try:
            content = task_file.read_text()
            if "claimed_by:" in content:
                # Parse claimed_by from frontmatter
                for line in content.split("\n"):
                    if line.startswith("claimed_by:"):
                        agent = line.split(":")[1].strip()
                        return True, agent
        except Exception:
            pass
        
        return False, None
    
    def get_unclaimed_tasks(self) -> list[Path]:
        """
        Get all unclaimed tasks.
        
        Returns:
            List of unclaimed task file paths
        """
        unclaimed = []
        
        # Check Needs_Action/shared
        shared_dir = self.needs_action_dir / "shared"
        if shared_dir.exists():
            for task_file in shared_dir.glob("*.md"):
                is_claimed, _ = self.is_claimed(task_file)
                if not is_claimed:
                    unclaimed.append(task_file)
        
        # Check Needs_Action root
        for task_file in self.needs_action_dir.glob("*.md"):
            is_claimed, _ = self.is_claimed(task_file)
            if not is_claimed:
                unclaimed.append(task_file)
        
        return unclaimed
    
    def get_claimed_tasks(self, agent: str) -> list[Path]:
        """
        Get all tasks claimed by specific agent.
        
        Args:
            agent: Agent name
            
        Returns:
            List of claimed task file paths
        """
        claimed = []
        
        agent_dir = self.in_progress_dir / agent
        if agent_dir.exists():
            for task_file in agent_dir.glob("*.md"):
                claimed.append(task_file)
        
        return claimed
    
    def complete_task(self, task_file: Path) -> tuple[bool, str]:
        """
        Mark task as complete by moving to Done.
        
        Args:
            task_file: Task file path
            
        Returns:
            Tuple of (success, message)
        """
        if not task_file.exists():
            return False, f"Task file not found: {task_file}"
        
        # Add completion metadata
        content = task_file.read_text()
        completion_metadata = f"""---
completed_at: {datetime.now().isoformat()}
status: complete
---

"""
        content = completion_metadata + content
        
        target = self.done_dir / task_file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        
        task_file.unlink()
        
        logger.info(f"Task completed: {task_file} -> {target}")
        return True, f"Task completed: {target}"


# Singleton instance
_task_claimer: Optional[TaskClaimer] = None


def get_task_claimer(vault_path: str | Path) -> TaskClaimer:
    """Get or create task claimer instance."""
    global _task_claimer
    if _task_claimer is None:
        _task_claimer = TaskClaimer(vault_path)
    return _task_claimer
