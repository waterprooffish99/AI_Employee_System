"""
Error Handler for AI Employee System - Gold Tier

Provides error categorization, handling strategies, and graceful degradation.
"""

import logging
from enum import Enum
from typing import Any, Optional, Callable
from functools import wraps


class ErrorCategory(Enum):
    """Categories of errors for handling strategies."""
    
    TRANSIENT = "transient"  # Temporary, retry will likely succeed
    AUTHENTICATION = "authentication"  # Auth failure, needs credential refresh
    RATE_LIMIT = "rate_limit"  # API rate limit, needs backoff
    VALIDATION = "validation"  # Invalid input, retry won't help
    CRITICAL = "critical"  # System failure, needs immediate attention
    NETWORK = "network"  # Network connectivity issues
    TIMEOUT = "timeout"  # Request timeout
    NOT_FOUND = "not_found"  # Resource not found
    PERMISSION = "permission"  # Insufficient permissions


class ErrorHandler:
    """
    Centralized error handler for AI Employee System.
    
    Features:
    - Error categorization
    - Appropriate handling strategy per category
    - User notification on critical errors
    - Graceful degradation
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.
        
        Args:
            logger: Logger instance (uses default if None)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_handlers: dict[ErrorCategory, Callable] = {
            ErrorCategory.TRANSIENT: self._handle_transient,
            ErrorCategory.AUTHENTICATION: self._handle_authentication,
            ErrorCategory.RATE_LIMIT: self._handle_rate_limit,
            ErrorCategory.VALIDATION: self._handle_validation,
            ErrorCategory.CRITICAL: self._handle_critical,
            ErrorCategory.NETWORK: self._handle_network,
            ErrorCategory.TIMEOUT: self._handle_timeout,
            ErrorCategory.NOT_FOUND: self._handle_not_found,
            ErrorCategory.PERMISSION: self._handle_permission,
        }
    
    def categorize(self, error: Exception) -> ErrorCategory:
        """
        Categorize an error.
        
        Args:
            error: The exception to categorize
            
        Returns:
            ErrorCategory enum value
        """
        error_name = type(error).__name__
        error_str = str(error).lower()
        
        # Authentication errors
        if any(x in error_name.lower() for x in ["auth", "unauthorized", "forbidden"]):
            return ErrorCategory.AUTHENTICATION
        if any(x in error_str for x in ["token", "credential", "api key", "authentication"]):
            return ErrorCategory.AUTHENTICATION
        
        # Rate limit errors
        if any(x in error_name.lower() for x in ["rate", "limit", "throttle"]):
            return ErrorCategory.RATE_LIMIT
        if "rate limit" in error_str or "too many requests" in error_str:
            return ErrorCategory.RATE_LIMIT
        
        # Validation errors
        if any(x in error_name.lower() for x in ["validation", "invalid", "format"]):
            return ErrorCategory.VALIDATION
        if any(x in error_str for x in ["invalid", "validation", "format", "required"]):
            return ErrorCategory.VALIDATION
        
        # Network errors
        if any(x in error_name.lower() for x in ["connection", "network", "socket"]):
            return ErrorCategory.NETWORK
        if any(x in error_str for x in ["connection", "network", "socket", "dns"]):
            return ErrorCategory.NETWORK
        
        # Timeout errors
        if any(x in error_name.lower() for x in ["timeout", "timed out"]):
            return ErrorCategory.TIMEOUT
        if "timeout" in error_str or "timed out" in error_str:
            return ErrorCategory.TIMEOUT
        
        # Not found errors
        if error_name.lower() in ["filenotfounderror", "keyerror", "indexerror"]:
            return ErrorCategory.NOT_FOUND
        if "not found" in error_str or "404" in error_str:
            return ErrorCategory.NOT_FOUND
        
        # Permission errors
        if any(x in error_name.lower() for x in ["permission", "access"]):
            return ErrorCategory.PERMISSION
        if any(x in error_str for x in ["permission", "access denied", "forbidden"]):
            return ErrorCategory.PERMISSION
        
        # Critical errors (system-level)
        if any(x in error_name.lower() for x in ["system", "fatal", "critical"]):
            return ErrorCategory.CRITICAL
        
        # Default to transient (retryable)
        return ErrorCategory.TRANSIENT
    
    def handle(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Handle an error using the appropriate strategy.
        
        Args:
            error: The exception to handle
            context: Additional context about the error
            
        Returns:
            Handling result dictionary
        """
        category = self.categorize(error)
        handler = self.error_handlers.get(category, self._handle_transient)
        
        self.logger.warning(
            f"Error occurred: {type(error).__name__} - {str(error)}",
            extra={"category": category.value, "context": context}
        )
        
        return handler(error, context)
    
    def _handle_transient(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle transient errors - retry recommended."""
        return {
            "category": ErrorCategory.TRANSIENT.value,
            "action": "retry",
            "message": f"Transient error: {str(error)}",
            "retry_recommended": True,
            "user_notification": False,
        }
    
    def _handle_authentication(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle authentication errors - credential refresh needed."""
        return {
            "category": ErrorCategory.AUTHENTICATION.value,
            "action": "refresh_credentials",
            "message": f"Authentication failed: {str(error)}",
            "retry_recommended": False,
            "user_notification": True,
            "notification_priority": "high",
        }
    
    def _handle_rate_limit(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle rate limit errors - backoff and queue."""
        return {
            "category": ErrorCategory.RATE_LIMIT.value,
            "action": "backoff_and_queue",
            "message": f"Rate limit exceeded: {str(error)}",
            "retry_recommended": True,
            "retry_delay_seconds": 60,
            "user_notification": False,
        }
    
    def _handle_validation(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle validation errors - log and skip."""
        return {
            "category": ErrorCategory.VALIDATION.value,
            "action": "log_and_skip",
            "message": f"Validation error: {str(error)}",
            "retry_recommended": False,
            "user_notification": False,
        }
    
    def _handle_critical(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle critical errors - stop and alert."""
        return {
            "category": ErrorCategory.CRITICAL.value,
            "action": "stop_and_alert",
            "message": f"Critical error: {str(error)}",
            "retry_recommended": False,
            "user_notification": True,
            "notification_priority": "critical",
        }
    
    def _handle_network(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle network errors - retry with backoff."""
        return {
            "category": ErrorCategory.NETWORK.value,
            "action": "retry_with_backoff",
            "message": f"Network error: {str(error)}",
            "retry_recommended": True,
            "retry_delay_seconds": 5,
            "user_notification": False,
        }
    
    def _handle_timeout(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle timeout errors - retry with longer timeout."""
        return {
            "category": ErrorCategory.TIMEOUT.value,
            "action": "retry_with_longer_timeout",
            "message": f"Timeout error: {str(error)}",
            "retry_recommended": True,
            "retry_delay_seconds": 10,
            "user_notification": False,
        }
    
    def _handle_not_found(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle not found errors - log and continue."""
        return {
            "category": ErrorCategory.NOT_FOUND.value,
            "action": "log_and_continue",
            "message": f"Not found error: {str(error)}",
            "retry_recommended": False,
            "user_notification": False,
        }
    
    def _handle_permission(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Handle permission errors - alert user."""
        return {
            "category": ErrorCategory.PERMISSION.value,
            "action": "alert_user",
            "message": f"Permission error: {str(error)}",
            "retry_recommended": False,
            "user_notification": True,
            "notification_priority": "high",
        }


def with_error_handling(
    fallback_value: Any = None,
    log_errors: bool = True,
):
    """
    Decorator for automatic error handling.
    
    Args:
        fallback_value: Value to return on error
        log_errors: Whether to log errors
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            error_handler = ErrorHandler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logging.getLogger(__name__).error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )
                result = error_handler.handle(e)
                if result.get("user_notification"):
                    logging.getLogger(__name__).warning(
                        f"User notification required: {result['message']}"
                    )
                return fallback_value
        return wrapper
    return decorator
