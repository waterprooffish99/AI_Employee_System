# Gold Tier: Autonomous Employee - Architecture Plan

## Overview

**Feature**: Gold Tier Autonomous Employee  
**Version**: 1.0.0  
**Status**: Implementation Plan

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SYSTEMS                                │
│  Gmail  │  WhatsApp  │  LinkedIn  │  Facebook  │  Instagram  │  X   │
│  Odoo ERP (Accounting) │  Bank APIs  │  Payment Processors         │
└─────────┬──────┬──────┬──────┬───────┬───────┬──────┬────────┬──────┘
          │      │      │      │       │       │      │        │
          ▼      ▼      ▼      ▼       ▼       ▼      ▼        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PERCEPTION LAYER (Watchers)                         │
│  GmailWatcher │ WhatsAppWatcher │ FileSystemWatcher │ SocialWatcher │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Memory/GUI)                       │
│  Dashboard.md (Personal + Business)                                  │
│  Company_Handbook.md | Business_Goals.md                             │
│  /Needs_Action | /Plans | /Pending_Approval | /Approved | /Done     │
│  /Accounting | /Social_Media | /Audit_Logs | /CEO_Briefings         │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              REASONING LAYER (Claude Code + Agent Skills)            │
│  Skills: 01-08 (Process, Dashboard, Approval, Execute, Log, Plan,   │
│         HITL, Ralph Wiggum Loop, CEO Briefing, Social Media, Audit) │
└────────────────────────┬────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼                             ▼
┌─────────────────────┐       ┌─────────────────────┐
│   HUMAN-IN-THE-LOOP │       │    ACTION LAYER     │
│   Approval Workflow │       │     (MCP Servers)   │
│   /Pending_Approval │       │  ┌──────┐ ┌──────┐  │
│   → /Approved       │       │  │Email │ │Social│  │
│   → /Rejected       │       │  │ MCP  │ │ MCPs │  │
└─────────────────────┘       │  └──────┘ └──────┘  │
                              │  ┌──────┐ ┌──────┐  │
                              │  │Odoo  │ │Twitter│ │
                              │  │ MCP  │ │ MCP  │  │
                              │  └──────┘ └──────┘  │
                              └──────────┬──────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  AUDIT & RECOVERY LAYER                              │
│  AuditLogger | ErrorHandler | RetryManager | GracefulDegradation   │
└─────────────────────────────────────────────────────────────────────┘
```

## MCP Servers

### 1. Email MCP (Existing - Enhanced)
- Send/receive emails via Gmail API
- Draft mode with approval workflow
- Attachment handling

### 2. LinkedIn MCP (Existing - Enhanced)
- Post business updates
- Generate engagement reports
- Connection management

### 3. Facebook MCP (NEW)
- Post to Facebook pages
- Generate engagement summaries
- Monitor comments/messages
- Schedule posts

### 4. Instagram MCP (NEW)
- Post images with captions
- Story posting
- Engagement metrics
- Hashtag optimization

### 5. Twitter/X MCP (NEW)
- Post tweets
- Thread creation
- Analytics and summaries
- Monitor mentions/replies

### 6. Odoo MCP (NEW)
- JSON-RPC API integration (Odoo 19+)
- Invoice creation and sending
- Payment tracking
- Financial reports (P&L, Balance Sheet)
- Customer/Vendor management
- Bank reconciliation
- Chart of accounts

## Agent Skills

### Existing Skills (Enhanced)
1. **01_process_needs_action.md** - Process items from Needs_Action folder
2. **02_update_dashboard.md** - Update Dashboard with cross-domain metrics
3. **03_request_approval.md** - Request human approval for actions
4. **04_execute_approved.md** - Execute approved actions
5. **05_log_events.md** - Comprehensive audit logging
6. **06_create_plan.md** - Create detailed execution plans
7. **07_execute_approved_hitl.md** - HITL workflow execution

### New Skills (Gold Tier)
8. **08_ralph_wiggum_loop.md** - Autonomous multi-step task completion
9. **09_ceo_briefing.md** - Weekly business and accounting audit
10. **10_social_media_manager.md** - Cross-platform social media management
11. **11_odoo_accounting.md** - Odoo accounting operations
12. **12_error_recovery.md** - Error handling and graceful degradation

## Data Model

### Dashboard.md Schema
```yaml
---
last_updated: ISO8601
personal:
  email_unread: number
  whatsapp_pending: number
  bank_balance: number
business:
  revenue_mtd: number
  revenue_wtd: number
  outstanding_invoices: number
  social_media:
    linkedin_followers: number
    facebook_engagement: number
    instagram_followers: number
    twitter_followers: number
  bottlenecks: array
tasks:
  pending: number
  in_progress: number
  awaiting_approval: number
---
```

### CEO Briefing Schema
```yaml
---
generated: ISO8601
period_start: DATE
period_end: DATE
---

# CEO Briefing: {period}

## Executive Summary
## Revenue Analysis
## Expense Analysis
## Profit & Loss
## Cash Flow
## Outstanding Invoices
## Upcoming Payments
## Social Media Performance
## Bottlenecks
## Recommendations
```

### Audit Log Schema
```json
{
  "timestamp": "ISO8601",
  "action_type": "string",
  "actor": "string",
  "target": "string",
  "parameters": {},
  "approval_status": "pending|approved|rejected",
  "approved_by": "string|null",
  "result": "success|failure",
  "error": "string|null",
  "retry_count": "number"
}
```

## Error Handling Strategy

### Error Categories
1. **Transient Errors** - Retry with exponential backoff
2. **Authentication Errors** - Notify user, pause operations
3. **Rate Limit Errors** - Backoff and queue
4. **Validation Errors** - Log and skip
5. **Critical Errors** - Stop and alert

### Retry Policy
- Max retries: 3
- Backoff: exponential (1s, 2s, 4s, 8s)
- Jitter: random 0-1s

### Graceful Degradation
- If Odoo unavailable: log transactions locally, sync later
- If social media API fails: queue posts, retry later
- If email fails: save draft locally

## Ralph Wiggum Loop Implementation

### Stop Hook Pattern
```python
# .claude/plugins/ralph-wiggum/stop-hook.py
def should_stop():
    # Check if task file moved to /Done
    # Check max iterations
    # Check completion promise in output
```

### State Persistence
- Task state in `/Plans/{task_id}_state.md`
- Iteration count tracked
- Previous output preserved

## Security Architecture

### Credential Management
- All credentials in `.env` (gitignored)
- Use environment variables
- Secrets manager for production (optional)

### Sandboxing
- DRY_RUN=true by default
- All actions logged before execution
- Rate limiting enforced

### Audit Trail
- Immutable logs in `/Logs/`
- Daily log rotation
- 90-day retention (configurable)

## Deployment

### Local Deployment
1. Install dependencies: `uv sync`
2. Configure `.env`
3. Set up OAuth credentials
4. Start watchers
5. Run orchestrator

### Odoo Deployment
1. Install Odoo Community 19+ (Docker or native)
2. Configure database
3. Set up chart of accounts
4. Configure MCP server connection

### Social Media Setup
1. Facebook Developer App
2. Instagram Business Account
3. Twitter Developer Account
4. OAuth configuration

## Testing Strategy

### Unit Tests
- Each watcher tested in isolation
- MCP server mocks
- Error handling tests

### Integration Tests
- End-to-end workflows
- API integration tests
- Odoo JSON-RPC tests

### Manual Tests
- OAuth flow verification
- Human-in-the-loop workflow
- Ralph Wiggum loop behavior

## Performance Budgets

- Watcher check interval: 1-2 minutes
- CEO Briefing generation: < 30 seconds
- Social media post: < 5 seconds
- Odoo invoice creation: < 10 seconds
- Dashboard update: < 2 seconds

## Migration Plan

### From Silver to Gold
1. Add new MCP servers (non-breaking)
2. Add new Agent Skills (non-breaking)
3. Enhance Dashboard schema (backward compatible)
4. Add audit logging (additive)
5. Enable Ralph Wiggum loop (opt-in)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Odoo API changes | High | Version pinning, contract tests |
| Social media API rate limits | Medium | Queue system, backoff |
| Credential exposure | High | Env vars only, no logging |
| Ralph loop infinite | Medium | Max iterations, timeout |
| Audit log growth | Low | Rotation, retention policy |

## Success Metrics

- All 10 Gold Tier requirements implemented
- 100% test coverage on new code
- Zero credential leaks
- < 1% error rate on API calls
- CEO Briefing generated weekly without manual intervention
