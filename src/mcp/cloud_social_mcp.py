"""
Cloud Social Media MCP - Draft-Only Social Operations

Cloud agent can only create social media drafts.
Local agent handles actual posting after approval.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from src.utils.audit_logger import get_audit_logger


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class CloudSocialMCP:
    """
    Cloud Social Media MCP - Draft-only social operations.
    
    This MCP server can ONLY create drafts.
    It cannot post to social media directly.
    """
    
    def __init__(self, vault_path: Optional[str | Path] = None):
        """
        Initialize cloud social MCP.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        self.updates_dir = self.vault_path / "Updates" / "social_drafts"
        self.updates_dir.mkdir(parents=True, exist_ok=True)
        self.audit_logger = get_audit_logger()
        
        logger.info("Cloud Social MCP initialized (draft-only mode)")
    
    def create_draft(
        self,
        platform: str,
        content: str,
        image_url: Optional[str] = None,
        scheduled_time: Optional[str] = None,
    ) -> Path:
        """
        Create social media draft for local approval.
        
        Args:
            platform: Platform name (facebook, instagram, twitter, linkedin)
            content: Post content
            image_url: Optional image URL
            scheduled_time: Optional scheduled time (ISO format)
            
        Returns:
            Path to draft file
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / f"{platform}_draft_{timestamp}.md"
        
        content_md = f"""---
type: social_draft
created: {datetime.now().isoformat()}
platform: {platform}
status: pending_approval
draft_mode: true
scheduled_time: {scheduled_time or 'immediate'}
---

# Social Media Draft

**Platform**: {platform.title()}
**Created**: {datetime.now().isoformat()}

---

## Content

{content}

{f'**Image**: {image_url}' if image_url else ''}

{f'**Scheduled**: {scheduled_time}' if scheduled_time else '**Post Immediately**'}

---

**Cloud Draft** - Requires Local Approval

This draft was created by the Cloud Agent in draft-only mode.
To post this:
1. Review the content above
2. Move this file to `/Pending_Approval/local/`
3. Local agent will execute the post after approval
"""
        
        draft_file.write_text(content_md)
        
        self.audit_logger.log_action(
            action_type="cloud_social_draft_created",
            actor="cloud_social_mcp",
            details={
                "draft_file": str(draft_file),
                "platform": platform,
                "content_length": len(content),
                "has_image": image_url is not None,
            },
        )
        
        logger.info(f"Created {platform} draft: {draft_file}")
        return draft_file
    
    def create_business_update_draft(
        self,
        update_type: str,
        content: str,
    ) -> Path:
        """
        Create business update draft for all platforms.
        
        Args:
            update_type: Type of update (milestone, announcement, promotion)
            content: Update content
            
        Returns:
            Path to draft file
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / f"business_{update_type}_{timestamp}.md"
        
        content_md = f"""---
type: business_update_draft
created: {datetime.now().isoformat()}
update_type: {update_type}
platforms: [linkedin, facebook, twitter]
status: pending_approval
draft_mode: true
---

# Business Update Draft

**Type**: {update_type.title()}
**Created**: {datetime.now().isoformat()}

---

## Content

{content}

---

## Platform Variations

### LinkedIn (Professional)
{content}

#BusinessUpdate #Professional

### Facebook (Friendly)
{content}

Feel free to share!

### Twitter (Concise)
{content[:280]}

---

**Cloud Draft** - Requires Local Approval

This draft was created by the Cloud Agent in draft-only mode.
To post this:
1. Review the content above
2. Move this file to `/Pending_Approval/local/`
3. Local agent will execute the posts after approval
"""
        
        draft_file.write_text(content_md)
        
        self.audit_logger.log_action(
            action_type="cloud_business_update_draft_created",
            actor="cloud_social_mcp",
            details={
                "draft_file": str(draft_file),
                "update_type": update_type,
                "platforms": ["linkedin", "facebook", "twitter"],
            },
        )
        
        logger.info(f"Created business update draft: {draft_file}")
        return draft_file
    
    def post_to_platform(self, platform: str, *args, **kwargs) -> dict:
        """
        Post to platform - DISABLED in cloud mode.
        
        This method always returns an error in cloud mode.
        Use create_draft() instead.
        """
        return {
            "success": False,
            "error": f"post_to_platform('{platform}') is disabled in cloud mode. Use create_draft() instead.",
            "mode": "draft_only",
        }
    
    def post_to_all(self, *args, **kwargs) -> dict:
        """
        Post to all platforms - DISABLED in cloud mode.
        
        This method always returns an error in cloud mode.
        Use create_draft() instead.
        """
        return {
            "success": False,
            "error": "post_to_all() is disabled in cloud mode. Use create_draft() instead.",
            "mode": "draft_only",
        }


# Singleton instance
_cloud_social_mcp: Optional[CloudSocialMCP] = None


def get_cloud_social_mcp(vault_path: Optional[str | Path] = None) -> CloudSocialMCP:
    """Get or create cloud social MCP instance."""
    global _cloud_social_mcp
    if _cloud_social_mcp is None:
        _cloud_social_mcp = CloudSocialMCP(vault_path)
    return _cloud_social_mcp
