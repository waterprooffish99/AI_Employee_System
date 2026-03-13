# Skill: Log Events

**Purpose**: Record all system events for audit and debugging.

## Trigger
On every significant action, decision, or state change.

## Log Format
```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.sssZ",
  "event_type": "<category.action>",
  "actor": "claude_code",
  "data": {
    "key": "value"
  },
  "result": "success|failure|pending"
}
```

## Event Categories

| Category | Actions |
|----------|---------|
| `orchestrator` | started, stopped, new_task_detected, plan_created |
| `plan` | generation_started, generation_completed, generation_failed |
| `approval` | requested, approved, rejected, expired |
| `execution` | started, completed, failed, dry_run |
| `dashboard` | updated, refresh_failed |
| `watcher` | started, stopped, item_detected, error |

## Instructions

1. **Create** log entry with current timestamp

2. **Append** to daily log file: `/Logs/YYYY-MM-DD.json`
   - One JSON object per line (JSONL format)

3. **Include** relevant context in `data` field

## Example
```json
{"timestamp": "2026-03-09T10:30:00.000Z", "event_type": "orchestrator.new_task_detected", "actor": "filesystem_watcher", "data": {"file": "Needs_Action/FILE_20260309_test.md"}, "result": "success"}
```

## Rules
- One entry per line (JSONL format)
- Always include timestamp and event_type
- Use ISO 8601 format for timestamps
- Never log sensitive data (credentials, tokens)
