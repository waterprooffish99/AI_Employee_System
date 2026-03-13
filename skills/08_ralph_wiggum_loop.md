# Ralph Wiggum Loop - Agent Skill for Autonomous Task Completion

## Overview

The Ralph Wiggum Loop enables autonomous multi-step task completion by intercepting Claude's exit attempts and re-injecting prompts until tasks are complete.

## When to Use

Use this skill when:
- Task requires multiple iterations to complete
- You want Claude to work autonomously until done
- Task has clear completion criteria
- You need state persistence across iterations

## How It Works

1. **State Initialization**: Creates state file in `/Plans/{task_id}_state.json`
2. **Work Iteration**: Claude works on task
3. **Exit Attempt**: Claude tries to exit
4. **Completion Check**: Stop hook checks if complete
5. **Re-injection**: If incomplete, prompt is re-injected
6. **Repeat**: Until complete or max iterations

## Usage

### Starting a Ralph Loop

```bash
# Via CLI
python -m src.utils.ralph_loop --task-id TASK_ID --prompt "Your task here"

# Or manually
1. Create task file in /Needs_Action/
2. Claude processes it
3. Ralph loop continues until done
```

### Completion Markers

Signal task completion with:
- `<promise>TASK_COMPLETE</promise>`
- `[TASK COMPLETE]`
- `✅ COMPLETE`
- Move task file to `/Done/`

### State File Structure

```json
{
  "task_id": "TASK_001",
  "prompt": "Original task prompt",
  "iteration": 3,
  "start_time": "2026-01-07T10:00:00",
  "last_updated": "2026-01-07T10:15:00",
  "status": "in_progress",
  "iterations": [
    {"number": 1, "timestamp": "...", "output_length": 1024},
    {"number": 2, "timestamp": "...", "output_length": 2048},
    {"number": 3, "timestamp": "...", "output_length": 1536}
  ]
}
```

## Configuration

Environment variables:
- `RALPH_MAX_ITERATIONS`: Maximum iterations (default: 10)
- `RALPH_TIMEOUT_SECONDS`: Loop timeout (default: 3600)

## Examples

### Example 1: Process Multiple Files

```
Task: Process all files in /Needs_Action
- Read each file
- Take appropriate action
- Move to /Done when complete
<promise>TASK_COMPLETE</promise>
```

### Example 2: Multi-Step Analysis

```
Task: Analyze business performance
1. Read Dashboard.md
2. Check Accounting folder
3. Review Social_Media metrics
4. Generate summary report
5. Save to CEO_Briefings/
✅ COMPLETE
```

### Example 3: Data Synchronization

```
Task: Sync Odoo invoices with local records
- Fetch invoices from Odoo
- Compare with local records
- Update discrepancies
- Log changes
[TASK COMPLETE]
```

## Best Practices

1. **Clear Completion Criteria**: Define what "done" looks like
2. **Progressive Output**: Show progress in each iteration
3. **State Updates**: Update state file with progress
4. **Error Handling**: Move to /Error/ if failed
5. **Iteration Limits**: Set reasonable max iterations

## Error Recovery

If loop fails:
1. Check state file in `/Plans/{task_id}_state.json`
2. Review last output in `/Plans/{task_id}_last_output.txt`
3. Check `/Error/` folder for error details
4. Manually move to `/Done/` if appropriate

## Integration

Works with:
- All Agent Skills
- MCP servers
- Watchers
- CEO Briefing generator

## Troubleshooting

**Loop won't stop**: Ensure completion marker is output
**State not updating**: Check file permissions
**Max iterations reached**: Task may need refinement

---

*Skill Version: 1.0.0 | Gold Tier*
