# Skill: Update Dashboard

**Purpose**: Keep the Dashboard.md current with system status and recent activity.

## Trigger
After any significant action or state change.

## Instructions

1. **Read** current `/Dashboard.md`

2. **Update** the following sections:
   - **Last Updated**: Current timestamp
   - **System Status**: Idle, Processing, Awaiting Approval, Executing
   - **Last Action Taken**: Brief description of what just happened
   - **Pending Approvals**: List items in `/Pending_Approval/`
   - **Recent Activity**: Add new entry to the activity table

3. **Write** updated content to `/Dashboard.md`

## Dashboard Format
```markdown
# AI Employee Dashboard

**Last Updated**: YYYY-MM-DD HH:MM:SS

## System Status
<Idle | Processing | Awaiting Approval | Executing>

## Last Action Taken
<Brief description>

## Pending Approvals
*List or "No pending approvals"*

## Recent Activity
| Timestamp | Action | Status |
|-----------|--------|--------|
| ... | ... | ... |
```

## Rules
- Keep it concise
- Always include timestamp
- Maintain the table format for activity
