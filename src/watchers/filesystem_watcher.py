"""
File System Watcher - Monitors a drop folder for new files and creates action files in Needs_Action.

This watcher follows the base_watcher pattern from the Hackathon-0 specification.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .base_watcher import BaseWatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DropFolderHandler(FileSystemEventHandler):
    """Handles file creation events in the drop folder."""

    def __init__(self, vault_path: Path):
        super().__init__()
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.logger = logging.getLogger(__name__)

    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return

        source = Path(event.src_path)
        self.logger.info(f'New file detected: {source.name}')

        # Skip hidden files and already processed files
        if source.name.startswith('.') or source.suffix == '.md':
            return

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_name = f'FILE_{timestamp}_{source.name}'
        dest = self.needs_action / dest_name

        # Copy file to Needs_Action
        try:
            shutil.copy2(source, dest)
            self.logger.info(f'Copied file to: {dest}')

            # Create metadata file
            self.create_metadata(source, dest)
        except Exception as e:
            self.logger.error(f'Error copying file: {e}')

    def create_metadata(self, source: Path, dest: Path):
        """Create a metadata markdown file for the dropped file."""
        meta_path = dest.with_suffix('.md')

        file_size = source.stat().st_size
        file_size_kb = file_size / 1024

        content = f"""---
type: file_drop
original_name: {source.name}
dropped_name: {dest.name}
size: {file_size} bytes ({file_size_kb:.2f} KB)
dropped_at: {datetime.now().isoformat()}
status: pending
---

# File Drop for Processing

A new file has been dropped for processing.

## File Details
- **Original Name**: {source.name}
- **Stored As**: {dest.name}
- **Size**: {file_size} bytes ({file_size_kb:.2f} KB)
- **Dropped At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Suggested Actions
- [ ] Review file content
- [ ] Determine required action
- [ ] Process or forward as needed
- [ ] Move to /Done when complete

## Notes
*Add any notes or context for processing this file*
"""

        try:
            meta_path.write_text(content)
            self.logger.info(f'Created metadata file: {meta_path}')
        except Exception as e:
            self.logger.error(f'Error creating metadata file: {e}')


class FileSystemWatcher:
    """
    Watches a drop folder for new files and creates action files in Needs_Action.

    Usage:
        watcher = FileSystemWatcher(vault_path='/path/to/vault', drop_path='/path/to/drop')
        watcher.run()
    """

    def __init__(self, vault_path: str, drop_path: str = None, check_interval: int = 60):
        """
        Initialize the file system watcher.

        Args:
            vault_path: Path to the Obsidian vault
            drop_path: Path to the drop folder (defaults to <vault>/Drop)
            check_interval: Interval in seconds (not used with watchdog)
        """
        self.vault_path = Path(vault_path)
        self.drop_path = Path(drop_path) if drop_path else self.vault_path / 'Drop'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.observer = None

        # Ensure directories exist
        self.drop_path.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)

        logger.info(f'FileSystemWatcher initialized')
        logger.info(f'  Drop folder: {self.drop_path}')
        logger.info(f'  Needs_Action: {self.needs_action}')
    
    def start(self):
        """Start the file system watcher."""
        logger.info(f'Starting FileSystemWatcher on: {self.drop_path}')

        # Use polling instead of events (more reliable on WSL2/Windows)
        self.running = True
        import threading
        self.thread = threading.Thread(target=self._poll_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Give observer time to initialize
        import time
        time.sleep(1)

        logger.info('FileSystemWatcher started successfully (polling mode)')
    
    def _poll_loop(self):
        """Poll the drop folder for new files."""
        known_files = set()
        
        # Get initial files
        if self.drop_path.exists():
            known_files = {f.name for f in self.drop_path.iterdir() if f.is_file()}
        
        import time
        while self.running:
            time.sleep(2)  # Poll every 2 seconds
            
            if not self.drop_path.exists():
                continue
            
            # Get current files
            current_files = {f.name for f in self.drop_path.iterdir() if f.is_file()}
            
            # Find new files
            new_files = current_files - known_files
            
            for filename in new_files:
                if filename.startswith('.') or filename.endswith('.md'):
                    continue
                    
                file_path = self.drop_path / filename
                logger.info(f'New file detected: {filename}')
                
                # Process the file
                try:
                    self._process_file(file_path)
                    known_files.add(filename)
                except Exception as e:
                    logger.error(f'Error processing {filename}: {e}')
    
    def _process_file(self, source: Path):
        """Process a dropped file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_name = f'FILE_{timestamp}_{source.name}'
        dest = self.needs_action / dest_name
        
        shutil.copy2(source, dest)
        logger.info(f'Copied file to: {dest}')
        
        # Create metadata
        self._create_metadata(source, dest)
    
    def _create_metadata(self, source: Path, dest: Path):
        """Create metadata file."""
        meta_path = dest.with_suffix('.md')
        file_size = source.stat().st_size
        
        content = f"""---
type: file_drop
original_name: {source.name}
dropped_name: {dest.name}
size: {file_size} bytes
dropped_at: {datetime.now().isoformat()}
status: pending
---

# File Drop for Processing

**Original Name**: {source.name}
**Stored As**: {dest.name}
**Size**: {file_size} bytes

## Actions
- [ ] Review and process
- [ ] Move to /Done when complete
"""
        meta_path.write_text(content)
        logger.info(f'Created metadata: {meta_path}')
    
    def stop(self):
        """Stop the file system watcher."""
        logger.info('Stopping FileSystemWatcher...')
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=5)
        logger.info('FileSystemWatcher stopped')
    
    def run(self):
        """Run the file system watcher."""
        self.start()
        try:
            while True:
                import time
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f'Error in watcher loop: {e}')
            self.stop()
            raise


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='File System Watcher')
    parser.add_argument('--vault', default='./AI_Employee_Vault', help='Path to Obsidian vault')
    parser.add_argument('--drop', default=None, help='Path to drop folder')

    args = parser.parse_args()

    watcher = FileSystemWatcher(vault_path=args.vault, drop_path=args.drop)
    watcher.run()
