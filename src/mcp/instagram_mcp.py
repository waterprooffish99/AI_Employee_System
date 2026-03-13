"""
Instagram MCP Server for AI Employee System - Gold Tier

Integrates with Instagram Graph API for posting and analytics.
"""

import logging
import os
import requests
from typing import Any, Optional
from pathlib import Path

from src.utils.audit_logger import get_audit_logger
from src.utils.error_handler import ErrorHandler
from src.utils.retry_manager import retryable


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class InstagramMCP:
    """
    Instagram MCP server for posting and analytics.
    
    Features:
    - Post images with captions
    - Post stories
    - Get media insights
    - List recent media
    """
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        business_account_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        Initialize Instagram MCP.
        
        Args:
            app_id: Facebook App ID (Instagram uses Facebook auth)
            app_secret: Facebook App Secret
            business_account_id: Instagram Business Account ID
            access_token: Access Token
        """
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET")
        self.business_account_id = (
            business_account_id or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        )
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        
        self.base_url = "https://graph.facebook.com/v19.0"
        self.error_handler = ErrorHandler()
        self.audit_logger = get_audit_logger()
        
        if not all([self.app_id, self.business_account_id]):
            logger.warning("Instagram credentials not fully configured")
    
    @retryable(max_retries=3)
    def post_image(
        self,
        image_url: str,
        caption: str,
        is_carousel: bool = False,
        carousel_media: Optional[list] = None,
    ) -> dict:
        """
        Post an image to Instagram.
        
        Args:
            image_url: URL of the image to post
            caption: Post caption
            is_carousel: Whether this is a carousel post
            carousel_media: List of media URLs for carousel
            
        Returns:
            Post result
        """
        try:
            # Step 1: Create media container
            endpoint = f"{self.base_url}/{self.business_account_id}/media"
            
            if is_carousel and carousel_media:
                # Create carousel children first
                children_ids = []
                for media_url in carousel_media:
                    child_params = {
                        "image_url": media_url,
                        "access_token": self.access_token,
                    }
                    response = requests.post(endpoint, params=child_params, timeout=30)
                    response.raise_for_status()
                    children_ids.append(response.json()["id"])
                
                params = {
                    "media_type": "CAROUSEL",
                    "children": ",".join(children_ids),
                    "caption": caption,
                    "access_token": self.access_token,
                }
            else:
                params = {
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.access_token,
                }
            
            response = requests.post(endpoint, params=params, timeout=30)
            response.raise_for_status()
            creation_id = response.json()["id"]
            
            # Step 2: Publish the media
            publish_endpoint = (
                f"{self.base_url}/{self.business_account_id}/media_publish"
            )
            publish_params = {
                "creation_id": creation_id,
                "access_token": self.access_token,
            }
            
            publish_response = requests.post(
                publish_endpoint, params=publish_params, timeout=30
            )
            publish_response.raise_for_status()
            result = publish_response.json()
            
            self.audit_logger.log_action(
                action_type="instagram_post",
                actor="instagram_mcp",
                details={
                    "media_id": result.get("id"),
                    "caption_length": len(caption),
                    "carousel": is_carousel,
                },
            )
            
            return {
                "success": True,
                "media_id": result.get("id"),
                "result": result,
            }
        except Exception as e:
            self.audit_logger.log_error(
                action_type="instagram_post",
                actor="instagram_mcp",
                error=str(e),
                target=self.business_account_id,
            )
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def post_story(
        self,
        image_url: str,
        caption: Optional[str] = None,
    ) -> dict:
        """
        Post an Instagram story.
        
        Args:
            image_url: URL of the story image
            caption: Optional story caption
            
        Returns:
            Post result
        """
        try:
            endpoint = f"{self.base_url}/{self.business_account_id}/media"
            
            params = {
                "image_url": image_url,
                "media_type": "STORIES",
                "access_token": self.access_token,
            }
            
            if caption:
                params["caption"] = caption
            
            response = requests.post(endpoint, params=params, timeout=30)
            response.raise_for_status()
            creation_id = response.json()["id"]
            
            # Publish
            publish_endpoint = (
                f"{self.base_url}/{self.business_account_id}/media_publish"
            )
            publish_params = {
                "creation_id": creation_id,
                "access_token": self.access_token,
            }
            
            publish_response = requests.post(
                publish_endpoint, params=publish_params, timeout=30
            )
            publish_response.raise_for_status()
            result = publish_response.json()
            
            self.audit_logger.log_action(
                action_type="instagram_story",
                actor="instagram_mcp",
                details={"media_id": result.get("id")},
            )
            
            return {
                "success": True,
                "media_id": result.get("id"),
            }
        except Exception as e:
            self.audit_logger.log_error(
                action_type="instagram_story",
                actor="instagram_mcp",
                error=str(e),
            )
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def get_media_insights(self, media_id: str) -> dict:
        """
        Get insights for a media post.
        
        Args:
            media_id: Media ID
            
        Returns:
            Media insights
        """
        try:
            endpoint = f"{self.base_url}/{media_id}/insights"
            
            params = {
                "metric": "impressions,reach,engagement,saved,video_views",
                "access_token": self.access_token,
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "media_id": media_id,
                "insights": result.get("data", []),
            }
        except Exception as e:
            logger.error(f"Failed to get Instagram media insights: {e}")
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def get_recent_media(self, limit: int = 10) -> list[dict]:
        """
        Get recent media posts.
        
        Args:
            limit: Number of posts to retrieve
            
        Returns:
            List of media posts
        """
        try:
            endpoint = f"{self.base_url}/{self.business_account_id}/media"
            
            params = {
                "limit": limit,
                "fields": "id,caption,media_type,media_url,permalink,timestamp",
                "access_token": self.access_token,
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Instagram media: {e}")
            return []
    
    def get_account_insights(self) -> dict:
        """
        Get account-level insights.
        
        Returns:
            Account insights
        """
        try:
            endpoint = f"{self.base_url}/{self.business_account_id}/insights"
            
            params = {
                "metric": "follower_count,profile_views,reach,impressions",
                "period": "day",
                "access_token": self.access_token,
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "business_account_id": self.business_account_id,
                "insights": result.get("data", []),
            }
        except Exception as e:
            logger.error(f"Failed to get Instagram account insights: {e}")
            return {"success": False, "error": str(e)}
    
    def get_engagement_summary(self, days: int = 7) -> dict:
        """
        Get engagement summary for specified period.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Engagement summary
        """
        media = self.get_recent_media(limit=25)
        
        total_impressions = 0
        total_reach = 0
        total_engagement = 0
        total_saved = 0
        
        for post in media:
            insights = self.get_media_insights(post["id"])
            if insights.get("success"):
                for metric in insights.get("insights", []):
                    if metric["name"] == "impressions":
                        total_impressions += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
                    elif metric["name"] == "reach":
                        total_reach += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
                    elif metric["name"] == "engagement":
                        total_engagement += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
                    elif metric["name"] == "saved":
                        total_saved += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
        
        return {
            "success": True,
            "period_days": days,
            "media_analyzed": len(media),
            "total_impressions": total_impressions,
            "total_reach": total_reach,
            "total_engagement": total_engagement,
            "total_saved": total_saved,
            "avg_engagement_rate": (
                total_engagement / total_reach * 100 if total_reach > 0 else 0
            ),
        }


# Singleton instance
_instagram_mcp: Optional[InstagramMCP] = None


def get_instagram_mcp() -> InstagramMCP:
    """Get or create Instagram MCP instance."""
    global _instagram_mcp
    if _instagram_mcp is None:
        _instagram_mcp = InstagramMCP()
    return _instagram_mcp
