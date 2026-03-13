"""
Cloud Email MCP - Draft-Only Email Operations

Cloud agent can only create email drafts.
Local agent handles actual sending after approval.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from src.utils.audit_logger import get_audit_logger


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class CloudEmailMCP:
    """
    Cloud Email MCP - Draft-only email operations.
    
    This MCP server can ONLY create drafts.
    It cannot send emails directly.
    """
    
    def __init__(self, vault_path: Optional[str | Path] = None):
        """
        Initialize cloud email MCP.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        self.updates_dir = self.vault_path / "Updates" / "email_drafts"
        self.updates_dir.mkdir(parents=True, exist_ok=True)
        self.audit_logger = get_audit_logger()
        
        logger.info("Cloud Email MCP initialized (draft-only mode)")
    
    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        original_email: Optional[dict] = None,
    ) -> Path:
        """
        Create email draft for local approval.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            original_email: Original email being replied to (if any)
            
        Returns:
            Path to draft file
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / f"draft_{timestamp}.md"
        
        content = f"""---
type: email_draft
created: {datetime.now().isoformat()}
to: {to}
subject: {subject}
status: pending_approval
draft_mode: true
---

# Email Draft

**To**: {to}
**Subject**: {subject}
**Created**: {datetime.now().isoformat()}

---

## Body

{body}

---

**Cloud Draft** - Requires Local Approval

This draft was created by the Cloud Agent in draft-only mode.
To send this email:
1. Review the content above
2. Move this file to `/Pending_Approval/local/`
3. Local agent will execute the send after approval
"""
        
        draft_file.write_text(content)
        
        self.audit_logger.log_action(
            action_type="cloud_email_draft_created",
            actor="cloud_email_mcp",
            details={
                "draft_file": str(draft_file),
                "to": to,
                "subject": subject,
                "body_length": len(body),
            },
        )
        
        logger.info(f"Created email draft: {draft_file}")
        return draft_file
    
    def create_reply_draft(
        self,
        original_email: dict,
        reply_body: str,
    ) -> Path:
        """
        Create reply draft for local approval.
        
        Args:
            original_email: Original email details
            reply_body: Reply content
            
        Returns:
            Path to draft file
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / f"reply_{timestamp}.md"
        
        original_from = original_email.get('from', 'Unknown')
        original_subject = original_email.get('subject', 'No Subject')
        original_date = original_email.get('date', 'Unknown')
        original_body = original_email.get('body', '')
        
        content = f"""---
type: email_reply_draft
created: {datetime.now().isoformat()}
in_reply_to: {original_email.get('id', 'unknown')}
to: {original_from}
subject: Re: {original_subject}
status: pending_approval
draft_mode: true
---

# Email Reply Draft

**To**: {original_from}
**Subject**: Re: {original_subject}
**In Reply To**: {original_date}

---

## Reply

{reply_body}

---

## Original Email

**From**: {original_from}
**Date**: {original_date}
**Subject**: {original_subject}

{original_body}

---

**Cloud Draft** - Requires Local Approval

This reply draft was created by the Cloud Agent in draft-only mode.
To send this email:
1. Review the content above
2. Move this file to `/Pending_Approval/local/`
3. Local agent will execute the send after approval
"""
        
        draft_file.write_text(content)
        
        self.audit_logger.log_action(
            action_type="cloud_email_reply_draft_created",
            actor="cloud_email_mcp",
            details={
                "draft_file": str(draft_file),
                "in_reply_to": original_email.get('id'),
                "reply_length": len(reply_body),
            },
        )
        
        logger.info(f"Created email reply draft: {draft_file}")
        return draft_file
    
    def send_email(self, *args, **kwargs) -> dict:
        """
        Send email - DISABLED in cloud mode.
        
        This method always returns an error in cloud mode.
        Use create_draft() instead.
        """
        return {
            "success": False,
            "error": "send_email() is disabled in cloud mode. Use create_draft() instead.",
            "mode": "draft_only",
        }


# Singleton instance
_cloud_email_mcp: Optional[CloudEmailMCP] = None


def get_cloud_email_mcp(vault_path: Optional[str | Path] = None) -> CloudEmailMCP:
    """Get or create cloud email MCP instance."""
    global _cloud_email_mcp
    if _cloud_email_mcp is None:
        _cloud_email_mcp = CloudEmailMCP(vault_path)
    return _cloud_email_mcp
