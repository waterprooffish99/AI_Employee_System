"""
Ralph Loop Helper for AI Employee System - Gold Tier

Utilities for Ralph Wiggum loop management including state persistence,
iteration counting, and completion detection.
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class RalphLoopManager:
    """
    Manager for Ralph Wiggum loop operations.
    
    Features:
    - State file management
    - Iteration tracking
    - Completion detection
    - File movement detection
    - Timeout handling
    """
    
    def __init__(
        self,
        vault_path: str | Path,
        task_id: str,
        max_iterations: int = 10,
        timeout_seconds: int = 3600,
    ):
        """
        Initialize Ralph loop manager.
        
        Args:
            vault_path: Path to Obsidian vault
            task_id: Task identifier
            max_iterations: Maximum loop iterations
            timeout_seconds: Loop timeout in seconds
        """
        self.vault_path = Path(vault_path)
        self.task_id = task_id
        self.max_iterations = int(os.getenv("RALPH_MAX_ITERATIONS", max_iterations))
        self.timeout_seconds = int(
            os.getenv("RALPH_TIMEOUT_SECONDS", timeout_seconds)
        )
        
        # Directories
        self.plans_dir = self.vault_path / "Plans"
        self.done_dir = self.vault_path / "Done"
        self.needs_action_dir = self.vault_path / "Needs_Action"
        
        # Files
        self.state_file = self.plans_dir / f"{task_id}_state.json"
        self.output_file = self.plans_dir / f"{task_id}_last_output.txt"
        self.task_file = self.needs_action_dir / f"{task_id}.md"
        self.done_file = self.done_dir / f"{task_id}.md"
        
        # Ensure directories exist
        self.plans_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_state(self, prompt: str, metadata: dict | None = None) -> dict:
        """
        Initialize task state.
        
        Args:
            prompt: Original task prompt
            metadata: Additional metadata
            
        Returns:
            State dictionary
        """
        state = {
            "task_id": self.task_id,
            "prompt": prompt,
            "iteration": 0,
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "iterations": [],
            "status": "in_progress",
            "metadata": metadata or {},
        }
        
        self._save_state(state)
        return state
    
    def _save_state(self, state: dict) -> Path:
        """
        Save state to file.
        
        Args:
            state: State dictionary
            
        Returns:
            Path to state file
        """
        self.state_file.write_text(json.dumps(state, indent=2))
        return self.state_file
    
    def _load_state(self) -> dict | None:
        """
        Load state from file.
        
        Returns:
            State dictionary or None if not found
        """
        if not self.state_file.exists():
            return None
        
        try:
            return json.loads(self.state_file.read_text())
        except (json.JSONDecodeError, IOError):
            return None
    
    def update_state(
        self,
        output: str,
        metadata: dict | None = None,
    ) -> dict:
        """
        Update state with iteration output.
        
        Args:
            output: Claude's output
            metadata: Additional metadata
            
        Returns:
            Updated state dictionary
        """
        state = self._load_state()
        if state is None:
            state = self.initialize_state("")
        
        # Increment iteration
        state["iteration"] = state.get("iteration", 0) + 1
        
        # Record iteration
        iteration_record = {
            "number": state["iteration"],
            "timestamp": datetime.now().isoformat(),
            "output_length": len(output),
            "metadata": metadata or {},
        }
        
        if "iterations" not in state:
            state["iterations"] = []
        state["iterations"].append(iteration_record)
        
        # Update timestamps
        state["last_updated"] = datetime.now().isoformat()
        
        # Save output
        self.output_file.write_text(output)
        
        # Save state
        self._save_state(state)
        return state
    
    def check_completion(self, output: str | None = None) -> tuple[bool, str]:
        """
        Check if task is complete.
        
        Args:
            output: Optional output to check for completion promise
            
        Returns:
            Tuple of (is_complete, reason)
        """
        # Check if task file moved to Done
        if self.done_file.exists():
            return True, "Task file moved to Done folder"
        
        # Check max iterations
        state = self._load_state()
        if state:
            iteration = state.get("iteration", 0)
            if iteration >= self.max_iterations:
                return True, f"Max iterations ({self.max_iterations}) reached"
            
            # Check timeout
            start_time = state.get("start_time")
            if start_time:
                start = datetime.fromisoformat(start_time)
                elapsed = (datetime.now() - start).total_seconds()
                if elapsed > self.timeout_seconds:
                    return True, f"Timeout ({self.timeout_seconds}s) reached"
        
        # Check output for completion promise
        if output:
            if self._contains_completion_promise(output):
                return True, "Completion promise detected"
        
        return False, "Task still in progress"
    
    def _contains_completion_promise(self, content: str) -> bool:
        """
        Check if content contains completion promise.

        Args:
            content: Output content

        Returns:
            True if completion promise found
        """
        # XML-style promises (including the Gold Tier standard: <promise>COMPLETED</promise>)
        xml_patterns = [
            r"<promise>COMPLETED</promise>",
            r"<promise>TASK_COMPLETE</promise>",
            r"<promise>DONE</promise>",
            r"<complete>true</complete>",
        ]

        for pattern in xml_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        # Text markers
        text_markers = [
            "COMPLETED",
            "TASK_COMPLETE",
            "[TASK COMPLETE]",
            "✓ COMPLETE",
            "✅ COMPLETE",
            "Task completed successfully",
        ]

        content_upper = content.upper()
        return any(marker.upper() in content_upper for marker in text_markers)
    
    def get_iteration_info(self) -> dict:
        """
        Get current iteration information.
        
        Returns:
            Iteration info dictionary
        """
        state = self._load_state()
        if not state:
            return {
                "iteration": 0,
                "max_iterations": self.max_iterations,
                "remaining": self.max_iterations,
            }
        
        iteration = state.get("iteration", 0)
        return {
            "iteration": iteration,
            "max_iterations": self.max_iterations,
            "remaining": max(0, self.max_iterations - iteration),
            "start_time": state.get("start_time"),
            "last_updated": state.get("last_updated"),
        }
    
    def get_reinjection_prompt(self) -> str:
        """
        Generate reinjection prompt.
        
        Returns:
            Reinjection prompt
        """
        state = self._load_state()
        iteration = state.get("iteration", 0) if state else 0
        prompt = state.get("prompt", "Continue task") if state else "Continue task"
        
        # Get last output
        last_output = ""
        if self.output_file.exists():
            last_output = self.output_file.read_text()[:5000]
        
        return f"""
# Ralph Wiggum Loop - Continuation (Iteration {iteration + 1})

**Task ID**: {self.task_id}
**Original Prompt**: {prompt}

## Previous Output
{last_output if last_output else "No previous output"}

## Instructions
Continue working on the task. Review the previous output above and:
1. Assess what has been completed
2. Identify what still needs to be done
3. Continue with the next steps
4. Move the task file to /Done when complete, OR
5. Output a completion promise like: <promise>TASK_COMPLETE</promise>

**Remember**: You are in an autonomous loop. Keep working until the task is fully complete.
"""
    
    def mark_complete(self, metadata: dict | None = None) -> dict:
        """
        Mark task as complete.
        
        Args:
            metadata: Completion metadata
            
        Returns:
            Updated state
        """
        state = self._load_state()
        if not state:
            state = self.initialize_state("")
        
        state["status"] = "complete"
        state["completion_time"] = datetime.now().isoformat()
        state["metadata"] = {**state.get("metadata", {}), **(metadata or {})}
        
        self._save_state(state)
        return state
    
    def mark_failed(self, error: str, metadata: dict | None = None) -> dict:
        """
        Mark task as failed.
        
        Args:
            error: Error message
            metadata: Failure metadata
            
        Returns:
            Updated state
        """
        state = self._load_state()
        if not state:
            state = self.initialize_state("")
        
        state["status"] = "failed"
        state["error"] = error
        state["failure_time"] = datetime.now().isoformat()
        state["metadata"] = {**state.get("metadata", {}), **(metadata or {})}
        
        self._save_state(state)
        
        # Move to error folder
        error_dir = self.vault_path / "Error"
        error_dir.mkdir(parents=True, exist_ok=True)
        error_file = error_dir / f"{self.task_id}_error.md"
        error_file.write_text(f"# Task Failed\n\n**Error**: {error}\n\n**Time**: {datetime.now().isoformat()}")
        
        return state
    
    def wait_for_completion(
        self,
        poll_interval: float = 2.0,
        callback: callable | None = None,
    ) -> tuple[bool, str]:
        """
        Wait for task completion (for external monitoring).
        
        Args:
            poll_interval: Polling interval in seconds
            callback: Optional callback on each iteration
            
        Returns:
            Tuple of (completed, reason)
        """
        while True:
            completed, reason = self.check_completion()
            
            if completed:
                return True, reason
            
            if callback:
                callback(self.get_iteration_info())
            
            time.sleep(poll_interval)


def create_ralph_loop(
    vault_path: str | Path,
    task_id: str,
    prompt: str,
    max_iterations: int = 10,
) -> RalphLoopManager:
    """
    Create and initialize a Ralph loop.
    
    Args:
        vault_path: Path to Obsidian vault
        task_id: Task identifier
        prompt: Task prompt
        max_iterations: Maximum iterations
        
    Returns:
        Initialized RalphLoopManager
    """
    manager = RalphLoopManager(
        vault_path=vault_path,
        task_id=task_id,
        max_iterations=max_iterations,
    )
    manager.initialize_state(prompt)
    return manager
