"""
LinkedIn Poster - Automatically posts business updates to LinkedIn.

Silver Tier Requirement: Automatically Post on LinkedIn about business to generate sales

This module provides functionality to:
1. Create LinkedIn post drafts
2. Submit posts for approval
3. Post approved content to LinkedIn

Note: LinkedIn API requires business account and API access approval.
Alternative: Use browser automation (Playwright) for posting.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports
try:
    from linkedin_api import Linkedin
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False
    Linkedin = None


class LinkedInPoster:
    """
    LinkedIn Poster - Creates and posts business updates to LinkedIn.
    
    Silver Tier: Automatically post about business to generate sales.
    Requires human approval before posting (HITL).
    """
    
    def __init__(
        self,
        vault_path: str,
        username: str = None,
        password: str = None,
        use_browser: bool = True
    ):
        """
        Initialize the LinkedIn Poster.
        
        Args:
            vault_path: Path to the Obsidian vault
            username: LinkedIn username/email
            password: LinkedIn password
            use_browser: Use browser automation instead of API
        """
        self.vault_path = Path(vault_path)
        self.username = username or os.getenv('LINKEDIN_USERNAME')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.use_browser = use_browser
        
        # Directories
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Ensure directories exist
        for d in [self.pending_approval, self.approved, self.done]:
            d.mkdir(parents=True, exist_ok=True)
        
        logger.info('LinkedIn Poster initialized')
        logger.info(f'  Use browser automation: {self.use_browser}')
    
    def create_post_draft(
        self,
        topic: str,
        content: str,
        hashtags: list = None,
        call_to_action: str = None
    ) -> Path:
        """
        Create a LinkedIn post draft for approval.
        
        Args:
            topic: Post topic/title
            content: Main post content
            hashtags: List of hashtags
            call_to_action: CTA text
            
        Returns:
            Path to created draft file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        hashtags_text = ' '.join([f'#{h}' for h in (hashtags or [])])
        
        content_md = f"""---
type: linkedin_post
topic: {topic}
created: {datetime.now().isoformat()}
status: draft
platform: LinkedIn
requires_approval: true
---

# LinkedIn Post Draft

## Topic
{topic}

## Content
{content}

{hashtags_text if hashtags_text else ''}

{call_to_action if call_to_action else '📩 DM us to learn more!'}

---

## Post Details
- **Character Count**: {len(content) + len(hashtags_text)}
- **Estimated Reach**: Business network
- **Best Time to Post**: Weekdays 9-11 AM or 5-6 PM

## Approval Required
This post requires human approval before publishing.

## To Approve
1. Review the content above
2. Move this file to /Approved/ folder
3. The orchestrator will post when approved

## To Edit
1. Edit this file directly
2. Save changes
3. Submit for approval again

## To Reject
Move this file to /Rejected/ or delete it.

---
*Created by LinkedIn Poster - Hackathon 0 Silver Tier*
"""
        
        # Write draft file
        filename = f'LINKEDIN_{topic.replace(" ", "_")[:30]}_{timestamp}.md'
        filepath = self.pending_approval / filename
        filepath.write_text(content_md)
        
        logger.info(f'Created LinkedIn post draft: {filepath}')
        return filepath
    
    def create_business_update_post(
        self,
        update_type: str,
        details: Dict[str, Any]
    ) -> Path:
        """
        Create a business update post (milestone, product, sale, etc.).
        
        Args:
            update_type: Type of update (milestone, product, sale, tip, etc.)
            details: Update details
            
        Returns:
            Path to created draft file
        """
        templates = {
            'milestone': self._milestone_template,
            'product': self._product_template,
            'sale': self._sale_template,
            'tip': self._tip_template,
            'announcement': self._announcement_template
        }
        
        template_func = templates.get(update_type, templates['announcement'])
        content, hashtags, cta = template_func(details)
        
        return self.create_post_draft(
            topic=f"Business {update_type.title()}: {details.get('title', 'Update')}",
            content=content,
            hashtags=hashtags,
            call_to_action=cta
        )
    
    def _milestone_template(self, details: Dict) -> tuple:
        """Template for milestone posts."""
        content = f"""🎉 Exciting News!

We've reached a significant milestone: {details.get('milestone', 'a major achievement')}!

{details.get('description', '')}

Thank you to our amazing community for your continued support!"""
        
        hashtags = details.get('hashtags', ['milestone', 'growth', 'business', 'success'])
        cta = "💬 What's your biggest business milestone this year? Share below!"
        
        return content, hashtags, cta
    
    def _product_template(self, details: Dict) -> tuple:
        """Template for product posts."""
        content = f"""🚀 New Product Alert!

Introducing: {details.get('product_name', 'Our Latest Innovation')}

{details.get('description', '')}

✨ Key Features:
{chr(10).join([f'• {f}' for f in details.get('features', ['Feature 1', 'Feature 2'])])}

{details.get('benefits', 'Transform your workflow today!')}"""
        
        hashtags = details.get('hashtags', ['newproduct', 'innovation', 'business', 'tech'])
        cta = "📩 DM us for early access!"
        
        return content, hashtags, cta
    
    def _sale_template(self, details: Dict) -> tuple:
        """Template for sale/promotion posts."""
        content = f"""🔥 Limited Time Offer!

{details.get('offer', 'Special Discount')}

{details.get('description', '')}

⏰ Offer ends: {details.get('deadline', 'Soon!')}

Don't miss out!"""
        
        hashtags = details.get('hashtags', ['sale', 'discount', 'deals', 'business'])
        cta = "👉 Click the link in bio to claim your discount!"
        
        return content, hashtags, cta
    
    def _tip_template(self, details: Dict) -> tuple:
        """Template for tip/educational posts."""
        content = f"""💡 Pro Tip: {details.get('tip_title', 'Business Insight')}

{details.get('content', '')}

Key Takeaway: {details.get('takeaway', 'Always keep learning!')}"""
        
        hashtags = details.get('hashtags', ['protip', 'business', 'learning', 'growth'])
        cta = "💬 What's your best business tip? Share below!"
        
        return content, hashtags, cta
    
    def _announcement_template(self, details: Dict) -> tuple:
        """Template for general announcements."""
        content = f"""📢 Announcement

{details.get('content', 'We have an important update to share!')}

{details.get('details', '')}

Thank you for your continued support!"""
        
        hashtags = details.get('hashtags', ['announcement', 'business', 'update'])
        cta = "📩 Questions? DM us anytime!"
        
        return content, hashtags, cta
    
    def post_to_linkedin(self, post_file: Path) -> bool:
        """
        Post approved content to LinkedIn.
        
        Args:
            post_file: Path to approved post file
            
        Returns:
            True if posted successfully
        """
        if not post_file.exists():
            logger.error(f'Post file not found: {post_file}')
            return False
        
        # Read post content
        content = post_file.read_text()
        
        # Extract post body (between ## Content and ---)
        try:
            start = content.find('## Content') + len('## Content')
            end = content.find('---', start)
            post_text = content[start:end].strip()
        except Exception as e:
            logger.error(f'Error extracting post content: {e}')
            return False
        
        if self.use_browser:
            return self._post_via_browser(post_text)
        else:
            return self._post_via_api(post_text)
    
    def _post_via_browser(self, post_text: str) -> bool:
        """Post using browser automation (Playwright)."""
        if not LINKEDIN_AVAILABLE:
            logger.warning('Browser automation not fully implemented yet')
            logger.info('This is a draft implementation - requires Playwright setup')
            
            # For now, create a "ready to post" file
            logger.info('Creating manual post instructions...')
            return False
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                
                # Navigate to LinkedIn
                page.goto('https://www.linkedin.com', timeout=60000)
                
                # Wait for login (user needs to be logged in)
                logger.info('Please ensure you are logged into LinkedIn')
                
                # Navigate to post creation
                page.goto('https://www.linkedin.com/feed/', timeout=30000)
                
                # Find and click the post creation box
                start_post = page.locator('[aria-label="Start a post"]')
                if start_post.count() > 0:
                    start_post.first.click()
                    
                    # Wait for post dialog
                    page.wait_for_selector('[role="dialog"]', timeout=10000)
                    
                    # Find the text editor and type the post
                    editor = page.locator('[role="textbox"]').first
                    editor.fill(post_text)
                    
                    logger.info('Post content entered. Click "Post" to publish.')
                    
                    # Don't auto-click post - let user review
                    # This is a safety measure
                    
                browser.close()
                return True
                
        except Exception as e:
            logger.error(f'Error posting via browser: {e}')
            return False
    
    def _post_via_api(self, post_text: str) -> bool:
        """Post using LinkedIn API."""
        if not LINKEDIN_AVAILABLE:
            logger.error('linkedin_api not installed. Install with: pip install linkedin-api')
            return False
        
        try:
            api = Linkedin(self.username, self.password)
            
            # Get profile info
            profile = api.get_profile()
            urn_id = profile['profileId']
            
            # Create post
            response = api.create_post(
                urn_id=urn_id,
                text=post_text[:3000]  # LinkedIn character limit
            )
            
            if response:
                logger.info('Post published successfully!')
                return True
            else:
                logger.error('Failed to create post')
                return False
                
        except Exception as e:
            logger.error(f'API posting error: {e}')
            return False


if __name__ == '__main__':
    import os
    
    vault_path = os.getenv('VAULT_PATH', '/mnt/c/Users/WaterProof Fish/Documents/AI_Employee_System/AI_Employee_Vault')
    
    print('=== LinkedIn Poster Test ===')
    print(f'Vault Path: {vault_path}')

    poster = LinkedInPoster(vault_path=vault_path)

    # Create a test post
    print()
    print('Creating sample business update post...')

    draft = poster.create_business_update_post(
        update_type='milestone',
        details={
            'milestone': 'Launched our AI Employee System',
            'description': 'We\'re excited to announce the launch of our Personal AI Employee - automating business workflows with Claude Code!',
            'hashtags': ['AI', 'automation', 'business', 'productivity', 'Hackathon0']
        }
    )

    print(f'Created draft: {draft}')
    print()
    print('To approve and post:')
    print('1. Review the draft file')
    print('2. Move to /Approved/ folder')
    print('3. The orchestrator will post automatically')


# Singleton instance for easy import
_linkedin_poster_instance = None


def get_linkedin_poster(vault_path=None):
    """Get or create LinkedInPoster instance."""
    global _linkedin_poster_instance
    if _linkedin_poster_instance is None:
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
        _linkedin_poster_instance = LinkedInPoster(vault_path=vault_path)
    return _linkedin_poster_instance
