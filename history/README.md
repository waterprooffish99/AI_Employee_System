# History Directory

This directory stores Prompt History Records (PHRs) and other historical data for the AI Employee System.

## Purpose

- **Audit Trail**: Track all AI decisions and actions
- **Learning**: Review past prompts and responses for improvement
- **Debugging**: Understand what happened when issues occur
- **Compliance**: Maintain records for accountability

## Structure

```
history/
├── prompts/           # Individual PHR files
│   ├── PHR-20260309-001.md
│   └── PHR-20260309-002.md
├── memory/            # Memory snapshots
│   └── snapshot_YYYYMMDD.md
├── scripts/           # Historical scripts
│   └── archive_YYYYMMDD.py
└── templates/         # PHR templates
    └── phr-template.md
```

## Prompt History Record (PHR)

Each PHR contains:
- **Context**: What triggered the prompt
- **Prompt**: Full prompt sent to Claude Code
- **Response**: Summary of Claude's response
- **Actions**: What was done
- **Outcome**: Result and lessons learned

## Usage

### Create a PHR

Use the template in `templates/phr-template.md`:

```bash
# Copy template
cp history/templates/phr-template.md history/prompts/PHR-$(date +%Y%m%d)-$(printf "%03d" $((RANDOM % 1000))).md
```

### Search History

```bash
# Find PHRs by keyword
grep -r "keyword" history/prompts/

# Find PHRs by date
ls history/prompts/ | grep "PHR-20260309"
```

### Archive Old PHRs

```bash
# Move PHRs older than 30 days to archive
find history/prompts/ -name "PHR-*.md" -mtime +30 -exec mv {} history/archive/ \;
```

## Retention Policy

| Type | Retention | Notes |
|------|-----------|-------|
| Active PHRs | 90 days | In `prompts/` |
| Archived PHRs | 1 year | In `archive/` |
| Memory Snapshots | Indefinite | Key system states |
| Scripts | Indefinite | Historical code |

## Privacy

- Never store credentials in PHRs
- Redact sensitive information
- PHRs are local-only (not synced to cloud)

---

*History is essential for learning and accountability*
