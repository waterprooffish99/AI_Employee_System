"""
Facebook MCP Server for AI Employee System - Gold Tier

Integrates with Facebook Graph API for posting and analytics.
"""

import logging
import os
import requests
from typing import Any, Optional
from datetime import datetime, timedelta

from src.utils.audit_logger import get_audit_logger
from src.utils.error_handler import ErrorHandler
from src.utils.retry_manager import retryable


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class FacebookMCP:
    """
    Facebook MCP server for posting and analytics.
    
    Features:
    - Post to Facebook pages
    - Get post insights
    - List page posts
    - Monitor comments
    """
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        page_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        Initialize Facebook MCP.
        
        Args:
            app_id: Facebook App ID
            app_secret: Facebook App Secret
            page_id: Facebook Page ID
            access_token: Page Access Token
        """
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        
        self.base_url = "https://graph.facebook.com/v19.0"
        self.error_handler = ErrorHandler()
        self.audit_logger = get_audit_logger()
        
        # Validate configuration
        if not all([self.app_id, self.app_secret, self.page_id]):
            logger.warning("Facebook credentials not fully configured")
    
    @retryable(max_retries=3)
    def post_to_page(
        self,
        message: str,
        link: Optional[str] = None,
        photo_url: Optional[str] = None,
        scheduled_time: Optional[str] = None,
    ) -> dict:
        """
        Post to Facebook page.
        
        Args:
            message: Post message
            link: Optional link to share
            photo_url: Optional photo URL
            scheduled_time: Optional scheduled publish time
            
        Returns:
            Post result
        """
        try:
            endpoint = f"{self.base_url}/{self.page_id}/feed"
            
            params = {
                "message": message,
                "access_token": self.access_token,
            }
            
            if link:
                params["link"] = link
            if photo_url:
                params["picture"] = photo_url
            if scheduled_time:
                params["scheduled_publish_time"] = scheduled_time
                params["published"] = False
            
            response = requests.post(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            self.audit_logger.log_action(
                action_type="facebook_post",
                actor="facebook_mcp",
                details={
                    "post_id": result.get("id"),
                    "message_length": len(message),
                    "scheduled": scheduled_time is not None,
                },
            )
            
            return {
                "success": True,
                "post_id": result.get("id"),
                "result": result,
            }
        except Exception as e:
            self.audit_logger.log_error(
                action_type="facebook_post",
                actor="facebook_mcp",
                error=str(e),
                target=self.page_id,
            )
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def get_post_insights(self, post_id: str) -> dict:
        """
        Get insights for a post.
        
        Args:
            post_id: Post ID
            
        Returns:
            Post insights
        """
        try:
            endpoint = f"{self.base_url}/{post_id}/insights"
            
            params = {
                "metric": "post_impressions,post_engagements,post_clicks,post_shares",
                "access_token": self.access_token,
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "post_id": post_id,
                "insights": result.get("data", []),
            }
        except Exception as e:
            logger.error(f"Failed to get Facebook post insights: {e}")
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def get_page_posts(self, limit: int = 10) -> list[dict]:
        """
        Get recent page posts.
        
        Args:
            limit: Number of posts to retrieve
            
        Returns:
            List of posts
        """
        try:
            endpoint = f"{self.base_url}/{self.page_id}/posts"
            
            params = {
                "limit": limit,
                "access_token": self.access_token,
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Facebook posts: {e}")
            return []
    
    @retryable(max_retries=3)
    def get_page_insights(self) -> dict:
        """
        Get page-level insights.
        
        Returns:
            Page insights
        """
        try:
            endpoint = f"{self.base_url}/{self.page_id}/insights"
            
            params = {
                "metric": "page_fan_adds,page_impressions,page_engaged_users,page_post_engagements",
                "period": "day",
                "access_token": self.access_token,
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "page_id": self.page_id,
                "insights": result.get("data", []),
            }
        except Exception as e:
            logger.error(f"Failed to get Facebook page insights: {e}")
            return {"success": False, "error": str(e)}
    
    def get_engagement_summary(self, days: int = 7) -> dict:
        """
        Get engagement summary for specified period.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Engagement summary
        """
        posts = self.get_page_posts(limit=50)
        
        total_impressions = 0
        total_engagements = 0
        total_clicks = 0
        total_shares = 0
        
        for post in posts:
            insights = self.get_post_insights(post["id"])
            if insights.get("success"):
                for metric in insights.get("insights", []):
                    if metric["name"] == "post_impressions":
                        total_impressions += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
                    elif metric["name"] == "post_engagements":
                        total_engagements += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
                    elif metric["name"] == "post_clicks":
                        total_clicks += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
                    elif metric["name"] == "post_shares":
                        total_shares += sum(
                            v.get("value", 0) for v in metric.get("values", [])
                        )
        
        return {
            "success": True,
            "period_days": days,
            "posts_analyzed": len(posts),
            "total_impressions": total_impressions,
            "total_engagements": total_engagements,
            "total_clicks": total_clicks,
            "total_shares": total_shares,
            "avg_engagement_rate": (
                total_engagements / total_impressions * 100
                if total_impressions > 0
                else 0
            ),
        }


# Singleton instance
_facebook_mcp: Optional[FacebookMCP] = None


def get_facebook_mcp() -> FacebookMCP:
    """Get or create Facebook MCP instance."""
    global _facebook_mcp
    if _facebook_mcp is None:
        _facebook_mcp = FacebookMCP()
    return _facebook_mcp
