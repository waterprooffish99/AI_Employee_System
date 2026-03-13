"""
Cloud Orchestrator for AI Employee System - Platinum Tier

Draft-only mode for cloud deployment.
All actions create drafts that require local approval.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.orchestrator.ceo_briefing import get_ceo_briefing_generator
from src.utils.audit_logger import get_audit_logger
from src.utils.dashboard_updater import DashboardUpdater


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class CloudOrchestrator:
    """
    Orchestrator for cloud deployment (draft-only mode).
    
    Features:
    - Draft-only email replies
    - Draft-only social posts
    - Draft-only Odoo actions
    - Writes to /Updates/ folder
    - Cannot send/post directly
    """
    
    def __init__(self, vault_path: Optional[str | Path] = None):
        """
        Initialize cloud orchestrator.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        self.cloud_mode = os.getenv("CLOUD_MODE", "true").lower() == "true"
        self.dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        
        # Directories
        self.updates_dir = self.vault_path / "Updates"
        self.signals_dir = self.vault_path / "Signals"
        self.needs_action_dir = self.vault_path / "Needs_Action" / "cloud"
        self.in_progress_dir = self.vault_path / "In_Progress" / "cloud"
        self.pending_approval_dir = self.vault_path / "Pending_Approval" / "cloud"
        
        # Ensure directories exist
        for directory in [
            self.updates_dir,
            self.signals_dir,
            self.needs_action_dir,
            self.in_progress_dir,
            self.pending_approval_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.audit_logger = get_audit_logger()
        
        logger.info("Cloud Orchestrator initialized (draft-only mode)")
    
    def create_email_draft(
        self,
        original_email: dict,
        draft_reply: str,
        subject: str,
    ) -> Path:
        """
        Create email draft for local approval.
        
        Args:
            original_email: Original email details
            draft_reply: Draft reply content
            subject: Email subject
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / "email_drafts" / f"email_draft_{timestamp}.md"
        draft_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""---
type: email_draft
created: {datetime.now().isoformat()}
status: pending_approval
original_from: {original_email.get('from', 'Unknown')}
original_subject: {original_email.get('subject', 'No Subject')}
---

# Email Draft

## Original Email
- **From**: {original_email.get('from', 'Unknown')}
- **Subject**: {original_email.get('subject', 'No Subject')}
- **Date**: {original_email.get('date', 'Unknown')}

## Draft Reply

{draft_reply}

---
**Cloud Draft** - Requires Local Approval
Move to `/Pending_Approval/local/` for review
"""
        
        draft_file.write_text(content)
        
        self.audit_logger.log_action(
            action_type="cloud_email_draft_created",
            actor="cloud_orchestrator",
            details={
                "draft_file": str(draft_file),
                "original_from": original_email.get('from'),
                "subject": subject,
            },
        )
        
        logger.info(f"Created email draft: {draft_file}")
        return draft_file
    
    def create_social_draft(
        self,
        platform: str,
        content: str,
        image_url: Optional[str] = None,
        scheduled_time: Optional[str] = None,
    ) -> Path:
        """
        Create social media draft for local approval.
        
        Args:
            platform: Platform name (facebook, instagram, twitter)
            content: Post content
            image_url: Optional image URL
            scheduled_time: Optional scheduled time
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / "social_drafts" / f"{platform}_draft_{timestamp}.md"
        draft_file.parent.mkdir(parents=True, exist_ok=True)
        
        content_md = f"""---
type: social_draft
created: {datetime.now().isoformat()}
platform: {platform}
status: pending_approval
scheduled_time: {scheduled_time or 'immediate'}
---

# Social Media Draft

**Platform**: {platform.title()}

## Content

{content}

{f'**Image**: {image_url}' if image_url else ''}

{f'**Scheduled**: {scheduled_time}' if scheduled_time else '**Post Immediately**'}

---
**Cloud Draft** - Requires Local Approval
Move to `/Pending_Approval/local/` for review
"""
        
        draft_file.write_text(content_md)
        
        self.audit_logger.log_action(
            action_type="cloud_social_draft_created",
            actor="cloud_orchestrator",
            details={
                "draft_file": str(draft_file),
                "platform": platform,
                "content_length": len(content),
            },
        )
        
        logger.info(f"Created {platform} draft: {draft_file}")
        return draft_file
    
    def create_odoo_draft(
        self,
        action_type: str,
        details: dict,
    ) -> Path:
        """
        Create Odoo action draft for local approval.
        
        Args:
            action_type: Action type (invoice, payment, journal_entry)
            details: Action details
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / "odoo_drafts" / f"odoo_{action_type}_draft_{timestamp}.md"
        draft_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""---
type: odoo_draft
created: {datetime.now().isoformat()}
action_type: {action_type}
status: pending_approval
---

# Odoo Draft: {action_type.title()}

## Details

"""
        
        for key, value in details.items():
            content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        content += f"""
---
**Cloud Draft** - Requires Local Approval
Move to `/Pending_Approval/local/` for review
"""
        
        draft_file.write_text(content)
        
        self.audit_logger.log_action(
            action_type="cloud_odoo_draft_created",
            actor="cloud_orchestrator",
            details={
                "draft_file": str(draft_file),
                "action_type": action_type,
            },
        )
        
        logger.info(f"Created Odoo {action_type} draft: {draft_file}")
        return draft_file
    
    def write_signal(self, signal_type: str, data: dict) -> Path:
        """
        Write signal to local agent.
        
        Args:
            signal_type: Signal type
            data: Signal data
            
        Returns:
            Path to signal file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        signal_file = self.signals_dir / f"{signal_type}_{timestamp}.md"
        
        content = f"""---
type: signal
created: {datetime.now().isoformat()}
signal_type: {signal_type}
---

# Signal: {signal_type.title()}

"""
        
        for key, value in data.items():
            content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        signal_file.write_text(content)
        
        logger.info(f"Written signal {signal_type}: {signal_file}")
        return signal_file
    
    def claim_task(self, task_file: Path) -> bool:
        """
        Claim a task by moving to In_Progress/cloud.
        
        Args:
            task_file: Task file path
            
        Returns:
            True if claimed successfully
        """
        if not task_file.exists():
            return False
        
        # Check if already claimed
        if str(task_file).startswith(str(self.in_progress_dir)):
            logger.info(f"Task already claimed: {task_file}")
            return True
        
        # Move to in progress
        target = self.in_progress_dir / task_file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        task_file.rename(target)
        
        self.audit_logger.log_action(
            action_type="cloud_task_claimed",
            actor="cloud_orchestrator",
            details={
                "task_file": str(task_file),
                "target": str(target),
            },
        )
        
        logger.info(f"Claimed task: {task_file} -> {target}")
        return True
    
    def release_task(self, task_file: Path, reason: str = "") -> bool:
        """
        Release a task back to Needs_Action.
        
        Args:
            task_file: Task file path
            reason: Reason for release
            
        Returns:
            True if released successfully
        """
        if not task_file.exists():
            return False
        
        # Move back to needs action
        target = self.vault_path / "Needs_Action" / "shared" / task_file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Add release note
        content = task_file.read_text()
        content += f"\n\n---\n**Released**: {datetime.now().isoformat()}\n**Reason**: {reason}\n"
        target.write_text(content)
        
        task_file.unlink()
        
        logger.info(f"Released task: {task_file} (reason: {reason})")
        return True


# Singleton instance
_cloud_orchestrator: Optional[CloudOrchestrator] = None


def get_cloud_orchestrator(vault_path: Optional[str | Path] = None) -> CloudOrchestrator:
    """Get or create cloud orchestrator instance."""
    global _cloud_orchestrator
    if _cloud_orchestrator is None:
        _cloud_orchestrator = CloudOrchestrator(vault_path)
    return _cloud_orchestrator
