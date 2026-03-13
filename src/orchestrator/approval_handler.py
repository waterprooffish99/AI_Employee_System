"""
Approval Handler for AI Employee System - Platinum Tier

Handles approval workflow for cloud drafts.
Local agent reviews and approves/rejects cloud drafts.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.utils.audit_logger import get_audit_logger


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class ApprovalHandler:
    """
    Approval handler for cloud drafts.
    
    Features:
    - Review cloud drafts
    - Create approval requests
    - Process approvals
    - Execute approved actions
    """
    
    def __init__(self, vault_path: Optional[str | Path] = None):
        """
        Initialize approval handler.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        
        # Directories
        self.updates_dir = self.vault_path / "Updates"
        self.pending_approval_dir = self.vault_path / "Pending_Approval" / "local"
        self.approved_dir = self.vault_path / "Approved"
        self.rejected_dir = self.vault_path / "Rejected"
        self.done_dir = self.vault_path / "Done"
        
        # Ensure directories exist
        for directory in [self.pending_approval_dir, self.approved_dir, self.rejected_dir, self.done_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.audit_logger = get_audit_logger()
        
        logger.info("Approval Handler initialized")
    
    def review_drafts(self) -> list[Path]:
        """
        Review all cloud drafts and create approval requests.
        
        Returns:
            List of approval request files created
        """
        approval_requests = []
        
        # Review email drafts
        email_drafts_dir = self.updates_dir / "email_drafts"
        if email_drafts_dir.exists():
            for draft_file in email_drafts_dir.glob("*.md"):
                approval_file = self._create_approval_request(draft_file, "email")
                if approval_file:
                    approval_requests.append(approval_file)
        
        # Review social drafts
        social_drafts_dir = self.updates_dir / "social_drafts"
        if social_drafts_dir.exists():
            for draft_file in social_drafts_dir.glob("*.md"):
                approval_file = self._create_approval_request(draft_file, "social")
                if approval_file:
                    approval_requests.append(approval_file)
        
        # Review Odoo drafts
        odoo_drafts_dir = self.updates_dir / "odoo_drafts"
        if odoo_drafts_dir.exists():
            for draft_file in odoo_drafts_dir.glob("*.md"):
                approval_file = self._create_approval_request(draft_file, "odoo")
                if approval_file:
                    approval_requests.append(approval_file)
        
        return approval_requests
    
    def _create_approval_request(self, draft_file: Path, draft_type: str) -> Optional[Path]:
        """
        Create approval request from draft.
        
        Args:
            draft_file: Draft file path
            draft_type: Type of draft (email, social, odoo)
            
        Returns:
            Path to approval request file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_file = self.pending_approval_dir / f"{draft_type}_approval_{timestamp}.md"
        
        # Read draft content
        draft_content = draft_file.read_text()
        
        # Create approval request
        approval_content = f"""---
type: approval_request
created: {datetime.now().isoformat()}
draft_type: {draft_type}
draft_source: {draft_file}
status: pending
priority: normal
---

# Approval Request: {draft_type.title()}

**Draft Created**: {draft_file.name}
**Review Required**: Please review and approve/reject

---

{draft_content}

---

## Actions

**To Approve**: Move this file to `/Approved/`
**To Reject**: Move this file to `/Rejected/` or delete

"""
        
        approval_file.write_text(approval_content)
        
        self.audit_logger.log_approval_request(
            action_type=f"{draft_type}_approval_request",
            actor="approval_handler",
            target=str(draft_file),
            parameters={
                "approval_file": str(approval_file),
                "draft_type": draft_type,
            },
        )
        
        logger.info(f"Created approval request: {approval_file}")
        return approval_file
    
    def approve(self, approval_file: Path) -> bool:
        """
        Approve an action.
        
        Args:
            approval_file: Approval file path
            
        Returns:
            True if approved successfully
        """
        if not approval_file.exists():
            logger.error(f"Approval file not found: {approval_file}")
            return False
        
        # Move to approved
        approved_file = self.approved_dir / approval_file.name
        approved_file.write_text(approval_file.read_text())
        approval_file.unlink()
        
        self.audit_logger.log_approval_granted(
            action_type="approval_granted",
            approved_by="local_user",
            target=str(approved_file),
            parameters={
                "original_file": str(approval_file),
            },
        )
        
        logger.info(f"Approved: {approval_file} -> {approved_file}")
        return True
    
    def reject(self, approval_file: Path, reason: str = "") -> bool:
        """
        Reject an action.
        
        Args:
            approval_file: Approval file path
            reason: Reason for rejection
            
        Returns:
            True if rejected successfully
        """
        if not approval_file.exists():
            logger.error(f"Approval file not found: {approval_file}")
            return False
        
        # Add rejection reason
        content = approval_file.read_text()
        content += f"\n\n---\n**Rejected**: {datetime.now().isoformat()}\n**Reason**: {reason}\n"
        
        # Move to rejected
        rejected_file = self.rejected_dir / approval_file.name
        rejected_file.write_text(content)
        approval_file.unlink()
        
        self.audit_logger.log_action(
            action_type="approval_rejected",
            actor="local_user",
            target=str(rejected_file),
            details={
                "reason": reason,
            },
        )
        
        logger.info(f"Rejected: {approval_file} -> {rejected_file} (reason: {reason})")
        return True
    
    def execute_approved_email(self, approved_file: Path) -> bool:
        """Execute approved email send."""
        logger.info(f"Executing approved email: {approved_file}")
        # Would integrate with Email MCP here
        return True
    
    def execute_approved_social(self, approved_file: Path) -> bool:
        """Execute approved social media post."""
        logger.info(f"Executing approved social post: {approved_file}")
        # Would integrate with Social Media MCP here
        return True
    
    def execute_approved_odoo(self, approved_file: Path) -> bool:
        """Execute approved Odoo action."""
        logger.info(f"Executing approved Odoo action: {approved_file}")
        # Would integrate with Odoo MCP here
        return True


# Singleton instance
_approval_handler: Optional[ApprovalHandler] = None


def get_approval_handler(vault_path: Optional[str | Path] = None) -> ApprovalHandler:
    """Get or create approval handler instance."""
    global _approval_handler
    if _approval_handler is None:
        _approval_handler = ApprovalHandler(vault_path)
    return _approval_handler
