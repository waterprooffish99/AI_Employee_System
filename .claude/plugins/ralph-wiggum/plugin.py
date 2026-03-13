"""
Ralph Wiggum Plugin for Claude Code

Autonomous multi-step task completion using stop hook pattern.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


# Plugin configuration
PLUGIN_NAME = "Ralph Wiggum Loop"
PLUGIN_VERSION = "1.0.0"


def log(message: str):
    """Log a message to stderr."""
    print(f"[{PLUGIN_NAME}] {message}", file=sys.stderr)


def get_vault_path() -> Path:
    """Get the Obsidian vault path from environment or config."""
    # Try environment variable first
    vault = os.getenv("OBSIDIAN_VAULT_PATH")
    if vault:
        return Path(vault)
    
    # Try to infer from current directory
    # Look for AI_Employee_Vault in parent directories
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        vault_dir = parent / "AI_Employee_Vault"
        if vault_dir.exists():
            return vault_dir
    
    # Default
    return Path.cwd() / "AI_Employee_Vault"


def check_task_completion(task_id: str) -> dict:
    """
    Check if a task is complete.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Status dictionary
    """
    vault_path = get_vault_path()
    
    # Check if task file exists in Done folder
    done_file = vault_path / "Done" / f"{task_id}.md"
    if done_file.exists():
        return {"complete": True, "reason": "Task file in Done folder"}
    
    # Check state file
    state_file = vault_path / "Plans" / f"{task_id}_state.json"
    if not state_file.exists():
        return {"complete": False, "reason": "No state file found"}
    
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
        
        # Check iteration count
        iteration = state.get("iteration", 0)
        max_iterations = int(os.getenv("RALPH_MAX_ITERATIONS", "10"))
        
        if iteration >= max_iterations:
            return {
                "complete": True,
                "reason": f"Max iterations ({max_iterations}) reached"
            }
        
        return {
            "complete": False,
            "reason": f"Task in progress (iteration {iteration}/{max_iterations})"
        }
    except Exception as e:
        return {"complete": False, "reason": f"Error reading state: {e}"}


def update_task_state(
    task_id: str,
    output: str,
    iteration: int | None = None,
) -> Path:
    """
    Update task state with output.
    
    Args:
        task_id: Task identifier
        output: Claude's output
        iteration: Iteration number (auto-increment if None)
        
    Returns:
        Path to state file
    """
    vault_path = get_vault_path()
    state_file = vault_path / "Plans" / f"{task_id}_state.json"
    output_file = vault_path / "Plans" / f"{task_id}_last_output.txt"
    
    # Load existing state
    state = {"task_id": task_id, "iteration": 0, "iterations": []}
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
        except:
            pass
    
    # Increment iteration
    if iteration is None:
        iteration = state.get("iteration", 0) + 1
    state["iteration"] = iteration
    
    # Save state
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)
    
    # Save output
    with open(output_file, "w") as f:
        f.write(output)
    
    log(f"Task {task_id} state updated (iteration {iteration})")
    return state_file


def get_reinjection_prompt(task_id: str) -> str:
    """
    Get reinjection prompt for continuing task.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Reinjection prompt
    """
    vault_path = get_vault_path()
    output_file = vault_path / "Plans" / f"{task_id}_last_output.txt"
    
    # Get last output
    last_output = ""
    if output_file.exists():
        last_output = output_file.read_text()[:5000]  # Limit length
    
    return f"""
# Ralph Wiggum Loop - Continuation

**Task**: {task_id}

## Previous Output
{last_output if last_output else "No previous output"}

## Instructions
Continue working on the task. Review the previous output and:
1. Assess what has been completed
2. Identify remaining work
3. Continue with next steps
4. Move task to /Done when complete OR output completion promise

Keep working until fully complete.
"""


def main():
    """Main plugin entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ralph Wiggum Plugin")
    parser.add_argument("command", choices=["check", "update", "reinject"])
    parser.add_argument("--task-id", required=True, help="Task identifier")
    parser.add_argument("--output", help="Output file to read")
    
    args = parser.parse_args()
    
    if args.command == "check":
        result = check_task_completion(args.task_id)
        print(json.dumps(result))
    
    elif args.command == "update":
        output = ""
        if args.output:
            with open(args.output, "r") as f:
                output = f.read()
        else:
            output = sys.stdin.read()
        
        state_file = update_task_state(args.task_id, output)
        print(f"State updated: {state_file}")
    
    elif args.command == "reinject":
        prompt = get_reinjection_prompt(args.task_id)
        print(prompt)


if __name__ == "__main__":
    main()
