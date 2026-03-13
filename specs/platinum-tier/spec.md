# Platinum Tier: Always-On Cloud + Local Executive - Specification

## Overview

**Feature**: Platinum Tier Autonomous Employee
**Tier**: Platinum 💎
**Estimated Time**: 60+ hours
**Status**: Implementation

## Platinum Tier Requirements

All Gold Tier requirements plus:

### 1. Cloud Deployment (24/7 Operation)
- Deploy AI Employee on Cloud VM (Oracle/AWS/GCP)
- Oracle Cloud Free VMs recommended (subject to availability)
- Always-on watchers
- Always-on orchestrator
- Health monitoring
- Auto-restart on failures

### 2. Work-Zone Specialization (Domain Ownership)

**Cloud Agent Owns** (Draft-Only):
- Email triage and draft replies
- Social post drafts and scheduling
- Odoo draft accounting actions
- Requires Local approval before send/post

**Local Agent Owns** (Final Actions):
- Human approvals
- WhatsApp session (privacy-sensitive)
- Payments/banking (security-sensitive)
- Final "send/post" actions
- Dashboard.md single-writer rule

### 3. Delegation via Synced Vault (Phase 1)

**Communication Pattern**:
- Agents communicate by writing files
- Directory structure:
  - `/Needs_Action/<domain>/`
  - `/Plans/<domain>/`
  - `/Pending_Approval/<domain>/`
  - `/In_Progress/<agent>/`
  - `/Updates/` or `/Signals/` (Cloud → Local)

**Conflict Prevention**:
- Claim-by-move rule: First agent to move item from `/Needs_Action` to `/In_Progress/<agent>/` owns it
- Other agents must ignore claimed items
- Single-writer rule for Dashboard.md (Local only)

### 4. Vault Sync (Phase 1)

**Sync Methods**:
- **Git (Recommended)**: Versioned sync, conflict resolution
- **Syncthing**: Real-time sync option

**Security Rules**:
- Vault sync includes ONLY markdown/state files
- Secrets NEVER sync:
  - `.env` files
  - OAuth tokens
  - WhatsApp sessions
  - Banking credentials
  - Payment tokens

### 5. Odoo on Cloud (24/7)

**Deployment Requirements**:
- Deploy Odoo Community on Cloud VM
- HTTPS enabled
- Automated backups
- Health monitoring
- Cloud Agent: Draft-only accounting via MCP
- Local Agent: Approval for posting invoices/payments

### 6. Optional A2A Upgrade (Phase 2)

**Agent-to-Agent Communication**:
- Replace some file handoffs with direct A2A messages
- Keep vault as audit record
- Faster communication for time-sensitive tasks

### 7. Platinum Demo (Minimum Passing Gate)

**Scenario**: Email arrives while Local is offline
1. Cloud detects email via Gmail Watcher
2. Cloud drafts reply (draft-only)
3. Cloud writes approval file to `/Pending_Approval/cloud/`
4. User approves when Local returns
5. Local executes send via MCP
6. Local logs action
7. Task moved to `/Done/`

## Success Criteria

- [ ] Cloud VM deployed and running 24/7
- [ ] Work-zone specialization implemented
- [ ] Vault sync working (Git or Syncthing)
- [ ] Claim-by-move rule enforced
- [ ] Security rules enforced (no secrets sync)
- [ ] Odoo deployed on cloud with HTTPS
- [ ] Cloud/Local agent communication working
- [ ] Platinum demo scenario passes
- [ ] Health monitoring operational
- [ ] All Gold Tier features still functional

## Non-Goals

- Mobile app development
- Custom UI beyond Obsidian
- Real-time collaboration beyond sync
- Multi-user support (single user only)

## Security Considerations

### Critical Security Rules

1. **Secrets Never Sync**:
   - `.env` files stay local
   - OAuth tokens stay local
   - WhatsApp sessions stay local
   - Banking credentials stay local

2. **Cloud Limitations**:
   - Cloud can only draft (not send)
   - Cloud cannot access WhatsApp
   - Cloud cannot execute payments
   - Cloud cannot post to social media directly

3. **Local Control**:
   - Local has final approval authority
   - Local owns Dashboard.md
   - Local owns all external actions
   - Local can operate independently if cloud is offline

## Architecture Principles

1. **Defense in Depth**: Multiple security layers
2. **Least Privilege**: Cloud has minimal permissions
3. **Fail-Safe Defaults**: If unsure, require approval
4. **Audit Everything**: All actions logged
5. **Local-First**: Local can operate standalone
