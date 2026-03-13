# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the risk assessment of the vulnerability.

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | :white_check_mark: |
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

## Reporting a Vulnerability

**IMPORTANT**: Please do not report security vulnerabilities through public GitHub issues.

Instead, please report them via email at [INSERT SECURITY EMAIL] or create a private vulnerability report using GitHub's private reporting feature.

### What to Include

Please include the following information in your report:

* **Type of issue** (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
* **Full paths of source file(s) related to the issue**
* **The specific location of the issue** (line numbers, function names, etc.)
* **Any special configuration required to reproduce the issue**
* **Step-by-step instructions to reproduce the issue**
* **Proof-of-concept or exploit code (if possible)**
* **Impact of the issue**, including how an attacker might exploit it

### Response Timeline

* **Within 48 hours**: We will acknowledge receipt of your report
* **Within 1 week**: We will provide a preliminary response
* **Within 30 days**: We will send a report on the status and planned fix
* **After fix**: We will notify you when the fix is deployed

## Security Best Practices

### For Users

#### Credential Management

* **Never commit credentials**: All secrets should be in `.env` file (gitignored)
* **Use environment variables**: Load credentials via `os.getenv()`
* **Rotate regularly**: Change API keys and passwords periodically
* **Use separate accounts**: Use test/sandbox accounts during development

#### Sandboxing

* **Enable DRY_RUN**: Set `DRY_RUN=true` during development
* **Review before executing**: Check approval files before moving to `/Approved/`
* **Monitor logs**: Review `AI_Employee_Vault/Audit_Logs/` regularly
* **Rate limiting**: Respect API rate limits to avoid bans

#### Vault Security

* **Encrypt at rest**: Consider encrypting your Obsidian vault
* **Backup regularly**: Use `scripts/backup_odoo.sh` and vault sync
* **Access control**: Limit file permissions on vault directory
* **Audit access**: Review who/what has access to your vault

### For Contributors

#### Code Security

* **Input validation**: Validate all user inputs
* **Output encoding**: Encode outputs to prevent injection
* **Error handling**: Don't leak sensitive information in errors
* **Logging**: Don't log credentials or sensitive data

#### Testing Security

* **Secret scanning**: Run `scripts/scan_secrets.sh` before committing
* **Dependency checks**: Run `uv pip compile --upgrade` regularly
* **Security audit**: Run `scripts/security_audit.sh` before PRs

#### Git Security

* **Signed commits**: Use GPG-signed commits when possible
* **Branch protection**: Use protected branches for main
* **Review changes**: Always review PRs before merging

## Security Features

### Built-in Protections

| Feature | Description | Status |
|---------|-------------|--------|
| **Secret Scanning** | Pre-commit hook scans for secrets | ✅ Active |
| **Environment Variables** | All credentials via `.env` | ✅ Active |
| **Audit Logging** | All actions logged with context | ✅ Active |
| **HITL Approval** | Human approval for sensitive actions | ✅ Active |
| **Dry Run Mode** | Test without external actions | ✅ Active |
| **Rate Limiting** | Prevent API abuse | ✅ Active |
| **Error Recovery** | Graceful degradation on failures | ✅ Active |

### Platinum Tier Security

* **Cloud/Local separation**: Cloud can only draft (not send)
* **Secrets never sync**: `.env` and tokens stay local
* **WhatsApp local only**: Sessions never leave local machine
* **Banking local only**: Payment credentials stay local
* **Dashboard single-writer**: Local owns Dashboard.md
* **Claim-by-move rule**: Prevents double-processing

## Known Limitations

* **WhatsApp Web automation**: Subject to WhatsApp's terms of service
* **API rate limits**: Respect third-party API limits
* **OAuth tokens**: Require secure storage and rotation
* **Local-first architecture**: Cloud deployment requires additional security hardening

## Security Updates

We will notify users of security updates via:

* GitHub Security Advisories
* Release notes
* Email notifications for critical issues

## Recognition

We believe in recognizing security researchers who help keep our project safe. If you report a valid security vulnerability, we will:

* Acknowledge your contribution (unless you prefer to remain anonymous)
* Add you to our Security Hall of Fame
* Provide updates on the fix progress

## Contact

For security-related questions or concerns, please contact us at:

* **Email**: [INSERT SECURITY EMAIL]
* **GitHub**: Use private vulnerability reporting

---

**Last Updated**: March 12, 2026

**Thank you for helping keep AI Employee System secure!**
