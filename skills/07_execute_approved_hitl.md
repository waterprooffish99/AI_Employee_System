# Skill: Execute Approved Actions (HITL)

**Purpose**: Execute approved actions via MCP servers.

**Silver Tier Requirement**: Human-in-the-loop approval workflow

---

## Trigger
When files appear in `/Approved/` folder

---

## Approval Workflow

### Before Approval (Pending)
1. Task detected in `/Needs_Action/`
2. Claude creates Plan.md in `/Plans/`
3. Plan moved to `/Pending_Approval/`
4. Human reviews plan

### Approval Process
```
/Pending_Approval/  → Human moves to →  /Approved/  → Orchestrator executes
```

### After Approval
1. Orchestrator detects file in `/Approved/`
2. Determines action type from file metadata
3. Executes via appropriate MCP server
4. Logs result
5. Moves file to `/Done/`

---

## Action Types and MCP Servers

| Action Type | MCP Server | Method |
|-------------|------------|--------|
| `email_send` | Email MCP | `execute_approved_send()` |
| `linkedin_post` | LinkedIn Poster | `post_to_linkedin()` |
| `payment` | (Future) Payment MCP | TBD |
| `file_operation` | Built-in | `shutil.move()` |

---

## Execution Process

### 1. Read Approval File
```python
content = approved_file.read_text()
```

### 2. Parse Metadata
Extract from YAML frontmatter:
- `type`: Action type
- `to`, `subject`, `body`: Action parameters
- `status`: Should be `pending_approval`

### 3. Execute via MCP
```python
if action_type == 'email_send':
    from src.mcp.email_mcp import EmailMCP
    mcp = EmailMCP(vault_path)
    success = mcp.execute_approved_send(approved_file)
    
elif action_type == 'linkedin_post':
    from src.mcp.linkedin_poster import LinkedInPoster
    poster = LinkedInPoster(vault_path)
    success = poster.post_to_linkedin(approved_file)
```

### 4. Handle Result
**Success**:
- Log event: `execution.completed`
- Move file to `/Done/`
- Update Dashboard: "Task Complete"

**Failure**:
- Log event: `execution.failed`
- Move file to `/Error/`
- Update Dashboard: "Execution Failed"

---

## Safety Rules

### Never Execute Without Approval
- Always check file is in `/Approved/`
- Never execute files from `/Pending_Approval/`
- Never execute files from `/Needs_Action/`

### Validate Before Execution
- Check required fields present
- Validate email addresses
- Validate amounts for payments
- Check approval not expired

### Rate Limiting
- Max 10 emails per hour
- Max 3 payments per hour
- Max 5 LinkedIn posts per day

---

## Error Handling

### Common Errors
| Error | Action |
|-------|--------|
| MCP not authenticated | Log error, move to /Error/, alert user |
| API rate limit | Retry with backoff, max 3 attempts |
| Invalid parameters | Log error, move to /Error/ |
| Network timeout | Retry once, then fail |

### Error Recovery
```python
if not success:
    # Move to Error directory
    error_file = ERROR_DIR / approved_file.name
    shutil.move(str(approved_file), str(error_file))
    
    # Log detailed error
    log_event("execution.failed", {
        "file": str(approved_file),
        "error": error_message
    })
    
    # Update dashboard
    update_dashboard("Execution Failed", f"Error: {error_message}")
```

---

## Logging Format

```json
{
  "timestamp": "2026-03-09T10:30:00Z",
  "event_type": "execution.completed",
  "actor": "orchestrator",
  "data": {
    "action_type": "email_send",
    "approved_file": "EMAIL_SEND_Invoice_20260309.md",
    "recipient": "client@example.com",
    "mcp_server": "email_mcp"
  },
  "result": "success"
}
```

---

## Example Flow

### Email Send Example

**1. Approval File Created** (by Email MCP):
```markdown
---
type: email_send
to: client@example.com
subject: Invoice #123
created: 2026-03-09T10:00:00Z
status: pending_approval
---

# Email Send Request
...
```

**2. Human Approves**:
- User moves file from `/Pending_Approval/` to `/Approved/`

**3. Orchestrator Detects**:
```
on_created: /Approved/EMAIL_SEND_Invoice_20260309.md
```

**4. Execution**:
```python
mcp = EmailMCP(vault_path)
success = mcp.execute_approved_send(approved_file)
# Email sent via Gmail API
```

**5. Completion**:
- File moved to `/Done/`
- Dashboard updated
- Event logged

---

*Skill for AI Employee System - Silver Tier*
