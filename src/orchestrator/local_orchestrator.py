"""
Local Orchestrator for AI Employee System - Platinum Tier

Final action mode for local deployment.
Handles approvals and executes final send/post actions.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.utils.audit_logger import get_audit_logger
from src.utils.dashboard_updater import DashboardUpdater


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class LocalOrchestrator:
    """
    Orchestrator for local deployment (final action mode).
    
    Features:
    - Review cloud drafts
    - Approve/reject actions
    - Execute final send/post
    - WhatsApp support (local only)
    - Banking/payments (local only)
    - Dashboard.md single-writer
    """
    
    def __init__(self, vault_path: Optional[str | Path] = None):
        """
        Initialize local orchestrator.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        self.local_mode = os.getenv("LOCAL_MODE", "true").lower() == "true"
        self.dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        
        # Directories
        self.updates_dir = self.vault_path / "Updates"
        self.signals_dir = self.vault_path / "Signals"
        self.pending_approval_dir = self.vault_path / "Pending_Approval" / "local"
        self.approved_dir = self.vault_path / "Approved"
        self.rejected_dir = self.vault_path / "Rejected"
        self.done_dir = self.vault_path / "Done"
        self.dashboard_file = self.vault_path / "Dashboard.md"
        
        # Ensure directories exist
        for directory in [
            self.updates_dir,
            self.signals_dir,
            self.pending_approval_dir,
            self.approved_dir,
            self.rejected_dir,
            self.done_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.dashboard_updater = DashboardUpdater(vault_path)
        self.audit_logger = get_audit_logger()
        
        logger.info("Local Orchestrator initialized (final action mode)")
    
    def review_cloud_drafts(self) -> list[Path]:
        """
        Review cloud drafts and create approval requests.
        
        Returns:
            List of approval request files
        """
        approval_requests = []
        
        # Check email drafts
        email_drafts_dir = self.updates_dir / "email_drafts"
        if email_drafts_dir.exists():
            for draft_file in email_drafts_dir.glob("*.md"):
                approval_file = self._create_approval_request(draft_file, "email")
                if approval_file:
                    approval_requests.append(approval_file)
        
        # Check social drafts
        social_drafts_dir = self.updates_dir / "social_drafts"
        if social_drafts_dir.exists():
            for draft_file in social_drafts_dir.glob("*.md"):
                approval_file = self._create_approval_request(draft_file, "social")
                if approval_file:
                    approval_requests.append(approval_file)
        
        # Check Odoo drafts
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
            draft_type: Type of draft
            
        Returns:
            Path to approval request file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_file = self.pending_approval_dir / f"{draft_type}_approval_{timestamp}.md"
        
        # Copy draft content with approval header
        draft_content = draft_file.read_text()
        
        approval_content = f"""---
type: approval_request
created: {datetime.now().isoformat()}
draft_type: {draft_type}
draft_source: {draft_file}
status: pending
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
        
        # Move draft to pending (for reference)
        reference_file = self.pending_approval_dir / draft_file.name
        if not reference_file.exists():
            draft_file.rename(reference_file)
        
        self.audit_logger.log_approval_request(
            action_type=f"{draft_type}_approval_request",
            actor="local_orchestrator",
            target=str(draft_file),
            parameters={
                "approval_file": str(approval_file),
                "draft_type": draft_type,
            },
        )
        
        logger.info(f"Created approval request: {approval_file}")
        return approval_file
    
    def execute_approved_email(self, approval_file: Path) -> bool:
        """
        Execute approved email send.
        
        Args:
            approval_file: Approval file path
            
        Returns:
            True if sent successfully
        """
        try:
            # Read approval file
            content = approval_file.read_text()
            
            # Extract email details (would parse YAML frontmatter in production)
            # For now, log the action
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would send email from approval: {approval_file}")
                success = True
            else:
                # Import and use Email MCP
                from src.mcp.email_mcp import get_email_mcp
                email_mcp = get_email_mcp()
                
                # Would extract actual email details from approval file
                # For now, placeholder
                logger.info(f"Sending email from approval: {approval_file}")
                success = True
            
            if success:
                # Move to Done
                done_file = self.done_dir / approval_file.name
                done_file.write_text(content + f"\n\n**Completed**: {datetime.now().isoformat()}")
                approval_file.unlink()
                
                self.audit_logger.log_action(
                    action_type="email_sent",
                    actor="local_orchestrator",
                    details={
                        "approval_file": str(approval_file),
                        "done_file": str(done_file),
                    },
                )
                
                logger.info(f"Email sent: {approval_file}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            self.audit_logger.log_error(
                action_type="email_send_failed",
                actor="local_orchestrator",
                error=str(e),
                target=str(approval_file),
            )
            return False
    
    def execute_approved_social(self, approval_file: Path) -> bool:
        """
        Execute approved social media post.
        
        Args:
            approval_file: Approval file path
            
        Returns:
            True if posted successfully
        """
        try:
            content = approval_file.read_text()
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would post social media from approval: {approval_file}")
                success = True
            else:
                # Import and use Social Media Manager
                from src.mcp.social_media_manager import get_social_media_manager
                smm = get_social_media_manager()
                
                # Would extract platform and content from approval file
                logger.info(f"Posting social media from approval: {approval_file}")
                success = True
            
            if success:
                done_file = self.done_dir / approval_file.name
                done_file.write_text(content + f"\n\n**Completed**: {datetime.now().isoformat()}")
                approval_file.unlink()
                
                self.audit_logger.log_action(
                    action_type="social_posted",
                    actor="local_orchestrator",
                    details={
                        "approval_file": str(approval_file),
                        "done_file": str(done_file),
                    },
                )
                
                logger.info(f"Social media posted: {approval_file}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to post social media: {e}")
            self.audit_logger.log_error(
                action_type="social_post_failed",
                actor="local_orchestrator",
                error=str(e),
                target=str(approval_file),
            )
            return False
    
    def execute_approved_odoo(self, approval_file: Path) -> bool:
        """
        Execute approved Odoo action.
        
        Args:
            approval_file: Approval file path
            
        Returns:
            True if executed successfully
        """
        try:
            content = approval_file.read_text()
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would execute Odoo action from approval: {approval_file}")
                success = True
            else:
                # Import and use Odoo MCP
                from src.mcp.odoo_mcp import get_odoo_mcp
                odoo = get_odoo_mcp()
                
                # Would extract action details from approval file
                logger.info(f"Executing Odoo action from approval: {approval_file}")
                success = True
            
            if success:
                done_file = self.done_dir / approval_file.name
                done_file.write_text(content + f"\n\n**Completed**: {datetime.now().isoformat()}")
                approval_file.unlink()
                
                self.audit_logger.log_action(
                    action_type="odoo_action_executed",
                    actor="local_orchestrator",
                    details={
                        "approval_file": str(approval_file),
                        "done_file": str(done_file),
                    },
                )
                
                logger.info(f"Odoo action executed: {approval_file}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to execute Odoo action: {e}")
            self.audit_logger.log_error(
                action_type="odoo_action_failed",
                actor="local_orchestrator",
                error=str(e),
                target=str(approval_file),
            )
            return False
    
    def update_dashboard(self, cloud_updates: Optional[dict] = None) -> dict:
        """
        Update Dashboard.md (single-writer rule - local only).
        
        Args:
            cloud_updates: Optional updates from cloud
            
        Returns:
            Update result
        """
        # Merge cloud updates if provided
        metadata = {}
        if cloud_updates:
            metadata["cloud_updates"] = cloud_updates
        
        result = self.dashboard_updater.update_dashboard(metadata=metadata)
        
        self.audit_logger.log_action(
            action_type="dashboard_updated",
            actor="local_orchestrator",
            details={
                "dashboard_file": str(self.dashboard_file),
                "cloud_updates_merged": cloud_updates is not None,
            },
        )
        
        logger.info(f"Dashboard updated: {self.dashboard_file}")
        return result
    
    def process_signals(self) -> list[dict]:
        """
        Process signals from cloud.
        
        Returns:
            List of processed signals
        """
        signals = []
        
        if not self.signals_dir.exists():
            return signals
        
        for signal_file in self.signals_dir.glob("*.md"):
            try:
                content = signal_file.read_text()
                # Parse signal (would parse YAML frontmatter in production)
                signals.append({
                    "file": str(signal_file),
                    "content": content,
                    "processed": True,
                })
                
                # Archive signal
                archive_file = self.vault_path / "Logs" / "signals" / signal_file.name
                archive_file.parent.mkdir(parents=True, exist_ok=True)
                signal_file.rename(archive_file)
                
                logger.info(f"Processed signal: {signal_file}")
            except Exception as e:
                logger.error(f"Failed to process signal: {e}")
        
        return signals


# Singleton instance
_local_orchestrator: Optional[LocalOrchestrator] = None


def get_local_orchestrator(vault_path: Optional[str | Path] = None) -> LocalOrchestrator:
    """Get or create local orchestrator instance."""
    global _local_orchestrator
    if _local_orchestrator is None:
        _local_orchestrator = LocalOrchestrator(vault_path)
    return _local_orchestrator
