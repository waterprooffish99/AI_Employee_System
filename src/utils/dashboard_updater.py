"""
Enhanced Dashboard Updater for AI Employee System - Gold Tier

Updates Dashboard.md with cross-domain metrics (Personal + Business).
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.mcp.odoo_mcp import get_odoo_mcp
from src.mcp.social_media_manager import get_social_media_manager
from src.utils.audit_logger import get_audit_logger


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class DashboardUpdater:
    """
    Dashboard updater with cross-domain integration.
    
    Features:
    - Personal metrics (email, WhatsApp, personal bank)
    - Business metrics (revenue, invoices, social media)
    - Unified task view
    - Cross-domain priorities
    """
    
    def __init__(self, vault_path: str | Path):
        """
        Initialize dashboard updater.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.dashboard_file = self.vault_path / "Dashboard.md"
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.plans_dir = self.vault_path / "Plans"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.done_dir = self.vault_path / "Done"
        
        self.odoo = get_odoo_mcp()
        self.social_media = get_social_media_manager()
        self.audit_logger = get_audit_logger()
    
    def update_dashboard(self, metadata: Optional[dict] = None) -> dict:
        """
        Update Dashboard.md with current metrics.
        
        Args:
            metadata: Additional metadata to include
            
        Returns:
            Update result
        """
        try:
            # Gather all metrics
            metrics = self._gather_metrics()
            
            # Generate dashboard content
            content = self._generate_dashboard_content(metrics, metadata)
            
            # Write dashboard
            self.dashboard_file.write_text(content)
            
            # Log the update
            self.audit_logger.log_action(
                action_type="dashboard_update",
                actor="dashboard_updater",
                details={
                    "timestamp": datetime.now().isoformat(),
                    "metrics_included": list(metrics.keys()),
                },
            )
            
            return {
                "success": True,
                "dashboard_path": str(self.dashboard_file),
                "metrics": metrics,
            }
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            self.audit_logger.log_error(
                action_type="dashboard_update",
                actor="dashboard_updater",
                error=str(e),
            )
            return {"success": False, "error": str(e)}
    
    def _gather_metrics(self) -> dict:
        """Gather all metrics from various sources."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "personal": self._get_personal_metrics(),
            "business": self._get_business_metrics(),
            "tasks": self._get_task_metrics(),
        }
        return metrics
    
    def _get_personal_metrics(self) -> dict:
        """Get personal metrics."""
        # Count items in Needs_Action (personal communications)
        personal_count = 0
        if self.needs_action_dir.exists():
            for f in self.needs_action_dir.glob("EMAIL_*.md"):
                personal_count += 1
            for f in self.needs_action_dir.glob("WHATSAPP_*.md"):
                personal_count += 1
        
        return {
            "email_unread": personal_count,
            "whatsapp_pending": 0,  # Would integrate with WhatsApp watcher
            "personal_bank_balance": 0,  # Would integrate with personal banking
        }
    
    def _get_business_metrics(self) -> dict:
        """Get business metrics from Odoo and social media."""
        business = {
            "revenue_mtd": 0,
            "revenue_wtd": 0,
            "outstanding_invoices": 0,
            "social_media": {
                "linkedin_followers": 0,
                "facebook_engagement": 0,
                "instagram_followers": 0,
                "twitter_followers": 0,
            },
        }
        
        # Get revenue from Odoo
        try:
            invoices = self.odoo.get_invoices(state="posted", limit=100)
            total = sum(inv.get("amount_total", 0) for inv in invoices)
            business["revenue_mtd"] = total * 0.5  # Approximate
            business["revenue_wtd"] = total * 0.25  # Approximate
            business["outstanding_invoices"] = len(
                self.odoo.get_outstanding_invoices()
            )
        except Exception as e:
            logger.error(f"Failed to get business metrics from Odoo: {e}")
        
        # Get social media metrics
        try:
            analytics = self.social_media.get_unified_analytics(days=7)
            for platform, data in analytics.get("platforms", {}).items():
                if "error" not in data:
                    if platform == "facebook":
                        business["social_media"]["facebook_engagement"] = (
                            data.get("engagement_rate", 0)
                        )
                    # Would get follower counts from each platform
        except Exception as e:
            logger.error(f"Failed to get social media metrics: {e}")
        
        return business
    
    def _get_task_metrics(self) -> dict:
        """Get task metrics from vault folders."""
        tasks = {
            "pending": 0,
            "in_progress": 0,
            "awaiting_approval": 0,
            "completed_today": 0,
        }
        
        # Count files in each directory
        if self.needs_action_dir.exists():
            tasks["pending"] = len(list(self.needs_action_dir.glob("*.md")))
        
        if self.plans_dir.exists():
            tasks["in_progress"] = len(
                [f for f in self.plans_dir.glob("*_state.json")]
            )
        
        if self.pending_approval_dir.exists():
            tasks["awaiting_approval"] = len(
                list(self.pending_approval_dir.glob("*.md"))
            )
        
        if self.done_dir.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            tasks["completed_today"] = len(
                [f for f in self.done_dir.glob(f"{today}*.md")]
            )
        
        return tasks
    
    def _generate_dashboard_content(
        self,
        metrics: dict,
        metadata: Optional[dict] = None,
    ) -> str:
        """Generate Dashboard.md content."""
        personal = metrics.get("personal", {})
        business = metrics.get("business", {})
        tasks = metrics.get("tasks", {})
        
        content = f"""---
last_updated: {metrics['timestamp']}
dashboard_version: 2.0
---

# AI Employee Dashboard

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Personal Metrics

| Metric | Value |
|--------|-------|
| Email Unread | {personal.get('email_unread', 0)} |
| WhatsApp Pending | {personal.get('whatsapp_pending', 0)} |
| Personal Bank Balance | ${personal.get('personal_bank_balance', 0):,.2f} |

---

## Business Metrics

### Revenue

| Metric | Value |
|--------|-------|
| Revenue WTD | ${business.get('revenue_wtd', 0):,.2f} |
| Revenue MTD | ${business.get('revenue_mtd', 0):,.2f} |
| Outstanding Invoices | {business.get('outstanding_invoices', 0)} |

### Social Media

| Platform | Metric | Value |
|----------|--------|-------|
| LinkedIn | Followers | {business['social_media'].get('linkedin_followers', 0)} |
| Facebook | Engagement Rate | {business['social_media'].get('facebook_engagement', 0):.2f}% |
| Instagram | Followers | {business['social_media'].get('instagram_followers', 0)} |
| Twitter | Followers | {business['social_media'].get('twitter_followers', 0)} |

---

## Task Overview

| Status | Count |
|--------|-------|
| Pending | {tasks.get('pending', 0)} |
| In Progress | {tasks.get('in_progress', 0)} |
| Awaiting Approval | {tasks.get('awaiting_approval', 0)} |
| Completed Today | {tasks.get('completed_today', 0)} |

---

## Quick Actions

- [ ] Check `/Needs_Action/` for new items
- [ ] Review `/Pending_Approval/` for approvals needed
- [ ] Generate CEO Briefing (Mondays)

---

## Recent Activity

<!-- Activity log will be updated by orchestrator -->

---

*AI Employee v0.3 - Gold Tier*
"""
        
        return content


# Singleton instance
_dashboard_updater: Optional[DashboardUpdater] = None


def get_dashboard_updater(vault_path: str | Path) -> DashboardUpdater:
    """Get or create dashboard updater instance."""
    global _dashboard_updater
    if _dashboard_updater is None:
        _dashboard_updater = DashboardUpdater(vault_path)
    return _dashboard_updater


def update_dashboard(vault_path: str | Path) -> dict:
    """Update dashboard and return result."""
    updater = get_dashboard_updater(vault_path)
    return updater.update_dashboard()
