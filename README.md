# 🤖 AI Employee System

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

[![Hackathon 0](https://img.shields.io/badge/Hackathon-0%20Platinum-blue)](https://forms.gle/JR9T1SJq5rmQyGkGA)
[![Tier](https://img.shields.io/badge/Tier-💎%20Platinum-success)](./docs/HACKATHON_VALIDATION_REPORT.md)
[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](./README.md)

**Hackathon 0**: Building Autonomous FTEs (Full-Time Equivalent) in 2026

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features by Tier](#-features-by-tier)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Agent Skills](#-agent-skills)
- [Security](#-security)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

A **Personal AI Employee** that works autonomously 24/7 to manage your personal and business affairs. Built with Claude Code as the reasoning engine and Obsidian as the memory/GUI, this system implements a complete autonomous agent architecture.

### 💡 The Digital FTE Revolution

| Metric | Human FTE | Digital FTE | Improvement |
|--------|-----------|-------------|-------------|
| **Availability** | 40 hrs/week | 168 hrs/week (24/7) | **4.2x** |
| **Monthly Cost** | $4,000–$8,000+ | $500–$2,000 | **85% savings** |
| **Ramp-up Time** | 3–6 months | Instant | **Immediate** |
| **Consistency** | 85–95% | 99%+ | **Predictable** |
| **Annual Hours** | ~2,000 | ~8,760 | **4.4x** |

> **The 'Aha!' Moment**: A Digital FTE works nearly 9,000 hours/year vs a human's 2,000. The cost per task reduction (from ~$5.00 to ~$0.50) is an **85–90% cost saving**.

---

## 🏆 Features by Tier

### 🥉 Bronze Tier - Foundation (8-12 hours)

✅ **Complete**

- Obsidian vault with Dashboard.md
- Company Handbook with rules of engagement
- Filesystem Watcher (monitors drop folder)
- Claude Code integration
- Basic folder structure (`/Inbox`, `/Needs_Action`, `/Done`)
- 5 core Agent Skills

### 🥈 Silver Tier - Functional Assistant (20-30 hours)

✅ **Complete**

- **All Bronze features** plus:
- 3 Watchers (Gmail, WhatsApp, Filesystem)
- LinkedIn auto-posting with approval
- Plan.md creation (Claude reasoning loop)
- Email + LinkedIn MCP servers
- Human-in-the-loop (HITL) approval workflow
- Cron scheduling
- 7 Agent Skills total

### 🥇 Gold Tier - Autonomous Employee (40+ hours)

✅ **Complete**

- **All Silver features** plus:
- **Odoo Accounting** integration (JSON-RPC 19+)
- **Social Media** MCPs (Facebook, Instagram, Twitter/X)
- **6 MCP servers** total
- **Weekly CEO Briefing** (automated business audit)
- **Error recovery** and graceful degradation
- **Comprehensive audit logging**
- **Ralph Wiggum Loop** (autonomous multi-step completion)
- 12 Agent Skills total

### 💎 Platinum Tier - Always-On Cloud + Local (60+ hours)

✅ **Complete**

- **All Gold features** plus:
- **Cloud deployment** (24/7 operation on Oracle Cloud Free Tier)
- **Work-zone specialization**:
  - ☁️ **Cloud**: Email triage, draft replies, social drafts (draft-only)
  - 💻 **Local**: Approvals, WhatsApp, payments, final actions
- **Vault sync** (Git or Syncthing)
- **Claim-by-move rule** (prevents double-processing)
- **Security**: Secrets never sync
- **Odoo on Cloud** (HTTPS, backups, health monitoring)
- **Health monitoring** with auto-restart
- Cloud MCP servers (draft-only mode)

---

## 🏗️ Architecture

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
                              │  │Odoo  │ │Cloud │  │
                              │  │ MCP  │ │ MCPs │  │
                              │  └──────┘ └──────┘  │
                              └──────────┬──────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  AUDIT & RECOVERY LAYER                              │
│  AuditLogger | ErrorHandler | RetryManager | GracefulDegradation   │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Components

| Layer | Components | Purpose |
|-------|------------|---------|
| **Perception** | Watchers (Gmail, WhatsApp, File, Social) | Monitor external systems 24/7 |
| **Memory** | Obsidian Vault | Long-term storage + GUI |
| **Reasoning** | Claude Code + 12 Agent Skills | Decision making + planning |
| **Action** | 10 MCP Servers | External system integration |
| **Safety** | HITL Approval | Human oversight for sensitive actions |
| **Audit** | Logging + Error Recovery | Accountability + resilience |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.13+
- **Claude Code** CLI (`npm install -g @anthropic/claude-code`)
- **Obsidian** (free)
- **UV** package manager

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd AI_Employee_System

# Install dependencies
uv sync
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# NEVER commit .env to version control!
```

### 3. Set Up Obsidian Vault

```bash
# Open Obsidian and select the AI_Employee_Vault folder
# Or use the provided vault structure
```

### 4. Start the System

```bash
# Start all watchers
bash .specify/scripts/bash/start_watchers.sh

# Or start individual components
uv run python -m src.watchers.filesystem_watcher
uv run python -m src.watchers.gmail_watcher

# Start orchestrator
python main.py
```

### 5. Test the System

```bash
# Run Bronze Tier test
bash test_bronze.sh

# Or run quick test
uv run python test_bronze_quick.py
```

---

## 📁 Project Structure

```
AI_Employee_System/
├── 📄 README.md                       # This file
├── 📄 Hackathon-0.txt                 # Hackathon specification
├── 📄 pyproject.toml                  # Python dependencies
├── 📄 .env.example                    # Environment template
├── 📄 .gitignore                      # Git ignore rules
├── 📄 docker-compose.yml              # Docker deployment
├── 📄 syncthing-config.xml            # Vault sync config
│
├── 🔧 .specify/                       # Project configuration
│   ├── memory/constitution.md         # Project constitution
│   └── scripts/bash/                  # Shell scripts
│
├── 📚 docs/                           # Documentation
│   ├── architecture.md                # System architecture
│   ├── HACKATHON_VALIDATION_REPORT.md # Complete validation
│   ├── ralph_wiggum_loop.md           # Ralph Wiggum guide
│   ├── cloud_deployment.md            # Cloud setup
│   ├── security.md                    # Security guide
│   └── ...
│
├── 🧠 skills/                         # Agent Skills (Claude prompts)
│   ├── 01_process_needs_action.md     # Bronze
│   ├── 02_update_dashboard.md         # Bronze
│   ├── ...
│   └── 12_error_recovery.md           # Gold
│
├── 🤖 src/                            # Python source code
│   ├── orchestrator/                  # Main orchestration
│   │   ├── main.py                    # Main orchestrator
│   │   ├── ceo_briefing.py            # CEO Briefing generator
│   │   ├── cloud_orchestrator.py      # Cloud mode (Platinum)
│   │   └── local_orchestrator.py      # Local mode (Platinum)
│   ├── watchers/                      # Perception layer
│   │   ├── base_watcher.py            # Base class
│   │   ├── filesystem_watcher.py      # Bronze
│   │   ├── gmail_watcher.py           # Silver
│   │   └── whatsapp_watcher.py        # Silver
│   ├── mcp/                           # Action layer
│   │   ├── email_mcp.py               # Silver
│   │   ├── linkedin_poster.py         # Silver
│   │   ├── odoo_mcp.py                # Gold
│   │   ├── facebook_mcp.py            # Gold
│   │   ├── instagram_mcp.py           # Gold
│   │   ├── twitter_mcp.py             # Gold
│   │   └── cloud_*.py                 # Platinum (draft-only)
│   ├── utils/                         # Utilities
│   │   ├── audit_logger.py            # Gold
│   │   ├── error_handler.py           # Gold
│   │   ├── ralph_loop.py              # Gold
│   │   └── ...
│   └── monitoring/                    # Health checks
│       └── health_check.py            # Platinum
│
├── 📝 AI_Employee_Vault/              # Obsidian Vault (Memory)
│   ├── Dashboard.md                   # Real-time status
│   ├── Company_Handbook.md            # Rules of engagement
│   ├── Business_Goals.md              # Objectives
│   ├── Inbox/                         # Raw incoming
│   ├── Needs_Action/                  # Requires attention
│   ├── Plans/                         # Execution plans
│   ├── Pending_Approval/              # Awaiting approval
│   ├── Approved/                      # Approved actions
│   ├── Done/                          # Completed tasks
│   └── ...
│
├── 🧪 tests/                          # Test suite
│   ├── test_bronze_quick.py           # Bronze test
│   └── test_platinum_demo.py          # Platinum demo
│
└── 📜 scripts/                        # Utility scripts
    ├── sync_vault.sh                  # Vault sync
    ├── backup_odoo.sh                 # Odoo backups
    └── security_audit.sh              # Security checks
```

---

## 🧠 Agent Skills (12 Total)

Agent Skills are Markdown files that define Claude's capabilities as reusable prompts.

### Bronze Tier (5 Skills)

| Skill | Purpose |
|-------|---------|
| `01_process_needs_action.md` | Process items in Needs_Action folder |
| `02_update_dashboard.md` | Keep dashboard current with metrics |
| `03_request_approval.md` | Request human approval for actions |
| `04_execute_approved.md` | Execute approved actions via MCP |
| `05_log_events.md` | Log all events for audit trail |

### Silver Tier (2 Skills)

| Skill | Purpose |
|-------|---------|
| `06_create_plan.md` | Create detailed execution plans |
| `07_execute_approved_hitl.md` | Human-in-the-loop workflow execution |

### Gold Tier (5 Skills)

| Skill | Purpose |
|-------|---------|
| `08_ralph_wiggum_loop.md` | Autonomous multi-step task completion |
| `09_ceo_briefing.md` | Weekly business and accounting audit |
| `10_social_media_manager.md` | Cross-platform social media management |
| `11_odoo_accounting.md` | Odoo accounting operations |
| `12_error_recovery.md` | Error handling and graceful degradation |

---

## 🔒 Security

### Credential Management

- ✅ All credentials in `.env` (gitignored)
- ✅ Environment variables only
- ✅ No credentials in logs or vault
- ✅ Regular rotation recommended

### Sandboxing

- ✅ `DRY_RUN=true` by default (no external actions)
- ✅ All actions logged before execution
- ✅ Rate limiting on all APIs
- ✅ Approval required for sensitive actions

### Audit Trail

- ✅ Every action logged with full context
- ✅ Immutable JSON log entries
- ✅ 90-day retention policy
- ✅ Searchable interface

### Human-in-the-Loop

Approval required for:
- External emails
- Social media posts
- Financial transactions (Odoo)
- File deletions
- API calls with side effects

### Platinum Security

- ✅ **Secrets never sync** (Cloud ↔ Local)
- ✅ **Cloud draft-only** (cannot send/post)
- ✅ **Local owns approvals** (final authority)
- ✅ **WhatsApp sessions local** (privacy)
- ✅ **Banking credentials local** (security)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](./README.md) | This file - overview and quick start |
| [Hackathon-0.txt](./Hackathon-0.txt) | Original hackathon specification |
| [docs/architecture.md](./docs/architecture.md) | Detailed system architecture |
| [docs/HACKATHON_VALIDATION_REPORT.md](./docs/HACKATHON_VALIDATION_REPORT.md) | Complete tier validation |
| [docs/ralph_wiggum_loop.md](./docs/ralph_wiggum_loop.md) | Ralph Wiggum usage guide |
| [docs/cloud_deployment.md](./docs/cloud_deployment.md) | Cloud deployment guide |
| [docs/vault_sync.md](./docs/vault_sync.md) | Vault synchronization |
| [docs/security.md](./docs/security.md) | Security best practices |
| [specs/gold-tier/](./specs/gold-tier/) | Gold Tier specifications |
| [specs/platinum-tier/](./specs/platinum-tier/) | Platinum Tier specifications |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone <your-fork-url>
cd AI_Employee_System

# Install dependencies
uv sync

# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

### Code Standards

- **Python**: Follow PEP 8
- **Type Hints**: Use type annotations
- **Documentation**: Docstrings for all public functions
- **Testing**: Write tests for new features
- **Security**: Never commit credentials

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎓 Learning Resources

### Prerequisites

| Topic | Resource | Time |
|-------|----------|------|
| Claude Code Fundamentals | [Docs](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows) | 3 hrs |
| Obsidian Basics | [Help](https://help.obsidian.md/Getting+started) | 30 min |
| Python File I/O | [Real Python](https://realpython.com/read-write-files-python) | 1 hr |
| MCP Introduction | [Spec](https://modelcontextprotocol.io/introduction) | 1 hr |
| Agent Skills | [Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | 2 hrs |

### Core Learning

| Topic | Resource | Type |
|-------|----------|------|
| Claude + Obsidian | [Video](https://www.youtube.com/watch?v=sCIS05Qt79Y) | Tutorial |
| Building MCP Servers | [Quickstart](https://modelcontextprotocol.io/quickstart) | Guide |
| Gmail API Setup | [Docs](https://developers.google.com/gmail/api/quickstart) | API |
| Playwright Automation | [Docs](https://playwright.dev/python/docs/intro) | Library |

---

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Check the [docs](./docs/) folder

---

## 🙏 Acknowledgments

- **Anthropic** for Claude Code
- **Obsidian** for the knowledge base
- **Hackathon 0** organizers for the specification
- **Community** contributors and testers

---

## 📈 Version History

| Version | Date | Tier | Status |
|---------|------|------|--------|
| v0.1.0 | 2026-01-01 | 🥉 Bronze | Complete |
| v0.2.0 | 2026-01-04 | 🥈 Silver | Complete |
| v0.3.0 | 2026-01-07 | 🥇 Gold | Complete |
| v0.4.0 | 2026-01-07 | 💎 Platinum | Complete |

---

<div align="center">

**Built with ❤️ for Hackathon 0**

[Report Bug](../../issues) · [Request Feature](../../issues) · [View Demo](../../)

</div>
