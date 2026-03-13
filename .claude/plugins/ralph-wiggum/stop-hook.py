"""
Ralph Wiggum Stop Hook for AI Employee System - Gold Tier

Intercepts Claude Code exit attempts and re-injects prompts if tasks are incomplete.
Implements autonomous multi-step task completion pattern.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


class RalphWiggumStopHook:
    """
    Stop hook for Ralph Wiggum loop pattern.
    
    Intercepts Claude's exit attempts and:
    - Checks if task is complete
    - Re-injects prompt if incomplete
    - Enforces max iterations
    - Preserves state across iterations
    """
    
    def __init__(
        self,
        vault_path: str,
        max_iterations: int = 10,
        timeout_seconds: int = 3600,
    ):
        """
        Initialize stop hook.
        
        Args:
            vault_path: Path to Obsidian vault
            max_iterations: Maximum loop iterations
            timeout_seconds: Loop timeout in seconds
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = int(
            os.getenv("RALPH_MAX_ITERATIONS", max_iterations)
        )
        self.timeout_seconds = int(
            os.getenv("RALPH_TIMEOUT_SECONDS", timeout_seconds)
        )
        
        # Directories
        self.plans_dir = self.vault_path / "Plans"
        self.done_dir = self.vault_path / "Done"
        self.error_dir = self.vault_path / "Error"
        
        # Ensure directories exist
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        self.error_dir.mkdir(parents=True, exist_ok=True)
    
    def check_should_stop(self, task_id: str) -> tuple[bool, str]:
        """
        Check if the loop should stop.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Tuple of (should_stop, reason)
        """
        state_file = self.plans_dir / f"{task_id}_state.json"
        
        # Check if state file exists
        if not state_file.exists():
            return True, "No state file found - task may be complete"
        
        # Load state
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return True, f"Error reading state file: {e}"
        
        # Check max iterations
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
        
        # Check if task file moved to Done
        task_file = self.done_dir / f"{task_id}.md"
        if task_file.exists():
            return True, "Task file moved to Done folder"
        
        # Check completion promise in output
        # This is checked by examining the last output
        last_output_file = self.plans_dir / f"{task_id}_last_output.txt"
        if last_output_file.exists():
            content = last_output_file.read_text()
            if self._contains_completion_promise(content):
                return True, "Completion promise detected in output"
        
        # Task still in progress
        return False, "Task still in progress - continuing loop"
    
    def _contains_completion_promise(self, content: str) -> bool:
        """
        Check if content contains a completion promise.
        
        Args:
            content: Output content to check
            
        Returns:
            True if completion promise found
        """
        # Look for completion markers
        markers = [
            "<promise>TASK_COMPLETE</promise>",
            "<promise>DONE</promise>",
            "TASK_COMPLETE",
            "[TASK COMPLETE]",
            "✓ COMPLETE",
            "✅ COMPLETE",
        ]
        
        content_upper = content.upper()
        return any(marker.upper() in content_upper for marker in markers)
    
    def update_state(
        self,
        task_id: str,
        iteration: int,
        output: str,
        metadata: dict | None = None,
    ) -> Path:
        """
        Update task state file.
        
        Args:
            task_id: Task identifier
            iteration: Current iteration number
            output: Last output from Claude
            metadata: Additional metadata
            
        Returns:
            Path to state file
        """
        state_file = self.plans_dir / f"{task_id}_state.json"
        
        # Load existing state or create new
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
            except (json.JSONDecodeError, IOError):
                state = {}
        else:
            state = {
                "task_id": task_id,
                "start_time": datetime.now().isoformat(),
                "iterations": [],
            }
        
        # Update state
        state["iteration"] = iteration
        state["last_updated"] = datetime.now().isoformat()
        state["iterations"].append({
            "number": iteration,
            "timestamp": datetime.now().isoformat(),
            "output_length": len(output),
        })
        
        if metadata:
            state["metadata"] = metadata
        
        # Save state
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        
        # Save last output
        output_file = self.plans_dir / f"{task_id}_last_output.txt"
        output_file.write_text(output)
        
        return state_file
    
    def get_reinjection_prompt(self, task_id: str, original_prompt: str) -> str:
        """
        Generate reinjection prompt for continuing task.
        
        Args:
            task_id: Task identifier
            original_prompt: Original task prompt
            
        Returns:
            Reinjection prompt
        """
        state_file = self.plans_dir / f"{task_id}_state.json"
        output_file = self.plans_dir / f"{task_id}_last_output.txt"
        
        # Load last output
        last_output = ""
        if output_file.exists():
            last_output = output_file.read_text()
        
        # Load state
        iteration = 0
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
                iteration = state.get("iteration", 0)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Create reinjection prompt
        reinjection = f"""
# Ralph Wiggum Loop - Continuation (Iteration {iteration + 1})

**Task ID**: {task_id}
**Original Prompt**: {original_prompt}

## Previous Output
{last_output[:5000] if last_output else "No previous output"}

## Instructions
Continue working on the task. Review the previous output above and:
1. Assess what has been completed
2. Identify what still needs to be done
3. Continue with the next steps
4. Move the task file to /Done when complete, OR
5. Output a completion promise like: <promise>TASK_COMPLETE</promise>

**Remember**: You are in an autonomous loop. Keep working until the task is fully complete.
"""
        return reinjection
    
    def on_exit_attempt(
        self,
        task_id: str,
        original_prompt: str,
        output: str,
    ) -> tuple[bool, str]:
        """
        Handle Claude's exit attempt.
        
        Args:
            task_id: Task identifier
            original_prompt: Original task prompt
            output: Claude's output
            
        Returns:
            Tuple of (allow_exit, message)
        """
        # Update state with this iteration
        state = self.plans_dir / f"{task_id}_state.json"
        iteration = 0
        if state.exists():
            try:
                with open(state, "r") as f:
                    state_data = json.load(f)
                iteration = state_data.get("iteration", 0)
            except (json.JSONDecodeError, IOError):
                pass
        
        self.update_state(task_id, iteration + 1, output)
        
        # Check if should stop
        should_stop, reason = self.check_should_stop(task_id)
        
        if should_stop:
            # Allow exit
            print(f"\n🎉 Ralph Wiggum Loop: {reason}", file=sys.stderr)
            return True, reason
        else:
            # Block exit and reinject
            print(f"\n🔄 Ralph Wiggum Loop: {reason}", file=sys.stderr)
            reinjection = self.get_reinjection_prompt(task_id, original_prompt)
            return False, reinjection


def main():
    """Main entry point for stop hook testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ralph Wiggum Stop Hook")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--task-id", required=True, help="Task identifier")
    parser.add_argument("--check", action="store_true", help="Check if should stop")
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update state with output from stdin"
    )
    
    args = parser.parse_args()
    
    hook = RalphWiggumStopHook(args.vault)
    
    if args.check:
        should_stop, reason = hook.check_should_stop(args.task_id)
        print(json.dumps({"should_stop": should_stop, "reason": reason}))
    elif args.update:
        output = sys.stdin.read()
        state_file = hook.update_state(args.task_id, 1, output)
        print(f"State updated: {state_file}")


if __name__ == "__main__":
    main()
