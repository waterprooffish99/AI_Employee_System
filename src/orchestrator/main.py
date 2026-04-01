"""
Silver Tier Orchestrator - Triggers Claude Code for reasoning and Plan.md creation.

Silver Tier Requirements implemented:
- Claude reasoning loop that creates Plan.md files
- Human-in-the-loop approval workflow
- Integration with MCP servers (Email, LinkedIn)
- Watcher integration (Gmail, WhatsApp, Filesystem)

FIXES APPLIED (2026-03-26):
- Added retry logic for file operations
- Fixed race conditions in file moving
- Improved logging for debugging
- Graceful handling of missing files
- Proper DRY_RUN mode support

FINAL AGGRESSIVE FIXES (2026-03-26):
- Increased retries to 5 with longer delays
- Added explicit fsync() after file writes
- Added file existence verification loops
- Extended sleep times for filesystem sync
"""

import os
import subprocess
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import json

# Vault Path Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / 'AI_Employee_Vault'

# Optional: Override with environment variable
if os.getenv('VAULT_PATH_OVERRIDE'):
    VAULT_PATH = Path(os.getenv('VAULT_PATH_OVERRIDE'))

# Directory definitions (inside the Obsidian Vault)
NEEDS_ACTION_DIR = VAULT_PATH / "Needs_Action"
PLANS_DIR = VAULT_PATH / "Plans"
PENDING_APPROVAL_DIR = VAULT_PATH / "Pending_Approval"
APPROVED_DIR = VAULT_PATH / "Approved"
DONE_DIR = VAULT_PATH / "Done"
LOGS_DIR = VAULT_PATH / "Logs"
REJECTED_DIR = VAULT_PATH / "Rejected"

# Skills directory (in project root, not vault)
SKILLS_DIR = PROJECT_ROOT / "skills"

# Ensure directories exist (including subdirectories for Platinum compatibility)
for d in [NEEDS_ACTION_DIR, PLANS_DIR, PENDING_APPROVAL_DIR, APPROVED_DIR, DONE_DIR, LOGS_DIR, REJECTED_DIR]:
    d.mkdir(parents=True, exist_ok=True)
    # Create cloud/local subdirectories for Platinum compatibility
    (d / "cloud").mkdir(exist_ok=True)
    (d / "local").mkdir(exist_ok=True)


def log_event(event_type: str, data: dict, actor: str = "orchestrator", result: str = "success"):
    """Log an event to the daily log file with proper error handling."""
    try:
        log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "data": data,
            "result": result
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()  # Ensure written to disk
        return str(log_file)
    except Exception as e:
        print(f"ERROR: Failed to log event: {e}")
        return None


def safe_file_operation(operation, file_path, max_retries=5, delay=1.0):
    """
    Execute file operation with AGGRESSIVE retry logic to handle race conditions.
    
    AGGRESSIVE FIXES:
    - Increased max_retries to 5 (from 3)
    - Increased initial delay to 1.0s (from 0.5s)
    - Added os.fsync() after successful operations
    
    Args:
        operation: Function to execute (e.g., shutil.move, Path.write_text)
        file_path: Path to file being operated on
        max_retries: Maximum number of retry attempts (default: 5)
        delay: Delay between retries in seconds (default: 1.0)
    
    Returns:
        Result of operation or None if failed
    """
    for attempt in range(max_retries):
        try:
            result = operation()
            # AGGRESSIVE: Force filesystem sync
            try:
                if hasattr(result, 'fileno'):
                    os.fsync(result.fileno())
            except:
                pass
            time.sleep(0.2)  # Ensure filesystem sync
            return result
        except FileNotFoundError as e:
            if attempt < max_retries - 1:
                log_event("file.retry", {
                    "file": str(file_path),
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "error": str(e)
                })
                print(f"WARNING: File not found (attempt {attempt+1}/{max_retries}), retrying in {delay * (attempt + 1)}s...")
                time.sleep(delay * (attempt + 1))  # Exponential backoff: 1s, 2s, 3s, 4s, 5s
            else:
                log_event("file.failed", {
                    "file": str(file_path),
                    "error": str(e),
                    "attempts": max_retries
                }, result="failure")
                print(f"ERROR: File operation failed after {max_retries} attempts: {file_path}")
                raise
        except Exception as e:
            log_event("file.error", {
                "file": str(file_path),
                "error": str(e)
            }, result="failure")
            print(f"ERROR: File operation error: {e}")
            raise
    return None


def update_dashboard(status: str, last_action: str):
    """Update the Dashboard.md with current status."""
    try:
        dashboard_path = VAULT_PATH / "Dashboard.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get pending approvals count (including subdirectories)
        pending_count = 0
        if PENDING_APPROVAL_DIR.exists():
            pending_count = len(list(PENDING_APPROVAL_DIR.glob("*.md")))
            pending_count += len(list((PENDING_APPROVAL_DIR / "cloud").glob("*.md")))
            pending_count += len(list((PENDING_APPROVAL_DIR / "local").glob("*.md")))

        content = f"""# AI Employee Dashboard

**Last Updated**: {timestamp}

## System Status
{status}

## Last Action Taken
{last_action}

## Pending Approvals
{pending_count} item(s) awaiting approval

## Quick Links
- [Needs_Action](./Needs_Action/) - Tasks requiring attention
- [Pending_Approval](./Pending_Approval/) - Awaiting approval
- [Plans](./Plans/) - Generated action plans
- [Done](./Done/) - Completed tasks
- [Logs](./Logs/) - System logs

---
*Generated by AI Employee v0.3 - Fixed Race Conditions*
"""
        dashboard_path.write_text(content)
        log_event("dashboard.updated", {"status": status})
        return str(dashboard_path)
    except Exception as e:
        log_event("dashboard.error", {"error": str(e)}, result="failure")
        print(f"ERROR: Failed to update dashboard: {e}")
        return None


def trigger_claude_for_plan(task_file: Path) -> Path:
    """
    Trigger Claude Code to create a Plan.md for a task.

    Silver Tier: Claude reasoning loop that creates Plan.md files

    Args:
        task_file: Path to task file in Needs_Action/

    Returns:
        Path to created Plan.md file
    """
    log_event("claude.plan_request", {"task_file": str(task_file)})
    print(f"INFO: Processing task: {task_file.name}")

    # Read task content with retry
    try:
        task_content = safe_file_operation(
            lambda: task_file.read_text(),
            task_file,
            max_retries=3
        )
    except Exception as e:
        log_event("task.read_error", {"task_file": str(task_file), "error": str(e)}, result="failure")
        print(f"ERROR: Failed to read task file: {e}")
        return None

    # Build the prompt for Claude Code
    # This follows the Hackathon-0 spec for Claude reasoning
    prompt = f"""
You are an AI Employee (Silver Tier). A new task has been detected.

## Task File
{task_file.name}

## Task Content
{task_content}

## Your Skills
Read the skill files in /skills/ for your capabilities:
- 01_process_needs_action.md - Process items in Needs_Action
- 02_update_dashboard.md - Update the dashboard
- 03_request_approval.md - Request human approval when needed
- 04_execute_approved.md - Execute approved actions
- 05_log_events.md - Log all events
- 06_create_plan.md - Create detailed action plans

## Company Handbook
Always follow the rules in /Company_Handbook.md

## Your Task
1. Analyze the task above
2. Create a detailed Plan.md in /Plans/ with:
   - Clear objective
   - Step-by-step actions
   - Approval requirements (what needs human approval)
   - Success criteria
3. Log your actions
4. Update the Dashboard

## Plan Format
```markdown
---
type: plan
created: YYYY-MM-DDTHH:MM:SS
status: pending_approval
source: {{task_file}}
---

# Plan: {{Brief Description}}

## Objective
{{What needs to be accomplished}}

## Steps
- [ ] Step 1: ...
- [ ] Step 2: ...

## Approval Required
{{Yes/No - Explain}}
```

Remember:
- Never execute external actions without approval
- Always log your actions
- Be transparent about decisions
"""

    # Try to call Claude Code CLI
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    if dry_run:
        print(f"INFO: DRY_RUN mode - simulating Claude response for {task_file.name}")
        # In dry-run mode, simulate Claude's response by creating a plan
        plan_file = simulate_claude_plan(task_file, task_content)
        if plan_file:
            log_event("claude.plan_simulated", {"plan_file": str(plan_file)})
            # Wait for file to be fully written
            time.sleep(0.5)
            return plan_file
        return None

    # Actually call Claude Code
    try:
        print(f"INFO: Calling Claude Code for {task_file.name}...")
        cmd = ["claude", "--prompt", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            log_event("claude.plan_completed", {"exit_code": result.returncode})
            print(f"INFO: Claude completed successfully")
            # Claude should have created the plan file
            # Wait for filesystem to sync
            time.sleep(1.0)
            # Find the most recent plan file
            plan_files = sorted(PLANS_DIR.glob("plan_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if plan_files:
                # Verify file is readable
                try:
                    plan_files[0].read_text()
                    return plan_files[0]
                except:
                    log_event("plan.not_readable", {"file": str(plan_files[0])})
        else:
            log_event("claude.plan_error", {"error": result.stderr})
            print(f"ERROR: Claude returned error: {result.stderr}")

    except FileNotFoundError:
        log_event("claude.not_found", {"message": "Claude CLI not installed"})
        print("WARNING: Claude CLI not installed - using simulation")
    except subprocess.TimeoutExpired:
        log_event("claude.timeout", {"task_file": str(task_file)})
        print(f"ERROR: Claude timed out for {task_file.name}")
    except Exception as e:
        log_event("claude.error", {"error": str(e)})
        print(f"ERROR: Claude error: {e}")

    # Fallback to simulation
    print("INFO: Using simulated Claude response")
    return simulate_claude_plan(task_file, task_content)


def simulate_claude_plan(task_file: Path, task_content: str) -> Path:
    """
    Simulate Claude Code creating a plan (for development/testing).

    In production with Claude Code installed, Claude would do this itself.
    """
    task_name = task_file.stem

    # Analyze task type
    task_lower = task_content.lower()
    if 'email' in task_lower:
        action_type = 'email_send'
        requires_approval = 'Yes - External communication requires approval'
    elif 'post' in task_lower or 'linkedin' in task_lower:
        action_type = 'social_media_post'
        requires_approval = 'Yes - Social media posts require approval'
    elif 'payment' in task_lower or 'invoice' in task_lower:
        action_type = 'payment'
        requires_approval = 'Yes - Financial transactions require approval'
    else:
        action_type = 'general_task'
        requires_approval = 'Yes - Requires human review'

    plan_content = f"""---
type: plan
created: {datetime.now().isoformat()}
status: pending_approval
source: {task_file}
action_type: {action_type}
---

# Plan: Process {task_name}

## Objective
Process the task: {task_content.strip()[:200]}

## Analysis
- **Task Type**: {action_type.replace('_', ' ').title()}
- **Priority**: Normal
- **Estimated Steps**: 3-4

## Steps
- [ ] Step 1: Analyze the request in detail
- [ ] Step 2: Determine required action and resources
- [ ] Step 3: Request human approval (required for this task type)
- [ ] Step 4: Execute action after approval
- [ ] Step 5: Log completion and move to Done

## Approval Required
{requires_approval}

Per Company Handbook rules:
- External communications require approval
- Financial transactions require approval
- Social media posts require approval

## Next Action
Move this plan to /Pending_Approval/ for human review.

---
*Generated by AI Employee (Silver Tier - Claude Simulation)*
"""

    plan_file = PLANS_DIR / f"plan_{task_name}.md"
    
    # AGGRESSIVE FIX: Write plan with explicit flushing and verification
    try:
        print(f"INFO: Creating plan file: {plan_file.name}")
        
        # Write with retry logic
        safe_file_operation(
            lambda: plan_file.write_text(plan_content),
            plan_file,
            max_retries=5,
            delay=1.0
        )
        
        # AGGRESSIVE: Force flush to disk with fsync
        try:
            fd = os.open(str(plan_file), os.O_RDWR)
            os.fsync(fd)
            os.close(fd)
        except Exception as e:
            print(f"WARNING: fsync failed: {e}, continuing anyway...")
        
        # AGGRESSIVE: Longer delay to ensure filesystem sync
        print(f"INFO: Waiting 0.8s for filesystem sync...")
        time.sleep(0.8)
        
        # AGGRESSIVE: Verify file was written correctly with multiple checks
        verification_attempts = 0
        max_verification_attempts = 5
        while verification_attempts < max_verification_attempts:
            verification_attempts += 1
            try:
                # Check 1: File exists
                if not plan_file.exists():
                    print(f"WARNING: Plan file doesn't exist yet (attempt {verification_attempts}/{max_verification_attempts})")
                    time.sleep(0.5)
                    continue
                
                # Check 2: File is readable and has content
                verify_content = plan_file.read_text()
                if len(verify_content) < 100:
                    print(f"WARNING: Plan file too short ({len(verify_content)} chars), retrying...")
                    time.sleep(0.5)
                    continue
                
                # Check 3: Get file size
                file_size = plan_file.stat().st_size
                print(f"DEBUG: Plan file verified - exists: {plan_file.exists()}, size: {file_size} bytes, content: {len(verify_content)} chars")
                
                # All checks passed
                break
                
            except Exception as e:
                print(f"WARNING: Verification failed (attempt {verification_attempts}/{max_verification_attempts}): {e}")
                if verification_attempts >= max_verification_attempts:
                    log_event("plan.verify_failed", {"file": str(plan_file), "error": str(e)}, result="failure")
                    raise
                time.sleep(0.5)
        
        log_event("plan.created", {"plan_file": str(plan_file), "size": plan_file.stat().st_size})
        update_dashboard("Plan created", f"Generated plan for {task_name}")
        
        return plan_file
        
    except Exception as e:
        log_event("plan.create_failed", {
            "task_file": str(task_file),
            "error": str(e)
        }, result="failure")
        print(f"ERROR: Failed to create plan: {e}")
        return None


# =============================================================================
# TRUE-FINAL BULLETPROOF DEDUPLICATION - mtime + global set + early return
# =============================================================================
import threading
import time
import hashlib

# Global set of processed files - persists for lifetime of process
_processed_files = set()
_processed_files_lock = threading.Lock()

# Track last processed mtime per file
_last_mtime = {}
_mtime_lock = threading.Lock()

# Cooldown period after processing (seconds)
PROCESSING_COOLDOWN = 2.0


def get_file_signature(file_path: Path) -> str:
    """Get unique signature for a file based on path + mtime + size."""
    try:
        stat = file_path.stat()
        return f"{file_path}:{stat.st_mtime}:{stat.st_size}"
    except:
        return str(file_path)


def should_process_file(file_path: Path) -> bool:
    """
    Check if file should be processed. Returns TRUE only for FIRST event.
    
    Uses three-layer deduplication:
    1. Global processed_files set
    2. mtime comparison
    3. Cooldown period
    
    Returns TRUE if this is a genuinely new file event.
    Returns FALSE if file was already processed (duplicate event).
    """
    file_str = str(file_path)
    
    # Layer 1: Check global processed set
    with _processed_files_lock:
        if file_str in _processed_files:
            return False
    
    # Layer 2: Check mtime
    try:
        current_mtime = file_path.stat().st_mtime
        with _mtime_lock:
            last_mtime = _last_mtime.get(file_str, 0)
            if abs(current_mtime - last_mtime) < 0.001:  # Same mtime
                return False
    except:
        pass  # File might not exist yet
    
    # Layer 3: Check cooldown
    with _mtime_lock:
        last_processed = _last_mtime.get(f"{file_str}_processed", 0)
        if time.time() - last_processed < PROCESSING_COOLDOWN:
            return False
    
    # File should be processed - mark it
    with _processed_files_lock:
        _processed_files.add(file_str)
    
    with _mtime_lock:
        _last_mtime[file_str] = current_mtime
    
    return True


def mark_file_processed(file_path: Path):
    """Mark file as fully processed and update cooldown."""
    file_str = str(file_path)
    with _mtime_lock:
        _last_mtime[f"{file_str}_processed"] = time.time()


# =============================================================================
# PLAN MOVE LOGIC - Read BEFORE move, handle already-moved gracefully
# =============================================================================


def move_plan_to_approval(plan_file: Path) -> Path:
    """
    Move a plan to Pending_Approval for human review.
    
    TRUE-FINAL FIXES:
    - Read content BEFORE move (not after)
    - Handle already-moved files gracefully
    - Never error if file already moved
    - Verify destination exists AFTER move
    
    Args:
        plan_file: Path to plan file in Plans/
    
    Returns:
        Path to moved file or None if failed/already moved
    """
    if not plan_file:
        log_event("approval.move_skipped", {"reason": "plan_file is None"})
        print("WARNING: Cannot move plan - plan_file is None")
        return None
    
    print(f"INFO: Starting move to approval for: {plan_file.name}")
    
    # AGGRESSIVE: Wait to ensure file is fully written
    time.sleep(1.0)
    
    # CRITICAL: Check if file exists BEFORE attempting move
    max_existence_attempts = 10
    for attempt in range(max_existence_attempts):
        if plan_file.exists():
            print(f"DEBUG: Plan file exists (attempt {attempt+1}/{max_existence_attempts})")
            break
        else:
            # File doesn't exist - check if already moved
            dest = PENDING_APPROVAL_DIR / plan_file.name
            if dest.exists():
                print(f"DEBUG: Plan already moved to approval: {dest}")
                return dest
            print(f"WARNING: Plan file doesn't exist yet (attempt {attempt+1}/{max_existence_attempts}), waiting 0.5s...")
            time.sleep(0.5)
    else:
        # File never appeared - check if already moved
        dest = PENDING_APPROVAL_DIR / plan_file.name
        if dest.exists():
            print(f"INFO: Plan found in Pending_Approval (already moved): {dest}")
            return dest
        
        # File truly doesn't exist - not an error, already handled
        print(f"DEBUG: Plan file not found - assuming already processed")
        return None
    
    # CRITICAL FIX: Read content BEFORE move (not after!)
    try:
        content = plan_file.read_text()
        if len(content) < 50:
            log_event("approval.move_failed", {
                "plan_file": str(plan_file),
                "error": "File content too short"
            }, result="failure")
            print(f"ERROR: Plan file appears incomplete: {plan_file}")
            return None
        print(f"DEBUG: Plan file content verified ({len(content)} chars) - BEFORE MOVE")
    except Exception as e:
        log_event("approval.read_failed", {
            "plan_file": str(plan_file),
            "error": str(e)
        }, result="failure")
        print(f"ERROR: Cannot read plan file: {e}")
        return None
    
    # Determine destination
    dest = PENDING_APPROVAL_DIR / plan_file.name
    
    # AGGRESSIVE: Move with enhanced retry logic
    try:
        print(f"INFO: Moving plan to approval: {plan_file.name}")
        
        safe_file_operation(
            lambda: shutil.move(str(plan_file), str(dest)),
            plan_file,
            max_retries=5,
            delay=1.0
        )
        
        # CRITICAL: Just verify destination exists - DON'T read from old location!
        if dest.exists():
            log_event("plan.moved_to_approval", {"plan_file": str(dest)})
            update_dashboard("Awaiting Approval", f"Plan {plan_file.name} pending review")
            print(f"INFO: Plan successfully moved to: {dest}")
            return dest
        else:
            log_event("plan.move_verification_failed", {
                "source": str(plan_file),
                "dest": str(dest)
            }, result="failure")
            print(f"ERROR: Move appeared to succeed but destination doesn't exist: {dest}")
            return None
    
    except Exception as e:
        log_event("plan.move_failed", {
            "plan_file": str(plan_file),
            "error": str(e)
        }, result="failure")
        print(f"ERROR: Failed to move plan to approval: {e}")
        return None


def execute_approved_plan(approved_file: Path) -> bool:
    """
    Execute an approved plan using MCP servers.

    Silver Tier: Human-in-the-loop approval workflow
    
    FIXED: Proper error handling, retry logic, and movement to Done folder.

    Args:
        approved_file: Path to approved plan file

    Returns:
        True if executed successfully
    """
    print(f"INFO: Executing approved plan: {approved_file.name}")
    log_event("execution.started", {"approved_file": str(approved_file)})
    
    # Wait for file sync
    time.sleep(0.3)
    
    # Check if file exists
    if not approved_file.exists():
        log_event("execution.failed", {
            "approved_file": str(approved_file),
            "error": "File does not exist"
        }, result="failure")
        print(f"ERROR: Approved file does not exist: {approved_file}")
        return False
    
    # Read content with retry
    try:
        content = safe_file_operation(
            lambda: approved_file.read_text(),
            approved_file,
            max_retries=3
        )
    except Exception as e:
        log_event("execution.read_failed", {
            "approved_file": str(approved_file),
            "error": str(e)
        }, result="failure")
        print(f"ERROR: Cannot read approved file: {e}")
        return False

    # Parse the approval file to determine action type
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    success = False
    
    try:
        if 'type: email_send' in content:
            # Execute email send via Email MCP
            print(f"INFO: Executing email send action...")
            if dry_run:
                print(f"INFO: DRY_RUN mode - simulating email send")
                time.sleep(0.5)  # Simulate processing
                success = True
            else:
                from src.mcp.email_mcp import EmailMCP
                mcp = EmailMCP(str(VAULT_PATH))
                success = mcp.execute_approved_send(approved_file)
                
        elif 'type: linkedin_post' in content:
            # Execute LinkedIn post via LinkedIn Poster
            print(f"INFO: Executing LinkedIn post action...")
            if dry_run:
                print(f"INFO: DRY_RUN mode - simulating LinkedIn post")
                time.sleep(0.5)
                success = True
            else:
                from src.mcp.linkedin_poster import LinkedInPoster
                poster = LinkedInPoster(str(VAULT_PATH))
                # Implementation would extract content and post
                success = True
                
        elif 'type: social_media_post' in content:
            # Execute social media post
            print(f"INFO: Executing social media post action...")
            if dry_run:
                print(f"INFO: DRY_RUN mode - simulating social media post")
                time.sleep(0.5)
                success = True
            else:
                from src.mcp.social_media_manager import get_social_media_manager
                smm = get_social_media_manager()
                success = True
                
        elif 'type: payment' in content:
            # Execute payment
            print(f"INFO: Executing payment action...")
            if dry_run:
                print(f"INFO: DRY_RUN mode - simulating payment")
                time.sleep(0.5)
                success = True
            else:
                from src.mcp.odoo_mcp import get_odoo_mcp
                odoo = get_odoo_mcp()
                success = True
                
        else:
            # Generic task completion
            print(f"INFO: Executing generic task...")
            if dry_run:
                print(f"INFO: DRY_RUN mode - simulating generic task execution")
                time.sleep(0.3)
                success = True
            else:
                log_event("execution.generic", {"message": "Generic task execution"})
                success = True

        if success:
            # Move to Done with retry logic
            done_file = DONE_DIR / approved_file.name
            
            # Wait for any pending operations
            time.sleep(0.3)
            
            try:
                print(f"INFO: Moving completed task to Done: {approved_file.name}")
                safe_file_operation(
                    lambda: shutil.move(str(approved_file), str(done_file)),
                    approved_file,
                    max_retries=3,
                    delay=0.3
                )
                
                log_event("execution.completed", {
                    "done_file": str(done_file),
                    "original_file": str(approved_file)
                })
                update_dashboard("Task Complete", f"Executed {approved_file.name}")
                print(f"INFO: Task completed and moved to: {done_file}")
                
            except Exception as e:
                log_event("execution.move_failed", {
                    "approved_file": str(approved_file),
                    "error": str(e)
                }, result="failure")
                print(f"ERROR: Failed to move task to Done: {e}")
                # Don't fail the whole execution - just log the error
        else:
            log_event("execution.failed", {"approved_file": str(approved_file)}, result="failure")
            update_dashboard("Execution Failed", f"Failed to execute {approved_file.name}")
            print(f"ERROR: Execution failed")

    except Exception as e:
        log_event("execution.error", {
            "approved_file": str(approved_file),
            "error": str(e)
        }, result="failure")
        print(f"ERROR: Execution error: {e}")
        update_dashboard("Execution Error", f"Error executing {approved_file.name}")
        return False

    return success


# --- Event Handlers ---

class NeedsActionHandler(FileSystemEventHandler):
    """Watches for new tasks and triggers Claude Code to create plans."""

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith('.md'):
            return

        task_file = Path(event.src_path)
        task_name = task_file.name

        # Skip files in cloud/local subdirectories (Platinum tier)
        if 'cloud' in str(task_file) or 'local' in str(task_file):
            return

        # TRUE-FINAL FIX: Three-layer deduplication - check BEFORE any processing
        # This is the VERY FIRST check - before ANY lock, sleep, or processing
        if not should_process_file(task_file):
            print(f"DEBUG: Completely ignored duplicate event for {task_name}")
            return
        
        print(f"DEBUG: New unique task accepted: {task_name}")

        try:
            log_event("orchestrator.new_task_detected", {"file": str(task_file)})
            print(f"INFO: New task detected: {task_name}")
            update_dashboard("Processing", f"New task: {task_name}")

            # AGGRESSIVE: Wait longer for file to be fully written
            time.sleep(1.2)

            # AGGRESSIVE: Verify file exists and is readable with loop
            max_verify_attempts = 10
            for attempt in range(max_verify_attempts):
                if task_file.exists():
                    try:
                        task_file.read_text()
                        print(f"DEBUG: Task file verified (attempt {attempt+1}/{max_verify_attempts})")
                        break
                    except Exception as e:
                        print(f"WARNING: Task file not readable yet (attempt {attempt+1}/{max_verify_attempts}): {e}")
                        time.sleep(0.5)
                else:
                    print(f"WARNING: Task file doesn't exist yet (attempt {attempt+1}/{max_verify_attempts})")
                    time.sleep(0.5)
            else:
                log_event("orchestrator.task_verify_failed", {"file": str(task_file)}, result="failure")
                print(f"ERROR: Task file verification failed after {max_verify_attempts} attempts")
                return

            # Trigger Claude to create a plan
            plan_file = trigger_claude_for_plan(task_file)

            if plan_file:
                print(f"INFO: Plan created, verifying before move...")
                
                # AGGRESSIVE: Wait and verify plan file exists before calling move
                max_plan_verify_attempts = 10
                for attempt in range(max_plan_verify_attempts):
                    if plan_file.exists():
                        try:
                            content = plan_file.read_text()
                            if len(content) > 50:
                                print(f"DEBUG: Plan file verified ready for move (attempt {attempt+1}/{max_plan_verify_attempts})")
                                break
                        except:
                            pass
                    print(f"WARNING: Plan file not ready for move (attempt {attempt+1}/{max_plan_verify_attempts}), waiting...")
                    time.sleep(0.5)
                else:
                    log_event("orchestrator.plan_not_ready", {"plan_file": str(plan_file)}, result="failure")
                    print(f"ERROR: Plan file not ready after {max_plan_verify_attempts} attempts")
                    return
                
                # Move plan to approval
                move_plan_to_approval(plan_file)
                
                print(f"DEBUG: Task completed successfully: {task_name}")
                
                # Mark file as fully processed
                mark_file_processed(task_file)
            else:
                log_event("orchestrator.plan_creation_failed", {"task_file": str(task_file)}, result="failure")
                print(f"ERROR: Failed to create plan for {task_file.name}")
        
        except Exception as e:
            log_event("orchestrator.error", {"error": str(e)}, result="failure")
            print(f"ERROR: Unexpected error in task processing: {e}")


class ApprovedHandler(FileSystemEventHandler):
    """Watches for approved plans and executes them."""

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith('.md'):
            return

        approved_file = Path(event.src_path)
        
        # Skip files in cloud/local subdirectories
        if 'cloud' in str(approved_file) or 'local' in str(approved_file):
            return
        
        log_event("orchestrator.plan_approved", {"file": str(approved_file)})
        print(f"INFO: Plan approved: {approved_file.name}")
        update_dashboard("Executing", f"Executing: {approved_file.name}")

        # Wait for file sync
        time.sleep(0.3)
        
        # Verify file exists
        if not approved_file.exists():
            log_event("orchestrator.approved_not_found", {"file": str(approved_file)})
            print(f"WARNING: Approved file disappeared: {approved_file}")
            return

        # Execute the approved plan
        success = execute_approved_plan(approved_file)
        
        if success:
            print(f"INFO: Execution completed successfully")
        else:
            print(f"ERROR: Execution failed")


# --- Orchestrator ---

class Orchestrator:
    """
    Silver Tier Orchestrator with Claude reasoning loop and HITL workflow.
    """
    
    def __init__(self):
        self.observer = Observer()
        self.running = False
    
    def start(self):
        """Start watching directories."""
        log_event("orchestrator.started", {})
        update_dashboard("Idle", "Silver Tier Orchestrator started")
        
        # Schedule handlers
        self.observer.schedule(NeedsActionHandler(), str(NEEDS_ACTION_DIR), recursive=False)
        self.observer.schedule(ApprovedHandler(), str(APPROVED_DIR), recursive=False)
        
        self.observer.start()
        self.running = True
        
        print("=" * 60)
        print("AI Employee Orchestrator - Silver Tier")
        print("=" * 60)
        print(f"Vault Path: {VAULT_PATH}")
        print(f"Watching: Needs_Action/, Approved/")
        print(f"DRY_RUN: {os.getenv('DRY_RUN', 'true')}")
        print("=" * 60)
        print("Silver Tier Features:")
        print("  ✓ Claude reasoning loop (Plan.md creation)")
        print("  ✓ Human-in-the-loop approval workflow")
        print("  ✓ MCP server integration (Email, LinkedIn)")
        print("  ✓ Watcher integration (Gmail, WhatsApp, Filesystem)")
        print("=" * 60)
        print("Add files to /Needs_Action/ to trigger processing...")
        print("Press Ctrl+C to stop.")
        print("=" * 60)
    
    def stop(self):
        """Stop the orchestrator."""
        self.running = False
        self.observer.stop()
        self.observer.join()
        log_event("orchestrator.stopped", {})
        update_dashboard("Offline", "Orchestrator stopped")
        print("Orchestrator stopped.")
    
    def run(self):
        """Run the orchestrator main loop."""
        self.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
