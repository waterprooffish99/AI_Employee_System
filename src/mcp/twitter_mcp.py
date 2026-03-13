"""
Twitter/X MCP Server for AI Employee System - Gold Tier

Integrates with Twitter API v2 for posting and analytics.
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


class TwitterMCP:
    """
    Twitter/X MCP server for posting and analytics.
    
    Features:
    - Post tweets
    - Create threads
    - Get tweet analytics
    - Monitor mentions
    - Search mentions
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
    ):
        """
        Initialize Twitter MCP.
        
        Args:
            api_key: Twitter API Key
            api_secret: Twitter API Secret
            access_token: Access Token
            access_token_secret: Access Token Secret
            bearer_token: Bearer Token for v2 API
        """
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = (
            access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        
        self.base_url = "https://api.twitter.com/2"
        self.base_url_v1 = "https://api.twitter.com/1.1"
        self.error_handler = ErrorHandler()
        self.audit_logger = get_audit_logger()
        
        if not all([self.api_key, self.api_secret]):
            logger.warning("Twitter credentials not fully configured")
    
    def _get_auth_headers(self) -> dict:
        """Get authentication headers for API requests."""
        if self.bearer_token:
            return {"Authorization": f"Bearer {self.bearer_token}"}
        return {}
    
    @retryable(max_retries=3)
    def post_tweet(
        self,
        text: str,
        media_ids: Optional[list] = None,
        reply_to: Optional[str] = None,
    ) -> dict:
        """
        Post a tweet.
        
        Args:
            text: Tweet text (max 280 chars)
            media_ids: Optional list of media IDs to attach
            reply_to: Optional tweet ID to reply to
            
        Returns:
            Post result
        """
        try:
            endpoint = f"{self.base_url}/tweets"
            
            payload = {"text": text}
            
            if media_ids:
                payload["media"] = {"media_ids": media_ids}
            if reply_to:
                payload["reply"] = {"in_reply_to_tweet_id": reply_to}
            
            headers = self._get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            
            self.audit_logger.log_action(
                action_type="twitter_post",
                actor="twitter_mcp",
                details={
                    "tweet_id": result.get("data", {}).get("id"),
                    "text_length": len(text),
                },
            )
            
            return {
                "success": True,
                "tweet_id": result.get("data", {}).get("id"),
                "text": text,
            }
        except Exception as e:
            self.audit_logger.log_error(
                action_type="twitter_post",
                actor="twitter_mcp",
                error=str(e),
                target="twitter",
            )
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def create_thread(self, tweets: list[str]) -> dict:
        """
        Create a tweet thread.
        
        Args:
            tweets: List of tweet texts in order
            
        Returns:
            Thread result with all tweet IDs
        """
        try:
            tweet_ids = []
            reply_to = None
            
            for i, text in enumerate(tweets):
                result = self.post_tweet(text, reply_to=reply_to)
                if result.get("success"):
                    tweet_id = result.get("tweet_id")
                    tweet_ids.append(tweet_id)
                    reply_to = tweet_id
                else:
                    return {
                        "success": False,
                        "error": f"Failed at tweet {i + 1}: {result.get('error')}",
                        "partial_ids": tweet_ids,
                    }
            
            self.audit_logger.log_action(
                action_type="twitter_thread",
                actor="twitter_mcp",
                details={
                    "thread_length": len(tweets),
                    "tweet_ids": tweet_ids,
                },
            )
            
            return {
                "success": True,
                "tweet_ids": tweet_ids,
                "thread_length": len(tweets),
            }
        except Exception as e:
            self.audit_logger.log_error(
                action_type="twitter_thread",
                actor="twitter_mcp",
                error=str(e),
            )
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def get_tweet_analytics(self, tweet_id: str) -> dict:
        """
        Get analytics for a tweet.
        
        Args:
            tweet_id: Tweet ID
            
        Returns:
            Tweet analytics
        """
        try:
            endpoint = f"{self.base_url}/tweets/{tweet_id}"
            
            params = {
                "tweet.fields": "public_metrics,created_at,author_id",
            }
            
            headers = self._get_auth_headers()
            response = requests.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            
            metrics = result.get("data", {}).get("public_metrics", {})
            
            return {
                "success": True,
                "tweet_id": tweet_id,
                "metrics": {
                    "impressions": metrics.get("impression_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get Twitter analytics: {e}")
            return {"success": False, "error": str(e)}
    
    @retryable(max_retries=3)
    def get_mentions(self, limit: int = 10) -> list[dict]:
        """
        Get recent mentions.
        
        Args:
            limit: Number of mentions to retrieve
            
        Returns:
            List of mention tweets
        """
        try:
            # Need user ID first - using 'me' endpoint
            me_endpoint = f"{self.base_url}/users/me"
            headers = self._get_auth_headers()
            
            me_response = requests.get(
                me_endpoint,
                headers=headers,
                timeout=30,
            )
            me_response.raise_for_status()
            user_id = me_response.json().get("data", {}).get("id")
            
            if not user_id:
                return []
            
            endpoint = f"{self.base_url}/users/{user_id}/mentions"
            
            params = {
                "max_results": min(limit, 100),
                "tweet.fields": "created_at,author_id,public_metrics",
            }
            
            response = requests.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Twitter mentions: {e}")
            return []
    
    @retryable(max_retries=3)
    def search_mentions(
        self,
        query: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Search for tweets mentioning the account.
        
        Args:
            query: Search query
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            limit: Number of results
            
        Returns:
            List of matching tweets
        """
        try:
            endpoint = f"{self.base_url}/tweets/search/recent"
            
            params = {
                "query": query,
                "max_results": min(limit, 100),
                "tweet.fields": "created_at,author_id,public_metrics",
            }
            
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            
            headers = self._get_auth_headers()
            response = requests.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to search Twitter: {e}")
            return []
    
    def get_engagement_summary(self, days: int = 7) -> dict:
        """
        Get engagement summary for specified period.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Engagement summary
        """
        # Get user's recent tweets
        try:
            me_endpoint = f"{self.base_url}/users/me"
            headers = self._get_auth_headers()
            
            me_response = requests.get(
                me_endpoint,
                headers=headers,
                timeout=30,
            )
            me_response.raise_for_status()
            user_id = me_response.json().get("data", {}).get("id")
            
            if not user_id:
                return {"success": False, "error": "Could not get user ID"}
            
            tweets_endpoint = f"{self.base_url}/users/{user_id}/tweets"
            params = {
                "max_results": min(100, days * 5),  # Approximate
                "tweet.fields": "created_at,public_metrics",
            }
            
            tweets_response = requests.get(
                tweets_endpoint,
                params=params,
                headers=headers,
                timeout=30,
            )
            tweets_response.raise_for_status()
            tweets = tweets_response.json().get("data", [])
            
            # Filter by date and aggregate metrics
            cutoff = datetime.now() - timedelta(days=days)
            total_impressions = 0
            total_likes = 0
            total_retweets = 0
            total_replies = 0
            
            for tweet in tweets:
                created = datetime.fromisoformat(
                    tweet["created_at"].replace("Z", "+00:00")
                )
                if created.replace(tzinfo=None) >= cutoff:
                    metrics = tweet.get("public_metrics", {})
                    total_impressions += metrics.get("impression_count", 0)
                    total_likes += metrics.get("like_count", 0)
                    total_retweets += metrics.get("retweet_count", 0)
                    total_replies += metrics.get("reply_count", 0)
            
            return {
                "success": True,
                "period_days": days,
                "tweets_analyzed": len(tweets),
                "total_impressions": total_impressions,
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "total_replies": total_replies,
                "avg_engagement_rate": (
                    (total_likes + total_retweets + total_replies)
                    / total_impressions * 100
                    if total_impressions > 0
                    else 0
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get Twitter engagement summary: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
_twitter_mcp: Optional[TwitterMCP] = None


def get_twitter_mcp() -> TwitterMCP:
    """Get or create Twitter MCP instance."""
    global _twitter_mcp
    if _twitter_mcp is None:
        _twitter_mcp = TwitterMCP()
    return _twitter_mcp
