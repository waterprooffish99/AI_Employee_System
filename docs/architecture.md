# Gold Tier Architecture Documentation

## Overview

This document describes the architecture of the AI Employee System - Gold Tier, an autonomous FTE (Full-Time Equivalent) that manages personal and business affairs 24/7.

## System Architecture

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
│  Skills: 01-12 (Process, Dashboard, Approval, Execute, Log, Plan,   │
│         HITL, Ralph Wiggum, CEO Briefing, Social, Odoo, Recovery)   │
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

## Components

### 1. Perception Layer (Watchers)

**Purpose**: Monitor external systems for changes and triggers.

**Components**:
- `GmailWatcher`: Monitors Gmail for new important emails
- `WhatsAppWatcher`: Monitors WhatsApp for urgent messages
- `FileSystemWatcher`: Watches drop folders for new files
- `SocialWatcher`: Monitors social media for mentions

**Pattern**: All watchers inherit from `BaseWatcher` and follow the same structure:
```python
class BaseWatcher:
    def check_for_updates() -> list
    def create_action_file(item) -> Path
    def run()  # Main loop
```

### 2. Memory Layer (Obsidian Vault)

**Purpose**: Long-term memory and user interface.

**Structure**:
```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status
├── Company_Handbook.md       # Rules and guidelines
├── Business_Goals.md         # Objectives and metrics
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring attention
├── Plans/                    # Execution plans + state files
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved for execution
├── Rejected/                 # Rejected items
├── Done/                     # Completed tasks
├── Accounting/               # Financial records
├── Social_Media/             # Social media content
├── Audit_Logs/               # System logs
├── CEO_Briefings/            # Weekly reports
└── Error_Recovery/           # Error state files
```

### 3. Reasoning Layer (Claude Code + Agent Skills)

**Purpose**: Decision making and task execution.

**Agent Skills**:
1. `01_process_needs_action.md` - Process incoming items
2. `02_update_dashboard.md` - Update dashboard metrics
3. `03_request_approval.md` - Request human approval
4. `04_execute_approved.md` - Execute approved actions
5. `05_log_events.md` - Audit logging
6. `06_create_plan.md` - Create execution plans
7. `07_execute_approved_hitl.md` - HITL workflow
8. `08_ralph_wiggum_loop.md` - Autonomous completion
9. `09_ceo_briefing.md` - Weekly audits
10. `10_social_media_manager.md` - Social media ops
11. `11_odoo_accounting.md` - Accounting operations
12. `12_error_recovery.md` - Error handling

### 4. Action Layer (MCP Servers)

**Purpose**: Execute actions on external systems.

**MCP Servers**:
- `email_mcp.py`: Gmail API integration
- `linkedin_poster.py`: LinkedIn posting
- `facebook_mcp.py`: Facebook Graph API
- `instagram_mcp.py`: Instagram Graph API
- `twitter_mcp.py`: Twitter API v2
- `odoo_mcp.py`: Odoo JSON-RPC (accounting)
- `social_media_manager.py`: Unified social interface

### 5. Audit & Recovery Layer

**Purpose**: Reliability and compliance.

**Components**:
- `audit_logger.py`: Comprehensive logging
- `error_handler.py`: Error categorization
- `retry_manager.py`: Exponential backoff
- `ralph_loop.py`: State persistence

## Data Flow

### Standard Task Flow

1. **Trigger**: Watcher detects change → Creates file in `/Needs_Action/`
2. **Process**: Claude reads skill → Creates plan in `/Plans/`
3. **Approve**: Plan moved to `/Pending_Approval/` → User reviews
4. **Execute**: User moves to `/Approved/` → MCP executes
5. **Complete**: File moved to `/Done/` → Logged to audit

### Ralph Wiggum Loop Flow

1. **Initialize**: State file created in `/Plans/{task_id}_state.json`
2. **Work**: Claude processes task
3. **Check**: Stop hook checks completion
4. **Continue**: If incomplete → Re-inject prompt
5. **Complete**: Move to `/Done/` or output completion promise

### CEO Briefing Flow

1. **Schedule**: Cron triggers every Monday 8 AM
2. **Gather**: Collect data from Odoo, social media, vault
3. **Analyze**: Calculate metrics, identify bottlenecks
4. **Generate**: Create markdown report
5. **Save**: Store in `/CEO_Briefings/`

## Security Architecture

### Credential Management

- All credentials in `.env` (never committed)
- Environment variables only
- No credentials in logs
- Regular rotation policy

### Sandboxing

- `DRY_RUN=true` by default
- All actions logged before execution
- Rate limiting on all APIs
- Approval required for sensitive actions

### Audit Trail

- Every action logged with full context
- Immutable log entries
- 90-day retention
- Searchable interface

## Error Handling

### Categories

| Category | Action | Notify |
|----------|--------|--------|
| Transient | Retry | No |
| Authentication | Refresh credentials | Yes |
| Rate Limit | Backoff and queue | No |
| Validation | Log and skip | No |
| Critical | Stop and alert | Yes |

### Retry Strategy

- Max retries: 3
- Backoff: Exponential (2^n seconds)
- Jitter: ±100% random
- Max delay: 60 seconds

## Configuration

### Environment Variables

```bash
# Core
DRY_RUN=true
LOG_LEVEL=INFO

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_API_KEY=your_key

# Social Media
FACEBOOK_APP_ID=your_id
FACEBOOK_APP_SECRET=your_secret
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_id
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret

# Retry
MAX_RETRIES=3
RETRY_BACKOFF_BASE=2

# Ralph Wiggum
RALPH_MAX_ITERATIONS=10
RALPH_TIMEOUT_SECONDS=3600
```

## Deployment

### Local Deployment

1. Install dependencies: `uv sync`
2. Configure `.env`
3. Set up OAuth credentials
4. Start watchers
5. Run orchestrator

### Odoo Setup

1. Install Odoo Community 19+
2. Configure database
3. Set up chart of accounts
4. Generate API key
5. Test connection

### Social Media Setup

1. Create Facebook Developer App
2. Convert Instagram to Business
3. Create Twitter Developer Account
4. Configure OAuth
5. Test each platform

## Performance Budgets

| Operation | Target |
|-----------|--------|
| Watcher check interval | 1-2 min |
| CEO Briefing generation | < 30 sec |
| Social media post | < 5 sec |
| Odoo invoice creation | < 10 sec |
| Dashboard update | < 2 sec |

## Monitoring

### Metrics to Track

- Tasks processed per day
- Average processing time
- Error rate by category
- Approval turnaround time
- API call success rate

### Alerts

- Authentication failures (immediate)
- Critical errors (immediate)
- High error rate (> 10%/hour)
- API rate limits approaching

## Future Enhancements

### Platinum Tier

- Cloud deployment (24/7 operation)
- Work-Zone Specialization
- A2A (Agent-to-Agent) communication
- Vault sync via Git/Syncthing

### Potential Improvements

- Voice interface integration
- Mobile app for approvals
- Advanced analytics dashboard
- Multi-language support
- Custom workflow builder

---

*Document Version: 1.0.0 | Gold Tier*
