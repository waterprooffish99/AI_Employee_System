# Skill: Execute Approved Actions

**Purpose**: Process approved actions and move tasks to completion.

## Trigger
When files appear in `/Approved/` folder.

## Instructions

1. **Read** all files in `/Approved/`

2. **For each approved action**:
   - Identify the action type
   - Execute via appropriate MCP server (or dry-run in development)
   - Log the execution result

3. **On successful execution**:
   - Move original task file from `/Needs_Action/` to `/Done/`
   - Move approval file from `/Approved/` to `/Done/`
   - Update Dashboard with completion status

4. **On failure**:
   - Move file to `/Error/`
   - Log the error details
   - Update Dashboard with error status

## Execution Flow
```
/Approved/action.md → Execute (MCP or dry-run) → Success → /Done/
                                          ↓
                                      Failure → /Error/
```

## Rules
- Always log execution attempts
- Never execute actions that weren't approved
- Clean up related files on completion
- Report failures to Dashboard
