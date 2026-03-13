# Ralph Wiggum Loop - Gold Tier Autonomous Execution

## Overview

The **Ralph Wiggum Loop** is an autonomous task execution system that keeps working until a task is complete. It's called "Ralph Wiggum" because it never gives up - it keeps iterating until the job is done!

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. Read task from Needs_Action/task_name.md                │
│  2. Call LLM (Claude/Gemini) to process task               │
│  3. Check: Did output contain <promise>COMPLETED</promise>? │
│     ├─ YES → Move task to Done/, exit successfully          │
│     └─ NO → Re-inject prompt, go back to step 2             │
│  4. Repeat until complete or max iterations reached         │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Use the Bash Script (Easiest)

```bash
# Basic usage
bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files

# With custom max iterations
bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files --max-iterations 5

# Test without calling LLM (dry run)
bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files --dry-run

# Use Gemini instead of Claude
bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files --model gemini

# Verbose output
bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files --verbose
```

### Option 2: Use UV Directly

```bash
# Basic usage
uv run python -m src.utils.ralph_wiggum_cli --task process_all_files

# With options
uv run python -m src.utils.ralph_wiggum_cli \
  --task process_all_files \
  --max-iterations 5 \
  --model claude \
  --dry-run
```

### Option 3: Use Python Directly (if venv is activated)

```bash
# Activate venv first
source .venv/bin/activate

# Then run
python -m src.utils.ralph_wiggum_cli --task process_all_files
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--task <id>` | **Required.** Task ID (filename without .md) | - |
| `--max-iterations <n>` | Maximum loop iterations | 10 |
| `--model <name>` | LLM model: `claude` or `gemini` | `claude` |
| `--dry-run` | Test without calling LLM API | `false` |
| `--verbose` | Enable debug logging | `false` |
| `--help` | Show help message | - |

## Task File Format

Create your task file in `AI_Employee_Vault/Needs_Action/`:

```markdown
---
task: process_all_files
priority: high
---
# Task: Process Drop Folder

Move all files from the AI_Employee_Vault/Drop/ folder to the AI_Employee_Vault/Done/ folder.

## Success Criteria
- [ ] Move file1.txt to AI_Employee_Vault/Done/
- [ ] Move file2.txt to AI_Employee_Vault/Done/
- [ ] Move file3.txt to AI_Employee_Vault/Done/

When finished, output: <promise>COMPLETED</promise>
```

**Important**: The task file **MUST** include the completion promise instruction:
```
When finished, output: <promise>COMPLETED</promise>
```

## Completion Detection

The loop detects completion in these ways:

### 1. XML-Style Promise (Recommended)
```
<promise>COMPLETED</promise>
<promise>TASK_COMPLETE</promise>
<promise>DONE</promise>
```

### 2. Text Markers
```
COMPLETED
TASK_COMPLETE
[TASK COMPLETE]
✓ COMPLETE
✅ COMPLETE
Task completed successfully
```

### 3. File Movement
If the task file is moved to `/Done/` folder, the loop considers it complete.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VAULT_PATH` | Path to Obsidian vault | `./AI_Employee_Vault` |
| `LLM_MODEL` | Default LLM model | `claude` |
| `GEMINI_API_KEY` | Gemini API key (if using gemini) | - |
| `RALPH_MAX_ITERATIONS` | Override max iterations | 10 |
| `RALPH_TIMEOUT_SECONDS` | Loop timeout in seconds | 3600 |

## Examples

### Example 1: Process Files

**Task file**: `Needs_Action/process_files.md`

```markdown
---
task: process_files
priority: high
---
# Process All Files in Drop Folder

1. List all files in AI_Employee_Vault/Drop/
2. For each file:
   - Read the content
   - Create a summary note in Needs_Action/
   - Move the file to Done/
3. When all files are processed, output: <promise>COMPLETED</promise>
```

**Run**:
```bash
uv run python -m src.utils.ralph_wiggum_cli --task process_files
```

### Example 2: Create Invoices

**Task file**: `Needs_Action/create_invoices.md`

```markdown
---
task: create_invoices
priority: high
---
# Create Invoices for All Clients

1. Read AI_Employee_Vault/Accounting/unbilled_work.md
2. For each client:
   - Create an invoice in Odoo
   - Save invoice PDF to Accounting/Invoices/
   - Log the invoice in Accounting/ledger.md
3. Send summary email to accountant
4. Output: <promise>COMPLETED</promise>
```

**Run**:
```bash
uv run python -m src.utils.ralph_wiggum_cli --task create_invoices --max-iterations 15
```

### Example 3: Social Media Campaign

**Task file**: `Needs_Action/social_campaign.md`

```markdown
---
task: social_campaign
priority: medium
---
# Create and Post Social Media Campaign

1. Read AI_Employee_Vault/Business_Goals.md for campaign theme
2. Create posts for each platform:
   - Facebook: Long form with link
   - Instagram: Image + caption
   - Twitter: Thread with hashtags
   - LinkedIn: Professional update
3. Save drafts to Pending_Approval/
4. After approval, post to all platforms
5. Output: <promise>COMPLETED</promise>
```

**Run**:
```bash
uv run python -m src.utils.ralph_wiggum_cli --task social_campaign --model claude
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'src'"

**Solution**: Install the package in development mode:
```bash
uv pip install -e .
```

### Problem: "Claude CLI not found"

**Solution**: Install Claude Code CLI:
```bash
npm install -g @anthropic/claude-code
```

Or switch to Gemini:
```bash
uv run python -m src.utils.ralph_wiggum_cli --task my_task --model gemini
```

### Problem: "GEMINI_API_KEY not set"

**Solution**: Set the API key in `.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

### Problem: Loop exits immediately without processing

**Possible causes**:
1. Task file not found in `Needs_Action/`
2. Task file already moved to `Done/`
3. Max iterations set too low

**Solution**:
```bash
# Check if task file exists
ls -la AI_Employee_Vault/Needs_Action/

# Increase max iterations
uv run python -m src.utils.ralph_wiggum_cli --task my_task --max-iterations 20
```

### Problem: Loop keeps running without completing

**Possible causes**:
1. LLM not outputting completion promise
2. Task too complex for single iteration

**Solutions**:
- Add clearer completion criteria to task file
- Break task into smaller subtasks
- Increase max iterations
- Check LLM output in `Plans/{task_id}_last_output.txt`

## State Files

The Ralph Loop creates these files for tracking:

| File | Purpose |
|------|---------|
| `Plans/{task_id}_state.json` | Loop state and iteration history |
| `Plans/{task_id}_last_output.txt` | Last LLM output |
| `Done/{task_id}.md` | Task file after completion |

## Best Practices

### 1. Clear Completion Criteria
Always specify exactly what "done" looks like:
```markdown
## Success Criteria
- [ ] File moved to Done/
- [ ] Summary written to Dashboard.md
- [ ] Email sent to stakeholder

When all criteria met, output: <promise>COMPLETED</promise>
```

### 2. Reasonable Max Iterations
- Simple tasks: 3-5 iterations
- Medium tasks: 5-10 iterations
- Complex tasks: 10-20 iterations

### 3. Monitor Progress
Check the state file during long runs:
```bash
cat AI_Employee_Vault/Plans/{task_id}_state.json | jq
```

### 4. Use Dry Run for Testing
Always test with `--dry-run` first:
```bash
uv run python -m src.utils.ralph_wiggum_cli --task my_task --dry-run
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ralph Wiggum CLI                         │
│  (src/utils/ralph_wiggum_cli.py)                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Loop Manager   │  │   LLM Caller    │                   │
│  │  (state track)  │  │ (Claude/Gemini) │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
│           └──────────┬─────────┘                             │
│                      │                                       │
│           ┌──────────▼──────────┐                           │
│           │ Completion Checker  │                           │
│           └──────────┬──────────┘                           │
│                      │                                       │
│           ┌──────────▼──────────┐                           │
│           │  File Mover (Done)  │                           │
│           └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

## Related Files

- `src/utils/ralph_loop.py` - Loop manager class (state tracking, completion detection)
- `src/utils/ralph_wiggum_cli.py` - CLI entry point (this file)
- `.specify/scripts/bash/run_ralph_loop.sh` - Bash wrapper script
- `skills/08_ralph_wiggum_loop.md` - Agent Skill documentation

## Next Steps

After mastering the Ralph Wiggum Loop:
1. Try the **CEO Briefing** generator
2. Set up **Odoo Accounting** integration
3. Configure **Social Media** auto-posting
4. Implement **Error Recovery** workflows

---

*Ralph Wiggum Loop - Because good enough isn't good enough!*
