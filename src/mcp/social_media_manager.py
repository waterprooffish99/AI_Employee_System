"""
Unified Social Media Manager for AI Employee System - Gold Tier

Provides a unified interface for cross-platform social media management.
"""

import logging
from typing import Any, Optional
from datetime import datetime

from src.mcp.facebook_mcp import FacebookMCP, get_facebook_mcp
from src.mcp.instagram_mcp import InstagramMCP, get_instagram_mcp
from src.mcp.twitter_mcp import TwitterMCP, get_twitter_mcp
from src.utils.audit_logger import get_audit_logger


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class SocialMediaManager:
    """
    Unified social media manager for cross-platform posting and analytics.
    
    Features:
    - Cross-platform posting
    - Unified analytics
    - Platform-specific optimizations
    - Engagement summaries
    """
    
    def __init__(
        self,
        facebook: Optional[FacebookMCP] = None,
        instagram: Optional[InstagramMCP] = None,
        twitter: Optional[TwitterMCP] = None,
    ):
        """
        Initialize social media manager.
        
        Args:
            facebook: Facebook MCP instance
            instagram: Instagram MCP instance
            twitter: Twitter MCP instance
        """
        self.facebook = facebook or get_facebook_mcp()
        self.instagram = instagram or get_instagram_mcp()
        self.twitter = twitter or get_twitter_mcp()
        self.audit_logger = get_audit_logger()
    
    def post_to_all(
        self,
        message: str,
        platforms: Optional[list[str]] = None,
        image_url: Optional[str] = None,
        link: Optional[str] = None,
    ) -> dict:
        """
        Post to all configured platforms.
        
        Args:
            message: Post message
            platforms: List of platforms (facebook, instagram, twitter)
            image_url: Optional image URL
            link: Optional link
            
        Returns:
            Results from each platform
        """
        if platforms is None:
            platforms = ["facebook", "instagram", "twitter"]
        
        results = {}
        
        # Twitter - text-focused
        if "twitter" in platforms:
            try:
                # Truncate for Twitter if needed
                twitter_text = message[:280]
                result = self.twitter.post_tweet(twitter_text)
                results["twitter"] = result
            except Exception as e:
                results["twitter"] = {"success": False, "error": str(e)}
        
        # Facebook - supports longer posts
        if "facebook" in platforms:
            try:
                result = self.facebook.post_to_page(
                    message=message,
                    link=link,
                    photo_url=image_url,
                )
                results["facebook"] = result
            except Exception as e:
                results["facebook"] = {"success": False, "error": str(e)}
        
        # Instagram - image-focused
        if "instagram" in platforms and image_url:
            try:
                result = self.instagram.post_image(
                    image_url=image_url,
                    caption=message,
                )
                results["instagram"] = result
            except Exception as e:
                results["instagram"] = {"success": False, "error": str(e)}
        
        # Log the cross-platform post
        self.audit_logger.log_action(
            action_type="social_media_cross_post",
            actor="social_media_manager",
            details={
                "platforms": platforms,
                "message_length": len(message),
                "results": {
                    k: "success" if v.get("success") else "failed"
                    for k, v in results.items()
                },
            },
        )
        
        return {
            "success": all(r.get("success", False) for r in results.values()),
            "results": results,
        }
    
    def get_unified_analytics(self, days: int = 7) -> dict:
        """
        Get unified analytics from all platforms.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Unified analytics
        """
        analytics = {
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "platforms": {},
            "totals": {
                "impressions": 0,
                "engagements": 0,
                "followers_gained": 0,
            },
        }
        
        # Facebook analytics
        try:
            fb_summary = self.facebook.get_engagement_summary(days=days)
            if fb_summary.get("success"):
                analytics["platforms"]["facebook"] = {
                    "impressions": fb_summary.get("total_impressions", 0),
                    "engagements": fb_summary.get("total_engagements", 0),
                    "engagement_rate": fb_summary.get("avg_engagement_rate", 0),
                    "posts": fb_summary.get("posts_analyzed", 0),
                }
                analytics["totals"]["impressions"] += fb_summary.get(
                    "total_impressions", 0
                )
                analytics["totals"]["engagements"] += fb_summary.get(
                    "total_engagements", 0
                )
        except Exception as e:
            logger.error(f"Failed to get Facebook analytics: {e}")
            analytics["platforms"]["facebook"] = {"error": str(e)}
        
        # Instagram analytics
        try:
            ig_summary = self.instagram.get_engagement_summary(days=days)
            if ig_summary.get("success"):
                analytics["platforms"]["instagram"] = {
                    "impressions": ig_summary.get("total_impressions", 0),
                    "reach": ig_summary.get("total_reach", 0),
                    "engagements": ig_summary.get("total_engagement", 0),
                    "engagement_rate": ig_summary.get("avg_engagement_rate", 0),
                    "posts": ig_summary.get("media_analyzed", 0),
                }
                analytics["totals"]["impressions"] += ig_summary.get(
                    "total_impressions", 0
                )
                analytics["totals"]["engagements"] += ig_summary.get(
                    "total_engagement", 0
                )
        except Exception as e:
            logger.error(f"Failed to get Instagram analytics: {e}")
            analytics["platforms"]["instagram"] = {"error": str(e)}
        
        # Twitter analytics
        try:
            tw_summary = self.twitter.get_engagement_summary(days=days)
            if tw_summary.get("success"):
                analytics["platforms"]["twitter"] = {
                    "impressions": tw_summary.get("total_impressions", 0),
                    "likes": tw_summary.get("total_likes", 0),
                    "retweets": tw_summary.get("total_retweets", 0),
                    "replies": tw_summary.get("total_replies", 0),
                    "engagement_rate": tw_summary.get("avg_engagement_rate", 0),
                    "tweets": tw_summary.get("tweets_analyzed", 0),
                }
                analytics["totals"]["impressions"] += tw_summary.get(
                    "total_impressions", 0
                )
                analytics["totals"]["engagements"] += (
                    tw_summary.get("total_likes", 0)
                    + tw_summary.get("total_retweets", 0)
                    + tw_summary.get("total_replies", 0)
                )
        except Exception as e:
            logger.error(f"Failed to get Twitter analytics: {e}")
            analytics["platforms"]["twitter"] = {"error": str(e)}
        
        # Calculate overall engagement rate
        if analytics["totals"]["impressions"] > 0:
            analytics["totals"]["overall_engagement_rate"] = (
                analytics["totals"]["engagements"]
                / analytics["totals"]["impressions"]
                * 100
            )
        else:
            analytics["totals"]["overall_engagement_rate"] = 0
        
        return analytics
    
    def generate_summary_report(self, days: int = 7) -> str:
        """
        Generate a human-readable summary report.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Markdown-formatted summary report
        """
        analytics = self.get_unified_analytics(days=days)
        
        report = f"""# Social Media Summary Report

**Period**: Last {days} days
**Generated**: {analytics['generated_at']}

## Overall Performance

| Metric | Value |
|--------|-------|
| Total Impressions | {analytics['totals']['impressions']:,} |
| Total Engagements | {analytics['totals']['engagements']:,} |
| Overall Engagement Rate | {analytics['totals']['overall_engagement_rate']:.2f}% |

## Platform Breakdown

"""
        for platform, data in analytics["platforms"].items():
            if "error" in data:
                report += f"### {platform.title()}\n- Error: {data['error']}\n\n"
            else:
                report += f"### {platform.title()}\n"
                report += f"- Impressions: {data.get('impressions', 0):,}\n"
                if "reach" in data:
                    report += f"- Reach: {data.get('reach', 0):,}\n"
                report += f"- Engagements: {data.get('engagements', 0):,}\n"
                report += f"- Engagement Rate: {data.get('engagement_rate', 0):.2f}%\n"
                if "posts" in data:
                    report += f"- Posts: {data.get('posts', 0)}\n"
                report += "\n"
        
        report += "---\n*Generated by AI Employee - Gold Tier*\n"
        
        return report


# Singleton instance
_social_media_manager: Optional[SocialMediaManager] = None


def get_social_media_manager() -> SocialMediaManager:
    """Get or create social media manager instance."""
    global _social_media_manager
    if _social_media_manager is None:
        _social_media_manager = SocialMediaManager()
    return _social_media_manager
