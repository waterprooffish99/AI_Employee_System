"""
Audit Logger for AI Employee System - Gold Tier

Provides comprehensive, immutable audit logging for all system actions.
All logs are structured JSON with daily rotation and 90-day retention.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from logging.handlers import TimedRotatingFileHandler


class AuditLogger:
    """
    Comprehensive audit logger for AI Employee System.
    
    Features:
    - Structured JSON logging
    - Daily log rotation
    - Immutable log entries
    - 90-day retention policy
    - Query interface
    """
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        retention_days: int = 90,
        log_level: str = "INFO",
    ):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory to store audit logs
            retention_days: Number of days to retain logs
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir) if log_dir else Path(
            os.getenv(
                "AUDIT_LOG_DIR",
                "./AI_Employee_Vault/Audit_Logs"
            )
        )
        self.retention_days = retention_days
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(self.log_level)
        self.logger.propagate = False
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create timed rotating file handler
        log_file = self.log_dir / "audit.log"
        handler = TimedRotatingFileHandler(
            log_file,
            when="D",
            interval=1,
            backupCount=retention_days,
            encoding="utf-8"
        )
        handler.setLevel(self.log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(handler)
        
        # Also add console handler for debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: dict[str, Any],
        result: str,
        approval_status: str = "approved",
        approved_by: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Log an audit event.
        
        Args:
            action_type: Type of action (e.g., "email_send", "invoice_create")
            actor: Who performed the action (e.g., "claude_code", "human_user")
            target: Target of the action (e.g., "client@example.com")
            parameters: Action parameters
            result: Result (success, failure, pending)
            approval_status: Approval status (pending, approved, rejected)
            approved_by: Who approved the action (if applicable)
            error: Error message (if failed)
            retry_count: Number of retry attempts
            metadata: Additional metadata
            
        Returns:
            The log entry as a dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "result": result,
            "error": error,
            "retry_count": retry_count,
            "metadata": metadata or {},
        }
        
        # Log the entry
        log_level = logging.ERROR if result == "failure" else logging.INFO
        self.logger.log(log_level, json.dumps(entry))
        
        return entry
    
    def log_action(
        self,
        action_type: str,
        actor: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Simplified logging for common actions.
        
        Args:
            action_type: Type of action
            actor: Who performed the action
            details: Action details
            
        Returns:
            The log entry
        """
        return self.log(
            action_type=action_type,
            actor=actor,
            target=details.get("target", "unknown"),
            parameters=details,
            result="success",
        )
    
    def log_error(
        self,
        action_type: str,
        actor: str,
        error: str,
        target: str = "unknown",
        parameters: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Log an error event.
        
        Args:
            action_type: Type of action that failed
            actor: Who performed the action
            error: Error message
            target: Target of the action
            parameters: Action parameters
            
        Returns:
            The log entry
        """
        return self.log(
            action_type=action_type,
            actor=actor,
            target=target,
            parameters=parameters or {},
            result="failure",
            error=error,
        )
    
    def log_approval_request(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Log an approval request.
        
        Args:
            action_type: Type of action requiring approval
            actor: Who is requesting
            target: Target of the action
            parameters: Action parameters
            
        Returns:
            The log entry
        """
        return self.log(
            action_type=action_type,
            actor=actor,
            target=target,
            parameters=parameters,
            result="pending",
            approval_status="pending",
        )
    
    def log_approval_granted(
        self,
        action_type: str,
        approved_by: str,
        target: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Log an approval grant.
        
        Args:
            action_type: Type of action approved
            approved_by: Who approved
            target: Target of the action
            parameters: Action parameters
            
        Returns:
            The log entry
        """
        return self.log(
            action_type=action_type,
            actor=approved_by,
            target=target,
            parameters=parameters,
            result="pending",
            approval_status="approved",
            approved_by=approved_by,
        )
    
    def query(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_type: Optional[str] = None,
        actor: Optional[str] = None,
        result: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Query audit logs.
        
        Args:
            start_date: Start date for query
            end_date: End date for query
            action_type: Filter by action type
            actor: Filter by actor
            result: Filter by result
            limit: Maximum number of entries to return
            
        Returns:
            List of matching log entries
        """
        entries = []
        
        # Get all log files
        log_files = sorted(self.log_dir.glob("audit.log*"))
        
        for log_file in log_files:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line.split(" - ", 3)[-1])
                                
                                # Apply filters
                                if start_date and entry["timestamp"] < start_date.isoformat():
                                    continue
                                if end_date and entry["timestamp"] > end_date.isoformat():
                                    continue
                                if action_type and entry["action_type"] != action_type:
                                    continue
                                if actor and entry["actor"] != actor:
                                    continue
                                if result and entry["result"] != result:
                                    continue
                                
                                entries.append(entry)
                                
                                if len(entries) >= limit:
                                    return entries
                            except json.JSONDecodeError:
                                continue
            except Exception:
                continue
        
        return entries
    
    def cleanup_old_logs(self) -> int:
        """
        Remove logs older than retention period.
        
        Returns:
            Number of files removed
        """
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        removed = 0
        
        for log_file in self.log_dir.glob("audit.log.*"):
            try:
                # Extract date from filename (audit.log.YYYY-MM-DD)
                date_str = log_file.name.replace("audit.log.", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff:
                    log_file.unlink()
                    removed += 1
            except Exception:
                continue
        
        return removed
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """
        Get audit log statistics.
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Statistics dictionary
        """
        entries = self.query(start_date=start_date, end_date=end_date, limit=10000)
        
        stats = {
            "total_entries": len(entries),
            "by_result": {},
            "by_action_type": {},
            "by_actor": {},
            "error_count": 0,
            "approval_pending": 0,
        }
        
        for entry in entries:
            # Count by result
            result = entry.get("result", "unknown")
            stats["by_result"][result] = stats["by_result"].get(result, 0) + 1
            
            # Count by action type
            action_type = entry.get("action_type", "unknown")
            stats["by_action_type"][action_type] = stats["by_action_type"].get(action_type, 0) + 1
            
            # Count by actor
            actor = entry.get("actor", "unknown")
            stats["by_actor"][actor] = stats["by_actor"].get(actor, 0) + 1
            
            # Count errors
            if entry.get("result") == "failure":
                stats["error_count"] += 1
            
            # Count pending approvals
            if entry.get("approval_status") == "pending":
                stats["approval_pending"] += 1
        
        return stats


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def log_audit_event(**kwargs) -> dict[str, Any]:
    """Log an audit event using the global logger."""
    return get_audit_logger().log(**kwargs)
