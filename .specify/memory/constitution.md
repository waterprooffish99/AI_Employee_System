# AI Employee System Constitution

## Core Principles

### I. Agent Skills First
All AI functionality MUST be implemented as Agent Skills for Claude Code. Skills are reusable, testable, and documented prompts that encode business logic and workflows.

### II. Local-First Architecture
All data and processing happens locally first. Cloud integration is optional and requires explicit user consent. User privacy and data sovereignty are paramount.

### III. Human-in-the-Loop (HITL)
All sensitive actions require human approval before execution. This includes:
- External communications (emails, social media posts)
- Financial transactions (payments, invoices)
- File deletions or modifications
- API calls with side effects

### IV. Test-First Development (NON-NEGOTIABLE)
TDD mandatory: Tests written → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced for all code changes.

### V. Comprehensive Audit Logging
Every action taken by the system MUST be logged with:
- Timestamp
- Action type
- Actor (human or agent)
- Parameters
- Result (success/failure)
- Approval status

### VI. Error Recovery and Graceful Degradation
The system MUST handle errors gracefully:
- Automatic retry with exponential backoff
- Fallback mechanisms for failed operations
- User notification on critical failures
- State preservation during errors

### VII. Ralph Wiggum Loop Pattern
Autonomous multi-step task completion using stop hook pattern:
- Task state persistence
- Completion detection
- Maximum iteration safeguards
- Continuous iteration until done

## Technical Standards

### Technology Stack
- **Language**: Python 3.13+
- **AI Engine**: Claude Code (or compatible via router)
- **Knowledge Base**: Obsidian (local Markdown)
- **Automation**: Playwright for browser automation
- **APIs**: REST, JSON-RPC (Odoo)
- **Scheduling**: cron (Linux/Mac) or Task Scheduler (Windows)

### Code Quality
- Type hints required for all functions
- Docstrings for all public APIs
- Logging at all entry/exit points
- Error handling with specific exceptions

### Security Requirements
- Credentials via environment variables only
- Never commit .env files
- DRY_RUN mode enabled by default
- Rate limiting on all external APIs
- Credential rotation policy

### Directory Structure
```
AI_Employee_System/
├── .specify/memory/constitution.md  # This file
├── specs/<feature>/                  # Feature specifications
│   ├── spec.md                       # Requirements
│   ├── plan.md                       # Architecture
│   └── tasks.md                      # Implementation tasks
├── src/                              # Python source code
│   ├── watchers/                     # Perception layer
│   ├── mcp/                          # Action layer (MCP servers)
│   ├── orchestrator/                 # Coordination
│   └── utils/                        # Shared utilities
├── skills/                           # Agent Skills (Claude prompts)
└── AI_Employee_Vault/                # Obsidian vault
    ├── Dashboard.md
    ├── Needs_Action/
    ├── Plans/
    ├── Pending_Approval/
    ├── Approved/
    ├── Done/
    └── Logs/
```

## Development Workflow

### Branch Naming
Feature branches: `<ticket>-<feature-name>` (e.g., `001-gold-tier-autonomous`)

### Commit Messages
- Clear and concise
- Reference tickets/features
- Explain WHY, not WHAT

### Quality Gates
1. All tests pass
2. Constitution compliance verified
3. Documentation updated
4. PHR (Prompt History Record) created

## Governance

This constitution supersedes all other practices. Amendments require:
1. Documentation of change
2. User approval
3. Migration plan if breaking

**Version**: 1.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07
