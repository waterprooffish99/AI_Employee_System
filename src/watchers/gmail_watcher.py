"""
Gmail Watcher - Monitors Gmail for new important/unread messages.

Following the Hackathon-0 specification for the Gmail Watcher implementation.
Creates action files in Needs_Action/ folder for Claude Code to process.

Silver Tier Requirement: Two or more Watcher scripts
"""

import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from .base_watcher import BaseWatcher

# Optional imports - will fail gracefully if not installed
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import client_config
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    Credentials = None
    build = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GmailWatcher(BaseWatcher):
    """
    Gmail Watcher - Monitors Gmail for new important/unread messages.
    
    Creates .md action files in Needs_Action/ folder when new emails arrive.
    Follows the BaseWatcher pattern from Hackathon-0 spec.
    """
    
    def __init__(
        self,
        vault_path: str,
        credentials_path: str = None,
        token_path: str = None,
        check_interval: int = 120,
        query: str = 'is:unread is:important'
    ):
        """
        Initialize the Gmail Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail OAuth credentials JSON
            token_path: Path to store OAuth token
            check_interval: Seconds between checks
            query: Gmail search query for messages to monitor
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = credentials_path
        self.token_path = token_path or str(self.vault_path.parent / 'gmail_token.json')
        self.query = query
        self.processed_ids = set()
        self.service = None
        
        # Load previously processed message IDs from cache
        self._load_cache()
    
    def _load_cache(self):
        """Load cache of processed message IDs."""
        cache_file = self.vault_path.parent / '.gmail_cache'
        if cache_file.exists():
            try:
                self.processed_ids = set(cache_file.read_text().splitlines())
                logger.info(f'Loaded {len(self.processed_ids)} message IDs from cache')
            except Exception as e:
                logger.warning(f'Could not load cache: {e}')
    
    def _save_cache(self):
        """Save cache of processed message IDs."""
        cache_file = self.vault_path.parent / '.gmail_cache'
        try:
            # Keep only last 1000 IDs to prevent unbounded growth
            ids = list(self.processed_ids)[-1000:]
            cache_file.write_text('\n'.join(ids))
        except Exception as e:
            logger.warning(f'Could not save cache: {e}')
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        if not GOOGLE_AVAILABLE:
            logger.error('Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib')
            return False
        
        try:
            creds = None
            
            # Load token if exists
            token_file = Path(self.token_path)
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(token_file, ['https://www.googleapis.com/auth/gmail.readonly'])
            
            # If no valid credentials, try to get from credentials file
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path or not Path(self.credentials_path).exists():
                        logger.error(f'Credentials file not found: {self.credentials_path}')
                        return False
                    
                    with open(self.credentials_path) as f:
                        client_config_data = client_config.load_from_client_config_file(f)
                    
                    # For now, log that manual auth is needed
                    logger.warning('Manual OAuth flow required. See documentation for setup.')
                    return False
            
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info('Gmail authentication successful')
            return True
            
        except Exception as e:
            logger.error(f'Authentication error: {e}')
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new Gmail messages.
        
        Returns:
            List of new messages to process
        """
        if not self.service:
            if not self._authenticate():
                return []
        
        try:
            # Fetch messages matching query
            results = self.service.users().messages().list(
                userId='me',
                q=self.query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]
            
            if new_messages:
                logger.info(f'Found {len(new_messages)} new messages')
            
            return new_messages
            
        except HttpError as e:
            logger.error(f'Gmail API error: {e}')
            if e.resp.status == 401:
                # Token expired, will re-auth on next check
                self.service = None
            return []
        except Exception as e:
            logger.error(f'Error checking Gmail: {e}')
            return []
    
    def create_action_file(self, message: Dict[str, str]) -> Path:
        """
        Create an action file in Needs_Action folder for a Gmail message.
        
        Args:
            message: Gmail message dict with 'id' key
            
        Returns:
            Path to created action file
        """
        try:
            # Fetch full message
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            # Determine priority
            priority = 'high' if 'important' in self.query else 'normal'
            
            # Create action file content
            timestamp = datetime.now().isoformat()
            content = f"""---
type: email
message_id: {message['id']}
from: {headers.get('From', 'Unknown')}
to: {headers.get('To', '')}
subject: {headers.get('Subject', 'No Subject')}
received: {timestamp}
priority: {priority}
status: pending
---

# Email: {headers.get('Subject', 'No Subject')}

**From**: {headers.get('From', 'Unknown')}  
**Received**: {timestamp}  
**Priority**: {priority}

## Content Preview
{msg.get('snippet', 'No preview available')}

## Suggested Actions
- [ ] Read full email
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Notes
*Add any notes or context for processing this email*

---
*Created by Gmail Watcher - Hackathon 0 Silver Tier*
"""
            
            # Write action file
            filepath = self.needs_action / f'EMAIL_{message["id"]}_{timestamp[:10]}.md'
            filepath.write_text(content)
            
            # Mark as processed
            self.processed_ids.add(message['id'])
            self._save_cache()
            
            logger.info(f'Created action file: {filepath}')
            return filepath
            
        except Exception as e:
            logger.error(f'Error creating action file: {e}')
            raise
    
    def run_once(self) -> int:
        """
        Run a single check cycle.
        
        Returns:
            Number of new messages processed
        """
        items = self.check_for_updates()
        count = 0
        
        for item in items:
            try:
                self.create_action_file(item)
                count += 1
            except Exception as e:
                logger.error(f'Error processing message {item.get("id", "unknown")}: {e}')
        
        return count
    
    def run(self):
        """
        Main loop for the Gmail Watcher.
        
        Continuously checks for new emails and creates action files.
        """
        logger.info(f'Starting GmailWatcher (check interval: {self.check_interval}s)')
        
        while True:
            try:
                count = self.run_once()
                if count > 0:
                    logger.info(f'Processed {count} new messages')
            except Exception as e:
                logger.error(f'Error in watcher loop: {e}')
            
            time.sleep(self.check_interval)


if __name__ == '__main__':
    import os
    import sys
    
    # Get vault path from environment or use default
    vault_path = os.getenv('VAULT_PATH', '/mnt/c/Users/WaterProof Fish/Documents/AI_Employee_System/AI_Employee_Vault')
    
    # Get credentials path from environment
    credentials_path = os.getenv('GMAIL_CREDENTIALS')
    
    print('=== Gmail Watcher Test ===')
    print(f'Vault Path: {vault_path}')
    print(f'Credentials: {credentials_path or "Not configured"}')
    
    if not credentials_path:
        print()
        print('To configure Gmail Watcher:')
        print('1. Create OAuth credentials at https://console.cloud.google.com/')
        print('2. Download credentials.json')
        print('3. Set GMAIL_CREDENTIALS environment variable')
        print('4. Run: python -m src.watchers.gmail_watcher')
        sys.exit(0)
    
    watcher = GmailWatcher(
        vault_path=vault_path,
        credentials_path=credentials_path,
        check_interval=30  # Short interval for testing
    )
    
    print()
    print('Running single check...')
    count = watcher.run_once()
    print(f'Found {count} new messages')
    
    if count == 0:
        print('No new messages. Start watcher with: python -m src.watchers.gmail_watcher')
