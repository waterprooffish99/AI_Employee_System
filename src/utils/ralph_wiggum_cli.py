#!/usr/bin/env python3
"""
Ralph Wiggum Loop CLI for AI Employee System - Gold Tier

Autonomous task execution with loop management.
Calls Claude/Gemini API and keeps iterating until task is complete.

Usage:
    uv run python -m src.utils.ralph_wiggum_cli --task "process_all_files"
    uv run python -m src.utils.ralph_wiggum_cli --task "process_all_files" --max-iterations 5
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.ralph_loop import RalphLoopManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_vault_path() -> Path:
    """
    Get the Obsidian vault path.
    
    Returns:
        Path to vault directory
    """
    # Check environment variable first
    if env_path := os.getenv("VAULT_PATH"):
        return Path(env_path)
    
    # Default to AI_Employee_Vault in current directory
    vault = Path.cwd() / "AI_Employee_Vault"
    
    if vault.exists():
        return vault
    
    # Try parent directory
    vault = Path.cwd().parent / "AI_Employee_Vault"
    if vault.exists():
        return vault
    
    raise FileNotFoundError(
        "Could not find AI_Employee_Vault directory. "
        "Set VAULT_PATH environment variable or run from project root."
    )


def call_llm_api(prompt: str, model: str = "claude") -> str:
    """
    Call the LLM API (Claude or Gemini).
    
    Args:
        prompt: Prompt to send to LLM
        model: Model to use ("claude" or "gemini")
    
    Returns:
        LLM response text
    """
    model_choice = os.getenv("LLM_MODEL", model).lower()
    
    if model_choice == "gemini":
        return call_gemini_api(prompt)
    else:
        return call_claude_api(prompt)


def call_claude_api(prompt: str) -> str:
    """
    Call Claude API via claude-code CLI.
    
    Args:
        prompt: Prompt to send
    
    Returns:
        Claude's response
    """
    try:
        # Use claude-code CLI
        result = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per call
            cwd=str(get_vault_path()),
        )
        
        if result.returncode != 0:
            logger.error(f"Claude CLI error: {result.stderr}")
            raise RuntimeError(f"Claude CLI failed: {result.stderr}")
        
        return result.stdout
        
    except FileNotFoundError:
        logger.warning("Claude CLI not found, trying gemini")
        # Fallback to gemini
        os.environ["LLM_MODEL"] = "gemini"
        return call_gemini_api(prompt)
        
    except subprocess.TimeoutExpired:
        logger.error("Claude API call timed out")
        raise RuntimeError("Claude API timeout - task too complex, try breaking it down")


def call_gemini_api(prompt: str) -> str:
    """
    Call Gemini API.
    
    Args:
        prompt: Prompt to send
    
    Returns:
        Gemini's response
    """
    try:
        import google.generativeai as genai
        
        # Configure API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Pro or Flash
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 8192,
            }
        )
        
        return response.text
        
    except ImportError:
        logger.error("google-generativeai not installed. Run: uv add google-generativeai")
        raise RuntimeError("Gemini API library not available")
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise RuntimeError(f"Gemini API failed: {e}")


def build_system_prompt() -> str:
    """
    Build the system prompt for the AI agent.
    
    Returns:
        System prompt string
    """
    return """
You are an AI Employee working in Gold Tier Autonomous Mode.
You have access to the Obsidian vault file system.

Your task is to complete the assigned work autonomously.

IMPORTANT RULES:
1. Work independently - no hand-holding needed
2. Use the file system to read tasks and write results
3. When you complete the task, output EXACTLY: <promise>COMPLETED</promise>
4. If you encounter errors, log them and try to recover
5. Move completed files to the /Done folder

You are in a loop that will continue until you output the completion promise.
Take your time and do the job thoroughly.
""".strip()


def run_ralph_loop(
    task_id: str,
    max_iterations: int = 10,
    model: str = "claude",
    dry_run: bool = False,
) -> bool:
    """
    Run the Ralph Wiggum loop for a task.
    
    Args:
        task_id: Task identifier (filename without .md)
        max_iterations: Maximum loop iterations
        model: LLM model to use
        dry_run: If True, don't actually call LLM
    
    Returns:
        True if task completed successfully
    """
    # Get vault path
    try:
        vault_path = get_vault_path()
    except FileNotFoundError as e:
        logger.error(str(e))
        return False
    
    logger.info(f"Vault path: {vault_path}")
    
    # Initialize Ralph loop manager
    loop_manager = RalphLoopManager(
        vault_path=vault_path,
        task_id=task_id,
        max_iterations=max_iterations,
    )
    
    # Read task file
    task_file = vault_path / "Needs_Action" / f"{task_id}.md"
    
    if not task_file.exists():
        logger.error(f"Task file not found: {task_file}")
        return False
    
    task_content = task_file.read_text()
    logger.info(f"Task file loaded: {task_file}")
    
    # Initialize state
    loop_manager.initialize_state(
        prompt=task_content,
        metadata={
            "task_file": str(task_file),
            "started": datetime.now().isoformat(),
        }
    )
    
    # Build initial prompt
    system_prompt = build_system_prompt()
    current_prompt = f"{system_prompt}\n\nTASK:\n{task_content}"
    
    logger.info(f"Starting Ralph Wiggum loop (max iterations: {max_iterations})")
    print(f"\n{'='*60}")
    print(f"🚀 Ralph Wiggum Loop Started")
    print(f"Task: {task_id}")
    print(f"Max Iterations: {max_iterations}")
    print(f"{'='*60}\n")
    
    # Main loop
    iteration = 0
    while True:
        iteration += 1
        
        # Get iteration info
        info = loop_manager.get_iteration_info()
        print(f"\n{'='*40}")
        print(f"📍 Iteration {info['iteration']} / {max_iterations}")
        print(f"{'='*40}")
        
        # Check if we should continue
        if info["remaining"] <= 0:
            logger.error("Max iterations reached")
            print("\n❌ Max iterations reached without completion")
            loop_manager.mark_failed(error="Max iterations reached")
            return False
        
        if dry_run:
            print("[DRY RUN] Would call LLM API")
            output = "Simulated output for testing. <promise>COMPLETED</promise>"
        else:
            # Call LLM API
            print(f"\n🤖 Calling {model.upper()} API...")
            try:
                output = call_llm_api(current_prompt, model=model)
                print(f"✅ API response received ({len(output)} chars)")
            except Exception as e:
                logger.error(f"LLM API call failed: {e}")
                print(f"\n❌ LLM API call failed: {e}")
                
                # Log error and retry
                loop_manager.update_state(output=f"ERROR: {e}")
                current_prompt = f"Previous attempt failed: {e}\n\nPlease retry the task."
                continue
        
        # Update state with output
        loop_manager.update_state(output=output)
        
        # Check for completion
        is_complete, reason = loop_manager.check_completion(output)
        
        if is_complete:
            print(f"\n✅ Task completed: {reason}")
            loop_manager.mark_complete(metadata={"reason": reason})
            
            # Move task file to Done if it still exists
            if task_file.exists():
                done_file = vault_path / "Done" / f"{task_id}.md"
                done_file.write_text(
                    task_content + 
                    f"\n\n**Completed**: {datetime.now().isoformat()}\n"
                    f"**Reason**: {reason}"
                )
                task_file.unlink()
                logger.info(f"Task file moved to Done: {done_file}")
            
            print(f"\n{'='*60}")
            print(f"✅ TASK COMPLETE")
            print(f"{'='*60}")
            return True
        
        # Not complete - prepare for next iteration
        print(f"\n⏳ Continuing loop... ({reason})")
        
        # Build reinjection prompt
        current_prompt = loop_manager.get_reinjection_prompt()
        
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    # Should never reach here
    return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ralph Wiggum Loop - Autonomous task execution"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Task ID (filename without .md extension)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum loop iterations (default: 10)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        choices=["claude", "gemini"],
        default="claude",
        help="LLM model to use (default: claude)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without calling LLM API (for testing)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the loop
    success = run_ralph_loop(
        task_id=args.task,
        max_iterations=args.max_iterations,
        model=args.model,
        dry_run=args.dry_run,
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
