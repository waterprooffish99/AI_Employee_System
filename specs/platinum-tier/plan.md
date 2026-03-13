# Platinum Tier: Architecture Plan

## Overview

**Feature**: Platinum Tier Autonomous Employee  
**Version**: 1.0.0  
**Status**: Implementation Plan

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLOUD VM (24/7)                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CLOUD AGENT (Draft-Only)                           │  │
│  │                                                                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│  │  │  Gmail Watcher  │  │ Social Watcher  │  │  Odoo Watcher   │      │  │
│  │  │  (Draft Mode)   │  │  (Draft Mode)   │  │  (Draft Mode)   │      │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │  │
│  │           │                    │                    │                 │  │
│  │           ▼                    ▼                    ▼                 │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              Cloud MCP Servers (Draft-Only)                  │    │  │
│  │  │  - Email: Create drafts only                                 │    │  │
│  │  │  - Social: Create drafts only                                │    │  │
│  │  │  - Odoo: Draft invoices only                                 │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              Cloud Vault Sync (Git/Syncthing)                │    │  │
│  │  │  - Writes to: /Updates/, /Signals/                           │    │  │
│  │  │  - Reads from: /Needs_Action/cloud/, /Pending_Approval/      │    │  │
│  │  │  - NEVER syncs: .env, tokens, sessions, credentials          │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CLOUD INFRASTRUCTURE                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  Odoo 19+    │  │  Health      │  │  Automated   │               │  │
│  │  │  (HTTPS)     │  │  Monitor     │  │  Backups     │               │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Vault Sync (Git/Syncthing)
                                    │ Markdown/State ONLY (No Secrets)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCAL MACHINE                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     LOCAL AGENT (Final Actions)                       │  │
│  │                                                                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│  │  │ WhatsAppWatcher │  │  Bank Watcher   │  │ Approval Handler│      │  │
│  │  │  (Local Only)   │  │  (Local Only)   │  │  (Final Send)   │      │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │  │
│  │           │                    │                    │                 │  │
│  │           ▼                    ▼                    ▼                 │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              Local MCP Servers (Final Actions)               │    │  │
│  │  │  - Email: Send (after approval)                              │    │  │
│  │  │  - Social: Post (after approval)                             │    │  │
│  │  │  - Odoo: Post invoices (after approval)                      │    │  │
│  │  │  - WhatsApp: Send messages                                   │    │  │
│  │  │  - Banking: Execute payments                                 │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              Local Vault (Single Writer)                     │    │  │
│  │  │  - Dashboard.md (Local only)                                 │    │  │
│  │  │  - /Approved/ → Execute                                      │    │  │
│  │  │  - /Rejected/ → Archive                                      │    │  │
│  │  │  - /Done/ → Complete                                         │    │  │
│  │  │  - Secrets: .env, tokens, sessions (NEVER sync)              │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Cloud/Local Division

### Cloud Agent Responsibilities

**Draft-Only Operations**:
1. **Email Triage**:
   - Monitor Gmail via watcher
   - Create draft replies
   - Write to `/Updates/email_drafts/`
   - Local approves and sends

2. **Social Media**:
   - Monitor mentions/engagement
   - Create draft posts
   - Write to `/Updates/social_drafts/`
   - Local approves and posts

3. **Odoo Accounting**:
   - Monitor transactions
   - Draft invoices
   - Draft payment entries
   - Local approves and posts

4. **Health Monitoring**:
   - Monitor own health
   - Report to `/Updates/health/`
   - Auto-restart on failure

### Local Agent Responsibilities

**Final Action Operations**:
1. **Approvals**:
   - Review cloud drafts
   - Approve/reject via file movement
   - Log all decisions

2. **WhatsApp**:
   - Maintain WhatsApp session
   - Send/receive messages
   - NEVER sync session data

3. **Banking/Payments**:
   - Execute approved payments
   - Monitor bank accounts
   - NEVER sync credentials

4. **Dashboard**:
   - Single writer for Dashboard.md
   - Merge cloud updates
   - Display unified view

5. **Final Send/Post**:
   - Execute email sends
   - Execute social posts
   - Execute Odoo postings

## Vault Sync Strategy

### Phase 1: File-Based Sync

**Git Sync (Recommended)**:
```bash
# Cloud pushes to remote
git add .
git commit -m "Cloud updates"
git push origin main

# Local pulls from remote
git pull origin main
git merge --strategy-option=theirs
```

**Syncthing Sync (Alternative)**:
- Real-time sync
- Conflict detection
- Version history

### Sync Rules

**Synced**:
- `*.md` files
- `*.json` state files
- `/Plans/`, `/Needs_Action/`, `/Done/`
- `/Updates/`, `/Signals/`

**NEVER Synced**:
- `.env` files
- `*.token` files
- `sessions/` directories
- `credentials/` directories
- `*.key`, `*.pem`, `*.crt`

### Claim-by-Move Rule

```
/Needs_Action/
  ├── email_123.md          # Unclaimed - any agent can process
  └── social_456.md         # Unclaimed - any agent can process

/In_Progress/
  ├── cloud/                # Cloud-owned items
  │   └── email_123.md      # Cloud moved here - owns it
  └── local/                # Local-owned items
      └── social_456.md     # Local moved here - owns it
```

**Rule**: First agent to move item from `/Needs_Action/` to `/In_Progress/<agent>/` owns it. Other agents must ignore.

## Health Monitoring

### Cloud Health Checks

```python
# Health check endpoint
GET /health
{
  "status": "healthy",
  "uptime": "72h 15m",
  "watchers": {
    "gmail": "running",
    "social": "running",
    "odoo": "running"
  },
  "last_sync": "2026-01-07T10:00:00Z"
}
```

### Auto-Recovery

1. **Watcher Crash**: Auto-restart within 30 seconds
2. **Orchestrator Crash**: Systemd restart
3. **Odoo Crash**: Auto-restart + notify
4. **Sync Failure**: Retry with backoff, alert on persistent failure

## Security Architecture

### Secret Management

**Cloud Secrets** (stored on cloud VM):
- Gmail OAuth tokens
- Social media API tokens
- Odoo API credentials
- Cloud database credentials

**Local Secrets** (stored on local machine ONLY):
- WhatsApp session data
- Personal banking credentials
- Payment tokens
- Local OAuth tokens

**Never Stored**:
- Secrets in git repository
- Secrets in sync folder
- Secrets in logs

### Network Security

**Cloud VM**:
- Firewall: Only required ports open
- HTTPS for Odoo
- SSH key-only access
- Regular security updates

**Local Machine**:
- Firewall for incoming connections
- Encrypted sync (Git SSH or Syncthing TLS)
- Local-only WhatsApp session

## Deployment

### Cloud VM Setup (Oracle Cloud Free Tier)

**VM Specifications**:
- 4 OCPU, 24GB RAM (ARM Ampere)
- 200GB storage
- Ubuntu 22.04 LTS

**Installation Steps**:
1. Create Oracle Cloud account
2. Launch Ubuntu 22.04 VM
3. Configure firewall (SSH, HTTPS)
4. Install Docker + Docker Compose
5. Deploy Odoo via Docker
6. Clone AI Employee repository
7. Configure environment
8. Set up systemd services
9. Configure Git sync
10. Test health monitoring

### Local Setup

**Requirements**:
- Python 3.13+
- Obsidian
- Claude Code
- Git
- (Optional) Syncthing

**Configuration**:
1. Clone repository
2. Configure `.env` (local secrets)
3. Set up Git remote
4. Configure sync schedule
5. Test approval workflow

## Testing Strategy

### Integration Tests

1. **Cloud→Local Sync**:
   - Cloud writes to `/Updates/`
   - Local receives via sync
   - Local merges to Dashboard.md

2. **Claim-by-Move**:
   - Cloud moves item to `/In_Progress/cloud/`
   - Local ignores claimed item
   - Verify no double-processing

3. **Approval Workflow**:
   - Cloud creates draft
   - Local approves
   - Local executes
   - Both log action

### Platinum Demo Test

**Scenario**: Email arrives while Local offline

1. Local machine offline
2. Email arrives
3. Cloud detects via Gmail Watcher
4. Cloud creates draft reply
5. Cloud writes to `/Pending_Approval/cloud/email_123.md`
6. Cloud syncs to remote
7. Local comes online
8. Local syncs from remote
9. User sees approval request
10. User approves (moves to `/Approved/`)
11. Local executes send via Email MCP
12. Local logs action
13. Local moves to `/Done/`
14. Sync propagates completion to cloud

**Success Criteria**:
- Email replied to successfully
- No data loss during offline period
- Sync resolves correctly
- Audit trail complete

## Migration from Gold Tier

### Phase 1: Cloud Setup
1. Deploy cloud VM
2. Install Odoo
3. Configure cloud agent (draft-only)

### Phase 2: Sync Setup
1. Set up Git remote
2. Configure sync rules
3. Test sync (no production data)

### Phase 3: Work-Zone Split
1. Modify cloud agent to draft-only
2. Modify local agent for approvals
3. Test approval workflow

### Phase 4: Production Cutover
1. Migrate watchers to cloud
2. Enable health monitoring
3. Monitor for 48 hours
4. Decommission old setup (if applicable)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sync conflicts | Medium | Git merge strategy, manual resolution process |
| Secret leakage | High | Strict .gitignore, secret scanning, audit logs |
| Cloud downtime | Medium | Local can operate standalone, auto-restart |
| Double-processing | Medium | Claim-by-move rule, state files |
| Approval bottleneck | Low | User notification, escalation process |

## Success Metrics

- **Uptime**: > 99% cloud availability
- **Sync Latency**: < 5 minutes cloud→local
- **Approval Response**: < 4 hours average
- **Zero Secret Leaks**: No secrets in git/sync
- **Platinum Demo Pass**: Scenario completes successfully

---

*Document Version: 1.0.0 | Platinum Tier*
