"""
Retry Manager for AI Employee System - Gold Tier

Provides exponential backoff with jitter for retry operations.
"""

import asyncio
import logging
import os
import random
import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

from retrying import retry


logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryManager:
    """
    Retry manager with exponential backoff and jitter.
    
    Features:
    - Exponential backoff
    - Random jitter
    - Max retries configuration
    - Custom retry conditions
    - Sync and async support
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_base: float = 2.0,
        backoff_max: float = 60.0,
        jitter: float = 1.0,
    ):
        """
        Initialize retry manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_base: Base for exponential backoff (seconds)
            backoff_max: Maximum backoff time (seconds)
            jitter: Jitter factor (0-1, adds randomness to backoff)
        """
        self.max_retries = int(os.getenv("MAX_RETRIES", max_retries))
        self.backoff_base = float(
            os.getenv("RETRY_BACKOFF_BASE", backoff_base)
        )
        self.backoff_max = float(
            os.getenv("RETRY_BACKOFF_MAX", backoff_max)
        )
        self.jitter = float(
            os.getenv("RETRY_BACKOFF_JITTER", jitter)
        )
    
    def calculate_backoff(self, attempt: int) -> float:
        """
        Calculate backoff time for an attempt.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Backoff time in seconds
        """
        # Exponential backoff
        backoff = self.backoff_base ** attempt
        
        # Cap at maximum
        backoff = min(backoff, self.backoff_max)
        
        # Add jitter
        jitter_range = backoff * self.jitter
        jitter_value = random.uniform(-jitter_range, jitter_range)
        backoff = backoff + jitter_value
        
        # Ensure non-negative
        return max(0, backoff)
    
    def retry_with_backoff(
        self,
        func: Callable[..., T],
        *args,
        max_retries: Optional[int] = None,
        retry_on_exception: Optional[Callable[[Exception], bool]] = None,
        **kwargs,
    ) -> T:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            max_retries: Override default max retries
            retry_on_exception: Custom exception filter (return True to retry)
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func
            
        Raises:
            Last exception if all retries fail
        """
        retries = max_retries or self.max_retries
        last_exception = None
        
        for attempt in range(retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Check if we should retry
                if retry_on_exception and not retry_on_exception(e):
                    raise
                
                # Check if we have retries left
                if attempt >= retries:
                    raise
                
                # Calculate backoff
                backoff = self.calculate_backoff(attempt)
                
                logger.warning(
                    f"Attempt {attempt + 1}/{retries + 1} failed: {type(e).__name__}. "
                    f"Retrying in {backoff:.2f}s"
                )
                
                time.sleep(backoff)
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry loop exit")
    
    async def retry_with_backoff_async(
        self,
        func: Callable[..., T],
        *args,
        max_retries: Optional[int] = None,
        retry_on_exception: Optional[Callable[[Exception], bool]] = None,
        **kwargs,
    ) -> T:
        """
        Execute an async function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            max_retries: Override default max retries
            retry_on_exception: Custom exception filter
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func
            
        Raises:
            Last exception if all retries fail
        """
        retries = max_retries or self.max_retries
        last_exception = None
        
        for attempt in range(retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Check if we should retry
                if retry_on_exception and not retry_on_exception(e):
                    raise
                
                # Check if we have retries left
                if attempt >= retries:
                    raise
                
                # Calculate backoff
                backoff = self.calculate_backoff(attempt)
                
                logger.warning(
                    f"Attempt {attempt + 1}/{retries + 1} failed: {type(e).__name__}. "
                    f"Retrying in {backoff:.2f}s"
                )
                
                await asyncio.sleep(backoff)
        
        # Should never reach here
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry loop exit")
    
    def should_retry_exception(
        self,
        exception: Exception,
        retryable_exceptions: Optional[tuple[type[Exception], ...]] = None,
    ) -> bool:
        """
        Determine if an exception should be retried.
        
        Args:
            exception: The exception to check
            retryable_exceptions: Tuple of exception types to retry
            
        Returns:
            True if should retry
        """
        if retryable_exceptions:
            return isinstance(exception, retryable_exceptions)
        
        # Default: retry on most exceptions
        non_retryable = (
            KeyboardInterrupt,
            SystemExit,
            NotImplementedError,
        )
        return not isinstance(exception, non_retryable)


def retryable(
    max_retries: int = 3,
    backoff_base: float = 2.0,
    backoff_max: float = 60.0,
    jitter: float = 1.0,
    retry_on_exception: Optional[Callable[[Exception], bool]] = None,
):
    """
    Decorator for making functions retryable.
    
    Args:
        max_retries: Maximum retry attempts
        backoff_base: Base for exponential backoff
        backoff_max: Maximum backoff time
        jitter: Jitter factor
        retry_on_exception: Custom exception filter
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        retry_manager = RetryManager(
            max_retries=max_retries,
            backoff_base=backoff_base,
            backoff_max=backoff_max,
            jitter=jitter,
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return retry_manager.retry_with_backoff(
                func,
                *args,
                retry_on_exception=retry_on_exception,
                **kwargs,
            )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await retry_manager.retry_with_backoff_async(
                func,
                *args,
                retry_on_exception=retry_on_exception,
                **kwargs,
            )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


# Default retry manager instance
_default_retry_manager: Optional[RetryManager] = None


def get_retry_manager() -> RetryManager:
    """Get or create the default retry manager."""
    global _default_retry_manager
    if _default_retry_manager is None:
        _default_retry_manager = RetryManager()
    return _default_retry_manager


def retry_function(
    func: Callable,
    *args,
    max_retries: Optional[int] = None,
    **kwargs,
) -> Any:
    """
    Retry a function using the default retry manager.
    
    Args:
        func: Function to retry
        *args: Arguments for func
        max_retries: Override max retries
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of func
    """
    return get_retry_manager().retry_with_backoff(
        func,
        *args,
        max_retries=max_retries,
        **kwargs,
    )


async def retry_function_async(
    func: Callable,
    *args,
    max_retries: Optional[int] = None,
    **kwargs,
) -> Any:
    """
    Retry an async function using the default retry manager.
    
    Args:
        func: Async function to retry
        *args: Arguments for func
        max_retries: Override max retries
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of func
    """
    return await get_retry_manager().retry_with_backoff_async(
        func,
        *args,
        max_retries=max_retries,
        **kwargs,
    )
