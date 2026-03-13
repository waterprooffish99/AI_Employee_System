"""
Sync Conflict Resolution for AI Employee System - Platinum Tier

Handles sync conflicts between cloud and local vault instances.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class SyncConflictResolver:
    """
    Sync conflict resolver.
    
    Features:
    - Detect conflicts
    - Backup before resolution
    - Timestamp-based resolution
    - Manual resolution flagging
    """
    
    def __init__(self, vault_path: Optional[str | Path] = None):
        """
        Initialize conflict resolver.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        self.conflict_dir = self.vault_path / ".conflicts"
        self.conflict_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Sync Conflict Resolver initialized")
    
    def detect_conflicts(self, local_file: Path, remote_file: Path) -> bool:
        """
        Detect if there's a conflict between local and remote files.
        
        Args:
            local_file: Local file path
            remote_file: Remote file path
            
        Returns:
            True if conflict detected
        """
        if not local_file.exists():
            return False
        if not remote_file.exists():
            return False
        
        # Compare content
        local_content = local_file.read_text()
        remote_content = remote_file.read_text()
        
        return local_content != remote_content
    
    def backup_file(self, file: Path, reason: str = "conflict") -> Path:
        """
        Backup a file before resolution.
        
        Args:
            file: File to backup
            reason: Reason for backup
            
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file.stem}_{timestamp}_{reason}{file.suffix}"
        backup_path = self.conflict_dir / backup_name
        
        shutil.copy2(file, backup_path)
        
        logger.info(f"Backed up {file} to {backup_path}")
        return backup_path
    
    def resolve_timestamp(self, local_file: Path, remote_file: Path, prefer: str = "newer") -> Path:
        """
        Resolve conflict based on timestamp.
        
        Args:
            local_file: Local file path
            remote_file: Remote file path
            prefer: "newer" or "older"
            
        Returns:
            Path to winning file
        """
        local_mtime = local_file.stat().st_mtime
        remote_mtime = remote_file.stat().st_mtime
        
        if prefer == "newer":
            winner = local_file if local_mtime > remote_mtime else remote_file
        else:  # older
            winner = local_file if local_mtime < remote_mtime else remote_file
        
        # Backup loser
        loser = remote_file if winner == local_file else local_file
        self.backup_file(loser, "conflict_loser")
        
        logger.info(f"Resolved conflict: {winner} wins (prefer={prefer})")
        return winner
    
    def resolve_manual(self, local_file: Path, remote_file: Path) -> Path:
        """
        Flag conflict for manual resolution.
        
        Args:
            local_file: Local file path
            remote_file: Remote file path
            
        Returns:
            Path to conflict marker file
        """
        # Backup both versions
        self.backup_file(local_file, "conflict_local")
        self.backup_file(remote_file, "conflict_remote")
        
        # Create conflict marker
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        conflict_marker = local_file.parent / f"{local_file.stem}_CONFLICT_{timestamp}{local_file.suffix}"
        
        content = f"""---
type: conflict_marker
created: {datetime.now().isoformat()}
local_file: {local_file}
remote_file: {remote_file}
status: requires_manual_resolution
---

# CONFLICT REQUIRES MANUAL RESOLUTION

This file has conflicting versions between cloud and local.

## Local Version
Location: {local_file}
Modified: {datetime.fromtimestamp(local_file.stat().st_mtime).isoformat()}

## Remote Version
Location: {remote_file}
Modified: {datetime.fromtimestamp(remote_file.stat().st_mtime).isoformat()}

## Resolution Steps

1. Review both versions above (backed up in `.conflicts/` folder)
2. Manually merge the content
3. Save the merged version
4. Delete this conflict marker file

## Backups

Both versions have been backed up to:
- Local backup: `{self.conflict_dir}/{local_file.stem}_*_conflict_local{local_file.suffix}`
- Remote backup: `{self.conflict_dir}/{local_file.stem}_*_conflict_remote{local_file.suffix}`

---

**DO NOT USE THIS FILE** - Merge manually and delete this marker.
"""
        
        conflict_marker.write_text(content)
        
        logger.warning(f"Conflict flagged for manual resolution: {conflict_marker}")
        return conflict_marker
    
    def resolve_git_merge(self, file: Path) -> bool:
        """
        Resolve Git merge conflict in file.
        
        Args:
            file: File with merge conflict
            
        Returns:
            True if resolved
        """
        content = file.read_text()
        
        # Check for Git conflict markers
        if "<<<<<<<" not in content or "=======" not in content or ">>>>>>>" not in content:
            logger.info(f"No Git conflict markers in {file}")
            return True  # No conflict
        
        # Backup conflicted file
        self.backup_file(file, "git_conflict")
        
        # Flag for manual resolution
        logger.warning(f"Git conflict in {file} - requires manual resolution")
        return False
    
    def auto_resolve_markdown(self, local_file: Path, remote_file: Path) -> Optional[Path]:
        """
        Attempt automatic resolution for Markdown files.
        
        For Markdown files, we can often merge by appending remote changes.
        
        Args:
            local_file: Local file path
            remote_file: Remote file path
            
        Returns:
            Path to resolved file, or None if manual resolution needed
        """
        if local_file.suffix != ".md":
            return None  # Only auto-resolve Markdown
        
        local_content = local_file.read_text()
        remote_content = remote_file.read_text()
        
        # If local is unchanged, use remote
        if not self.detect_conflicts(local_file, remote_file):
            return remote_file
        
        # If both changed, flag for manual resolution
        logger.info(f"Both versions changed, flagging for manual resolution: {local_file}")
        return None


# Singleton instance
_conflict_resolver: Optional[SyncConflictResolver] = None


def get_conflict_resolver(vault_path: Optional[str | Path] = None) -> SyncConflictResolver:
    """Get or create conflict resolver instance."""
    global _conflict_resolver
    if _conflict_resolver is None:
        _conflict_resolver = SyncConflictResolver(vault_path)
    return _conflict_resolver
