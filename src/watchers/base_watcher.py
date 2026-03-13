"""
Base Watcher - Abstract base class for all watchers.

Following the Hackathon-0 specification pattern.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers.
    
    Watchers monitor external systems (Gmail, WhatsApp, filesystems)
    and create action files in the Needs_Action folder for Claude Code to process.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the base watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (for polling-based watchers)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure Needs_Action directory exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            List of new items that need to be processed
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md action file in Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created action file
        """
        pass
    
    def run(self):
        """
        Main loop for the watcher.
        
        Continuously checks for updates and creates action files.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error in watcher loop: {e}')
            
            time.sleep(self.check_interval)
    
    def start(self):
        """Start the watcher (for non-polling implementations)."""
        pass
    
    def stop(self):
        """Stop the watcher (for non-polling implementations)."""
        pass
